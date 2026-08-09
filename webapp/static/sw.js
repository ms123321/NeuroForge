/* NeuroForge service worker — iOS/Android/Web PWA push + local notifications */
/* Scope: / (served from /sw.js) */

const CACHE = "neuroforge-shell-v2";
const SHELL = ["/", "/static/app.css?v=1.8.2", "/static/app.js?v=1.8.2", "/static/push.js?v=1.8.2"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {})).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  // Network-first for API; cache-first for shell statics is optional — keep API live
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(event.request));
    return;
  }
});

/** Remote Web Push (FCM/APNs via push service → browser) */
self.addEventListener("push", (event) => {
  let data = { title: "NeuroForge", body: "Time to train.", tag: "neuroforge", url: "/" };
  try {
    if (event.data) {
      const j = event.data.json();
      data = { ...data, ...j, ...(j.notification || {}), ...(j.data || {}) };
      if (j.aps && j.aps.alert) {
        data.title = j.aps.alert.title || data.title;
        data.body = j.aps.alert.body || data.body;
      }
    }
  } catch (_) {
    try {
      data.body = event.data.text();
    } catch (__) {}
  }
  event.waitUntil(showLocal(data));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || "/";
  event.waitUntil(
    self.clients.matchAll({ type: "window", includeUncontrolled: true }).then((list) => {
      for (const c of list) {
        if ("focus" in c) {
          c.navigate && c.navigate(url);
          return c.focus();
        }
      }
      if (self.clients.openWindow) return self.clients.openWindow(url);
    })
  );
});

/** Messages from the open page (local schedule / test / session complete) */
self.addEventListener("message", (event) => {
  const msg = event.data || {};
  if (msg.type === "show-notification" && msg.payload) {
    event.waitUntil(showLocal(msg.payload));
  }
  if (msg.type === "schedule-check") {
    event.waitUntil(runScheduleCheck(msg.schedule || {}));
  }
});

async function showLocal(payload) {
  const title = payload.title || "NeuroForge";
  const body = payload.body || "";
  const tag = payload.tag || "neuroforge";
  const opts = {
    body,
    tag,
    renotify: true,
    data: payload.data || { url: payload.url || "/" },
    icon: "/static/icon-192.png",
    badge: "/static/icon-192.png",
    vibrate: payload.sound === false ? [] : [80, 40, 80],
    silent: payload.sound === false,
  };
  return self.registration.showNotification(title, opts);
}

/**
 * Lightweight schedule check when the SW wakes (page open / periodic sync).
 * Native apps should use OS local notifications for reliability when killed.
 */
async function runScheduleCheck(schedule) {
  if (!schedule || !schedule.enabled) return;
  const now = new Date();
  const dayMap = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
  const code = dayMap[now.getDay()];
  const days = (schedule.daily && schedule.daily.days) || [];
  if (days.length && !days.includes(code)) return;

  // Quiet hours
  const q = schedule.quiet_hours || {};
  if (q.enabled) {
    const h = now.getHours();
    const s = q.start_hour ?? 22;
    const e = q.end_hour ?? 7;
    const quiet = s < e ? h >= s && h < e : h >= s || h < e;
    if (quiet) return;
  }

  const key = `nf-fired-${now.toDateString()}`;
  const store = await caches.open("neuroforge-meta");
  // Use cache as mini-KV for last fire markers
  async function fired(id) {
    const r = await store.match(key + "-" + id);
    return !!r;
  }
  async function mark(id) {
    await store.put(key + "-" + id, new Response("1"));
  }

  async function maybe(slot) {
    if (!slot || !slot.enabled) return;
    if (now.getHours() !== slot.hour || now.getMinutes() !== slot.minute) return;
    if (await fired(slot.id)) return;
    await showLocal({
      title: slot.title,
      body: slot.body,
      tag: slot.id,
      sound: schedule.sound !== false,
      data: { url: "/", kind: slot.id },
    });
    await mark(slot.id);
  }

  await maybe(schedule.daily);
  await maybe(schedule.evening);
}
