# 🎙️ Algerian Darija STT Dataset Pipeline

A complete pipeline to build a **Speech-to-Text dataset** from YouTube videos — designed for Algerian Darija (Algerian Arabic dialect) but adaptable to any language. The output is a Hugging Face dataset ready to fine-tune [Whisper](https://github.com/openai/whisper) or any other ASR model.

---

## 📋 Pipeline Overview

```
YouTube Video
      │
      ▼
1. Download audio (yt-dlp)          ← download_audio (manual command)
      │
      ▼
2. Remove background music          ← remove_music.py
      │
      ▼
3. Fetch YouTube transcript         ← transcript.py
      │
      ▼
4. Segment audio + align transcript ← segment.py
      │
      ▼
5. (Manual) Review & correct CSV    ← open metadata CSV in Excel/LibreOffice
      │
      ▼
6. Push dataset to Hugging Face     ← push_to_hf.py
      │
      ▼
7. Count total dataset hours        ← count.py
```

---

## ⚙️ Installation

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install PyTorch (required by Demucs)
Visit [pytorch.org](https://pytorch.org/get-started/locally/) and pick the right command for your system.

**CPU only:**
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**CUDA 12.1 (GPU):**
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. Install ffmpeg (required by pydub & yt-dlp)
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
- **Linux/macOS:** `sudo apt install ffmpeg` or `brew install ffmpeg`

### 5. Authenticate with Hugging Face
```bash
huggingface-cli login
```

---

## 🚀 Step-by-Step Usage

> **For each new YouTube video, repeat all steps below.**

---

### Step 1 — Download audio from YouTube

```bash
python -m yt_dlp -x --audio-format wav --audio-quality 0 -o "output_name.%(ext)s" https://youtu.be/VIDEO_ID
```

**Arguments to change:**
| Argument | Description |
|---|---|
| `output_name` | Base name for the output `.wav` file (e.g. `output_23`) |
| `VIDEO_ID` | The YouTube video ID from the URL |

---

### Step 2 — Remove background music

```bash
# Place the .wav file in the current directory, then run:
python remove_music.py
```

**Arguments to change inside `remove_music.py`:**
| Variable | Description |
|---|---|
| `DATASET_ROOT` | Directory where your `.wav` files live (default: `.`) |

The script uses [Demucs](https://github.com/facebookresearch/demucs) to isolate vocals and overwrites the original `.wav` file with the cleaned version.

---

### Step 3 — Fetch YouTube transcript

```bash
python transcript.py
```

**Arguments to change inside `transcript.py`:**
| Variable | Description |
|---|---|
| `youtube_id` | YouTube video ID (e.g. `"GMNzJHdZxcU"`) |
| `output_dir` | Where to save the `.json` transcript (default: `.`) |

> ⚠️ **The video must have a YouTube-provided transcript (auto-generated or manual).** The script tries Arabic (`ar`) first, then French (`fr`), then falls back to whatever is available.

Output: `{youtube_id}_transcript.json`

---

### Step 4 — Segment audio and align transcript

```bash
python segment.py
```

**Arguments to change inside `segment.py`:**
| Variable | Description |
|---|---|
| `video_id` | Must match your `.wav` filename without extension (e.g. `"output_23"`) |
| `audio_filename` | Full `.wav` filename (e.g. `"output_23.wav"`) |
| `transcript_file` | Path to the `.json` from Step 3 |
| `segment_sec` | Duration of each audio segment in seconds (default: `5`) |

Output:
- `{video_id}/segments/` — folder of `.wav` clips
- `{video_id}/{video_id}_metadata.csv` — CSV with `file_name` and `sentence` columns

---

### Step 5 — Review & correct the CSV (manual)

Open `{video_id}_metadata.csv` in **Excel** or **LibreOffice Calc** and:
- Fill in any empty `sentence` cells
- Fix transcription errors (dialect words, diacritics, etc.)
- Remove segments with irrelevant audio (music, silence, noise)

---

### Step 6 — Push to Hugging Face

Once **all** videos are processed and their CSVs are corrected, merge them into one `metadata.csv` and run:

```bash
python push_to_hf.py
```

**Arguments to change inside `push_to_hf.py`:**
| Variable | Description |
|---|---|
| `CSV_PATH` | Full path to your merged `metadata.csv` |
| `DATASET_ROOT` | Root folder that contains all audio subfolders |
| `HF_REPO` | Your Hugging Face dataset repo (e.g. `"username/dataset-name"`) |
| `PRIVATE` | `True` to keep the dataset private, `False` to make it public |

---

### Step 7 — Count total hours

```bash
# Run from the dataset root folder
python count.py
```

Prints a table showing the number of `.wav` files and total duration per subfolder, plus a grand total.

---

## 📁 Expected Folder Structure

```
dataset/
├── output_23/
│   ├── segments/
│   │   ├── output_23_seg_0000.wav
│   │   ├── output_23_seg_0001.wav
│   │   └── ...
│   └── output_23_metadata.csv
├── output_24/
│   └── ...
├── metadata.csv          ← merged CSV for all videos
├── requirements.txt
└── *.py
```

---

## 📦 Dataset Format (Hugging Face)

The uploaded dataset has two columns:

| Column | Type | Description |
|---|---|---|
| `audio` | `Audio` (16 kHz) | WAV audio clip |
| `sentence` | `string` | Transcription text |

---

## 🛠️ Troubleshooting

**`No WAV files found` in remove_music.py**
→ Make sure you run the script from the folder where the `.wav` file is located.

**`vocals not found` warning**
→ Demucs couldn't separate that file. The original audio is kept as-is.

**Empty segments in segment.py**
→ Normal — happens when a segment falls between transcript chunks. Fill them manually in Excel.

**`No text/sentence column found` in push_to_hf.py**
→ Your CSV must have a column named `sentence`, `text`, or `transcription`.

**Demucs is slow**
→ Use a GPU. With a CPU, processing is significantly slower for long audio files.

---

## 📄 License

MIT
