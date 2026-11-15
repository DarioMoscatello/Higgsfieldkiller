---
name: ultracode-music-dance-video
description: Make a finished motion-graphics music and dance video drawn entirely by code from a song passage and its measurement files (beats, drum hits, notes, layer envelopes, lyric timings), when you cannot hear the audio or watch video. Open concept - you choose the idea. Covers concept method, story devices, choreography, sync to measured hits, the web frame renderer, sub-frame motion blur, checks that measure sync, contact-sheet review, delivery encode, the report, and how to brief helper agents without running out of usage. Use for any request to make a music video, lyric video or dance video from song data in this folder.
---

# Music and dance video from song data (open concept)

Everything here was learned by an earlier session that made a 79-second motion-graphics music video from this
same kind of folder: song data, a headless-Chrome frame renderer, FFmpeg, no ears and no eyes for motion. It delivered
a valid, in-sync file that was well received. It also lost hours to avoidable problems. This skill keeps what worked and
says plainly what went wrong, so you do not pay for the same lessons twice.

Deeper detail, with values and code patterns, is in `references/`:

| File | Read it when |
|---|---|
| `references/song-facts.md` | Before planning: what the earlier session measured about this song passage (verify it yourself) |
| `references/engine.md` | Building the renderer, rig, dance sequencer, mirror/paper looks, font guard |
| `references/pipeline-and-checks.md` | Data generation, rendering, the measured checks, contact sheets, the delivery encode |
| `references/helper-agents.md` | Only if you start helper agents: sizing, budgets, briefs, stops |

## 0. The non-negotiables

1. **You cannot hear or watch.** Never say you listened to or watched anything. Judge the picture from rendered stills
   and contact sheets, and sync from measurements. Say so in the report.
2. **Deliver first, polish second.** A valid `final/music-video.mp4` that passes the measured checks matters more than a
   review round. Get a complete, checked file on disk early, then improve it and re-render.
3. **Every frame is a pure function of the song time `t`.** No counters, no "previous value", no `Math.random()`, no
   `Date`. Seeded hashes only. This is what makes parallel rendering, single-frame re-renders and time offsets free.
4. **Hits land on exact frames.** Measure the audio yourself, build a frame clock from it, and put every impact on the
   hit's own frame.
5. **Only words you chose appear on screen.** A fixed whitelist in code, a renderer guard that refuses any other font or
   character, and an audit of every string drawn. An uncertain lyric word is removed from the data before the page
   ever sees it.
6. **The concept is yours.** This skill gives the craft, not the idea. If a concept skill sits beside it (for example
   `ultracode-music-dance-video-jack-of-mirrors`), the concept skill decides the idea and this one decides how to build it.

## 1. Order of work (with time boxes)

The earlier session's order was right, but its last stages never happened because helpers ate the usage allowance.
Use this order, and keep the review in the middle, not at the end.

| Step | What | Box |
|---|---|---|
| 1 | Scout: read `song/README.md`, the story, lyrics, map; both tool READMEs; probe the PC (GPU, NVENC, fonts with licences) | 10 min |
| 2 | Measure the audio and generate one data module the page imports (section 3) | 15 min |
| 3 | Concept: two or three distinct concepts in writing, pick one, write a one-paragraph idea plus a hit-level plan (section 2) | 20 min |
| 4 | Engine core and a stand-in scene; run the **whole pipeline end to end** on it: full-length low-res preview, a short full-res clip, mux, verify | 45 min |
| 5 | **One full-length 1920x1080 test render early** (even of rough scenes): it exposes time per frame, bitrate/level and script bugs while time is cheap | 20 min |
| 6 | Build scenes in passes (block, time, polish, critique), each checked on contact sheets and hit strips | most of the run |
| 7 | Render the deliverable, run every check, write `report.md` | 30 min |
| 8 | Review every bar on sheets cut from the rendered file, fix, re-render, re-check, update the report | what is left |

Write `report.md` early and keep it true as you go. If you are stopped, the report and the file already exist.

## 2. Concept and story

**Find one structural fact in the song and build everything on it.** The strongest concepts came from a fact the song
itself gives (its title, its repeated form, a recurring silence), not from a list of nouns in the lyric. Test: can the
whole film be drawn with one object or one rule? If each section needs a new unrelated device, it is a list of ideas,
not a concept.

**Ideas earlier runs on this song kept reaching for** (choose them knowingly, or go elsewhere for something unique):
cracks mended with gold on a figure or its reflection (five of six earlier videos); a faceted or porcelain 3D dancer
with a cracked reflection (the common 3D answer); a mirror floor whose reflection is a second performer.

