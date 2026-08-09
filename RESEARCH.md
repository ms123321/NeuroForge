# Research basis (NIH / neurology–aligned paradigms)

NeuroForge is **not a medical device**. Modes are **inspired by** cognitive tasks used in research and clinical neuropsychology. Citations are for scientific context only.

## Adaptive difficulty engine

Implements progressive challenge consistent with the **mismatch model of cognitive plasticity**: demand is kept near the upper edge of ability so resources expand under load. Adaptive dual n-back protocols (accuracy-gated n increases) are a common reference in NIH-funded working-memory training work.

| Mechanism | Behavior |
|-----------|----------|
| Between-session level (1–10) | Multi-axis profile: speed, set size, conflict, dual load, n-depth |
| Within-session pressure | Rolling accuracy tightens/eases deadlines & conflict |
| Promote / demote | ~82%+ accuracy → level up; ~52%− → level down |

Code: `neuroforge/logic/engine.py` (`AdaptiveEngine`, `DifficultyProfile`).

## Paradigm map

| Mode | Research lineage (illustrative) |
|------|----------------------------------|
| N-Back / Dual Stream | Working-memory updating; dual n-back training literature (e.g. Jaeggi et al.; PMC reviews) |
| Op Span | Complex span (Turner & Engle) — storage + processing |
| Digit Reverse / Block Span | Digit span, Corsi — WAIS / neuropsych batteries |
| Change Detect | Visual WM capacity (Luck & Vogel) |
| Focus / Stop / SART | Go/no-go, stop-signal (Logan), SART (Robertson et al.) |
| Flanker / Simon / Stroop | Conflict monitoring (Eriksen; Simon; Stroop 1935) |
| Posner Cue | Spatial attention orienting (Posner 1980) |
| Trail / Number Path | Trail Making Test (TMT) — sequencing / flexibility |
| PASAT / Add Stream | Paced Auditory Serial Addition (Gronwall) — attention under load |
| Symbol Code | SDMT — processing speed in MS/TBI neurology batteries |
| Dual Load | Cognitive dual-task training (neurology/rehab dual-task literature) |
| Rule Hunt | WCST-inspired executive set shifting |
| Flash Stream (RSVP) | Rapid serial visual presentation / attentional selection |
| Object Track | Multiple-object tracking (Pylyshyn & Storm) |
| Mind Rotate | Mental rotation (Shepard & Metzler) |
| Anti Saccade | Antisaccade / inhibitory control (Hallett; Munoz & Everling) |
| Running Span | Running memory span (Broadway & Engle) |
| Tower Plan | Tower of London–style planning (Shallice) |
| Feature Hunt | Conjunction visual search (Treisman & Gelade) |
| Pattern Matrix | Raven-like abstract reasoning / fluid IQ tasks |
| Reverse Blocks | Backward Corsi spatial span |
| Serial Sevens | MMSE-style mental control / serial subtraction |
| Cancel Marks | Letter/symbol cancellation (attention, neglect screening) |
| Oddball | Rare-target / P300-style clinical attention |
| Choice RT | Simple/choice reaction time (psychomotor speed) |
| Word List | RAVLT/CVLT-inspired verbal free recall |
| Trigram Hold | Brown–Peterson distractor delay (STM) |


## Example open literature

- Dual n-back WM training in healthy adults — *PLOS ONE* / PMC (e.g. Lawlor-Savage & Goghari).
- Dual-task training and cognition after stroke — *Frontiers in Neurology* meta-analyses.
- N-back as WM measure/training vehicle — recent PMC reviews.
- SDMT as processing-speed marker in MS — neurology clinical literature.

## Disclaimer

Training transfer to real-world outcomes is **task-specific and debated**. Market and document NeuroForge as **brain-training entertainment / personal practice**, not treatment for disease.
