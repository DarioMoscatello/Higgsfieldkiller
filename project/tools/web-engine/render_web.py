"""Frame-exact video from any HTML page - Canvas 2D, SVG, three.js/WebGL,
anime.js - through headless Chrome (CDP) and FFmpeg.

The page is a folder with an index.html that sets window.__ready = true once it
has loaded (or window.__error = "message") and defines window.renderAt(t): draw
the frame at t seconds and return "ok" (or a promise of it). Every frame is a
function of t alone, so any range renders identically and ranges can be
concatenated. tools/web-engine/lib is served at /lib/ (three.js, anime.js), and
templates live in tools/web-engine/templates/.

  python tools/web-engine/render_web.py <page_dir> --out clip.mp4 --end 5 [--start 0] [--fps 30]
  python tools/web-engine/render_web.py <page_dir> --stills 0.5,2,4.25 --out stills_dir
  python tools/web-engine/render_web.py <page_dir> --frames-dir strip_dir --start 1 --end 2
  python tools/web-engine/render_web.py <page_dir> --info

GPU by default: Chrome draws with Direct3D 11 and FFmpeg encodes with NVENC.
--cpu draws with SwiftShader and encodes with x264. The Chrome profile lives in a
temp folder. Set KIT_CHROME if Chrome is installed somewhere else.
Progress goes to stdout: redirect long renders to a log file.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import functools
import http.server
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import websockets
from PIL import Image

LIB = Path(__file__).resolve().parent / "lib"
CHROME = Path(os.environ.get("KIT_CHROME", r"C:\Program Files\Google\Chrome\Application\chrome.exe"))
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
RGB_TO_709 = ("scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+full_chroma_inp,"
              "format=yuv420p")


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves the page folder at / and tools/web-engine/lib at /lib/."""

    def translate_path(self, path: str) -> str:
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean.startswith("/lib/"):
            return str(LIB / urllib.request.url2pathname(clean[len("/lib/"):]))
        return super().translate_path(path)

    def log_message(self, *args: object) -> None:  # silence per-request logging
        pass

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start_server(page: Path) -> tuple[http.server.ThreadingHTTPServer, int]:
    Handler.extensions_map.update({".js": "text/javascript", ".mjs": "text/javascript",
                                   ".json": "application/json", ".svg": "image/svg+xml",
                                   ".ttf": "font/ttf", ".woff2": "font/woff2", ".wasm": "application/wasm"})
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Handler, directory=str(page)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


class CDP:
    def __init__(self, socket: object) -> None:
        self.socket = socket
        self.seq = 0

    @staticmethod
    def _event(msg: dict) -> None:
        method, params = msg.get("method"), msg.get("params", {})
        if method == "Runtime.consoleAPICalled":
            text = " ".join(str(a.get("value", a.get("description", ""))) for a in params.get("args", []))
            print(f"[page {params.get('type')}] {text}", flush=True)
        elif method == "Runtime.exceptionThrown":
            det = params.get("exceptionDetails", {})
            print(f"[page exception] {det.get('exception', {}).get('description') or det.get('text')}", flush=True)

    async def call(self, method: str, params: dict | None = None) -> dict:
        self.seq += 1
        ident = self.seq
        await self.socket.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(await self.socket.recv())
            if msg.get("id") == ident:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method}: {msg['error']}")
                return msg.get("result", {})
            if "method" in msg:
                self._event(msg)

    async def evaluate(self, expr: str) -> object:
        res = await self.call("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        if "exceptionDetails" in res:
            det = res["exceptionDetails"]
            raise RuntimeError(f"evaluate failed: {det.get('exception', {}).get('description') or det}")
        return res.get("result", {}).get("value")


GPU_NAME = """(() => { const c = document.createElement('canvas'); const gl = c.getContext('webgl');
  if (!gl) return 'no WebGL'; const d = gl.getExtension('WEBGL_debug_renderer_info');
  return d ? gl.getParameter(d.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER); })()"""


def kill_profile_processes(profile: Path) -> None:
    """Stop any chrome.exe still using this run's private profile (and only those)."""
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { $_.CommandLine -like '*"
          + str(profile).replace("'", "''") + "*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force "
          "-ErrorAction SilentlyContinue }")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False, creationflags=NO_WINDOW)


