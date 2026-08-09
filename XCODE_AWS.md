# NeuroForge on iPhone via Xcode + AWS (Mac)

Apple only accepts iOS apps **built and signed on a Mac with Xcode**.  
AWS hosts your **game server** (Flask). Xcode builds the **iPhone app** that talks to it.

```
┌─────────────────┐         HTTPS          ┌──────────────────────┐
│  iPhone app     │  ───────────────────►  │  AWS (your game)     │
│  Xcode / WKWeb  │                        │  Flask + engines     │
│  View shell     │  ◄───────────────────  │  https://….aws…      │
└─────────────────┘                        └──────────────────────┘
```

You **cannot** put the Windows tkinter window on the App Store.  
Use the **web app** (`webapp/`) as what the phone loads.

---

## What you need

| Item | Why |
|------|-----|
| **Mac** (or cloud Mac — see bottom) | Xcode only runs on macOS |
| **Xcode** (Mac App Store, free) | Build, sign, Archive |
| **Apple Developer** ($99/year) | TestFlight + App Store |
| **AWS account** | Host the Flask game publicly |
| This repo on the Mac | Source + icons |

---

## Path overview (recommended)

| Step | Where | What |
|------|--------|------|
| 1 | Anywhere | Confirm web game works locally |
| 2 | **AWS** | Deploy Flask → get `https://…` URL |
| 3 | **Mac + Xcode** | Create a simple iOS app that opens that URL |
| 4 | Xcode | Sign, run on Simulator / iPhone |
| 5 | App Store Connect | Archive → TestFlight → Review |

Alternative (Python-on-device): BeeWare **Briefcase** → open generated project in Xcode (section at end). That uses `mobile_app.py` (simpler UI), not the full web UI.

---

# Part A — Host the game on AWS

The phone needs a public **HTTPS** URL. Pick one AWS option.

## Option A1 — AWS App Runner (simplest “just run my Flask app”)

1. Push NeuroForge to **GitHub**.
2. AWS Console → **App Runner** → Create service → Source: GitHub.
3. Build settings (or `apprunner.yaml` if you add one):

```text
Runtime: Python 3
Build command:  pip install -r requirements-web.txt
Start command:  gunicorn -b 0.0.0.0:8080 -w 2 webapp.app:app
Port: 8080
```

4. Environment:

```text
SECRET_KEY=<long-random-string>
PORT=8080
```

5. Deploy → copy the HTTPS service URL, e.g.  
   `https://xxxxx.us-east-1.awsapprunner.com`

## Option A2 — AWS Elastic Beanstalk

1. Install EB CLI on your machine, or use Console “Create application”.
2. Platform: **Python 3.11/3.12**.
3. Upload zip of the project (or connect GitHub).
4. Set process:

```text
gunicorn -b 0.0.0.0:8000 -w 2 webapp.app:app
```

5. Open the environment URL (HTTPS).

## Option A3 — EC2 (more control)

1. Launch **Ubuntu** t3.small (or free tier if available).
2. Security group: open **80** and **443** (and 22 for SSH).
3. SSH in:

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx
cd /opt
sudo git clone <your-repo-url> neuroforge
cd neuroforge
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-web.txt
```

4. Systemd service `/etc/systemd/system/neuroforge.service`:

```ini
[Unit]
Description=NeuroForge
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/neuroforge
Environment=SECRET_KEY=change-me
Environment=PORT=8080
ExecStart=/opt/neuroforge/.venv/bin/gunicorn -b 127.0.0.1:8080 -w 2 webapp.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now neuroforge
```

5. Nginx reverse proxy + HTTPS (Let’s Encrypt):

```nginx
server {
    server_name your-domain.com;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo certbot --nginx -d your-domain.com
```

## Test before Xcode

On any phone browser open:

```text
https://YOUR-AWS-URL/
```

- Home loads  
- Daily Circuit plays  
- `/api/health` returns `{"ok": true, ...}`  

If the **phone browser** fails, fix AWS first. Xcode will only show the same site.

---

# Part B — Xcode app that loads your AWS game

This is a thin **native shell** (WKWebView) — same idea as Despia, but you own the Xcode project.

## B1. Create the project on the Mac

1. Install **Xcode** from the Mac App Store → open once → accept license.
2. **File → New → Project → iOS → App**
3. Settings:

| Field | Value |
|-------|--------|
| Product Name | NeuroForge |
| Team | Your Apple Developer team |
| Organization Identifier | `com.yourname` |
| Bundle Identifier | `com.yourname.neuroforge` |
| Interface | **Storyboard** *or* **SwiftUI** |
| Language | **Swift** |

4. Save the project (e.g. `~/Projects/NeuroForgeIOS`).

## B2. SwiftUI WebView (copy-paste)

Replace `ContentView.swift` with:

```swift
import SwiftUI
import WebKit

struct ContentView: View {
    // ⚠️ Put your real AWS HTTPS URL here
    private let gameURL = URL(string: "https://YOUR-AWS-URL/")!

    var body: some View {
        GameWebView(url: gameURL)
            .ignoresSafeArea() // full screen like a game
    }
}

struct GameWebView: UIViewRepresentable {
    let url: URL

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.scrollView.bounces = false
        webView.allowsBackForwardNavigationGestures = false
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}
}
```

In `Info.plist` (or Target → Info), if you ever load non-HTTPS during dev:

- Prefer **HTTPS only** for App Store.
- For local Mac testing against a PC, use your Mac’s LAN URL only in Debug.

Optional: allow arbitrary loads only for debug (not for production):

```xml
<key>NSAppTransportSecurity</key>
<dict>
  <key>NSAllowsArbitraryLoads</key>
  <false/>
