# How to save NeuroForge (session, progress, project)

## 1. Game progress (scores, levels, streaks) — automatic

The game **already auto-saves** when you finish a mode.

| What | Where on your PC |
|------|------------------|
| Progress | `%LOCALAPPDATA%\NeuroForge\progress.json` |
| Free/Pro plan | `%LOCALAPPDATA%\NeuroForge\entitlement.json` |

Full path example:

```
C:\Users\gssei\AppData\Local\NeuroForge\
```

You do **not** need to click Save after playing.

---

## 2. Source code (all game files) — already on disk

Everything we built is here:

```
C:\Users\gssei\NeuroForge\
```

Closing this chat does **not** delete the project.

---

## 3. Full backup (recommended)

Double-click or run:

```powershell
cd C:\Users\gssei\NeuroForge
.\scripts\backup_everything.ps1
```

Creates:

```
C:\Users\gssei\NeuroForge\backups\NeuroForge_backup_YYYYMMDD_HHMM.zip
```

That zip includes:

- Full game code  
- Your progress  
- Your Free/Pro entitlement  

Copy the zip to OneDrive, USB, or another PC.

### Restore progress later

1. Unzip the backup  
2. Copy files from `PlayerData\` into:

```
C:\Users\gssei\AppData\Local\NeuroForge\
```

---

## 4. This chat / AI session

- The **Grok Build chat** is separate from the game files.  
- To keep a record of the conversation: use your product’s export/share if available, or copy important notes into a text file in the project (e.g. `NOTES.md`).  
- The **important work is already saved** as files under `NeuroForge\`.

---

## 5. Optional: Git (for developers)

```powershell
cd C:\Users\gssei\NeuroForge
git init
git add .
git commit -m "NeuroForge brain training game"
```

Then push to GitHub if you want cloud source control.
