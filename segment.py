import json
import soundfile as sf
import numpy as np
import pandas as pd
from pathlib import Path
from pydub import AudioSegment

audio_name        = "output_name"
audio_filename  = f"{audio_name}.wav"
transcript_file = "video-ID_transcript.json"
segment_sec     = 5
# ==================================================

base_dir     = Path(audio_name)
segments_dir = base_dir / "segments"
base_dir.mkdir(exist_ok=True)
segments_dir.mkdir(exist_ok=True)

print(f"📄 Loading transcript: {transcript_file}")
with open(transcript_file, "r", encoding="utf-8") as f:
    chunks = json.load(f)
print(f"   {len(chunks)} chunks loaded")

print(f"\n🎵 Loading audio: {audio_filename}")
audio     = AudioSegment.from_wav(audio_filename)
total_sec = len(audio) / 1000
print(f"   Duration: {total_sec:.1f}s")

def get_text_for_segment(seg_start, seg_end, chunks):
    texts = []
    for chunk in chunks:
        overlap_start = max(seg_start, chunk["start"])
        overlap_end   = min(seg_end,   chunk["end"])
        overlap       = overlap_end - overlap_start
        chunk_dur     = chunk["end"] - chunk["start"]
        if chunk_dur <= 0:
            continue
        if overlap / chunk_dur > 0.30:
            texts.append(chunk["text"])
    return " ".join(texts).strip()

print(f"\n✂️  Segmenting + aligning...\n")
segments = []
start_ms = 0
seg_idx  = 0

while start_ms < len(audio):
    end_ms   = min(start_ms + segment_sec * 1000, len(audio))
    seg_clip = audio[start_ms:end_ms]

    filename = segments_dir / f"{audio_name}_seg_{seg_idx:04d}.wav"

    # Save using soundfile (avoids torchaudio/torchcodec on Windows)
    samples = np.array(seg_clip.get_array_of_samples(), dtype=np.float32)
    samples = samples / (2**15)
    if seg_clip.channels == 2:
        samples = samples.reshape(-1, 2).mean(axis=1)
    sf.write(str(filename), samples, seg_clip.frame_rate)

    seg_start_s = start_ms / 1000
    seg_end_s   = end_ms   / 1000
    text        = get_text_for_segment(seg_start_s, seg_end_s, chunks)
    char_count  = len(text)

    segments.append({
        "file_name":  str(filename),
        "sentence":   text,
    })

    status = "✅" if text else "⚠️  EMPTY"
    print(f"  {filename.name} [{seg_start_s:.1f}s → {seg_end_s:.1f}s] {char_count} chars {status}")
    if text:
        print(f"      → {text[:80]}{'...' if len(text) > 80 else ''}")

    start_ms += segment_sec * 1000
    seg_idx  += 1

df       = pd.DataFrame(segments)
df       = df[["file_name", "sentence"]]
csv_path = base_dir / f"{audio_name}_metadata.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

empty  = df[df["sentence"] == ""]
filled = df[df["sentence"] != ""]


print(f"\n{'─'*50}")
print(f"✅ {len(df)} segments total")
print(f"   Transcribed : {len(filled)}")
print(f"   Empty       : {len(empty)} (fix manually in Excel)")
print(f"   CSV saved   : {csv_path}")

if len(empty) > 0:
    print(f"\n⚠️  Empty segments:")
    for _, row in empty.iterrows():
        print(f"   {row['file_name']}  [{row['start_time']}s → {row['end_time']}s]")

