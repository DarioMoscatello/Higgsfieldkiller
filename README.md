# MirrorScore

**Your song. An AI crew. A world in motion.**

MirrorScore is a music-video experiment built around a multi-agent workflow using Gemini. It turns structured music analysis into editable, code-generated motion graphics. The prototype uses the first 79.172 seconds of "Mirror Mirror" by Anno Domini Beats.

## Punchline

Give your song an AI creative crew. MirrorScore combines a multi-agent workflow with Gemini to turn musical structure into code-generated motion graphics, connecting rhythm, visual design, animation, and rendering in one music-video production experiment.

## Why it matters

Independent musicians often have a track before they have the budget or skills to produce matching visuals. MirrorScore explores how agents can help bridge that gap, with generated animation code that a creator can inspect and change.

## What the prototype does

1. Provides a song brief and precomputed timing data: beats, bars, drum events, loudness, frequency bands, and estimated separated-layer envelopes.
2. Uses those measurements as context for a Gemini-assisted creative coding workflow.
3. Draws a Three.js scene: a reflective sphere, a 48 by 48 grid of animated columns, colored lights, moving camera, and particles.
4. Maps bass, frequency-band energy, onsets, and drum strength to geometry, motion, and lighting.
5. Captures frames in Chrome through a Python rendering tool and encodes the result with FFmpeg.
6. Combines the rendered video with the song passage for the local finished demo.

## Demo and source

The local finished demo is `project/clips/Mirror_Mirror_Music_Video.mp4`. Its verified container duration is 79.166667 seconds, with 1920 x 1080 H.264 video at 30 fps, yuv420p pixels, and AAC audio. The difference from the requested 79.172-second passage is less than one video frame.

A compact presentation copy is generated at `demo/mirrorscore-demo.mp4`. Audio and video files are excluded from Git by default. Obtain the track from the YouTube Audio Library and verify its current license before redistributing the soundtrack or a video containing it.

The visual implementation is [project/clips/mirror/index.html](project/clips/mirror/index.html). The frame renderer is [project/tools/web-engine/render_web.py](project/tools/web-engine/render_web.py).

## Technologies

| Technology | Role |
|---|---|
| Gemini API and Gemini CLI | AI reasoning and creative coding workflow, as described by the project author and kit |
| Multi-agent framework | External orchestration described by the author; its implementation is not included in this folder |
| JavaScript, HTML, Three.js, WebGL | Procedural 3D scene and data-driven animation |
| Python, websockets, Pillow | Chrome frame capture and rendering automation |
| FFmpeg and ffprobe | Video encoding, audio muxing, and media inspection |
| JSON music-analysis data | Timing and control signals for the visuals |
| Git and GitHub | Source sharing and project documentation |

The kit also bundles anime.js, Canvas/SVG templates, and Blender helper scripts. These are optional tools, not evidence that they were used in the demonstrated Three.js scene.

## Reproduce the visual render

1. Install Python 3.10 or later, Google Chrome, and FFmpeg. Ensure `ffmpeg` and `ffprobe` are available on PATH.
2. Install the renderer dependencies from the repository root:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Enter the working folder and check the scene:

   ```powershell
   cd project
   python -X utf8 tools/web-engine/render_web.py clips/mirror --info
   ```

4. Render sample frames before committing to the full video:

   ```powershell
   python -X utf8 tools/web-engine/render_web.py clips/mirror --stills 0.5,20,55 --out preview
   ```

5. Render the full visual track with a software H.264 encoder:

   ```powershell
   python -X utf8 tools/web-engine/render_web.py clips/mirror --end 79.172 --fps 30 --width 1920 --height 1080 --encoder x264 --out mirror-render.mp4
   ```

6. Download the correct full track from YouTube Studio > Audio Library. Extract the passage:

   ```powershell
   python -X utf8 song/make_passage.py "PATH_TO_DOWNLOADED_TRACK.mp3"
   ```

7. Add the soundtrack:

   ```powershell
   ffmpeg -i mirror-render.mp4 -i song/passage.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart music-video.mp4
   ```

The renderer refuses to overwrite existing outputs. Choose a new output name when repeating a run. Set `KIT_CHROME` if Chrome is installed outside its default Windows location. Rendering is offline frame capture, not real-time video generation.

## Scope and limitations

The repository contains the music-analysis kit, a working visual scene, rendering utilities, optional agent instructions, and presentation material. It does not currently contain the author's multi-agent framework, Gemini API client, execution logs, model/version record, or a completed generation report. Those components must be supplied before the full orchestration can be independently reproduced.

The supplied music analysis includes estimates and documented timing uncertainty. The scene's initial particle positions use `Math.random()`, so separate launches can differ. It is a procedural music visualizer prototype, not evidence of generated choreography, filmed footage, or a Veo-based video pipeline.

## Attribution and provenance

Track: "Mirror Mirror" by Anno Domini Beats, identified in the supplied kit as coming from the YouTube Audio Library. Audio is not covered by a source-code license.

Three.js and anime.js retain their bundled MIT license notices. The original kit documentation is preserved in [docs/ORIGINAL_KIT.md](docs/ORIGINAL_KIT.md). The kit's top-level license field was empty, so this repository does not assign a new blanket license to inherited material. The author should record the kit's source and reuse permission before presenting it as wholly original work.

See [docs/SUBMISSION.md](docs/SUBMISSION.md) for the judge-facing draft and [docs/DEMO.md](docs/DEMO.md) for a short demonstration sequence.