Generate at least three concepts from different lenses (a formal rule about the frame; a dancer-first concept; a
three-act story; letters and symbols as performers; a 3D world and camera journey), then pick one and write why.

**Story tools that worked:**
- **One story variable that moves one way** across the song (for example a second figure's lag behind the lead
  shrinking from a whole beat to zero). Put it in one shared function of `t`.
- **A counter per bar** that pays off on a lyric (one new mark per verse bar, then transformed on the line it belongs to).
- **Plant a promise early and pay it on the last hit** (two hands that stop short of touching three times, then touch).
- **Repeat one signature routine in every hook; escalate by force and number** (solo, duet, a row, a crowd, a giant,
  back to one), not by changing the moves, so the viewer recognises it on the third pass.
- **Make silence visible.** When the data says no hits for N seconds, stop everything: one slow camera move and one
  small event series on the beat grid.
- **One colour tracks one music layer** (for example one metallic colour = the bass). Freeze any frame and ask whether you can tell
  from the colours alone if that layer is playing.
- **Lone drum hits become events with a body** (a knock, a string snapping, a pin), not just a flash.
- **One literal, one-still-readable image per bar on its key kick**, made by a physical transform the viewer knows
  (topple about an edge, turn edge-on, flip upside down, spin about the vertical axis). Make puns with geometry, not text.
- **The ending lands on the last real hits and holds.** The passage ends mid-line at full level; stage the last kicks
  and hold a poster frame. No fade, nothing scheduled after the last hit.

**Write a hit-level plan before building.** A pitch that is "twenty one-line sections with no hit times" is a synopsis,
not a score. Every scene needs bar-by-bar times and the hit each image lands on.

**What one reviewer of six earlier videos said** (all six liked, none ranked): dance and story are wanted; less
on-screen text read better; 3D models and movement improved with more care; a 2D-only video proved "no need 3D to make
better"; the 2D character on a 3D stage was called the most creative. Story can be told by lyric text or by movement
that matches the music; both were valued.

## 3. Turning song data into a frame clock

Full method and numbers: `references/pipeline-and-checks.md` section A.

1. Decode `song/passage.mp3` to PCM once (`ffmpeg -i song/passage.mp3 -c:a pcm_s16le work/audio/passage.wav`).
2. Subtract the analysis clock offset that `song/README.md` documents, then **check the hit times against the waveform**.
   The earlier session found the listed drum times early by roughly 16-30 ms and the true onsets on a clean grid within
   2 ms. Use an onset (start of rise) method, not "maximum rise", which finds the attack peak and reads late.
3. If the hits sit on a grid, make it the clock: `at(bar, beat)`, sixteenth, beat and bar in whole frames. Snap detected
   hits to the grid within a tolerance (the earlier session: nearest 0.1 s within 45 ms) and keep the snapped list as the
   single source of hit times.
4. **Detected hi-hats have holes.** For anything that must tick steadily, use the nominal grid, not the detected list.
5. **Word times are estimates (about ±0.1 s).** Tie big moves to drum hits, use word times only to order things inside
   a bar, and drive mouths from the measured voice envelope.
6. Look in the layer envelopes (voice, drums, bass, other) for a **repeating event**: print, per bar, the mean of each layer
   in slices of the bar. Encode it once as a function (`gap(t)` in the earlier film) and hang a device on it.
7. Generate one ES module (`data.js`) with hits, sections, lines, notes, envelopes, `DUR`, `FPS`, `NFRAMES`. The page never
   fetches the analysis JSON. Replace any uncertain lyric word with `[?]` here, so it cannot reach the page.
8. Frame count = `int(DUR * 30)`. Keep the audio at its full length so the song's hard stop is not clipped; the picture is
   then a few ms shorter than the audio, which is fine and worth one line in the report.

## 4. The engine

Full detail: `references/engine.md`. The design that worked:

- **The supplied web renderer** (`tools/web-engine/render_web.py`) drives headless Chrome over the DevTools protocol;
  the page sets `window.__ready` (or `window.__error`) and defines `window.renderAt(t)`. three.js and Canvas 2D both work.
  Code-drawn graphics in the browser iterate in seconds; Blender was never needed.
- **Sub-frame accumulation:** each output frame is the average of N renders (12 final, 6 preview, 4 quick sheets, 1 text
  audit) in a float buffer, giving motion blur, depth of field and anti-aliasing in one loop.
