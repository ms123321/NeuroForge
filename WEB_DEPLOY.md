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

1. Create a free account on [Railway](https://railway.app), [Render](https://render.com), or [Fly.io](https://fly.io).  
2. Connect this GitHub repo (or upload the project zip).  
3. Set start command:

```text
gunicorn -b 0.0.0.0:$PORT -w 2 webapp.app:app
```

4. Install:

```text
pip install -r requirements-web.txt
```

5. Set env vars:

```text
SECRET_KEY=<long-random-string>
PORT=8080
```

6. Deploy → open the public HTTPS URL.

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
