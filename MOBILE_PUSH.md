# NeuroForge push — iPhone & Android first

Notifications are designed for **phone push**, not Windows toast.

| Platform | System | How NeuroForge uses it |
|----------|--------|-------------------------|
| **iPhone / iPad** | **APNs** (native) or **Home Screen Web Push** (PWA) | Local scheduled reminders + optional remote |
| **Android** | **FCM** (native) or **Chrome notifications** (PWA) | Local alarms + optional remote |
| **Web / PWA** | **Notification API + Service Worker** | Settings UI + test + session events |
| Desktop Windows | Toast / Task Scheduler | Dev fallback only (`platform=desktop`) |

---

## In the app (web / PWA)

1. Open **Settings**
2. Tap **Enable phone push** (allow OS permission)
3. Toggle reminder types, morning/evening times, days, quiet hours
4. **Save & apply schedule**
5. **Send test notification**

### iPhone tips
- Safari → **Share → Add to Home Screen**
- Open NeuroForge from the **home screen icon** (standalone mode)
- Then enable push — iOS is strict about web push unless installed

### Android tips
- Chrome → **Install app** / Allow notifications
- Enable phone push in Settings

Service worker: `/sw.js`  
Client: `/static/push.js`  
Prefs API: `/api/notifications`

---

## API (same for native shells)

### Get prefs + schedule plan
```http
GET /api/notifications
```
Returns `prefs`, `schedule` (for `UNCalendarNotificationTrigger` / `AlarmManager`), and registered devices.

### Save prefs
```http
POST /api/notifications
Content-Type: application/json

{
  "enabled": true,
  "daily_reminder": true,
  "daily_hour": 9,
  "daily_minute": 0,
  "evening_reminder": false,
  "evening_hour": 18,
  "evening_minute": 0,
  "streak_alerts": true,
  "session_complete": true,
  "level_up": true,
  "weekly_summary": true,
  "motivational": false,
  "quiet_hours": false,
  "quiet_start_hour": 22,
  "quiet_end_hour": 7,
  "sound": true,
  "days": {"mon": true, "tue": true, "wed": true, "thu": true, "fri": true, "sat": true, "sun": true},
  "platform": "ios"
}
```

### Register device token (APNs / FCM / web)
```http
POST /api/notifications/register
{
  "token": "<apns_or_fcm_token>",
  "platform": "ios",
  "label": "iPhone 15"
}
```

### Test / event payloads
```http
POST /api/notifications/test
POST /api/notifications/event
{"kind": "session", "fmt": {"score": 120, "acc": "88"}}
```
Kinds: `daily`, `evening`, `streak`, `session`, `level`, `weekly`, `test`

### Native schedule only
```http
GET /api/notifications/schedule
```

Python helpers (shared with desktop prefs file):

```python
from neuroforge.mobile_push import register_token, schedule_plan, deliver, build_event_payload
from neuroforge.notifications import NotificationPrefs

register_token(token, "ios")          # or "android" / "web"
plan = schedule_plan()                # local notification plan
payload = build_event_payload("daily")
deliver(payload)
```

---

## iOS App Store (native / BeeWare / Despia)

1. Xcode → **Signing & Capabilities → Push Notifications**
2. Apple Developer → **Keys → APNs** (`.p8`)
3. On launch:
   - Request `UNUserNotificationCenter` authorization  
   - Register for remote notifications → get device token  
   - `POST /api/notifications/register` with `platform: "ios"`
4. **Local daily/evening** (recommended first — no server):
   - Read `GET /api/notifications/schedule`
   - Create `UNCalendarNotificationTrigger` for hour/minute + weekday mask
5. **Remote** (optional): send via APNs HTTP/2 from your server using the stored token

Android notification channel id used in payloads: `neuroforge_training`

---

## Android Play Store (native / BeeWare / Despia)

1. Firebase project → Cloud Messaging → `google-services.json`
2. Android 13+: request `POST_NOTIFICATIONS`
3. Get FCM token → `POST /api/notifications/register` with `platform: "android"`
4. Local: `AlarmManager` / WorkManager from the same schedule JSON
5. Remote: FCM HTTP v1; inject sender:

```python
from neuroforge.mobile_push import set_remote_sender

def send_fcm(payload, devices):
    # call Google FCM HTTP v1 with service account
    n = 0
    for d in devices:
        if d.platform != "android":
            continue
        # post payload.fcm_message(d.token)
        n += 1
    return n

set_remote_sender(send_fcm)
```

---

## Recommended product setup

| Notification | Best implementation |
|--------------|---------------------|
| Morning / evening training | **Local** on device (works offline, no server cost) |
| Session complete / level-up | Local when app is open; remote optional |
| Streak risk | Local on app open + optional remote morning |
| Marketing | Remote only + privacy policy |

---

## Privacy (App Store / Play)

- Declare push notifications in questionnaires  
- Privacy policy if tokens hit your backend  
- Always keep an in-app **master OFF** (`enabled: false`)  
- Quiet hours + weekday filters are stored in prefs

---

## Files

| File | Role |
|------|------|
| `neuroforge/mobile_push.py` | Mobile-first payloads, schedule, delivery |
| `neuroforge/push_devices.py` | Device token registry |
| `neuroforge/notifications.py` | Shared prefs + optional desktop fallback |
| `webapp/static/push.js` | Phone/PWA client |
| `webapp/static/sw.js` | Service worker (push + local show) |
| `webapp/app.py` | `/api/notifications*` routes |

Windows toast remains only when `platform` is desktop and no mobile token is registered.
