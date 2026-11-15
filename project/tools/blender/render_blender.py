"""Render a Blender scene to a video file.

  python tools/blender/render_blender.py --script scene.py --out clip.mp4 [--blend file.blend]
         [--frames 1-120] [--fps 30] [--size 1920x1080] [--engine eevee|cycles|workbench] [--samples 64] [--cpu]

Blender is called by its full path: the Windows default install of Blender 5.2, or the path in the
KIT_BLENDER environment variable. --script builds or edits
the scene in Python (see templates/); --blend opens a saved file first; either or both.

The GPU is used by default: EEVEE always draws on the graphics card, and Cycles is switched to OptiX
(or CUDA) on an NVIDIA card; --cpu renders Cycles on the processor. Frames are rendered as PNG into
a temp folder, then encoded with
NVENC (--cpu: x264) using the same accurate BT.709 conversion as the web engine. Never overwrites a file.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

BLENDER = Path(os.environ.get("KIT_BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"))
RGB_TO_709 = ("scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+full_chroma_inp,"
              "format=yuv420p")

SETUP = """
import bpy
scene = bpy.context.scene
scene.render.engine = {engine!r}
scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = {w}, {h}, 100
scene.render.fps, scene.render.fps_base = {fps}, 1.0
scene.render.image_settings.file_format = 'PNG'
if {engine!r} == 'CYCLES':
    scene.cycles.samples = {samples}
    if {gpu}:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for kind in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = kind
                prefs.get_devices()
                if any(d.type == kind for d in prefs.devices):
                    break
            except TypeError:
                continue
        for d in prefs.devices:
            d.use = d.type != 'CPU'
        scene.cycles.device = 'GPU'
        print('blender: Cycles on', prefs.compute_device_type, [d.name for d in prefs.devices if d.use])
    else:
        scene.cycles.device = 'CPU'
"""

LATE = """
import bpy
scene = bpy.context.scene
first, last = {first}, {last}
if first is not None:
    scene.frame_start, scene.frame_end = first, last
print('blender: frames', scene.frame_start, 'to', scene.frame_end)
"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Render a Blender scene to video.")
    ap.add_argument("--script", help="Python that builds or edits the scene")
    ap.add_argument("--blend", help="a .blend file to open first")
    ap.add_argument("--out", required=True)
    ap.add_argument("--frames", help="first-last, e.g. 1-120 (default: the scene's range)")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--engine", choices=("eevee", "cycles", "workbench"), default="eevee")
    ap.add_argument("--samples", type=int, default=64, help="Cycles samples")
    ap.add_argument("--cpu", action="store_true", help="Cycles on the CPU, x264 encoding")
    args = ap.parse_args()
    if not (args.script or args.blend):
        raise SystemExit("give --script, --blend, or both")
    out = Path(args.out).resolve()
    if out.exists():
        raise SystemExit(f"{out} exists: render to a new file")
    width, height = (int(v) for v in args.size.lower().split("x"))
    first, last = (int(v) for v in args.frames.split("-")) if args.frames else (None, None)
    engine = {"eevee": "BLENDER_EEVEE", "cycles": "CYCLES", "workbench": "BLENDER_WORKBENCH"}[args.engine]

    work = Path(tempfile.mkdtemp(prefix="kit-blender-"))
    try:
        setup = work / "setup.py"
        setup.write_text(SETUP.format(engine=engine, w=width, h=height, fps=args.fps, samples=args.samples,
                                      gpu=not args.cpu), encoding="utf-8")
        late = work / "range.py"
        late.write_text(LATE.format(first=first, last=last), encoding="utf-8")
        cmd = [str(BLENDER), "--background", "--factory-startup"]
        if args.blend:
            cmd.append(str(Path(args.blend).resolve()))
        cmd += ["--python", str(setup)]
        if args.script:
            cmd += ["--python", str(Path(args.script).resolve())]
        # The runner's settings are applied again after the scene script, which may have replaced them.
        cmd += ["--python", str(setup), "--python", str(late),
                "--render-output", str(work / "frames" / "f_####"), "--render-format", "PNG", "--render-anim"]
        subprocess.run(cmd, check=True)
        frames = sorted((work / "frames").glob("f_*.png"))
        if not frames:
            raise SystemExit("Blender rendered no frames")
        start = int(frames[0].stem.split("_")[1])
        codec = (["-c:v", "libx264", "-preset", "medium", "-crf", "17"] if args.cpu else
                 ["-c:v", "h264_nvenc", "-preset", "p7", "-tune", "hq", "-rc", "vbr", "-cq", "19", "-b:v", "0"])
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-n", "-framerate", str(args.fps), "-start_number", str(start),
                        "-i", str(work / "frames" / "f_%04d.png"), "-an", *codec, "-vf", f"format=rgb24,{RGB_TO_709}",
                        "-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-movflags", "+faststart", str(out)], check=True)
        print(f"wrote {out} ({len(frames)} frames)")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
