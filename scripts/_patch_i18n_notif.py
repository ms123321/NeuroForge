from pathlib import Path

p = Path(__file__).resolve().parents[1] / "neuroforge" / "i18n.py"
text = p.read_text(encoding="utf-8")
if "notif.evening" in text:
    print("already patched")
    raise SystemExit(0)

block = r'''
    "notif.evening": {"en": "Evening reminder"},
    "notif.session": {"en": "Session complete alerts"},
    "notif.levelup": {"en": "Level-up celebrations"},
    "notif.weekly": {"en": "Weekly progress summary"},
    "notif.motivational": {"en": "Motivational tips"},
    "notif.quiet": {"en": "Quiet hours"},
    "notif.sound": {"en": "Notification sound"},
    "notif.time_morning": {"en": "Morning time"},
    "notif.time_evening": {"en": "Evening time"},
    "notif.days": {"en": "Reminder days"},
    "notif.apply": {"en": "Apply schedule"},
    "notif.session_title": {"en": "Session complete!"},
    "notif.session_body": {"en": "Score {score} · {acc}% accuracy. Great work!"},
    "notif.level_title": {"en": "Level up!"},
    "notif.level_body": {"en": "You reached level {level}. Keep building those circuits!"},
    "notif.weekly_title": {"en": "Your week in NeuroForge"},
    "notif.weekly_body": {"en": "{sessions} sessions · streak {streak}. Ready for another week?"},
    "notif.evening_title": {"en": "Evening brain check-in"},
    "notif.evening_body": {"en": "A short evening drill can seal today's progress."},
    "notif.quiet_range": {"en": "Quiet from {start}:00 to {end}:00"},
'''
text = text.replace('    "session.complete":', block + '    "session.complete":')
p.write_text(text, encoding="utf-8")
print("patched")
