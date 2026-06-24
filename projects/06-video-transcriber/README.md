# Video Transcriber — autonomous speech-to-text

Drop a video into a watched folder and subtitles appear automatically. Prefers
existing captions; otherwise runs **OpenAI Whisper** on the GPU.

## How it works
- **Folder-watcher** auto-starts at login (Windows `shell:startup`) and processes
  new files with no manual step — fully hands-off.
- **GPU-accelerated** Whisper inference on an RTX card (CUDA).
- Model size tuned per language (`small`, `medium` for Polish).
- Reproducible Python environment via **`uv`** (Python 3.12); output written into Obsidian.

## What it demonstrates
Practical local ML deployment (real ASR models on GPU), automation, and
environment/reproducibility discipline.

## Stack
Python 3.12 · OpenAI Whisper · CUDA/GPU (RTX) · uv · Windows auto-start watcher

> Source lives in `C:\Users\gonta\video-transcriber\`.
