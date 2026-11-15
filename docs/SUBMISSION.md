# MirrorScore submission draft

## Project name

MirrorScore

## Punchline (34 words)

Give your song an AI creative crew. MirrorScore combines a multi-agent workflow with Gemini to turn musical structure into code-generated motion graphics, connecting rhythm, visual design, animation, and rendering in one music-video production experiment.

## Description

Independent musicians can record a song long before they have the resources to produce a music video. MirrorScore explores a different production workflow: give an AI creative crew the music's structure, then let it help build the visuals as editable code.

The project connects a multi-agent framework with Gemini for creative coding. Its demonstration uses a 79-second passage of "Mirror Mirror" by Anno Domini Beats. A structured song brief and precomputed analysis describe beats, bars, drum events, loudness, frequency bands, and estimated vocal, bass, and drum activity. These signals drive a procedural Three.js world with a reflective sphere, thousands of animated columns, particles, moving lights, and an orbiting camera.

Python tools capture the scene frame by frame in Chrome. FFmpeg encodes the visual track and combines it with the song passage. The finished local demo is 1920 x 1080 at 30 fps, with H.264 video and AAC audio.

The creative output remains inspectable: animation behavior lives in source code, so timing, geometry, lighting, and camera choices can be modified. This prototype demonstrates a concrete path from structured musical context to rendered visuals. Its next step is to package the external agent orchestration alongside the renderer so the complete process can be reproduced from one brief.

## Technologies used

Gemini API, Gemini CLI, a custom multi-agent framework, JavaScript, HTML, Three.js, WebGL, Python, websockets, Pillow, FFmpeg, ffprobe, JSON music-analysis data, Git, and GitHub.

## Demo and source code

Demo: local `demo/mirrorscore-demo.mp4` or the original `project/clips/Mirror_Mirror_Music_Video.mp4`. A public demo URL has not yet been published.

Source: https://github.com/DarioMoscatello/Higgsfieldkiller

## Author verification before submission

1. Add the framework's name, orchestration code or source link, agent roles, Gemini model, and a short execution log. The renderer repository alone does not establish those details.
2. Record which files were built during the hackathon and which came from the starting kit. Preserve the kit's original attribution and confirm its reuse terms.
3. Confirm the soundtrack's license before publishing audio or the finished video.
4. Replace the pending public demo and source links with actual published URLs.
