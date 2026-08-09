# NeuroForge

**Adaptive brain-training for neuroplasticity** — Python desktop game with pure logic ready for an Apple App Store port.

## Run

```powershell
cd C:\Users\gssei\NeuroForge
.\run.ps1
```

Or:

```powershell
& "$env:LOCALAPPDATA\Python\bin\python.exe" main.py
```

**Dependencies:** Python 3.10+ stdlib only (`tkinter`, `wave`, `winsound` on Windows).

## What's new in 1.1

1. **Sound + haptic-style feedback** — tones on correct/wrong/countdown; top-bar flash stand-in for phone vibration; toggle on home  
2. **UI-free logic layer** — `neuroforge/logic/` for Toga / SwiftUI port (see `PORTING.md`)  
3. **App Store icons** — `assets/icon.png` (1024×1024) + size variants  
4. **3 new modes** — Dual Stream, Mind Rotate, Color Clash (8 total)

## Training modes

| Mode | Domain | Paradigm |
|------|--------|----------|
| **Focus Pulse** | Attention & inhibition | Go / No-Go |
| **Memory Lattice** | Working memory | Sequence recall |
| **Switch Path** | Cognitive flexibility | Rule switching |
| **Speed Mirror** | Processing speed | Speeded match |
| **N-Back Lite** | Working memory | N-back |
| **Dual Stream** | Dual WM | Dual n-back (letter + position) |
| **Mind Rotate** | Visuospatial | Mental rotation |
| **Color Clash** | Executive control | Stroop conflict |

### Circuits

- **Daily Circuit** — 5 core modes  
- **Full Gym** — all 8 modes  

## Project layout

```
NeuroForge/
├── main.py
├── neuroforge/
│   ├── app.py              # menus / navigation
│   ├── feedback.py         # sound + haptic flash
│   ├── progress.py         # stats, streaks, adaptive levels
│   ├── logic/              # PURE engines (no UI) ← port this
│   └── modes/              # tkinter adapters
├── assets/
│   ├── icon.png            # 1024 App Store icon
│   └── sounds/             # auto-generated WAVs
├── tests/test_logic.py
├── PORTING.md              # Toga / SwiftUI guide
├── APP_STORE.md            # submission checklist
└── README.md
```

## Tests

```powershell
python tests/test_logic.py
```

## Web app (browser)

```powershell
cd C:\Users\gssei\NeuroForge
python -m pip install -r requirements-web.txt
python -m webapp.app
```

Open **http://127.0.0.1:8080** — full guide: **[WEB_DEPLOY.md](WEB_DEPLOY.md)**  
(Railway / Render / Despia wrap, etc.)

## iOS & Android packaging

Desktop = tkinter (`python main.py`).  
Mobile = BeeWare **Toga** shell + **Briefcase** (`neuroforge.mobile_app`).

| Platform | Command / guide |
|----------|------------------|
| **Android** | `.\scripts\package_android.ps1` → Play AAB |
| **iOS** | On a **Mac**: `bash scripts/package_ios.sh` → Xcode → App Store |
| Full guide | **[MOBILE_PACKAGING.md](MOBILE_PACKAGING.md)** |
| Pricing | See same doc — recommend **$4.99/mo** or **$29.99/yr** freemium |

Also: **[APP_STORE.md](APP_STORE.md)** · **[PORTING.md](PORTING.md)** · **[RESEARCH.md](RESEARCH.md)**

> Not a medical device. Entertainment & personal training only.

## License

MIT
