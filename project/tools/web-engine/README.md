# Web engine: Canvas 2D, SVG, three.js, anime.js

`render_web.py` opens a page folder in headless Chrome and captures it frame by
frame. The page's `index.html` must set `window.__ready = true` once loaded (or
`window.__error = "…"`) and define `window.renderAt(t)`: draw the frame at `t`
seconds and return `"ok"` (or a promise of it). `lib/` is served at `/lib/`
(`/lib/three/three.module.js`, `/lib/anime/anime.esm.min.js`).

Commands, run from the project folder:

```bash
python -X utf8 tools/web-engine/render_web.py <page_dir> --info
python -X utf8 tools/web-engine/render_web.py <page_dir> --stills 0.5,2,3.5 --out <stills_dir>
python -X utf8 tools/web-engine/render_web.py <page_dir> --frames-dir <strip_dir> --start 1 --end 2
python -X utf8 tools/web-engine/render_web.py <page_dir> --out <clip.mp4> --end 5
```

- **Templates:** `templates/canvas2d/`, `templates/svg-anime/`, `templates/three/`
  and `templates/math/`. Copy one into your own page folder and edit the copy.
- **Output:** 1920×1080 at 30 fps unless you pass `--width`, `--height` or
  `--fps`. H.264 `yuv420p`, BT.709 limited range, no audio. It refuses to
  overwrite an existing file.
- **Frames are a function of time only**, so any range can be re-rendered and
  joined. Review stills and full-rate strips of a clip before using it.
- **Drawing and encoding:** by default Chrome draws on the graphics card
  (Direct3D 11), frames are captured as PNG, and NVENC encodes. `--cpu` uses
  SwiftShader and x264. `--jpeg` captures faster but slightly less exactly.
- **Black frames:** a frame that comes back all black is re-rendered (WebGL
  readbacks can fail). One that stays black is kept and counted, or fails with
  `--strict-black`.
- **Colour:** RGB frames are converted with the BT.709 matrix and accurate
  rounding
  (`scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int+full_chroma_inp`).
- **It needs:** Python 3.10+ with `websockets` and Pillow, Chrome (set
  `KIT_CHROME` for another copy), and FFmpeg on PATH.

## Libraries

| Part | Version | Licence |
|---|---|---|
| three.js | r186 | MIT (`lib/three/three-LICENSE.txt`) |
| anime.js | 4.5.0 | MIT (`lib/anime/LICENSE.md`) |
