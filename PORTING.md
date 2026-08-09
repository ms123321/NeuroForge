# Porting NeuroForge to iOS (Toga / SwiftUI)

## Architecture

```
neuroforge/
  logic/          ← PURE Python (no tkinter). Port this first.
    scoring.py
    focus.py
    memory.py
    switch.py
    speed.py
    nback.py
    dual.py
    rotate.py
    stroop.py
  modes/          ← Desktop UI adapters (tkinter)
  feedback.py     ← Desktop sound/haptics; replace with AVAudio + UIImpactFeedback
  app.py          ← Desktop shell; replace with Toga App or SwiftUI App
  progress.py     ← Shared persistence (JSON) — works on mobile with path change
```

## Contract for each engine

Every engine in `logic/` follows the same shape:

```python
engine = FocusEngine(level=3)
trial = engine.next_trial()      # generate stimulus data
event = engine.respond(...)      # or choose / answer / tap
engine.advance()
if engine.done():
    score = engine.state.score
```

UI only:

1. Renders `trial` fields  
2. Collects user input  
3. Calls engine method  
4. Shows `event["message"]` / `event["good"]`  
5. Plays sound/haptic  

## Toga sketch

```python
# pseudo — keep engines identical
from neuroforge.logic import FocusEngine

class FocusScreen(toga.Box):
    def start(self, level):
        self.engine = FocusEngine(level)
        self.show_trial(self.engine.next_trial())

    def on_tap(self, widget):
        event = self.engine.respond(tapped=True)
        self.feedback(event)
        self.engine.advance()
        ...
```

## Haptics on iOS

| Desktop (`feedback.py`) | iOS |
|-------------------------|-----|
| `play_correct` WAV | short high `SystemSound` / custom audio |
| `play_wrong` WAV | low error tone |
| `haptic_flash` top bar | `UIImpactFeedbackGenerator` (light/medium/heavy) |
| countdown tick | light impact each second |

## Progress path on iOS

Replace `_data_dir()` in `progress.py` with app sandbox Documents, e.g.:

```python
# Toga / Briefcase
path = Path(toga.App.app.paths.data) / "progress.json"
```

## Test pure logic without UI

```bash
python -c "from neuroforge.logic import *; e=DualNBackEngine(3); print(e.next_trial())"
```

See also `APP_STORE.md` for packaging and review guidelines.