</dict>
```

## B3. Icons & display name

1. Drag `assets/icon_1024.png` into **Assets → AppIcon** (or export sizes in Xcode).
2. Target → **Display Name:** NeuroForge  
3. Target → **Deployment:** iOS 15+ is fine.

## B4. Run on Simulator / iPhone

1. Top bar: choose **iPhone 15** simulator (or your device).
2. Plug in iPhone → Trust computer → select device.
3. **Signing & Capabilities:**  
   - Automatically manage signing  
   - Team = your paid Developer account  
4. Press **▶ Run**.

You should see the NeuroForge web UI from AWS inside the app.

## B5. Push notifications (optional, Xcode)

1. Target → **Signing & Capabilities → + Capability → Push Notifications**
2. Also add **Background Modes → Remote notifications** if you use remote push
3. In [developer.apple.com](https://developer.apple.com) create an **APNs key**
4. Register device token to your AWS backend:

```http
POST https://YOUR-AWS-URL/api/notifications/register
Content-Type: application/json

{
  "token": "<deviceToken hex or string>",
  "platform": "ios",
  "label": "iPhone"
}
```

Full API: `MOBILE_PUSH.md`.

## B6. Ship to App Store Connect

1. Xcode → product destination **Any iOS Device (arm64)**  
2. **Product → Archive**  
3. **Distribute App → App Store Connect → Upload**  
4. [appstoreconnect.apple.com](https://appstoreconnect.apple.com):
   - Create app with same Bundle ID  
   - Privacy policy URL, screenshots, description  
   - Submit for **TestFlight** first, then **App Review**

Store copy rules: entertainment / brain training — **not** medical claims  
(see `APP_STORE_STEP_BY_STEP.md`).

---

# Part C — BeeWare + Xcode (Python engines on device)

Use this if you want a **native Python UI** (`neuroforge/mobile_app.py`) instead of the web UI.  
Still needs a **Mac + Xcode**. AWS is optional (no server required for offline play of the Toga shell).

On the Mac:

```bash
# Copy project to Mac (USB, git, or zip)
cd ~/Projects/NeuroForge

# Python 3.10–3.12 (Briefcase may not like 3.14)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-mobile.txt
pip install 'briefcase>=0.3.19' 'toga>=0.4.5'

# Icons
cp assets/icon_1024.png assets/icon.png

# Create & open iOS project
briefcase create iOS
briefcase build iOS
briefcase run iOS          # Simulator

# Or open in Xcode for signing / Archive:
open build/neuroforge/ios/xcode/NeuroForge.xcodeproj
```

Then in Xcode: set **Team**, unique Bundle ID, **Product → Archive**.

Script helper (on Mac): `scripts/package_ios.sh`

**Note:** Toga mobile shell is a **simpler** control set than the full web/desktop game.  
For the **full web UI** you already built, prefer **Part A + Part B**.

---

# If you don’t own a Mac

| Option | Notes |
|--------|--------|
| **MacStadium / MacinCloud / AWS EC2 Mac** | Rent a Mac in the cloud; install Xcode; same steps as above |
| **AWS EC2 Mac instances** | Real Mac hardware in AWS; more setup (Dedicated Host) |
| Friend’s Mac | Install Xcode, sign with *your* Apple Developer team |
| Despia | Skip Xcode; paste AWS HTTPS URL (see `DESPIA.md`) |

**AWS EC2 Mac (high level):**

1. AWS → EC2 → allocate **Dedicated Host** (Mac)  
2. Launch **macOS** AMI instance  
3. Connect via VNC / SSH + Screen Sharing  
4. Install Xcode from App Store on that Mac  
5. Clone repo, do Part B or Part C  

This is pricier than a used Mac Mini for many solo devs—but it works.

---

# Checklist

- [ ] Apple Developer enrolled ($99)  
- [ ] Web game plays on `https://YOUR-AWS-URL` from a **phone browser**  
- [ ] Mac with Xcode installed  
- [ ] Xcode project Bundle ID unique  
- [ ] WebView points at AWS HTTPS URL  
- [ ] Signing Team set  
- [ ] Runs on Simulator  
- [ ] Runs on physical iPhone  
- [ ] Archive uploaded to App Store Connect  
- [ ] Privacy policy + screenshots  
- [ ] TestFlight → App Review  

---

# Common failures

| Problem | Fix |
|---------|-----|
| Blank white screen | Wrong URL, HTTP blocked, or AWS down — open URL in Safari on the phone |
| ATS / secure connection error | Use HTTPS; fix cert on AWS (App Runner / certbot) |
| Signing error | Paid Developer team; unique Bundle ID; automatic signing on |
| Archive grayed out | Select “Any iOS Device”, not a simulator |
| Game slow | Use App Runner/Beanstalk closer region; gunicorn workers ≥ 2 |
| Progress resets on AWS | Ephemeral disk on some hosts — add DB later for multi-user |
| “Works on PC localhost only” | Xcode cannot use `127.0.0.1` of your Windows PC — deploy AWS |

---

# One-sentence summary

**Deploy NeuroForge web to AWS → create a Swift WKWebView app in Xcode that loads that HTTPS URL → Archive → TestFlight → App Store.**

Related docs: `WEB_DEPLOY.md`, `DESPIA.md`, `MOBILE_PUSH.md`, `APP_STORE_STEP_BY_STEP.md`, `MOBILE_PACKAGING.md`.
