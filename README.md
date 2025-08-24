## APPUI: Reactive Streamlit-like framework

APPUI pairs a FastAPI backend and a React renderer. The backend streams a JSON UI tree over WebSockets; the frontend renders it and sends events back.

### Install (pip)
```
pip install appui
```

### Run an app (CLI)
Create a file `examples/app.py`:
```
from appui.runtime import Session
from appui.dsl import text, button, vstack

def build_ui(session: Session):
    clicks = session.vars.get("clicks", 0)
    def inc(): session.vars["clicks"] = clicks + 1
    return vstack([text(f"Clicks: {clicks}"), button("+", on_click=inc)])
```
Run:
```
appui run examples/app.py:build_ui --host 127.0.0.1 --port 8000
```
Open `http://127.0.0.1:8000` in your browser.

### Develop this repo
Backend dev server (optional):
```
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.server:app --reload
```
Frontend (optional):
```
cd frontend
corepack enable && corepack prepare pnpm@9.12.2 --activate
pnpm install && pnpm dev
```

### Package structure
- `appui/`: installable Python package
- `appui/dsl`: UI primitives (`text`, `button`, `vstack`, `input_text`, `number_input`)
- `appui/runtime.py`: per-session state and event dispatch
- `appui/server.py`: FastAPI app factory serving static SPA and `/ws`
- `appui/static/`: compiled frontend assets (served at `/`)
- `examples/`: example app(s)

