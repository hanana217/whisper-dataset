import os
os.environ["TORCHAUDIO_USE_BACKEND_DISPATCHER"] = "1"

import glob
import subprocess
import shutil
import soundfile as sf
import numpy as np
from pathlib import Path

try:
    import torchaudio
    import torch
    def _sf_save(path, src, sample_rate, **kwargs):
        arr = src.numpy()
        if arr.ndim == 2:
            arr = arr.T  
        if arr.shape[-1] == 1 or arr.ndim == 1:
            arr = arr.squeeze()
        sf.write(str(path), arr, sample_rate)
    torchaudio.save = _sf_save
    print("✅ torchaudio.save patched to use soundfile")
except Exception as e:
    print(f"⚠️  Could not patch torchaudio: {e}")

DATASET_ROOT = "."     
all_wavs = sorted(glob.glob("/segments/*.wav", recursive=False))
print(f"🔍 Found {len(all_wavs)} WAV files across all segments folders\n")

if not all_wavs:
    print("❌ No WAV files found. Make sure you run this from the dataset root.")
    raise SystemExit(1)

from collections import defaultdict
by_folder = defaultdict(list)
for wav in all_wavs:
    folder = str(Path(wav).parent)
    by_folder[folder].append(wav)

print(f"📁 Processing {len(by_folder)} segments folders...\n")

total_done  = 0
total_fail  = 0
temp_out    = Path("_demucs_temp")

for folder, wavs in by_folder.items():
    folder_path = Path(folder)
    print(f"🎛️  {folder} — {len(wavs)} files")

    temp_out.mkdir(exist_ok=True)
    result = subprocess.run(
        ["python", "-m", "demucs",
         "--two-stems", "vocals",
         "--out", str(temp_out)]
        + wavs,
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"   ❌ Demucs failed for {folder}")
        print(result.stderr[-500:])
        total_fail += len(wavs)
        shutil.rmtree(temp_out, ignore_errors=True)
        temp_out.mkdir(exist_ok=True)
        continue

    done = 0
    for wav_path in wavs:
        stem        = Path(wav_path).stem
        orig_path   = Path(wav_path)

        vocals_path = temp_out / "htdemucs" / stem / "vocals.wav"

        if not vocals_path.exists():
            matches = list(temp_out.rglob(f"{stem}/vocals.wav"))
            if matches:
                vocals_path = matches[0]
            else:
                print(f"   ⚠️  vocals not found for {stem}")
                total_fail += 1
                continue

        vocals, sr = sf.read(str(vocals_path))
        if vocals.ndim > 1:
            vocals = vocals.mean(axis=1)   
        if np.abs(vocals).max() < 0.001:
            print(f"   ⚠️  Silent output for {stem} — keeping original")
            total_fail += 1
            continue

        vocals = (vocals / (np.abs(vocals).max() + 1e-8) * 0.95).astype(np.float32)

        sf.write(str(orig_path), vocals, sr)
        done += 1

    total_done += done
    print(f"   ✅ {done}/{len(wavs)} cleaned\n")

    shutil.rmtree(temp_out, ignore_errors=True)

print(f"{'─'*50}")
print(f"✅ All done!")
print(f"   Cleaned : {total_done} files")
print(f"   Failed  : {total_fail} files")
print(f"   Files overwritten in-place (same name, same folder)")
