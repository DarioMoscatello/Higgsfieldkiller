# Blender runner

`render_blender.py` calls Blender by its full path: the Windows default install of Blender 5.2, or the executable named
in the `KIT_BLENDER` environment variable.

Command, run from the project folder:

```bash
python -X utf8 tools/blender/render_blender.py --script <scene.py> --out <clip.mp4> [--blend file.blend] [--frames 1-120] [--engine eevee|cycles|workbench]
```

- The scene script builds or edits the scene in Python, starting from Blender's
  factory scene. `templates/title.py` is an example.
- **Output:** 1920×1080 at 30 fps unless you pass `--size` or `--fps`. No audio.
- EEVEE draws on the graphics card. Cycles uses the graphics card too; `--cpu`
  renders Cycles on the processor and encodes with x264.
- Frames are rendered as PNG into a temp folder, then encoded with NVENC using
  the same colour conversion as the web engine.
