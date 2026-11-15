# Song data

Everything in this folder describes one song: "Mirror Mirror" by Anno Domini Beats, from the YouTube Audio Library.

`passage.mp3` is the first 79.172 seconds of the full song (148.8 seconds), in one piece, with no fade at either end.
It was cut with `make_passage.py`.

The lyric words are not written out here, only their timings.

| File | What it is |
|---|---|
| `passage.mp3` | The audio for the video, 79.172 seconds. |
| `song-story.md` | What the whole song is about and how it moves, in plain words. Start here. |
| `lyric-lines.md` | The start time of each sung line in the passage (no words). |
| `song-map.md` | A readable summary of an automatic analysis of the **full** song: tempo, bars, sections, layers, moments and lyric line times. |
| `song-map.json` | The same with exact times: the beat and bar grid, and for each section its layers, drum hits, chords and lyric line count. Read its `how_to_read` list first. |
| `report.json` | Every observation behind the map: beats, bar beats, drum hits with class and strength, onsets, chord candidates, and lyric word timings (without the words). About 1 MB: look at its shape before loading all of it. |
| `envelopes.json` | Curves at 100 values per second: loudness, low, mid and high bands, onset strength, and the strength of each separated layer (voice, drums, bass, other). |

## Clocks

- The analysis files count in microseconds on the source timeline, which starts
  25,057 µs before the first sound. Subtract 25,057 µs to get the time in
  `passage.mp3`.
- After that subtraction the passage runs from 0 to 79,172,000 µs.
- The analysis covers the full song. Anything after 79.172 seconds is not in
  `passage.mp3`. It is here so the passage can be understood in its context.
- `song-story.md` and `lyric-lines.md` already use the `passage.mp3` clock.

## Bars

The bar tracker lost its place in the first 6.4 seconds of the song, so every bar
number in the analysis is two higher than a straight count. `song-story.md`
explains this under "What is uncertain".

## Lyrics

A listener checked the passage by ear: the transcribed lines are correct except the
first word of the fourth hook line (at 0:10.2, 1:04.7 and 1:17.5), which is
uncertain. Never show that word on screen. For the part of the song after the
passage, nobody has checked the words by ear.

## Everything else

Every value in the analysis is an estimate or a model's suggestion unless the
report marks it as measured. Nobody listened to the song to produce it.
