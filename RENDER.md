# Deploy NeuroForge on Render (for Despia)

Railway is no longer required. Use **Render** → free HTTPS URL → paste into Despia.

**Repo:** https://github.com/ms123321/NeuroForge  
**Start command:** `python start.py` (Waitress on `0.0.0.0:$PORT`)

---

## Option A — One-click Blueprint (easiest)

1. Log in at [https://dashboard.render.com](https://dashboard.render.com)
2. **New** → **Blueprint**
3. Connect GitHub → select **`ms123321/NeuroForge`**
4. Render reads `render.yaml` and creates the **neuroforge** web service
5. Apply / create
6. Wait for deploy → green **Live**
7. Open the URL Render shows, e.g.  
   `https://neuroforge.onrender.com`

---

## Option B — Manual Web Service

1. **New** → **Web Service**
2. Connect **`ms123321/NeuroForge`** (branch `main`)
3. Settings:

| Field | Value |
|--------|--------|
| **Name** | `neuroforge` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python start.py` |
| **Instance type** | Free |

4. **Environment** variables:

| Key | Value |
|-----|--------|
| `SECRET_KEY` | any long random string |
| `PYTHON_VERSION` | `3.12.8` (optional) |

Do **not** set `PORT` yourself — Render injects it.

5. **Create Web Service** → wait for Live

---

## Test before Despia

| URL | Expect |
|-----|--------|
| `https://YOUR-SERVICE.onrender.com/api/health` | `{"ok":true,...}` |
| `https://YOUR-SERVICE.onrender.com/` | NeuroForge home |

On free tier, the first request after ~15 min idle can take **30–60 seconds** (cold start). That’s normal.

---

## Despia

1. Open your Despia builder  
2. **Web URL** = `https://YOUR-SERVICE.onrender.com`  
   (not localhost, not railway.com)  
3. Save → rebuild/preview if needed  

---

## Logs if deploy fails

Render dashboard → service → **Logs**

You want:

```text
NeuroForge production start
 PORT=10000   (or whatever Render assigned)
 server=waitress
 Flask app loaded OK
 Starting Waitress on 0.0.0.0:...
```

**Start command must be** `python start.py` — never bare `gunicorn`.

---

## Checklist

- [ ] GitHub repo connected: `ms123321/NeuroForge`
- [ ] Build: `pip install -r requirements.txt`
- [ ] Start: `python start.py`
- [ ] Deploy Live
- [ ] `/api/health` works in browser (wait if cold)
- [ ] Same HTTPS URL in Despia

---

## After code updates

Push to `main` → Render auto-deploys → force-close Despia app → reopen for new web UI.
