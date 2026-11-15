# Pipeline and checks

Layout that worked: helper scripts in `build/`, outputs in `work/`, the deliverable in `final/`, the page in its own
folder (`mv/` with `index.html`, `src/`, `fonts/`). The supplied `tools/web-engine/` is not edited; scripts that need its
internals import `render_web.py` with `importlib` (its local server, DevTools client and Chrome path).

## A. Data generation (`build/gen_data.py`)

1. Decode the mp3 to PCM wav; `DUR` = wav length.
2. Convert analysis microseconds to the mp3 clock (subtract the documented offset), drop anything after `DUR`.
3. Snap each drum hit to the nearest 0.1 s if within 45 ms; keep `[time, strength]` pairs per class (kick, snare/clap,
   hat/cymbal). The 0.1 s snap is finer than the 0.2 s music grid on purpose, so genuinely off-grid hits survive.
4. Lyrics: take the line start times from `song/lyric-lines.md` and the word slots from the report's `lyric_word`
   observations; assert the line count and that every line start is within 60 ms of the listed time. If the folder holds
   lyric text at all, keep any word marked uncertain out of the data here (replace it with `[?]`).
5. Write one ES module: `KICKS, SNARES, HATS, LINES, SECTIONS, ENV` (100 Hz), `DUR, FPS = 30,
   NFRAMES = int(DUR·30), BPM, BEAT, BAR, S16` (plus note lists if your song data has pitches).
6. Grep the page sources and the generated module for the uncertain word: it must be 0.

## B. Rendering (`build/render_all.py`)

- Split the frame range into `--jobs` equal segments (measure 1, 2 and 4 once; on one GPU four Chrome processes gave
  about no speed-up). Each segment: one `render_web.py` process (headless Chrome, D3D11, PNG capture) writing an x264 CRF 10
  intermediate; retry up to 3 times if the browser dies; collect log lines containing page error, page exception, black,
  warning or retry and print them.
- Join with the concat demuxer and **encode once**: libx264, preset slow, CRF 18, `-maxrate 30M -bufsize 60M`,
  `-profile:v high -level 4.2`, yuv420p, GOP 60 (a keyframe every 2 s), BT.709 tags, `+faststart`.
- Audio: decode to PCM, encode once to AAC 256 kb/s, mapped as stream 1 (`-map 0:v:0 -map 1:a:0`), full length.
- `--preview`: 960x540, JPEG capture, CRF 23, stream-copy join. `--reuse-segments`: redo only the join and encode.
  `--start/--end`: a sub-range with the audio trimmed to match.
- Measured on the earlier run: full-length preview at 960x540 with 6 sub-frames, 15 min 31 s (with other agents sharing the
  GPU); final 1080p with 12 sub-frames, 18.5 min; 1.8-2.3 s per frame per job. A 4 s 1080p clip at 20 sub-frames: 69 s.
- [mistake] The earlier delivery stream-copied CRF 17 segments into the final file: 52 Mb/s at level 4.0. A 16 s re-encode
  with the settings above gave 31.5 Mb/s at level 4.2, average PSNR 40.6 dB against the original.
- Test the whole chain on a stand-in scene before real scenes exist: this found three pipeline bugs early (a wrong audio
  length check, a missing overlay group, a missing per-sub-frame draw hook).

## C. The checks (`build/verify.py`)

Make each a named boolean, and make `all_checks_pass` include every one, including picture sync. The earlier script only
printed the picture-sync numbers, so "all checks pass" said nothing about them.

1. **Streams** (`ffprobe -show_format -show_streams -count_frames`): codec h264; yuv420p; 1920x1080; `r_frame_rate` and
   `avg_frame_rate` 30/1; AAC; `nb_read_frames == int(DUR·30)`; format duration within 10 ms of the song; audio within
   2 ms; both `start_time` below 1e-6. **Add:** profile, level ≤ 4.2, `bit_rate` ≤ 30 Mb/s.
2. **Plays to the end:** `ffmpeg -xerror -map 0:v:0 -map 0:a:0 -f null -` exits 0 with empty stderr; extract the last
   frame (`select=eq(n,N-1)`) and require a non-trivial PNG; a 160x90 decode yields exactly N frames.
3. **Audio sync and identity:** decode file audio and the mp3 to 44.1 kHz stereo, mono mix; FFT cross-correlation
   (`nfft = 2^20`) on three 10 s windows (start, middle, end) → lags; Pearson correlation at zero lag; RMS difference in dB;
   decoded padding after the song. Pass: all lags ≤ 2 samples, correlation > 0.99, level within 0.2 dB, extra samples
   0-1024 (one AAC frame) and near silent. Earlier result: lags 0/0/0, correlation 0.99976, -0.032 dB, 335 samples of
   padding. [mistake → fix: an exact-length check failed on AAC padding alone]
