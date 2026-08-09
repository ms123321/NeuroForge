# Get NeuroForge on Despia (iPhone + Android)

Despia does **not** package the Python tkinter desktop app.  
It wraps your **web version** (`webapp/`) as a native shell for the App Store / Play Store.

```
Phone (Despia app)  →  loads HTTPS URL  →  Flask server (your engines)
```

Local `http://127.0.0.1:8080` only works on your PC. Phones need a **public HTTPS** site.

---

## Overview (4 steps)

| Step | What |
|------|------|
| 1 | Confirm the game works in a browser (`Start Web App.bat`) |
| 2 | Deploy web app to the internet (Railway / Render / Fly) |
| 3 | Create a Despia project and paste that HTTPS URL |
| 4 | Enable push / IAP in Despia → build & submit stores |

---

## Step 1 — Web game works locally

```powershell
cd C:\Users\gssei\NeuroForge
# double-click Start Web App.bat
# or:
& "$env:LOCALAPPDATA\Python\bin\python.exe" -m webapp.app
```

Open **http://127.0.0.1:8080** — Daily Circuit / modes should play.

If this fails, fix the web app first. Despia only shows whatever that site serves.

---

## Step 2 — Put the site on HTTPS (required)

Despia and App Store review need a real URL, e.g. `https://neuroforge.onrender.com`.

### Easiest path: Render (recommended)

Full guide: **[`RENDER.md`](RENDER.md)** · Blueprint: `render.yaml`

1. [dashboard.render.com](https://dashboard.render.com) → **New → Web Service**  
2. Connect GitHub **`ms123321/NeuroForge`** (branch `main`)  
3. **Build command:** `pip install -r requirements.txt`  
4. **Start command:** `python start.py`  
5. Env: `SECRET_KEY` = any long random string (Render sets `PORT`)  
6. Deploy → copy URL, e.g. `https://neuroforge.onrender.com`  

Or **New → Blueprint** and use the repo’s `render.yaml`.

### Alternatives

- Railway — optional (`RAILWAY.md`)  
- Fly.io / AWS — `WEB_DEPLOY.md` / `XCODE_AWS.md`

**Test on your phone’s browser first**  
Open the HTTPS link on iPhone/Android Safari/Chrome. Play a mode.  
If the phone browser works, Despia will too.

---

## Step 3 — Connect Despia

1. Sign up / log in at [despia.com](https://despia.com)
2. **Create a new app** (or project)
3. Set the **Web URL / App URL** to your HTTPS address from Step 2  
   - Example: `https://your-app.up.railway.app`  
   - **Not** `http://127.0.0.1:8080`  
   - **Not** `http://` (use **https://**)
4. Fill store metadata:
   - **Name:** NeuroForge  
   - **Bundle / package id:** e.g. `com.yourname.neuroforge`  
   - **Icon:** use `assets/icon_1024.png` (or `webapp/static/icon-512.png`)  
   - **Splash / theme:** dark `#0B1020`
5. Save / preview in Despia’s simulator if available

Despia loads your game inside a native WebView (WKWebView / Android WebView) with extra native APIs.

---

## Step 4 — Native features (push, purchases)

### Push notifications (iPhone / Android)

NeuroForge already has mobile push prefs + APIs:

- Settings → **Enable phone push**
- APIs: `/api/notifications`, `/api/notifications/register`  
- Full detail: `MOBILE_PUSH.md`

In Despia:

1. Turn on **Push Notifications** for the project  
2. Follow Despia’s wizard for APNs (Apple) + FCM (Google)  
3. When Despia gives you a **device token**, register it:

```http
POST https://YOUR-DOMAIN/api/notifications/register
Content-Type: application/json

{
  "token": "<device-token-from-despia>",
  "platform": "ios",
  "label": "iPhone"
}
```

Use `"android"` on Play builds.  
Schedule local daily/evening reminders from:

```http
GET https://YOUR-DOMAIN/api/notifications/schedule
```

If Despia injects a JS bridge (check their docs), call register from the app after permission is granted.  
Until remote FCM/APNs keys are wired, users still get **in-app / PWA-style** notifications when the WebView allows them.

### In-app purchases (Pro)

Web currently **simulates** buy buttons (same as desktop demo).  
For real money on the stores:

1. Enable **In-App Purchases** in Despia  
2. Create products in App Store Connect / Google Play Console:
   - Monthly `$4.99`
   - Yearly `$29.99`
   - Lifetime `$49.99`
3. Wire Despia’s purchase callbacks to unlock Pro  
   (today Pro is stored server-side via `/api/pro/buy` — replace that path with real receipt validation when you go live)

---

## Step 5 — Build & ship

1. In Despia: **Build** iOS and/or Android  
2. Download or let Despia publish:
   - **iOS** → App Store Connect / TestFlight  
   - **Android** → Play Console (internal testing first)
3. Apple/Google need:
   - Privacy policy URL (host a simple page or Notion link)
   - Screenshots (phone running the game)
   - Age rating, support URL, description

App Store checklist also lives in `APP_STORE_STEP_BY_STEP.md` (general store steps).

---

## Checklist

- [ ] Local web works at `127.0.0.1:8080`
- [ ] Project on GitHub (or uploaded to host)
- [ ] Deployed with gunicorn + `requirements-web.txt`
- [ ] `SECRET_KEY` set
- [ ] HTTPS URL opens on a **real phone browser** and modes play
- [ ] Despia Web URL = that HTTPS URL
- [ ] Icon 1024×1024 uploaded
- [ ] Bundle id reserved
- [ ] Push enabled (optional but recommended)
- [ ] IAP products created (for real Pro)
- [ ] Privacy policy URL
- [ ] TestFlight / internal testing before public release

---

## Common problems

| Problem | Fix |
|---------|-----|
| Blank app in Despia | URL wrong, or still `http://127.0.0.1` — use public **https** |
| Works on PC, not phone | Host not public, or firewall; test HTTPS in phone Safari first |
| “Connection refused” | Server asleep (free tiers) — open URL once to wake, or use always-on plan |
| Game loads but play fails | Check `/api/health` on the public URL; logs on Railway/Render |
| Push never shows | iOS needs permission + Despia push setup; see `MOBILE_PUSH.md` |
| Progress resets | Server filesystem is ephemeral on some hosts — for production, add a DB later |
| Pro “buys” free | Expected until real StoreKit / Play Billing is connected via Despia |

---

## What Despia uses vs what it does not

| Included | Not used by Despia |
|----------|--------------------|
| `webapp/` Flask app | `main.py` tkinter desktop |
| `neuroforge/logic/` engines (on server) | Windows toast / Task Scheduler |
| HTTPS public URL | `Play NeuroForge.bat` |
| Optional Despia push / IAP | BeeWare-only packaging path |

---

## Minimal “do this today” path

1. Push code to GitHub  
2. Railway → New project from repo → wait for HTTPS link  
3. Open that link on your phone — play Daily Circuit  
4. Despia → New app → paste HTTPS link → Build  
5. Install TestFlight / internal APK and play  

That’s the whole pipeline: **host the web game → paste URL into Despia → build stores.**
