# NeuroForge — iOS & Android packaging

## Important (read first)

| Platform | Can you ship **today’s tkinter desktop** as-is? | Real path |
|----------|--------------------------------------------------|-----------|
| **Windows desktop** | Yes — `python main.py` | Done |
| **iOS App Store** | **No** — no tkinter on iPhone | BeeWare **Toga** + **Briefcase** on a **Mac**, or SwiftUI rewrite |
| **Google Play** | **No** — same UI limit | BeeWare **Toga** + **Briefcase**, or Kivy/Buildozer |

**What is already packaged in this repo**

- Pure game logic (`neuroforge/logic/`) — works on mobile as-is  
- Progress / adaptive levels (`progress.py`)  
- **Toga mobile shell** (`neuroforge/mobile_app.py`) for Briefcase  
- Briefcase config in `pyproject.toml`  
- Icons under `assets/icon*.png`  
- This guide + scripts  

**What you still need on your side**

| iOS | Android |
|-----|---------|
| Mac + Xcode | Android Studio / SDK (or Briefcase will guide) |
| [Apple Developer](https://developer.apple.com/programs/) **$99/year** | [Google Play Console](https://play.google.com/console) **$25 one-time** |
| Unique Bundle ID (change `com.neuroforge.app` if taken) | Same application id |

You **cannot** finish a signed App Store IPA from Windows alone. Android APK/AAB **can** be built on Windows with Briefcase + Android SDK.

---

## 1. Install build tools

```bash
cd NeuroForge
python -m pip install -r requirements-mobile.txt
# Prefer Python 3.10–3.12 for Briefcase (3.14 may be unsupported)
```

---

## 2. Android package (Windows, Mac, or Linux)

```bash
cd NeuroForge
briefcase create android
briefcase build android
briefcase run android          # emulator or device
briefcase package android      # → .aab / .apk for Play Store
```

Output is typically under:

```
build/neuroforge/android/gradle/.../outputs/
```

### Upload to Google Play

1. Create app in Play Console  
2. Complete store listing, content rating, privacy policy URL  
3. Upload **AAB** from `briefcase package android`  
4. Internal testing → production  

Privacy: on-device progress only (say so in the policy).

---

## 3. iOS package (Mac only)

```bash
cd NeuroForge
briefcase create iOS
briefcase build iOS
briefcase run iOS              # Simulator
briefcase package iOS          # for device / archive workflow
```

Then:

1. Open the Xcode project Briefcase generated under `build/neuroforge/ios/`  
2. Set **Team**, signing, unique Bundle ID  
3. **Product → Archive** → Distribute → App Store Connect  
4. TestFlight → App Review  

Icons: Briefcase uses `assets/icon` (provide `assets/icon.png` 1024×1024 — already in repo as `assets/icon_1024.png`; copy/rename if needed):

```bash
cp assets/icon_1024.png assets/icon.png
```

---

## 4. Scripts in this repo

| Script | Purpose |
|--------|---------|
| `scripts/package_android.ps1` | Create/build/package Android on Windows |
| `scripts/package_ios.sh` | Create/build/package iOS on Mac |
| `scripts/make_release_zip.ps1` | Zip source for handoff / CI |

---

## 5. Mobile app entry

| Entry | UI | Use |
|-------|----|-----|
| `python main.py` | tkinter | Desktop (full 27 modes) |
| `neuroforge.mobile_app` | Toga | Briefcase iOS/Android (simplified controls for most modes) |

Complex multi-step desktop UIs (full MOT animation, Corsi flash sequences, etc.) are simplified on mobile v1; **all scoring engines are shared**.

---

## 6. Store listing checklist

- [ ] Unique app id (`com.yourname.neuroforge`)  
- [ ] Privacy policy URL (on-device data)  
- [ ] Support URL / email  
- [ ] Screenshots (6.7" + 6.1" iPhone; phone + 7" Android)  
- [ ] Age rating 4+ / Everyone  
- [ ] **No medical claims** (“brain training entertainment”, not “treats ADHD/Alzheimer’s”)  
- [ ] In-app disclaimer (already in app)  

---

## 7. How much to charge on iOS (recommended)

Market context (Elevate / Lumosity / Peak style apps):

| Product | Typical pricing |
|---------|-----------------|
| Elevate | ~**$9.99/mo** or **$39.99/yr** (+ free tier / trial) |
| Lumosity | ~**$12/mo** or **$60/yr** (+ free daily limit) |
| Category freemium | Often **$10–20/mo** or **$40–100/yr** |

### Recommended pricing for NeuroForge (indie launch)

**Best default: Freemium + annual focus**

| Tier | Price (USD) | What they get |
|------|-------------|----------------|
| **Free** | $0 | Daily Circuit + **5 modes**, basic progress, ads optional |
| **Pro monthly** | **$4.99 / month** | All 27 modes, full adaptive levels, no ads |
| **Pro yearly** | **$29.99 / year** | Same as Pro (~$2.50/mo) — main revenue target |
| **Lifetime unlock** (optional) | **$49.99 once** | All Pro features forever |

**Trial:** 7-day free Pro trial on yearly plan (App Store subscription).

### Why this band

1. **Undercuts** Elevate (~$40/yr) and Lumosity (~$60/yr) while looking premium.  
2. **$4.99/mo** is a familiar “cheap subscription” impulse price.  
3. **Yearly at $29.99** is the plan you promote in-app (higher LTV).  
4. New apps with limited brand should **not** open at $60/yr.  

### Alternative if you want simpler billing

| Model | Price | When |
|-------|-------|------|
| Paid upfront only | **$3.99 – $5.99** one-time | No server, no free tier complexity |
| Paid upfront | **$9.99** | If you add iCloud sync / more polish later |

For a first release with 27 modes and adaptive engine, **freemium + $29.99/year** is the strongest App Store fit.

### Revenue note

Apple takes **15%** (Small Business Program) or **30%** of subscriptions. Price so that **you** keep enough after the cut.

---

## 8. Android pricing

Use the **same USD price points** ($4.99 / $29.99).  
Google Play billing is separate but users expect parity with iOS.

---

## 9. What “packaged files” means here

This repository is the **source package** ready for Briefcase:

```
NeuroForge/
  pyproject.toml          ← Briefcase iOS + Android
  neuroforge/mobile_app.py ← Toga entry
  neuroforge/logic/        ← shared engines
  assets/icon*.png
  requirements-mobile.txt
  MOBILE_PACKAGING.md      ← this file
  scripts/
```

**Signed store binaries (.ipa / .aab) are produced on your machine** with the commands above—not checked into git (they include secrets/signing).

---

## 10. Next engineering steps (optional polish)

1. Flesh out remaining multi-step modes on Toga (memory flash, MOT, opspan).  
2. StoreKit 2 / Play Billing for Pro.  
3. Replace Bundle ID with your org.  
4. Host privacy policy.  
5. TestFlight + Play internal track.
