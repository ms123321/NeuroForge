# Getting NeuroForge onto the Apple App Store

This document is the honest engineering path from this Python project to a listing on the App Store.

## Reality check

| Fact | Implication |
|------|-------------|
| App Store apps must be signed iOS/iPadOS binaries | You need a **Mac**, **Xcode**, and an **Apple Developer Program** membership ($99/year) |
| **tkinter is not available on iOS** | The desktop UI cannot be packaged “as-is” for iPhone |
| Apple reviews health-related claims carefully | Market as **brain training / entertainment**, not therapy or medical treatment |
| Python *can* ship via BeeWare or Kivy | UI must use a mobile-capable toolkit (Toga, Kivy, or native SwiftUI) |

NeuroForge is structured so **game logic and progress** are separate from **presentation**, which makes a port feasible.

---

## Option A — BeeWare (Python → iOS) [recommended for staying in Python]

### Prerequisites

- Mac with recent macOS  
- Xcode (from App Store) + Command Line Tools  
- [Apple Developer Program](https://developer.apple.com/programs/) enrollment  
- Python 3.10–3.12 on the Mac (Briefcase-supported versions)

### Steps

1. **Create a Toga UI shell** that reuses:
   - `neuroforge/progress.py` (stats, adaptive levels)
   - Pure logic extracted from each mode (sequences, n-back rules, scoring)

2. **Install Briefcase** on the Mac:

   ```bash
   python -m pip install briefcase
   cd NeuroForge
   briefcase new   # or configure existing pyproject.toml
   briefcase create iOS
   briefcase build iOS
   briefcase run iOS
   ```

3. **Open the generated Xcode project**, set:
   - Bundle ID: `com.yourorg.neuroforge` (must be unique)
   - Team / signing certificates
   - Privacy strings if you later add mic/camera (this app needs none)
   - App icons & launch screen (`assets/`)

4. **Archive** in Xcode → upload to **App Store Connect** → **TestFlight** → submit for review.

### What to reimplement in Toga

| Desktop (tkinter) | iOS (Toga) |
|-------------------|------------|
| `RoundedButton` / Canvas | `toga.Button`, `toga.Box`, optional canvas |
| Mode screens | `toga.App` + window content swaps |
| `simpledialog` rename | `toga.TextInput` dialog |
| Local JSON file | Same `progress.py` (app sandbox path) |

Keep scoring, adaptive level math, and session recording identical so desktop and mobile stay comparable.

---

## Option B — Kivy + kivy-ios

Strong choice if you want richer animation:

1. Rewrite screens with Kivy `ScreenManager`  
2. On a Mac: install [kivy-ios](https://kivy.org/doc/stable/guide/packaging-ios.html)  
3. Build Xcode project → sign → TestFlight  

Same App Store Connect process as Option A.

---

## Option C — SwiftUI rewrite (best App Store polish)

1. Create a new Xcode iOS app (`NeuroForge`)  
2. Port each mode’s rules from `neuroforge/modes/*.py`  
3. Store progress with `UserDefaults` or JSON in Documents  
4. Submit via standard Xcode workflow  

This is more work but matches how most top brain-training apps ship.

---

## App Store Connect checklist

### Metadata

- **Name:** NeuroForge (or check availability)  
- **Subtitle:** Adaptive brain training  
- **Category:** Games → Education / Puzzle, or Education  
- **Age rating:** 4+ (no violence, no user-generated content)  
- **Keywords:** brain training, memory, focus, n-back, cognitive  

### Copy guidelines (important)

**Do say**

- “Brain training drills for attention, memory, and flexibility”  
- “Adaptive difficulty based on your performance”  
- “Inspired by cognitive paradigms used in research”

**Do not say** (without clinical evidence & regulatory path)

- “Treats ADHD / Alzheimer’s / depression”  
- “Clinically proven to raise IQ”  
- “Medical device” / “therapy” / “cures”

Apple and FTC have scrutinized overstated brain-training claims. Keep language educational and entertainment-focused. Include a short disclaimer in-app (already on the Progress screen).

### Privacy

- No account → no privacy nutrition labels for tracking  
- If progress is **only on-device**, say so in the privacy policy  
- Host a simple privacy policy URL (required by App Store Connect)

### Assets

- App icon 1024×1024  
- 6.7" and 6.1" iPhone screenshots (and iPad if you support it)  
- Optional preview video  

---

## Suggested milestone plan

| Phase | Deliverable | Where |
|-------|-------------|--------|
| 1 | Desktop game playable | **Done — this repo** |
| 2 | Extract pure logic modules (no tkinter imports in rules) | 1–2 days |
| 3 | Toga or SwiftUI UI parity | 1–2 weeks |
| 4 | TestFlight beta | Mac + Developer account |
| 5 | App Review submission | App Store Connect |

---

## Windows note

You can develop and play the full game on Windows right now. **Building the iOS binary must happen on a Mac** (Apple requirement). Cloud Mac services (MacStadium, AWS EC2 Mac, GitHub macOS runners for CI) can help if you do not own a Mac.

---

## Support contacts (fill before submit)

- Support URL  
- Marketing URL  
- Privacy policy URL  
- Contact email for App Review notes

---

## Pricing (iOS recommendation)

See **[MOBILE_PACKAGING.md](MOBILE_PACKAGING.md)** for full market notes.

**Recommended for NeuroForge launch**

| Tier | USD |
|------|-----|
| Free | Daily circuit + limited modes |
| Pro monthly | **$4.99** |
| Pro yearly (promote this) | **$29.99** |
| Optional lifetime | **$49.99** |

Comparables: Elevate ~$40/yr, Lumosity ~$60/yr. Undercut with $29.99/yr + 7-day trial.

**Do not** market as medical treatment — entertainment / personal brain training only.
