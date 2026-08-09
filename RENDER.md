# Deploy NeuroForge on Render (for Despia)

**Repo:** https://github.com/ms123321/NeuroForge  

## Critical: Start command

Render’s **default** is broken for this app:

```text
gunicorn your_application.wsgi   ← default (often wrong / missing package)
```

You **must** set:

```text
python start.py
```

| Field | Value |
|--------|--------|
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python start.py` |
| **Python** | `3.12.8` (set env `PYTHON_VERSION=3.12.8` or use `.python-version`) |

If the service was created with the wrong start command, open:

**Dashboard → your service → Settings → Build & Deploy → Start Command**  
→ change to `python start.py` → **Save** → **Manual Deploy**.

---

## New service (manual)

1. [dashboard.render.com](https://dashboard.render.com) → **New → Web Service**
2. GitHub **`ms123321/NeuroForge`**, branch **`main`**
3. Runtime: **Python 3**
4. Build: `pip install -r requirements.txt`
5. Start: **`python start.py`**  ← do not leave default
6. Env:
   - `SECRET_KEY` = long random string  
   - `PYTHON_VERSION` = `3.12.8`
7. Create → wait for **Live**
8. Open `https://YOUR.onrender.com/api/health`

---

## Blueprint

**New → Blueprint** → this repo (`render.yaml` already sets `startCommand: python start.py`).

---

## Despia

Paste: `https://YOUR-SERVICE.onrender.com`  
(not localhost, not Railway)

Free tier cold start: first open after idle can take 30–60s.

---

## Logs you want

```text
NeuroForge production start
 server=waitress
 Flask app loaded OK
 Starting Waitress on 0.0.0.0:...
```

**Not:** `Running 'gunicorn your_application.wsgi'` / `gunicorn: command not found`
