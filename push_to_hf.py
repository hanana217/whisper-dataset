import os
os.environ["HF_HUB_DISABLE_XET"] = "1"

from pathlib import Path
from datasets import Dataset, Audio
import pandas as pd

# ===================== CONFIG =====================
CSV_PATH      = r"C:\Users\hanan\OneDrive\Desktop\dataset\metadata.csv"
DATASET_ROOT  = r"C:\Users\hanan\OneDrive\Desktop\dataset"   # Root folder containing all audio subfolders

HF_REPO       = "hananeek2/STT-algerian-dialect"
PRIVATE       = True
# ==================================================

print("📂 Loading CSV...")
df = pd.read_csv(CSV_PATH)

# Fix column names if needed
if 'file_name' not in df.columns and 'path' in df.columns:
    df = df.rename(columns={'path': 'file_name'})

# Detect text column
text_col = None
for col in ['sentence', 'text', 'transcription']:
    if col in df.columns:
        text_col = col
        break

if text_col is None:
    print("❌ No text/sentence column found!")
    print("Columns available:", df.columns.tolist())
    exit(1)

print(f"✅ Using '{text_col}' column for transcription")

# Build full audio paths
root = Path(DATASET_ROOT).resolve()
df["audio_path"] = df["file_name"].apply(lambda x: str(root / x))

# Check missing files
missing = df[~df["audio_path"].apply(os.path.exists)]
if len(missing) > 0:
    print(f"⚠️  {len(missing)} audio files missing!")
    df = df[df["audio_path"].apply(os.path.exists)].reset_index(drop=True)

print(f"✅ {len(df)} audio files ready")

# Generator (memory efficient)
def data_generator():
    for _, row in df.iterrows():
        yield {
            "audio": row["audio_path"],
            "sentence": str(row[text_col])
        }

print("\n🔄 Creating Dataset...")
ds = Dataset.from_generator(data_generator)
ds = ds.cast_column("audio", Audio(sampling_rate=16000))

print(f"✅ Dataset ready: {len(ds)} examples")

# Push to private repo
print(f"\n🚀 Pushing to private dataset → {HF_REPO}")
ds.push_to_hub(
    repo_id=HF_REPO,
    private=PRIVATE,
    commit_message="Upload Algerian Darija dataset",
)

print("\n🎉 Successfully pushed to your private dataset!")
print(f"Link: https://huggingface.co/datasets/{HF_REPO}")