4. **Picture on the drums:** decode at 160x90 grey (`scale=160:90:flags=area,format=gray`); per frame, mean absolute
   difference to the previous frame and mean luminance. For each hit after the drums start, value = `max(diff[k], diff[k+1])`
   at `k = round(t·30)`; compare with all other frames (mask k-1..k+2 around hits); report the median ratio and the share of
   hits that are local peaks (≥ 1.5 × the median over k-8..k+8). Earlier result: kicks 8.9× (73 of 78 local peaks), snares 5×
   but only 26 of 45 local peaks, which nobody explained. Set thresholds. A global flash on every hit would pass; keep strips.
5. **Your signature switch:** for each instance, the difference on the frame where it must switch in and out exceeds a
   threshold (the earlier film: 16 of 16).
6. **Black and frozen:** luminance < 2 counts dark frames; difference < 0.02 counts identical frames. Earlier: 0 and 0.
7. **Text audit (`build/text_audit.py`):** open the page at 480x270, 1 sub-frame; inside one evaluate call run
   `renderFrame(t)` for every frame (use step 1, not 3: a string shown for 1-2 frames can be missed), then print
   `window.__drawnText`. It must equal the whitelist.
8. **Render order (`build/check_history.py`):** pick frames at each scene cut (+0, +1, +7), the first two frames of each
   segment, plus a golden-ratio spread up to 36; render them in reverse time order in one fresh page at the final
   sub-frame count; compare with the same frames decoded from the video. Use a structural measure: blur both 6 px, take the
   max per-pixel difference; pass below 10/255. [mistake → fix: PSNR flagged a correct render (min 30.9 dB) because of film
   grain and compression; one frame's blurred difference was mean 0.91, max 3.29] Run it before the first full render.

Save every check's output to a file next to the video, with the video's hash.

## D. Contact sheets and strips

- **Rendered sheets (`build/sheet.py`):** `--range A B STEP` or `--times`, `--cols`, `--tile`; each tile labelled
  `t=..  f<frame>  bar <k>  beat <b>`; default `sub=4`; print page errors. Commands: a bar at 0.2 s steps (16 tiles at 480 px);
  a hit at every frame (step 0.0333, 6-7 columns at 270-320 px); full-resolution stills at sub 12. 16 tiles take about 10 s.
- **Review sheets from the rendered video (`build/review_sheets.py`, no re-render):** per bar a 4x4 sheet (a tile every
  sixteenth); a cuts sheet with the 3 frames before and after each cut; for each signature instance every frame from 4
  before to 6 after. Downscale to 960 px on read [mistake → fix: loading all 2,375 full-HD frames ran out of memory].
- **Grab (`build/grab.py`):** full-resolution PNGs by time or frame, or a labelled every-frame strip of a range, from the mp4.
- Order of looking: the bar sheet first, then the every-frame strip of each hit (where "impact on its frame" is judged),
  then cut sheets.
- **Timing probe (`build/timing.py`):** update, render and wall ms per sample time, to find slow scenes.

## E. Long jobs and scripts

- Run renders in the background, writing to a log ending with an exit marker (`...; echo "exit $?" >> log`), and wait on the
  marker with a loop that has a deadline. Look at the log 20-30 s after launch.
- Syntax-check every edited script before a long job. Make patch scripts idempotent. Edit backslash-heavy text with an edit
  tool, not a heredoc.
- `render_web.py` refuses to overwrite: delete first or use a new folder. Its useful switches: `--info` (three.js revision),
  `--stills t1,t2 --out dir`, `--start/--end` (seconds; pass exact frame boundaries), `--query "a=b&c=d"`, `--encoder x264
  --crf N`, `--jpeg --width 960 --height 540`, `--frames-dir`. An all-black capture is retried up to 3 times (a WebGL readback
  can come back empty).
- Clean up: kill headless Chrome trees (`taskkill /PID <pid> /T /F`) and delete their temp profiles. At one point the earlier
  run had 45 Chrome processes and 7 leftover profiles.

## F. Things the earlier run did not check that you should

- The delivery spec (profile, level, bit rate).
- Picture-sync ratios, the signature switch and black/frozen counts as hard pass/fail.
- That each scene's first and last frames match the cut list.
- The final render frame by frame (its bar-by-bar look was at an earlier preview; scenes changed after it).
- Any motion measure (it only had stills).
