# Music video round kit

A starting folder for one test: give an AI coding agent a song passage and measurements of the music, and ask it for a
finished motion-graphics music video drawn entirely by code. The agent cannot hear the song or watch video; it works
from the data and checks its own pictures as still frames.

## Quick start with Gemini

You need: a YouTube account (for the song), Gemini CLI with a Gemini API key, Python, FFmpeg and Chrome.

1. **Get the song.** In YouTube Studio, open Audio Library, search for "Mirror Mirror" by Anno Domini Beats and download it.
2. **Unzip the kit** somewhere that has no `GEMINI.md` or `AGENTS.md` in a parent folder (for example a new folder on
your desktop).
3. **Setup session.** Open a terminal in the kit's `project` folder, run `gemini`, and paste this (put your own path in):

```
   Set up this music video kit, but don't make any video. My copy of "Mirror Mirror" by Anno Domini Beats is at <path to the mp3>. Run song/make_passage.py with it and tell me if it matched. Then check what this machine has (Python packages, FFmpeg, Chrome, Blender, graphics card) and rewrite tools/README.md so it lists only what is really installed. Change nothing else.
   ```

When it says the setup is done, close the session (`/quit`).

4. **The run.** In the same `project` folder start a **new** Gemini CLI session with the best model and auto approval
(for example `gemini -m gemini-3.1-pro-preview --approval-mode yolo`). Paste the request from "The request" below as
your **only** message. Don't answer questions or add notes; let it work until `final/music-video.mp4` and `report.md`
exist. It can take from under an hour to several hours.
(Optional: before this step, copy a skill folder from `skills/` into `project/.gemini/skills/`. See "Skills".)
5. **Share the result** with the model, the Gemini CLI version, and whether you added a skill.

## What is inside

* `project/song/` — measurements of one song ("Mirror Mirror" by Anno Domini Beats, YouTube Audio Library): beat and
bar grid, drum hits, onsets, chord guesses, loudness and separated-layer curves at 100 values per second, the start
times of the sung lines, and a plain-words description of the song. **No audio and no lyric words** (see below).
* `project/tools/` — a frame renderer that turns a web page (Canvas 2D, SVG with anime.js, or three.js) into video,
and a Blender runner. Using them is optional.
* `skills/` — two optional agent skills, **not used unless you copy them in** (see "Skills" below).

## Skills (optional)

Two skills written from what an earlier run on this song learned. A run without them tests the agent alone; a run with
them tests the agent plus the skill. Say which you did when you share results.

|Skill|What it gives|
|-|-|
|`ultracode-music-dance-video`|The craft, open concept: concept method, story devices, frame clock from the measurements, a code-drawn renderer with motion blur, dance timing, measured sync checks, contact-sheet review, the delivery encode, the report, and how to brief helper agents without running out of usage. The run picks its own idea.|
|`ultracode-music-dance-video-jack-of-mirrors`|One finished concept for this song ("Jack of Mirrors": a paper court-card Jack and his mirror twin in a world of playing cards), with a scene plan and known weak spots. Use it together with the craft skill.|

To use one or both, copy the skill folder into `project/.gemini/skills/` before the run (step 4 of the quick start).
Gemini CLI finds it by itself.

## Details (what the quick start does, for other agents or by hand)

1. **Get the audio.** Download "Mirror Mirror" by Anno Domini Beats from the YouTube Audio Library (YouTube Studio >
Audio Library). Then, from the `project` folder:
`python -X utf8 song/make_passage.py "<path to the downloaded mp3>"`
It checks the file against the analysed track and writes `song/passage.mp3` (the first 79.172 s).
Check the track's licence in the Audio Library yourself before publishing a video made with it.
2. **Describe your machine.** Edit `project/tools/README.md` so it lists what your machine really has (Python packages,
FFmpeg, Chrome, Blender, graphics card). The agent can only use what it is told exists.
3. **Use a clean location.** Unzip somewhere that has no `GEMINI.md` or `AGENTS.md` in a parent folder, so the run reads
only this kit.
4. **Optional skill.** To test an agent with a skill, put the skill folder in `project/.gemini/skills/`. Without it, the
run tests the agent alone. Say which you did when you share results.

## The request

Paste this unchanged as the only message of a fresh session in `project`. One run at a time; rendering uses a lot of
memory.

```
Make a music video for the song in this folder.

What I want: a full music video like a real official music video, with a lot of dance or some story, but made as motion graphics only. No filmed footage. It can be 2D, 3D or both. What matters to me is that it's creative and unique.

- The song is song/passage.mp3. Use all of it (79.172 seconds), with its audio unchanged.
- Read song/README.md first. The folder has what the whole song is about, the timing of the sung lines, and measurements of the music: beats, bars, drum hits, chords, loud and quiet parts.
- tools/README.md lists ready-made tools in this folder and what is installed on this machine. Using them is optional.
- Deliver one finished video: final/music-video.mp4, 1920×1080, 30 fps, H.264 yuv420p with AAC audio, the same length as the song file.
- Work on your own from start to finish. Don't stop to ask me for approval; deliver the finished video.
- Keep all your work inside this folder. Use only free tools already installed on this machine. Don't download footage or artwork. Fonts must be open-licensed (for example OFL), with the licence file kept.
- You can't hear the audio. Don't say you listened to or watched something you didn't.
- Before you finish, check that the file plays to the end and that the music is in sync with the song file.
- Then write report.md: what you made and the idea behind it, how you made it, what you checked, and what you're unsure about.
```

## What is not included, and why

* **The lyric words and note pitches.** Lyrics are part of the song's copyright, and a dense list of pitches would
amount to a transcription of it. The kit keeps only their timings and counts. An agent that wants words on screen has none to use, which is part of the test.

## Libraries

three.js r186 and anime.js 4.5.0 are included under the MIT licence (`tools/web-engine/lib/`).

## Licence

