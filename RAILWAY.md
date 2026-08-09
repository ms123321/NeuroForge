# Fix Railway “404 lost” for NeuroForge

## Important: two different URLs

| URL type | Example | What it is |
|----------|---------|------------|
| **Project dashboard** (login required) | `https://railway.com/project/bae4522f-…` | Settings UI — **not** the game |
| **Public app domain** | `https://neuroforge-production.up.railway.app` | What Despia / phones open |

If you open the **project** link while logged out, or the project has **no running service**, you see **404 / lost**.

That does **not** mean the game URL is ready. You must **deploy a service** first.

---

## Healthcheck failure (Deploy → Network › Healthcheck)

Railway aborted the deploy because `/api/health` did not return 200 in time
(or the app was not listening yet).

**Fix:**

1. Pull latest `main` (healthcheck removed from `railway.toml`).
2. In Railway **Service → Settings → Deploy**:
   - **Healthcheck Path** → clear it / disable healthcheck  
   - **Custom Start Command** → clear it (use Docker `start.sh`)
3. Variables: `PORT=8080`, `SECRET_KEY=...`
4. Public Networking port: **8080**
5. **Redeploy**

After the site loads, you can re-enable healthcheck with path `/api/health`.

---

## “Application failed to respond”

Railway’s domain works, but nothing answers inside the container.

### Fix (most common)

1. **Service → Variables** — set:
   ```text
   PORT=8080
   SECRET_KEY=any-long-random-string
   ```
2. **Public Networking** — domain port must be **`8080`** (same as PORT).
3. **Settings → Deploy** — start command (must match git):
   ```text
   python start.py
   ```
   Delete any old command that starts with bare `gunicorn`.
4. **Deployments** → open the latest deploy → **View Logs**.
   - Look for `Listening at: http://0.0.0.0:8080` or similar.
   - Red traceback = crash (copy it and fix).
5. **Redeploy** (Deployments → ⋯ → Redeploy) after changing variables.

### Port rule

| Place | Value |
|-------|--------|
| Variable `PORT` | `8080` |
| Public Networking port | `8080` |
| App bind | `0.0.0.0:$PORT` |

If those three disagree → **Application failed to respond**.

---

## Fix in ~10 minutes

### 1. Open Railway while logged in

1. Go to [https://railway.com](https://railway.com) and **log in**  
2. Open your project (or create a new one if the old one is empty)

### 2. Deploy from GitHub

1. In the project → **+ New** → **GitHub Repo**  
2. Select **`ms123321/NeuroForge`**  
   (https://github.com/ms123321/NeuroForge)  
3. If GitHub isn’t connected: **Configure GitHub App** → allow the NeuroForge repo  
4. Railway will detect Python and use:

```text
Install:  pip install -r requirements.txt
Start:    gunicorn -b 0.0.0.0:$PORT -w 2 webapp.app:app
```

(Repo already has `Procfile`, `railway.toml`, `requirements.txt` with Flask.)

### 3. Variables

Service → **Variables** → add:

```text
SECRET_KEY=any-long-random-string-you-choose
```

(Optional) Railway sets `PORT` automatically — do not hardcode it.

### 4. Generate a public domain

1. Click the **service** (not just the project)  
2. **Settings** → **Networking** → **Generate Domain**  
3. Copy the URL, e.g.:

```text
https://neuroforge-production-xxxx.up.railway.app
```

4. Open **that** URL in a browser — you should see NeuroForge home  
5. Check health: `https://YOUR-DOMAIN/api/health` → `{"ok":true,...}`

### 5. Paste into Despia

Use the **`.up.railway.app` domain**, **not**:

- `https://railway.com/project/bae4522f-…`  
- `http://127.0.0.1:8080`

---

## If deploy fails (red build)

Open **Deployments** → failed deploy → **View logs**.

| Log message | Fix |
|-------------|-----|
| `No module named flask` | Redeploy after latest GitHub push (`requirements.txt` has flask) |
| `No module named webapp` | Root directory must be repo root (where `webapp/` lives) |
| `Address already in use` | Don’t set PORT yourself; use `$PORT` |
| Build OK but 404 on `/` | Wrong domain; use **Generate Domain** on the **service** |
| App sleeps / intermittent | Free tier — open the URL once to wake; or enable always-on |

### Manual start command (if auto-detect wrong)

**Settings → Deploy → Custom Start Command:**

```text
gunicorn -b 0.0.0.0:$PORT -w 2 webapp.app:app
```

**Custom Build Command** (only if needed):

```text
pip install -r requirements.txt
```

---

## Fresh project (if old one is broken)

1. Railway → **New Project** → **Deploy from GitHub** → `ms123321/NeuroForge`  
2. Wait for green deploy  
3. **Generate Domain**  
4. Test in browser  
5. Put that domain in Despia  

You can delete the empty `bae4522f-…` project if it never had a service.

---

## Checklist

- [ ] Logged into railway.com  
- [ ] Service connected to **ms123321/NeuroForge**  
- [ ] Latest deploy **green**  
- [ ] `SECRET_KEY` set  
- [ ] **Generate Domain** done  
- [ ] `https://….up.railway.app` loads NeuroForge  
- [ ] Same URL pasted into Despia  

---

## After GitHub updates

Push to `main` → Railway auto-redeploys → close/reopen Despia app (OTA web content).
