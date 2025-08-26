
# QuickTools (Stateless Flask on Render)

A small, useful toolbox with **no database or file storage**:
- Text Analyzer
- Unit Converter
- QR Code Generator
- Image Resizer (in-memory)

## Run locally
```bash
pip install -r requirements.txt
flask --app app run --debug
```

## Deploy on Render
1. Push this folder to a new GitHub repo.
2. On Render, create a **Web Service** → **Build & deploy from a Git repo**.
3. Select your repo. Render will auto-detect `Python` via `requirements.txt`.
4. Start command is taken from `Procfile`: `web: gunicorn app:app`.
5. Click Deploy. Done!
