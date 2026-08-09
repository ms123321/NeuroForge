"""
NeuroForge Web App — Flask
Run locally:  python -m webapp.app
Deploy:       see WEB_DEPLOY.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, render_template, request, session

from neuroforge import __version__
from neuroforge.logic import ENGINES
# meta only — never import tkinter UI modes on the server
from neuroforge.modes.meta import MODE_META
from neuroforge import theme as T
from neuroforge.progress import Progress
from neuroforge.monetization import FREE_MODE_KEYS, Entitlement

from webapp.session_store import STORE
from webapp.trial_api import apply_answer, trial_to_json

from neuroforge.notifications import NotificationPrefs, DAY_CODES
from neuroforge import mobile_push
from neuroforge import push_devices

app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
    static_folder=str(Path(__file__).parent / "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "neuroforge-dev-change-me")

# Trust Railway / reverse-proxy headers (HTTPS, host)
try:
    from werkzeug.middleware.proxy_fix import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
except Exception:
    pass


@app.after_request
def _cors(resp):
    resp.headers["Cache-Control"] = "no-store"
    # Allow service worker scope
    if request.path.endswith("/sw.js"):
        resp.headers["Service-Worker-Allowed"] = "/"
        resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/health")
@app.get("/healthz")
@app.get("/api/healthz")
def healthz_alias():
    """Extra health paths some hosts probe by default."""
    return jsonify({"ok": True, "version": __version__, "port": os.environ.get("PORT", "8080")})


@app.get("/")
def index():
    return render_template("index.html", version=__version__)


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "version": __version__, "modes": len(MODE_META)})


@app.get("/api/modes")
def list_modes():
    ent = Entitlement.load()
    prog = Progress.load()
    modes = []
    for key, meta in MODE_META.items():
        st = prog.modes.get(key)
        modes.append(
            {
                "key": key,
                "title": meta["title"],
                "subtitle": meta["subtitle"],
                "blurb": meta["blurb"],
                "domain": meta["domain"],
                "color": T.MODE_COLORS.get(key, "#6C8CFF"),
                "locked": not ent.can_play_mode(key) if not ent.is_pro() else False,
                "free": key in FREE_MODE_KEYS,
                "level": st.level if st else 1,
            }
        )
    return jsonify(
        {
            "modes": modes,
            "pro": ent.is_pro(),
            "status": ent.status_line(),
            "free_keys": list(FREE_MODE_KEYS),
            "daily": ["focus", "memory", "switch", "speed", "nback"],
            "version": __version__,
        }
    )


@app.post("/api/pro/buy")
def pro_buy():
    body = request.get_json(force=True, silent=True) or {}
    plan = (body.get("plan") or "").lower()
    ent = Entitlement.load()
    if plan == "monthly":
        rec = ent.purchase_monthly()
    elif plan == "yearly":
        rec = ent.purchase_yearly()
    elif plan == "lifetime":
        rec = ent.purchase_lifetime()
    elif plan == "restore":
        msg = ent.restore_purchases()
        return jsonify({"ok": True, "message": msg, "status": ent.status_line(), "pro": ent.is_pro()})
    else:
        return jsonify({"error": "Unknown plan"}), 400
    return jsonify(
        {
            "ok": True,
            "message": f"Activated {plan}",
            "status": ent.status_line(),
            "pro": ent.is_pro(),
            "purchase": rec,
        }
    )


@app.post("/api/play/start")
def play_start():
    body = request.get_json(force=True, silent=True) or {}
    mode_key = body.get("mode")
    level = int(body.get("level") or 1)
    level = max(1, min(10, level))
    if mode_key not in ENGINES or mode_key not in MODE_META:
        return jsonify({"error": "Unknown mode"}), 400

    ent = Entitlement.load()
    ok, msg = ent.can_start_session()
    if not ok:
        return jsonify({"error": msg, "paywall": True}), 403
    if not ent.can_play_mode(mode_key):
        return jsonify({"error": "Pro mode — upgrade to unlock", "paywall": True}), 403

    # Use saved adaptive level when client doesn't override
    if not body.get("level"):
        level = Progress.load().level_for(mode_key)
    eng = ENGINES[mode_key](level)
    # slightly shorter web sessions for snappy play
    if hasattr(eng, "rounds") and eng.rounds > 14:
        eng.rounds = min(eng.rounds, 14)

    sess = STORE.create(mode_key, level, eng)
    trial = eng.next_trial()
    sess.last_trial = trial
    return jsonify(
        {
            "session_id": sess.id,
            "mode": mode_key,
            "title": MODE_META[mode_key]["title"],
            "level": level,
            "rounds": eng.rounds,
            "score": eng.state.score,
            "round": eng.state.round_i,
            "trial": trial_to_json(mode_key, trial),
        }
    )


@app.post("/api/play/answer")
def play_answer():
    body = request.get_json(force=True, silent=True) or {}
    sid = body.get("session_id")
    sess = STORE.get(sid or "")
    if not sess or sess.finished:
        return jsonify({"error": "Session expired"}), 404

    eng = sess.engine
    trial = sess.last_trial
    event = apply_answer(sess.mode_key, eng, trial, body)

    # dualtask commit
    if sess.mode_key == "dualtask" and not event.get("partial"):
        if body.get("phase") != "digit" and not getattr(trial, "probe_digit", False):
            eng.commit_trial()
        elif body.get("phase") == "digit":
            eng.commit_trial()

    partial = bool(event.get("partial") or event.get("continue"))
    if not partial and not event.get("warmup"):
        # advance only when trial fully resolved
        # for multi-step engines that return partial, don't advance
        pass

    if partial:
        return jsonify(
            {
                "session_id": sess.id,
                "event": event,
                "score": eng.state.score,
                "correct": eng.state.correct,
                "attempts": eng.state.attempts,
                "round": eng.state.round_i,
                "rounds": eng.rounds,
                "done": False,
                "partial": True,
            }
        )

    # Full trial complete
    if event.get("warmup") and sess.mode_key in ("pasat", "countkeep"):
        eng.advance()
    elif not event.get("warmup"):
        eng.advance()
    else:
        eng.advance()

    if eng.done():
        sess.finished = True
        prog = Progress.load()
        entry = prog.record_session(
            mode=sess.mode_key,
            score=eng.state.score,
            correct=eng.state.correct,
            attempts=max(1, eng.state.attempts),
            duration_sec=30.0,
            level=sess.level,
            max_streak=eng.state.max_streak,
        )
        Entitlement.load().record_free_session()
        return jsonify(
            {
                "session_id": sess.id,
                "event": event,
                "score": eng.state.score,
                "correct": eng.state.correct,
                "attempts": eng.state.attempts,
                "accuracy": eng.state.accuracy,
                "done": True,
                "entry": entry,
                "title": MODE_META[sess.mode_key]["title"],
            }
        )

    next_trial = eng.next_trial()
    sess.last_trial = next_trial
    return jsonify(
        {
            "session_id": sess.id,
            "event": event,
            "score": eng.state.score,
            "correct": eng.state.correct,
            "attempts": eng.state.attempts,
            "round": eng.state.round_i,
            "rounds": eng.rounds,
            "done": False,
            "trial": trial_to_json(sess.mode_key, next_trial),
        }
    )


@app.get("/api/progress")
def progress():
    p = Progress.load()
    return jsonify(
        {
            "name": p.player_name,
            "growth": p.growth_points,
            "title": p.growth_title(),
            "streak": p.current_streak,
            "best_streak": p.best_streak,
            "sessions": p.total_sessions,
            "sound": p.sound_enabled,
            "modes": {
                k: {
                    "level": v.level,
                    "high": v.high_score,
                    "sessions": v.sessions,
                    "accuracy": round(v.accuracy, 3),
                }
                for k, v in p.modes.items()
            },
        }
    )


@app.post("/api/player")
def set_player():
    body = request.get_json(force=True, silent=True) or {}
    name = (body.get("name") or "").strip()[:24]
    if not name:
        return jsonify({"error": "Name required"}), 400
    p = Progress.load()
    p.player_name = name
    p.save()
    return jsonify({"ok": True, "name": p.player_name})


@app.post("/api/settings")
def set_settings():
    body = request.get_json(force=True, silent=True) or {}
    p = Progress.load()
    if "sound" in body:
        p.sound_enabled = bool(body["sound"])
    p.save()
    return jsonify({"ok": True, "sound": p.sound_enabled})


# ── Mobile push (iOS / Android / Web PWA) ─────────────────────


@app.get("/api/notifications")
def notifications_get():
    prefs = NotificationPrefs.load()
    return jsonify(
        {
            "prefs": prefs.to_dict(),
            "schedule": mobile_push.schedule_plan(prefs),
            "devices": push_devices.summary(),
            "copy": mobile_push.DEFAULT_COPY,
            "target": "ios_android_web",
        }
    )


@app.post("/api/notifications")
def notifications_save():
    body = request.get_json(force=True, silent=True) or {}
    prefs = NotificationPrefs.load()
    bool_keys = (
        "enabled",
        "daily_reminder",
        "evening_reminder",
        "streak_alerts",
        "session_complete",
        "level_up",
        "weekly_summary",
        "motivational",
        "quiet_hours",
        "sound",
    )
    for k in bool_keys:
        if k in body:
            setattr(prefs, k, bool(body[k]))
    for k in ("daily_hour", "daily_minute", "evening_hour", "evening_minute",
              "quiet_start_hour", "quiet_end_hour"):
        if k in body:
            try:
                setattr(prefs, k, int(body[k]))
            except (TypeError, ValueError):
                pass
    prefs.daily_hour = max(0, min(23, prefs.daily_hour))
    prefs.evening_hour = max(0, min(23, prefs.evening_hour))
    prefs.daily_minute = max(0, min(59, prefs.daily_minute))
    prefs.evening_minute = max(0, min(59, prefs.evening_minute))
    if isinstance(body.get("days"), dict):
        for code in DAY_CODES:
            if code in body["days"]:
                prefs.days[code] = bool(body["days"][code])
    if body.get("platform") in ("ios", "android", "web", "desktop"):
        prefs.platform = body["platform"]
    prefs.save()
    return jsonify(
        {
            "ok": True,
            "prefs": prefs.to_dict(),
            "schedule": mobile_push.schedule_plan(prefs),
        }
    )


@app.post("/api/notifications/register")
def notifications_register():
    """Register APNs / FCM / Web Push subscription for this device."""
    body = request.get_json(force=True, silent=True) or {}
    try:
        result = mobile_push.register_token(
            token=str(body.get("token") or body.get("endpoint") or ""),
            platform=str(body.get("platform") or "web"),
            label=str(body.get("label") or "")[:64],
            endpoint=str(body.get("endpoint") or ""),
            p256dh=str(body.get("p256dh") or ""),
            auth=str(body.get("auth") or ""),
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.post("/api/notifications/unregister")
def notifications_unregister():
    body = request.get_json(force=True, silent=True) or {}
    key = str(body.get("token") or body.get("endpoint") or "")
    ok = push_devices.unregister_device(key)
    return jsonify({"ok": ok})


@app.post("/api/notifications/test")
def notifications_test():
    """Return a test push payload for the client (and any registered devices)."""
    prefs = NotificationPrefs.load()
    payload = mobile_push.build_event_payload("test")
    assert payload is not None
    report = mobile_push.deliver(payload, prefs)
    return jsonify(report)


@app.post("/api/notifications/event")
def notifications_event():
    """Fire an event push (session / level / streak) for mobile clients."""
    body = request.get_json(force=True, silent=True) or {}
    kind = str(body.get("kind") or "session")
    prefs = NotificationPrefs.load()
    # Respect event toggles
    if kind == "session" and not prefs.session_complete:
        return jsonify({"ok": False, "reason": "session_complete_off"})
    if kind == "level" and not prefs.level_up:
        return jsonify({"ok": False, "reason": "level_up_off"})
    if kind == "streak" and not prefs.streak_alerts:
        return jsonify({"ok": False, "reason": "streak_off"})
    payload = mobile_push.build_event_payload(kind, **(body.get("fmt") or {}))
    if not payload:
        return jsonify({"error": "unknown kind"}), 400
    report = mobile_push.deliver(payload, prefs)
    return jsonify(report)


@app.get("/api/notifications/schedule")
def notifications_schedule():
    """Native apps poll this to configure local UNCalendar / AlarmManager."""
    prefs = NotificationPrefs.load()
    return jsonify(mobile_push.schedule_plan(prefs))


@app.get("/sw.js")
def service_worker():
    """Serve SW from root so scope covers the whole app (required for PWA push)."""
    from flask import send_from_directory

    return send_from_directory(
        str(Path(__file__).parent / "static"),
        "sw.js",
        mimetype="application/javascript",
    )


def main():
    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"NeuroForge web → http://127.0.0.1:{port}", flush=True)
    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