- **Forward shutter** (`ts = t + ((k+0.5)/N) * (0.5/fps)`): a change scheduled exactly at a hit is fully visible on the
  hit's own frame. Make impacts instantaneous at the hit, then decay. A centred shutter smears the impact into the frame
  before.
- **Clamp everything in float pipelines** (texture colours, soft clip, each accumulated sample). One NaN or overshoot
  produced a blown speckle band until clamped.
- **Reset shared state in the host loop:** `stage.reset()` and `kit.reset()` before every scene update. A brief that says
  "set everything every frame" is not enough once several scenes share objects.
- **Cuts stay hard:** pick the owning scene once per frame and clamp every sub-frame's time into that scene's range.
- **A paper doll rig** (front view, planar joint rotations, a flat pose dictionary so blending is a lerp) avoids 3D
  skinning and reads well in stills. Two-bone IK for legs always and arms on demand.
- **Dance sequencer:** poses are reached on a hit with a short travel window before it (0.07-0.1 s snaps on kicks,
  0.15-0.2 normal, 0.4+ legato); limbs overshoot slightly, hips and feet never do; distal joints sample slightly
  earlier times for free follow-through; a groove layer dips hips and nods the head on the beat while a pose holds.
  Moves arrive on the beat and hold; they never drift between beats.
- **Camera as data per sub-frame,** with shot sizes defined in units and a small drift always on. Cut only on a bar line,
  a kick or a snare.

## 5. Text, fonts and licences

- Decide the allowed on-screen words before building and hard-code them. Only the cut-in time of each word may come from
  the data. Lyric lettering is limited to what the voice sings alone, appears in place (lay out the whole phrase once,
  reveal words), and is fully up within about 0.3 s of its start.
- **A font that "loaded" may hold almost no glyphs.** The earlier session copied two serif files that held 9 glyphs and no
  A-Z; `document.fonts` reported them loaded and the canvas silently fell back to a system font. Check coverage by parsing
  the font's character map (or measuring a specimen with two different fallbacks) the moment you copy a font.
- Install a **font guard** in the page: patch the canvas `font` setter and `fillText`/`strokeText`/`measureText` to throw on
  any family not in your list or any character outside printable ASCII, and record every string drawn. Draw symbols
  (suits, arrows, bullets) as vector paths.
