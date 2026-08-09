# Deploy NeuroForge as a web app

Balloon Risk and Line Match were removed. The browser app runs the remaining research modes via Flask + your existing Python engines.

## Run locally

```powershell
cd C:\Users\gssei\NeuroForge
& "$env:LOCALAPPDATA\Python\bin\python.exe" -m pip install -r requirements-web.txt
& "$env:LOCALAPPDATA\Python\bin\python.exe" -m webapp.app
```

Open: **http://127.0.0.1:8080**

Or:

```powershell
$env:PORT=8080
python -m webapp.app
```

## What you get

| Feature | Web |
|---------|-----|
| Mode list | Yes |
| Play modes in browser | Yes (all engines) |
| Adaptive scoring | Yes (same `logic/`) |
| Progress save | Yes (server disk / same progress.json when local) |
| Free vs Pro gate | Same free mode list |
| Desktop polish UI | Desktop `main.py` still best for some multi-step modes |

## Deploy to the internet

### Option A — Railway / Render / Fly.io (recommended)

**Full Railway fix guide:** [`RAILWAY.md`](RAILWAY.md)  
(If you see **404 lost** on `railway.com/project/…`, that is the *dashboard*, not the game — generate a service domain.)

1. Create a free account on [Railway](https://railway.com), [Render](https://render.com), or [Fly.io](https://fly.io).  
2. Connect GitHub repo **`ms123321/NeuroForge`**.  
3. Start command (also in `Procfile` / `railway.toml` / `Dockerfile`):

```text
python start.py
```

(Do **not** use bare `gunicorn` — use `python start.py` so PATH is never required.)

4. Install uses root `requirements.txt` (includes Flask + gunicorn).  
5. Env:

```text
SECRET_KEY=<long-random-string>
```

6. **Generate Domain** on the service → open `https://….up.railway.app` (not the project settings URL).

### Option B — PythonAnywhere

1. Upload project.  
2. Web tab → Manual configuration → Flask.  
3. Point WSGI to `webapp.app:app`.  
4. Install `flask` in the virtualenv.

### Option C — Local network (friends on Wi‑Fi)

```powershell
# finds your LAN IP then serves
python -m webapp.app
# others open http://YOUR-LAN-IP:8080
```

### Option D — Docker (optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements-web.txt
ENV PORT=8080
CMD gunicorn -b 0.0.0.0:8080 -w 2 webapp.app:app
```

## Despia (iPhone / Android App Store)

**Full guide:** [`DESPIA.md`](DESPIA.md)

Short version:

1. Deploy this web app so you have a public **`https://…`** URL (not `127.0.0.1`).  
2. Confirm the game plays in the **phone’s browser** at that URL.  
3. In [Despia](https://despia.com): create app → set **Web URL** to that address.  
4. Enable push / IAP in Despia if you want native features.  
5. Build iOS/Android through Despia → TestFlight / Play internal test.

Your Python engines stay on the server; Despia is the native phone shell around the site.

## Project layout

```
webapp/
  app.py           # Flask API + pages
  trial_api.py     # engine ↔ JSON
  session_store.py
  templates/index.html
  static/app.css
  static/app.js
Procfile           # for Heroku-style hosts
requirements-web.txt
```

## Security notes for production

- Set a strong `SECRET_KEY`.  
- Use HTTPS only.  
- Progress is per-server filesystem unless you add a database.  
- Free/Pro is local entitlement file — for multi-user cloud, plug in real auth later.
