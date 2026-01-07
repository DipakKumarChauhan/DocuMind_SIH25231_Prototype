# DocuMind Prototype

## Environment Setup

1. Copy the example env file and fill in real values (keep it private and never commit `.env`):

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and set:
# QDRANT_URL=...
# QDRANT_API_KEY=...
# GROQ_API_KEY=...
# ENV=development
# (Optional) CLIP_MODEL_PATH=/absolute/path/to/clip-vit-base-patch32  # avoids network
# IMAGE_EMBEDDING_MODE=auto  # auto|remote|local|ocr
```

2. Ensure local files are ignored by Git (already configured):
- `.env`, `*.env`, `.env.local`, `.env.*.local`
- `backend/app/venv/` and `venv/`

3. Install backend dependencies (in a venv you create outside the repo or under `backend/app/venv` which is gitignored):

```bash
cd backend/app
# Optional: python3 -m venv ../app-venv && source ../app-venv/bin/activate
pip install -r requirements.txt
```

## Notes
- Rotate any API keys that were previously present locally, just to be safe.
- Do not commit `.env` or any virtual environment folders.