async def page_socket(profile: Path) -> str:
    port_file = profile / "DevToolsActivePort"
    for _ in range(300):
        if port_file.is_file() and port_file.read_text(encoding="ascii").strip():
            break
        await asyncio.sleep(0.1)
    else:
        raise RuntimeError("Chrome DevTools port did not appear")
    port = int(port_file.read_text(encoding="ascii").splitlines()[0])
    for _ in range(200):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1) as r:
                for p in json.load(r):
                    if p.get("type") == "page":
                        return str(p["webSocketDebuggerUrl"])
        except (OSError, ValueError):
            pass
        await asyncio.sleep(0.1)
    raise RuntimeError("no page target")


def encoder_args(args: argparse.Namespace, out: Path) -> list[str]:
    use_nvenc = args.encoder == "nvenc" or (args.encoder == "auto" and not args.cpu)
    codec = (["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", str(args.cq), "-b:v", "0"]
             if use_nvenc else ["-c:v", "libx264", "-preset", "medium", "-crf", str(args.crf)])
    # Frames are full-range RGB: convert with the BT.709 matrix to the limited range the tags declare, with
    # accurate rounding. The default swscale path came out 1.4 levels dark from PNG and 3 from JPEG; this one
    # is within 1 level of a lossless still (measured).
    return ["ffmpeg", "-v", "error", "-nostdin", "-n", "-f", "image2pipe", "-vcodec", "mjpeg" if args.jpeg else "png",
            "-framerate", str(args.fps), "-i", "pipe:0", "-an", *codec,
            "-vf", f"format=rgb24,{RGB_TO_709}", "-color_range", "tv",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-movflags", "+faststart", str(out)]


async def session(args: argparse.Namespace) -> None:
    page = Path(args.page).resolve()
    if not (page / "index.html").is_file():
        raise SystemExit(f"{page} has no index.html")
    server, port = start_server(page)
    profile = Path(tempfile.gettempdir()) / f"kit-web-{os.getpid()}-{time.time_ns()}"
    profile.mkdir(parents=True)
    chrome_log = (profile / "chrome.log").open("wb")
    drawing = (["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"] if args.cpu else
               ["--ignore-gpu-blocklist", "--enable-gpu-rasterization", "--use-angle=d3d11"])
    url = f"http://127.0.0.1:{port}/index.html" + (f"?{args.query}" if args.query else "")
    chrome = subprocess.Popen(
        [str(CHROME), "--headless=new", "--no-first-run", "--no-default-browser-check",
         "--disable-background-networking", "--disable-extensions", "--hide-scrollbars", "--mute-audio",
         *drawing, "--disable-background-timer-throttling", "--disable-renderer-backgrounding",
         "--disable-backgrounding-occluded-windows", "--remote-debugging-address=127.0.0.1",
         "--remote-debugging-port=0", f"--user-data-dir={profile}", f"--window-size={args.width},{args.height}",
         "--force-device-scale-factor=1", url],
        stdin=subprocess.DEVNULL, stdout=chrome_log, stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    encoder = None
    enc_log = None  # the encoder's stderr file: closed before the profile folder is removed
    black = 0
    try:
        async with websockets.connect(await page_socket(profile), max_size=256_000_000, ping_timeout=120) as sock:
            cdp = CDP(sock)
            await cdp.call("Runtime.enable")
            await cdp.call("Emulation.setDeviceMetricsOverride", {"width": args.width, "height": args.height,
                                                                   "deviceScaleFactor": 1, "mobile": False})
            for _ in range(1200):
                ready = await cdp.evaluate("window.__ready === true ? 'yes' : (window.__error || 'no')")
                if ready == "yes":
                    break
                if ready not in ("no", None):
                    raise RuntimeError(f"page failed: {ready}")
                await asyncio.sleep(0.1)
            else:
                raise RuntimeError("page did not set window.__ready within 120 s")
            print(f"page ready; drawing on {await cdp.evaluate(GPU_NAME)}", flush=True)
            if args.info:
                print(await cdp.evaluate("JSON.stringify(window.__info || {})"), flush=True)
                return

            async def shot(t: float, fmt: str) -> bytes:
                # An all-black frame is retried at the same time (a WebGL readback can come back empty),
                # never replaced by a neighbour. A scene that is really black is kept
                # after three tries and counted, unless --strict-black makes it an error.
                nonlocal black
                for attempt in range(3):
                    res = await cdp.evaluate(f"window.renderAt({t:.9f})")
                    if res != "ok":
                        raise RuntimeError(f"renderAt({t}) returned {res!r}")
                    p = {"format": fmt, "fromSurface": True, "captureBeyondViewport": False}
                    if fmt == "jpeg":
                        p["quality"] = args.quality
                    data = base64.b64decode((await cdp.call("Page.captureScreenshot", p))["data"])
                    if Image.open(io.BytesIO(data)).convert("L").getextrema()[1] > 0:
                        return data
                    if attempt < 2:
                        print(f"all-black frame at t={t:.4f}; retrying", flush=True)
                if args.strict_black:
                    raise RuntimeError(f"persistent black frame at t={t:.4f}")
                black += 1
                return data

            if args.stills:
                out = Path(args.out)
                out.mkdir(parents=True, exist_ok=True)
                for tt in [float(x) for x in args.stills.split(",") if x.strip()]:
                    name = out / f"still-{tt:08.3f}.png"
                    name.write_bytes(await shot(tt, "png"))
                    print(f"still {tt:.3f}s -> {name}", flush=True)
            elif args.frames_dir:
                out = Path(args.frames_dir)
                out.mkdir(parents=True, exist_ok=True)
                for n in range(round(args.start * args.fps), round(args.end * args.fps)):
                    (out / f"f{n:05d}.jpg").write_bytes(await shot(n / args.fps, "jpeg"))
                print(f"wrote frames to {out}", flush=True)
            else:
                if args.end is None:
                    raise SystemExit("--end is required for a video")
                out = Path(args.out)
                if out.exists():
                    raise FileExistsError(f"{out} exists: render to a new file")
                out.parent.mkdir(parents=True, exist_ok=True)
                enc_log = (profile / "ffmpeg.log").open("wb")
                encoder = subprocess.Popen(encoder_args(args, out), stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                           stderr=enc_log, creationflags=NO_WINDOW)
                n0, n1 = round(args.start * args.fps), round(args.end * args.fps)
                t0 = time.time()
                for n in range(n0, n1):
                    encoder.stdin.write(await shot(n / args.fps, "jpeg" if args.jpeg else "png"))
                    if (n - n0) % (args.fps * 2) == 0:
                        done = n - n0 + 1
                        print(f"frame {n}/{n1}  {time.time() - t0:.0f}s, {(time.time() - t0) / done:.3f}s/frame",
                              flush=True)
                encoder.stdin.close()
                if encoder.wait(timeout=600) != 0:
                    enc_log.close()
                    raise RuntimeError((profile / "ffmpeg.log").read_text(errors="replace")[-2000:])
                encoder = None
                print(f"wrote {out} ({n1 - n0} frames at {args.fps} fps)", flush=True)
            if black:
                print(f"note: {black} frame(s) stayed all black after retries; check that the scene is black there",
                      flush=True)
    finally:
        if encoder is not None:
            try:
                if encoder.stdin and not encoder.stdin.closed:
                    encoder.stdin.close()
            except OSError:
                pass
            encoder.terminate()
            encoder.wait(timeout=30)
        # Popen.terminate() stops only the launcher on Windows: kill the whole browser tree.
        subprocess.run(["taskkill", "/PID", str(chrome.pid), "/T", "/F"], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=False, creationflags=NO_WINDOW)
        try:
            chrome.wait(timeout=20)
        except subprocess.TimeoutExpired:
            chrome.kill()
        kill_profile_processes(profile)
        chrome_log.close()
        if enc_log is not None and not enc_log.closed:
            enc_log.close()
        server.shutdown()
        for _ in range(120):
            shutil.rmtree(profile, ignore_errors=True)
            if not profile.exists():
                break
            time.sleep(0.25)
        else:
            print(f"warning: could not remove {profile}; clean_render_temp.py removes it later", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Frame-exact video from an HTML page.")
    ap.add_argument("page", help="folder with index.html")
    ap.add_argument("--out", default="out.mp4", help="video file, or the folder for --stills")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--stills", default="", help="comma-separated times: PNG stills instead of a video")
    ap.add_argument("--frames-dir", default="", help="write every frame of [start, end) as JPEG for QA strips")
    ap.add_argument("--info", action="store_true", help="print window.__info and the graphics device, then stop")
    ap.add_argument("--cpu", action="store_true", help="draw with SwiftShader and encode with x264")
    ap.add_argument("--encoder", choices=("auto", "nvenc", "x264"), default="auto")
    ap.add_argument("--crf", type=int, default=17, help="x264 quality")
    ap.add_argument("--cq", type=int, default=19, help="NVENC quality")
    ap.add_argument("--jpeg", action="store_true", help="capture JPEG frames: faster, about 1 level less exact")
    ap.add_argument("--quality", type=int, default=95, help="JPEG capture quality")
    ap.add_argument("--strict-black", action="store_true", help="fail on a frame that stays all black")
    ap.add_argument("--query", default="", help="URL query passed to the page, e.g. variant=b")
    asyncio.run(session(ap.parse_args()))


if __name__ == "__main__":
    main()
