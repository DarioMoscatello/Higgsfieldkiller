"""Cut song/passage.mp3 from the full track.

Make song/passage.mp3 from the full track of "Mirror Mirror" by Anno Domini Beats (YouTube Audio Library).
From the project folder:

  python -X utf8 song/make_passage.py "<path to the full mp3>"

It checks that your file is the one the analysis was made from, then writes the first 79.172 seconds, unchanged in
timing and level, to song/passage.mp3. Needs FFmpeg and ffprobe on PATH.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

EXPECTED_SHA256 = "6d6a7e8ad9249decb66ea38032b2babafd6b90c9bf2c9bbd2066df056885cf5d"
EXPECTED_BYTES = 5_954_910
PASSAGE_SECONDS = 79.172
OUT = Path(__file__).resolve().parent / "passage.mp3"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    src = Path(sys.argv[1])
    if not src.is_file():
        print(f"not a file: {src}")
        return 2
    if OUT.exists():
        print(f"{OUT} already exists; delete it first if you want to make it again.")
        return 2
    data = src.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest == EXPECTED_SHA256:
        print("Your file matches the analysed track exactly.")
    else:
        print(f"WARNING: your file differs from the analysed track ({len(data):,} bytes, sha256 {digest[:16]}...;"
              f" expected {EXPECTED_BYTES:,} bytes, {EXPECTED_SHA256[:16]}...).")
        print("The music is probably the same, but timings in the analysis may be a few milliseconds off.")
        print("Check that the first drum hits fall at about 11.2 s and 12.0 s in the passage.")
    subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(src), "-t", str(PASSAGE_SECONDS),
                    "-map", "0:a:0", "-c:a", "libmp3lame", "-b:a", "320k", str(OUT)], check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT)],
                         capture_output=True, text=True, check=True).stdout.strip()
    print(f"wrote {OUT} ({float(dur):.3f} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
