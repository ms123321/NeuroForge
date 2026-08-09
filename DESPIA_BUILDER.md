# Your Despia builder — do this now

**Builder:** https://v3.despia.com/builder/3fb85979-0977-422c-9a3b-7de2dd70fef3  

**GitHub (web source):** https://github.com/ms123321/NeuroForge  

I cannot log into Despia for you (it asks for your email OTP / Google).  
Below is the exact checklist to finish **everything** in that builder.

---

## A. Confirm the Web URL (you already pasted HTTPS)

1. Open the **same HTTPS URL** in your **phone browser**.  
2. You must see NeuroForge home and be able to play.  
3. If it fails → fix hosting first (Railway/Render must be awake).

In Despia builder:

| Field | Value |
|-------|--------|
| **Web / Dynamic source URL** | Your `https://…` (already set) |
| Deployment model | **Remote hydration** (default) — OTA updates when you change the website |

---

## B. App identity (fill these)

| Field | Recommended value |
|-------|-------------------|
| **App name** | `NeuroForge` |
| **Subtitle** | `Rewire. Adapt. Grow.` |
| **Bundle ID (iOS)** | `com.ms123321.neuroforge` *(or your company domain)* |
| **Package name (Android)** | `com.ms123321.neuroforge` |
| **Category** | Games → Puzzle **or** Education |
| **Age** | 4+ |

Use **one** bundle/package ID everywhere (Despia + App Store Connect + Play Console).

---

## C. Icon (required — 1024×1024 PNG, **no transparency**)

File on your PC:

```
C:\Users\gssei\NeuroForge\assets\icon_1024.png
```

1. Despia → **Icon / iOS icon**  
2. Upload `icon_1024.png`  
3. Must be **exactly 1024×1024**, PNG, **solid background** (no alpha)

If Apple rejects alpha: open in Paint → Save as PNG with solid `#0B1020` background.

---

## D. Splash screen (1024×1024 GIF or PNG as Despia requires)

1. Despia → **Splash**  
2. Use same icon on dark background `#0B1020`  
3. Export GIF/PNG 1024×1024 and upload  

---

## E. Native integrations (turn these ON)

### 1) Push (iPhone + Android)

In Despia **Settings → Integrations**:

1. Enable **OneSignal** (Despia’s push path)  
2. Create free [OneSignal](https://onesignal.com) app → iOS + Android  
3. Paste OneSignal App ID / keys into Despia  
4. Enable **Push Notifications** capability for the project  

In the live app: **Settings → Enable phone push**  
(NeuroForge already calls `setonesignalplayerid://` when running in Despia.)

### 2) In‑app purchases / Pro (optional but for real money)

1. Enable **RevenueCat** in Despia Integrations  
2. Create [RevenueCat](https://www.revenuecat.com) project  
3. Products:  
   - Monthly `neuroforge_pro_monthly` → $4.99  
   - Yearly `neuroforge_pro_yearly` → $29.99  
   - Lifetime `neuroforge_pro_lifetime` → $49.99  
4. Entitlement id: **`pro`** or **`premium`**  
5. Offering id: **`default`**  
6. Link App Store Connect + Play Console products  

NeuroForge **Go Pro** buttons call:

```text
revenuecat://launchPaywall?external_id=…&offering=default
```

when the user agent is Despia.

---

## F. Privacy / store text (prepare URLs)

Host these (GitHub Pages, Notion public, or your domain):

**Privacy (short):**

- Progress / scores stored to run the app  
- Optional push device tokens (OneSignal / APNs / FCM)  
- Purchases handled by Apple/Google via RevenueCat  
- Not a medical device; entertainment / personal training  
- Contact: your email  

**Support URL:** same site or mailto  

**App description (safe language):**

> NeuroForge is adaptive brain training with research-inspired drills for attention, memory, and flexibility. Short sessions. Adaptive difficulty. Not a medical device.

**Do not say:** treats ADHD, cures dementia, clinical therapy.

---

## G. Build & test

1. Despia → **Publish / Build**  
   - iOS and/or Android  
   - Wait 15–30 minutes  
2. **iOS:** build → App Store Connect → **TestFlight**  
3. **Android:** internal testing track  
4. Install on phone and verify:

- [ ] Home loads full screen  
- [ ] Daily Circuit plays  
- [ ] Haptics on correct/wrong (Despia)  
- [ ] Settings → Enable push  
- [ ] Go Pro opens paywall (if RevenueCat set)  

---

## H. Store submit

### Apple (needs $99 Developer)

1. [appstoreconnect.apple.com](https://appstoreconnect.apple.com) → New App  
2. Bundle ID = same as Despia  
3. Screenshots (phone), description, privacy, age rating  
4. Select Despia/TestFlight build → **Submit for Review**

### Google (needs $25 Play Console)

1. Create app with same package name  
2. Upload AAB from Despia  
3. Content rating, privacy, screenshots  
4. Internal test → Production  

---

## I. After launch (OTA)

Change the **website** (GitHub → host redeploy) → force-close the phone app → reopen.  
**No new Despia build** needed for UI/game fixes.  

Rebuild only if you change: icon, splash, bundle id, push certs, native capabilities.

---

## What NeuroForge already does for Despia

Code in repo (`webapp/static/despia.js`):

| Feature | Behavior inside Despia |
|---------|-------------------------|
| Full-screen safe areas | `--safe-area-top/bottom` + full bleed |
| Haptics | success / error on answers |
| Device UUID | `get-uuid://` → push register |
| OneSignal | `setonesignalplayerid://` |
| Pro paywall | RevenueCat launch on Go Pro |
| Entitlements | `getpurchasehistory://` → unlock Pro |

---

## If the builder looks empty / stuck

1. Hard refresh Despia tab  
2. Log out / log in  
3. Confirm Web URL still HTTPS and loads in a normal browser  
4. Email Despia support: **hey@despia.com** with project id:  
   `3fb85979-0977-422c-9a3b-7de2dd70fef3`

---

## Minimum path (fastest)

1. Icon 1024 upload  
2. Splash upload  
3. Bundle ID set  
4. **Build**  
5. Install TestFlight / Android test  
6. Play Daily Circuit  

Do Apple/Google paid accounts only when you want public store listing.
