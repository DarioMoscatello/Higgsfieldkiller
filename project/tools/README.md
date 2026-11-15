# Tools

| Folder | Purpose |
|---|---|
| `web-engine/` | Captures HTML, Canvas, SVG, or Three.js scenes in Chrome and encodes the frames with FFmpeg. |
| `blender/` | Optional Blender runner and templates; Blender is not required by the demonstrated Three.js scene. |

## Renderer requirements

1. Python 3.10 or later with `websockets` and `Pillow`, installable from the root `requirements.txt`.
2. Google Chrome. Set `KIT_CHROME` if it is not at the default Windows location.
3. FFmpeg and ffprobe on PATH, with libx264 and AAC encoding available.

Use `--encoder x264` on machines without NVIDIA NVENC. Chrome can still use an integrated GPU to draw WebGL. Render sample stills before the full clip and run only one renderer at a time on low-memory machines.

The original local environment note reported Windows 11, an Intel Core i5-1240P with integrated Iris Xe graphics, about 8 GB RAM, and no Blender. Those are development-machine observations, not requirements or a promise that the same tools are installed elsewhere.

See `web-engine/README.md` for the complete rendering interface and the root README for a reproduction sequence.