- Run a **text audit**: step through every frame with one sub-frame and print every string drawn. It must equal the whitelist.
- Open-licensed fonts on this PC are in odd places (a game launcher's font folder, user fonts, the Blender install). Copy the
  licence file with each family. A font whose licence you cannot read is not used.

## 6. Checks that measure instead of look

All of these are scripted in the earlier pipeline; recipes in `references/pipeline-and-checks.md` section C. Make every
one a **pass/fail with a threshold**, not a printout.

| Check | Method | Pass |
|---|---|---|
| Streams | ffprobe | h264, yuv420p, 1920x1080, 30/1, AAC, frame count = `int(DUR*30)`, durations within a few ms |
| Delivery spec | ffprobe | **profile High, level 4.2 or lower, bit rate at most ~30 Mb/s**, BT.709 tags, faststart |
| Plays to the end | `ffmpeg -xerror ... -f null -`; extract the last frame | exit 0, empty stderr, last frame decodes |
| Audio sync and identity | cross-correlate decoded file audio with decoded mp3 at start, middle, end; Pearson correlation; RMS level | lag ≤ 2 samples, correlation > 0.99, level within 0.2 dB, length within one 1024-sample AAC frame |
| Picture on the drums | per-frame mean abs difference at 160x90 grey; hit frames vs other frames | set thresholds for the kick and snare ratios and for the share of hits that are local peaks |
| Your signature device | the frame difference on the frames where it must switch | every instance switches on its frame |
| Black / frozen | mean luminance; identical consecutive frames | zero, unless deliberate |
| Text audit | strings recorded by the font guard | equals the whitelist |
| Render order | re-render sampled frames (after cuts, at segment boundaries) in reverse order in a fresh page; blur both 6 px; max difference | below ~10/255 (raw PSNR fails on film grain) |

A lossy AAC re-encode adds a few hundred samples of padding; an exact-length audio check fails for that reason alone.

The picture-change measure says "something changed on the hit", not "the right thing changed". Keep the frame-strip
review for that.

## 7. Looking without watching: contact sheets and strips

- A **sheet of a bar at one tile per sixteenth**, labelled with time, frame, bar and beat, then an **every-frame strip around
  each hit**, where "impact on the hit's frame" is judged. First and last frames of each scene side by side at every cut.
- Cut review sheets from the **rendered video** (downscaled on read, never all full-HD frames in memory), so reviewing costs
  no re-render.
- A burn-in overlay (`?guides=1`: time, frame, bar.beat, safe area), `?only=<scene>`, `?sub=N`, `?dev=<sheet>` on one page.
- **Images are expensive.** Every image you open stays in your context. Prefer one sheet of many small tiles over many
  single stills; never open the same image twice; at most about 16 tiles per sheet at 480 px.
- Stills cannot show easing, repeated drawings, or whether planted feet stay put. Add a numeric motion check where you
  can (joint speed per frame from the pose solver is cheap because poses are functions of `t`), and say what stays untested.

**Known weak spots to check on purpose** (the earlier film shipped all of them):
1. The performer small in wide shots: set a minimum figure height (about 250 px of 1080) except in one designed pull-back.
2. A busy, bright background behind the dancer: keep a value gap between figure and background; threshold a sheet to test
   silhouettes.
3. Blown-out flashes: one boost source per hit (bloom or exposure or gain), cap the sum, check the brightest frame's
   histogram.
4. Long mostly-black stretches: give black something alive and cut its time.
5. Repeated compositions of the signature moment: one named composition per instance, checked side by side as thumbnails.

## 8. Rendering and the delivery file

- Render segments in parallel only if it actually helps: measure jobs = 1, 2, 4 once. On one GPU, four Chrome processes
  gave roughly no speed-up over one in the earlier run (about 1.8 s per frame per job at 1080p, 12 sub-frames).
- Segments as near-lossless intermediates (x264 CRF 10), joined with the concat demuxer, then **encoded once** to the
  delivery file: libx264, preset slow, CRF 18, `-maxrate 30M -bufsize 60M`, High profile, level 4.2, yuv420p, GOP 60,
  BT.709 tags, `+faststart`. Audio: decode the mp3 to PCM, encode once to AAC 256 kb/s.
- **Do not stream-copy segments into the final file.** The earlier delivery came out at 52 Mb/s, level 4.0, which some
  players refuse; nobody checked until after delivery.
- The renderer refuses to overwrite a file or stills folder: delete first or use a new name.
- Retry a segment if the browser dies under GPU pressure; grep segment logs for page errors and black-frame retries.

## 9. Scripts and long jobs (avoid the earlier session's lost time)

- Syntax-check any script you changed before a long job (`python -c "import ast; ast.parse(open(f).read())"`). A heredoc
  patch turned `\n` into real newlines inside an f-string; the final render failed 4 minutes in and 14 minutes of a
  limited window were lost.
- Edit text containing backslash escapes with an edit tool, not a heredoc; make patch scripts idempotent.
- Run long jobs in the background writing to a log with an exit marker; look at the log 20-30 s after launch; wait with a
  loop that has a deadline. On Windows, kill headless Chrome with `taskkill /PID <pid> /T /F` and remove its temp profile.
- Use `python -X utf8` on Windows.

## 10. If you start helper agents

Read `references/helper-agents.md` first. The short version: helpers cost most of the earlier session's usage, hit the
limit twice, and two of five teams returned nothing.

- A single session can make this film. Use helpers only for clearly separable work, at most four or five at once.
- Freeze the engine, a reference scene and a written brief (with exact hit times and first/last frames per scene) before
  any helper starts. Publish later kit changes in a changelog file they re-read.
- Every helper prompt carries a **budget** (minutes, images, rounds) and must **append its findings or status to a file as
  it goes**; the structured return is a summary, never the only copy.
- One owner per file. Stopped helpers' half-finished edits are untrusted until re-rendered and viewed.
- At the first usage-limit warning: stop every helper first, then deliver.
- Judges of concepts must be blind to work in progress, and decide beforehand whether the panel picks the concept or
  only adds to it.

## 11. The report

Sections: what you made and the idea; how you made it (tools, fonts with licences, engine, data); lyrics and every string on
screen; what you checked, **attached to a specific render and file hash** (anything changed after a check is unchecked);
what you did not do; what you are unsure about, including the weak spots from section 7 that you know remain. State that
you did not hear the song or watch the video play. Any on-screen words you added that the request did not ask for are named
as your additions.

## 12. Stop rule

When `final/music-video.mp4` exists, every check in section 6 passes, and `report.md` is true for that file, finish and
say so. After delivery, the earlier session kept running review and fix rounds that cost a large share of the total and
changed nothing in the delivered file.
