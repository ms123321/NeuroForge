# Step-by-step: Get NeuroForge on the Apple App Store

This is a practical checklist from this codebase to a live App Store listing.

---

## Phase 0 — What you have now

| Piece | Status |
|-------|--------|
| Desktop game (Windows) | ✅ `python main.py` — 33 research modes |
| Adaptive difficulty engine | ✅ |
| Free + ads / Subscribe / Lifetime | ✅ (desktop simulated IAP) |
| Toga mobile shell | ✅ `neuroforge/mobile_app.py` |
| Briefcase iOS/Android config | ✅ `pyproject.toml` |
| Icons | ✅ `assets/icon_1024.png` |

**Reality:** Apple only accepts apps built and signed on a **Mac** with **Xcode**.  
Windows can develop and test desktop; **shipping iOS requires a Mac** (or a cloud Mac).

---

## Phase 1 — Accounts & money (do these first)

### 1.1 Apple Developer Program

1. Go to [developer.apple.com/programs](https://developer.apple.com/programs/)  
2. Enroll with your Apple ID  
3. Pay **US $99 / year**  
4. Wait for approval (often same day–48 hours)

### 1.2 App Store Connect

1. Open [appstoreconnect.apple.com](https://appstoreconnect.apple.com)  
2. Accept agreements (Paid Apps, if selling IAP)  
3. Banking + tax forms (required before paid apps/IAP go live)

### 1.3 Optional: Google Play (Android later)

- [play.google.com/console](https://play.google.com/console) — **$25 one-time**

---

## Phase 2 — Legal & store content (do before coding IAP)

### 2.1 Privacy policy (required)

Host a simple page (GitHub Pages, Notion public, your site) that says:

- Progress is stored **on device**  
- Free tier may show **ads** (AdMob)  
- Subscriptions billed by Apple  
- Contact email  
- No sale of health data  

Example URL: `https://yoursite.com/neuroforge/privacy`

### 2.2 Support URL + email

Apple asks for a support URL and contact email for review.

### 2.3 App identity

| Field | Example | Notes |
|-------|---------|--------|
| Name | NeuroForge | Check availability in Connect |
| Bundle ID | `com.yourname.neuroforge` | **Change** from `com.neuroforge.app` if taken |
| SKU | `neuroforge001` | Internal only |
| Category | Games → Education / Puzzle **or** Education | |
| Age | 4+ | No violence / UGC |

### 2.4 Marketing copy (safe language)

**Do say:** brain training, cognitive drills, adaptive difficulty, entertainment  

**Do not say:** treats ADHD, cures dementia, clinical therapy, medical device  

In-app disclaimer already exists — keep it.

---

## Phase 3 — Mac build environment

On a Mac:

```bash
# 1. Install Xcode from Mac App Store, open it once, accept license
xcode-select --install

# 2. Python 3.10–3.12 recommended for Briefcase
brew install python@3.12   # or use pyenv

# 3. Copy this project to the Mac
cd ~/Projects
# unzip NeuroForge-mobile-source-*.zip  OR  git clone …

cd NeuroForge
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-mobile.txt

# 4. Icon
cp assets/icon_1024.png assets/icon.png
```

Edit `pyproject.toml`:

```toml
bundle = "com.yourname.neuroforge"   # YOUR unique id
```

---

## Phase 4 — Build the iOS app with Briefcase

```bash
cd NeuroForge
source .venv/bin/activate

briefcase create iOS
briefcase build iOS
briefcase run iOS          # Simulator test
```

Or: `bash scripts/package_ios.sh`

### 4.1 Sign in Xcode

1. Open the project under `build/neuroforge/ios/` (Briefcase shows the path)  
2. Select the app target → **Signing & Capabilities**  
3. Team = your Developer team  
4. Bundle Identifier = your unique id  
5. Run on a **physical iPhone** at least once (device registered)

### 4.2 Archive for App Store

1. Xcode menu: **Product → Destination → Any iOS Device**  
2. **Product → Archive**  
3. Organizer → **Distribute App** → App Store Connect → Upload  

---

## Phase 5 — Create the app record in App Store Connect

1. App Store Connect → **My Apps → +**  
2. New App → iOS  
3. Name, language, Bundle ID, SKU  
4. Fill:

- Screenshots (required sizes: e.g. 6.7" and 6.1" iPhone)  
- Description, keywords, support URL, marketing URL  
- Privacy Policy URL  
- App icon 1024×1024 (no alpha)  
- Age rating questionnaire  
- Pricing: Free (with IAP) — see Phase 6  

---

## Phase 6 — Monetization in App Store Connect (IAP)

You already designed three products in code (`neuroforge/monetization.py`):

| Product ID | Type | Price (set in Connect) |
|------------|------|-------------------------|
| `com.neuroforge.app.pro.monthly` | Auto-renewable subscription | **$4.99** |
| `com.neuroforge.app.pro.yearly` | Auto-renewable subscription | **$29.99** |
| `com.neuroforge.app.lifetime` | Non-consumable | **$49.99** |

### Steps

1. Connect → your app → **Monetization → Subscriptions**  
2. Create a **Subscription Group** e.g. `NeuroForge Pro`  
3. Add monthly + yearly subscriptions with those product IDs  
4. Add **Non-Consumable** for lifetime  
5. Add localization (display name, description)  
6. Submit IAPs for review **with** the app (or follow Apple’s current IAP review flow)  
7. Sandbox testers: Users & Access → Sandbox → add test Apple IDs  

### Wire real StoreKit (engineering)

Desktop **simulates** purchases. For production iOS:

1. Use StoreKit 2 (Swift) or a Python/Toga bridge / RevenueCat / native plugin  
2. On successful purchase → call the same entitlement logic as `purchase_yearly()` etc.  
3. Free tier ads → **Google AdMob** (or AppLovin) interstitial + banner  
4. Product IDs in `monetization.py` must match Connect exactly  

### Free tier behavior (already in app)

- Limited mode list (`FREE_MODE_KEYS`)  
- Banner ad + interstitial every few sessions  
- Cap: **5 sessions/day**  
- Pro removes ads + unlocks all modes  

---

## Phase 7 — TestFlight

1. After upload processing finishes in Connect  
2. TestFlight → Internal testing → add yourself  
3. Install via TestFlight app on iPhone  
4. Test: free limits, ads (test ads), subscribe sandbox, lifetime sandbox, restore  

---

## Phase 8 — Submit for App Review

1. App Store Connect → prepare **Version 1.0**  
2. “What’s New” text  
3. Choose build from TestFlight  
4. Answer export compliance (usually encryption = HTTPS only → standard answers)  
5. Review notes:  

```
NeuroForge is a brain-training entertainment app (not a medical device).
Free tier includes ads (AdMob test/production).
IAP: monthly, yearly, lifetime Pro.
Demo: open app → Train a skill → Focus Pulse.
Sandbox IAP available for review.
```

6. **Submit for Review**  
7. Typical review: 24–48 hours (can vary)

---

## Phase 9 — After approval

1. App goes **Ready for Sale** (or you schedule release)  
2. Monitor crashes (Xcode Organizer / App Store Connect)  
3. Reply to reviews  
4. Plan updates: more modes, real StoreKit polish, AdMob mediation  

---

## Pricing recap (recommended)

| Plan | Price | Role |
|------|-------|------|
| Free + ads | $0 | Acquisition |
| Pro Monthly | **$4.99/mo** | Casual payers |
| Pro Yearly | **$29.99/yr** | Primary revenue (promote) |
| Lifetime | **$49.99 once** | Anti-subscription users |

Promote yearly in the paywall (best value). Undercuts Elevate (~$40/yr) and Lumosity (~$60/yr).

---

## Parallel: Android (optional same week)

```powershell
# On Windows with Android SDK:
.\scripts\package_android.ps1
```

Upload AAB to Play Console; create same three IAP products; AdMob for free tier.

---

## Timeline (realistic)

| Week | Milestone |
|------|-----------|
| 1 | Developer account, privacy page, Bundle ID, Mac env |
| 2 | Briefcase iOS build, device run, screenshots |
| 3 | StoreKit + AdMob integration, TestFlight |
| 4 | App Review + launch |

---

## Quick command cheat sheet

```bash
# Desktop (Windows) — full game + simulated paywall
python main.py

# iOS package (Mac)
briefcase create iOS && briefcase build iOS && briefcase package iOS

# Android package
briefcase create android && briefcase build android && briefcase package android
```

More detail: `MOBILE_PACKAGING.md` · research notes: `RESEARCH.md`

---

## Checklist before you click Submit

- [ ] Unique Bundle ID  
- [ ] Privacy policy URL live  
- [ ] Support URL / email  
- [ ] Screenshots all required sizes  
- [ ] 1024 icon  
- [ ] IAP products created & priced  
- [ ] No medical claims in copy  
- [ ] TestFlight build tested on real iPhone  
- [ ] Sandbox IAP works  
- [ ] Age rating completed  
- [ ] Banking/tax active for paid IAP  
