from youtube_transcript_api import YouTubeTranscriptApi
import json
from pathlib import Path

youtube_id = "video_id"   
output_dir = "."               
# ==================================================

api = YouTubeTranscriptApi()

print(f"📥 Fetching transcript for: {youtube_id}")

try:
    entries = api.fetch(youtube_id, languages=["ar"])
    lang = "ar"
except Exception:
    try:
        entries = api.fetch(youtube_id, languages=["fr"])
        lang = "fr"
    except Exception:
        entries = api.fetch(youtube_id)
        lang = "auto"

chunks = []
for e in entries:
    chunks.append({
        "start": e.start,
        "end":   e.start + e.duration,
        "text":  e.text.strip().replace("\n", " "),
    })

out_path = Path(output_dir) / f"{youtube_id}_transcript.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"✅ {len(chunks)} chunks saved → {out_path}")
print(f"   Language: {lang}")
print(f"\nPreview (first 5):")
for c in chunks[:5]:
    print(f"  [{c['start']:.1f}s → {c['end']:.1f}s] {c['text'][:60]}")
