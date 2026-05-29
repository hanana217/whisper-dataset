import os
from pathlib import Path
import soundfile as sf

ROOT = "."

total_sec = 0
total_files = 0
errors = 0

folder_stats = []

for segments_dir in sorted(Path(ROOT).rglob("segments")):
    wav_files = sorted(segments_dir.glob("*.wav"))
    if not wav_files:
        continue

    folder_sec = 0
    for wav in wav_files:
        try:
            info = sf.info(str(wav))
            folder_sec += info.duration
            total_files += 1
        except Exception:
            errors += 1

    total_sec += folder_sec
    folder_stats.append((segments_dir.parent.name, len(wav_files), folder_sec))

print(f"\n{'─'*55}")
print(f"{'Folder':<30} {'Files':>6} {'Duration':>12}")
print(f"{'─'*55}")

for name, count, sec in folder_stats:
    h, m, s = int(sec//3600), int((sec%3600)//60), int(sec%60)
    print(f"{name:<30} {count:>6}   {h:02d}:{m:02d}:{s:02d}")

print(f"{'─'*55}")
h, m, s = int(total_sec//3600), int((total_sec%3600)//60), int(total_sec%60)
print(f"{'TOTAL':<30} {total_files:>6}   {h:02d}:{m:02d}:{s:02d}")
if errors:
    print(f"\n⚠️  {errors} files could not be read")