# Railway from scratch — NeuroForge

Repo is ready: **https://github.com/ms123321/NeuroForge** (branch `main`)

What runs in production:

| Piece | Value |
|-------|--------|
| Build | `Dockerfile` |
| Start | `python start.py` |
| Bind | `0.0.0.0:8080` |
| Workers | 1 gunicorn worker |
| Health | `/api/health` |

---

## Part 0 — Delete the old broken project (optional)

1. Open [https://railway.com/dashboard](https://railway.com/dashboard) (log in)
2. Open the old **NeuroForge** project (the one that 502’d)
3. **Settings** (project settings, gear) → scroll to **Delete Project**
4. Confirm delete  

You can also leave it and just create a **new** project.

---

## Part 1 — New project from GitHub

1. Go to [https://railway.com/new](https://railway.com/new)  
   or Dashboard → **New Project**
2. Choose **Deploy from GitHub repo**
3. If asked, **Configure GitHub App** → grant access to **`ms123321/NeuroForge`**
4. Click repo **`NeuroForge`** (ms123321)
5. Prefer **Add variables** first (not Deploy Now), if you see both options  

---

## Part 2 — Variables (before first successful run)

Click the new **service** card → **Variables** → **+ New Variable** (or raw editor):

```text
PORT=8080
SECRET_KEY=neuroforge-change-this-to-any-long-random-string
```

Then click **Deploy** (top of canvas) if deploy didn’t start automatically.

---

## Part 3 — Wait for green deploy

1. Click the service → **Deployments**
2. Open the latest deployment
3. Wait until status is **Success** (not Failed)

**Build logs** should include something like:

```text
build-import-ok
```

**Deploy logs** should include:

```text
NeuroForge production start
 PORT=8080
 Flask app loaded OK
 Starting gunicorn on 0.0.0.0:8080
```

### If Build fails

- Confirm root has `Dockerfile` and `requirements.txt` (they do on GitHub)
- Settings → no wrong “Root Directory” (leave empty / `/`)

### If Deploy fails on Healthcheck

1. Service → **Settings** → **Deploy**
2. **Healthcheck Path** → **clear / disable**
3. **Custom Start Command** → **must be empty**
4. Redeploy

---

## Part 4 — Public domain (this is the game URL)

1. Click the **service** (not only the project name)
2. **Settings**
3. Scroll to **Networking** / **Public Networking**
4. **Generate Service Domain** (or Generate Domain)
5. **Port = `8080`** ← same as `PORT`
6. Save

You get a URL like:

```text
https://neuroforge-xxxx.up.railway.app
```

### Test in browser

1. `https://YOUR-DOMAIN.up.railway.app/api/health`  
   → `{"ok":true,"modes":45,...}`
2. `https://YOUR-DOMAIN.up.railway.app/`  
   → NeuroForge home screen

**Do not use** `https://railway.com/project/...` for Despia.

---

## Part 5 — Despia

1. Open your Despia builder  
2. Set **Web URL** to the **`.up.railway.app`** URL from Part 4  
3. Save  
4. Rebuild / preview Despia if needed  

---

## Checklist (print this)

- [ ] Old project deleted (optional)
- [ ] New project → GitHub → `ms123321/NeuroForge`
- [ ] Variables: `PORT=8080`, `SECRET_KEY=...`
- [ ] Deploy **Success**
- [ ] Healthcheck **off**, custom start command **empty**
- [ ] Generate domain, port **8080**
- [ ] `/api/health` works in browser
- [ ] Home page loads
- [ ] Same URL pasted into Despia

---

## Common mistakes

| Mistake | Result |
|---------|--------|
| Domain port ≠ 8080 | Application failed to respond / 502 |
| Custom start command with wrong `$PORT` | App never listens |
| Healthcheck on before app is up | Deploy “failed” at Network › Healthcheck |
| Using project dashboard URL in Despia | 404 lost |
| Root directory set to `webapp/` | Docker/build breaks |

---

## After it works

Every `git push` to `main` can auto-redeploy.  
Despia will load the new web UI on next app open (OTA) — no rebuild needed for pure web changes.
