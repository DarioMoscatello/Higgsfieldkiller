# Song facts measured by the earlier session

These are measurements an earlier session made on this same song passage (79.172 s). They saved it hours. **Re-measure
the key ones yourself** before building on them (a two-minute check): if the folder's song has changed, these are wrong.
Bar numbers here count from the audio itself (bar k starts at 3.2·k s from 0); `song/README.md` warns that the analysis
tracker's bar numbers run two higher than a straight count.

## Clock

- Analysis times are on a clock that starts 25,057 µs before the first sound (documented in `song/README.md`); subtract it.
- After that, the listed drum times were still early: a "maximum rise" low-band method gave mean +26 ms (median +30 ms,
  n = 80 kicks); a full-band onset method (2 ms envelope steps, 35 % of local rise) put kicks at 11.2, 12.0, 25.6, 52.8,
  54.4 s at +0 ms and snares at 13.6 / 26.4 s at +2 ms against a 0.2 s grid.
- Tempo 75 BPM. Beat 0.8 s = 24 frames; sixteenth 0.2 s = 6 frames; bar 3.2 s = 96 frames. Every kick and snare sits on
  the 0.2 s grid, so every hit lands on an exact integer frame at 30 fps.
- `at(bar, beat) = bar·3.2 + beat·0.8`. Example: kick at bar 8 + 1.75 beats = `at(8, 1.75)` = 27.0 s.
- Frames: `int(79.17244 · 30)` = 2,375 (79.1667 s). Audio keeps 79.172 s.
- After snapping detected hits to the nearest 0.1 s within 45 ms (mean shift 8.9 ms): 80 kicks, 52 snares, 158 hats.

## Form

| Time | Bars | What the data shows |
|---|---|---|
| 0.0-12.8 | 0-3 | Hook 1, no drums. Bass and "other" leave at about 10.0-10.3 (voice alone). Two lone low hits at 11.2 and 12.0, the first drums of the song |
| 12.8-25.6 | 4-7 | Quiet verse: hi-hats on every sixteenth, snare at bar+0.8 and bar+2.4. Hits stop at 23.8 (the last hat); none until 25.6: a 1.8 s silence |
| 25.6 | 8 | The drop: level up about +6.7 dB, low hits begin, bass much stronger |
| 25.6-51.2 | 8-15 | Loud verse with a kick at bar+1.4. Bar 14 is thinner (no snares) |
| 51.2-54.4 | 16 | Break: drums and bass out from about 51.0-51.3; lone low hits at 52.8, 53.6 and 54.4 |
| 54.4-67.2 | 17-20 | Hook 2, the loudest part |
| 67.2-79.17 | 21-24 | Hook 3, then a hard stop mid-line at full level. The last four hits: kick 78.2, snare 78.4, kick 78.6, kick 78.8 |

## The per-bar drop-out ("gap")

- In 16 bars (8-15 and 17-24) drums and bass vanish from bar+0.8 (the snare) to bar+1.4 (the next kick), about 0.6 s,
  level down about 8 dB, the voice alone. Re-measured from `song/envelopes.json` over all bars: about bar+0.86 to bar+1.36.
- Method that found it: per bar, print the mean bass at +0.2..0.7 s and at +0.9..1.3 s, and drums at +0.9..1.3 s.
- The earlier film used the nominal grid window (0.8 to 1.4) because kick and snare sit on the grid within 2 ms.
  Its final check found the picture switching into the gap on the snare frame and out on the kick frame in 16 of 16 bars.
- The gap and the drum grid are the song's facts; how the earlier film used them (a world swap, a leap, lettering) is
  its own design. Use the facts and find your own device.

## Hi-hats

- Detections have holes: 48 of the 56 sixteenth slots between 12.8 and 23.8 carry a detected hat (none at 13.0, 18.0,
  19.0, 19.2, 19.6, 20.4, 20.8, 22.4). For steady ticks use the nominal list `12.8 + 0.2·k`, k = 0..55. The quiet verse holds
  exactly 56 sixteenth slots.

## Words

- Word times are model estimates, good to about ±0.1 s inside a line. The 26 lines' start times matched the confirmed
  lyric file within 60 ms.
- The first word of the fourth hook line (about 10.2, 64.7 and 77.5 s) is uncertain. Never draw it; replace it with
  `[?]` when you generate the page data.
- Do not reproduce the lyric beyond the few words you decide to show.

## Envelopes

`song/envelopes.json` has 100 values per second: loudness (dBFS), low/mid/high bands, onset strength, and separated
voice, drums, bass and other layers. The earlier session normalised layers to the song's 99th percentile and mapped
loudness -26 dBFS → 0 and -4 dBFS → 1. Mouth movement from the voice layer:
`vox(t) = clamp(avg(vox, t, 0.04 s) · 1.25)`, `mouth = clamp((vox - 0.2) · 1.7)`.
