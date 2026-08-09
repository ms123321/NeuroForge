/* NeuroForge mobile push client — iPhone / Android / Web PWA */
(() => {
  const NFPush = {
    permission: typeof Notification !== "undefined" ? Notification.permission : "denied",
    registration: null,
    platform: detectPlatform(),
    schedule: null,
    prefs: null,
    _tick: null,

    detectPlatform,

    async init() {
      this.platform = detectPlatform();
      if (!("serviceWorker" in navigator)) {
        return { ok: false, reason: "no_service_worker", platform: this.platform };
      }
      try {
        this.registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
        await navigator.serviceWorker.ready;
      } catch (e) {
        return { ok: false, reason: String(e), platform: this.platform };
      }
      await this.refreshPrefs();
      this.startScheduleTicker();
      return {
        ok: true,
        platform: this.platform,
        permission: this.permission,
        schedule: this.schedule,
      };
    },

    async refreshPrefs() {
      try {
        const r = await fetch("/api/notifications", { cache: "no-store" });
        const data = await r.json();
        this.prefs = data.prefs;
        this.schedule = data.schedule;
        localStorage.setItem("nf_push_schedule", JSON.stringify(this.schedule || {}));
        return data;
      } catch (e) {
        return null;
      }
    },

    async enable() {
      if (!("Notification" in window)) {
        return { ok: false, reason: "Notifications API unavailable on this browser" };
      }
      // iOS Safari: must be installed to Home Screen for reliable push
      if (this.platform === "ios" && !isStandalone()) {
        return {
          ok: false,
          reason: "ios_add_to_home",
          message:
            "On iPhone: Share → Add to Home Screen, open NeuroForge from the icon, then enable push again.",
        };
      }
      const perm = await Notification.requestPermission();
      this.permission = perm;
      if (perm !== "granted") {
        return { ok: false, reason: "denied", permission: perm };
      }

      // Register this browser as a web push device (token = local device id)
      const deviceId =
        localStorage.getItem("nf_device_id") ||
        (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()));
      localStorage.setItem("nf_device_id", deviceId);

      try {
        await fetch("/api/notifications/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token: deviceId,
            platform: this.platform === "desktop" ? "web" : this.platform,
            label: navigator.userAgent.slice(0, 48),
          }),
        });
        await fetch("/api/notifications", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            enabled: true,
            platform: this.platform === "desktop" ? "web" : this.platform,
          }),
        });
      } catch (_) {}

      await this.refreshPrefs();
      await this.show({
        title: "NeuroForge push ready",
        body: "Daily reminders will use this phone’s notification system.",
        tag: "setup",
      });
      return { ok: true, permission: perm, platform: this.platform };
    },

    async show(payload) {
      if (!payload) return false;
      if (this.permission !== "granted" && Notification.permission !== "granted") {
        return false;
      }
      this.permission = Notification.permission;
      // Prefer service worker (works better when tab is backgrounded)
      if (this.registration && this.registration.showNotification) {
        await this.registration.showNotification(payload.title || "NeuroForge", {
          body: payload.body || "",
          tag: payload.tag || "neuroforge",
          renotify: true,
          data: payload.data || { url: "/" },
          silent: payload.sound === false,
          vibrate: payload.sound === false ? [] : [80, 40, 80],
        });
        return true;
      }
      // Fallback
      new Notification(payload.title || "NeuroForge", {
        body: payload.body || "",
        tag: payload.tag || "neuroforge",
      });
      return true;
    },

    async test() {
      try {
        const r = await fetch("/api/notifications/test", { method: "POST" });
        const data = await r.json();
        if (data.payload) await this.show(data.payload);
        return data;
      } catch (e) {
        return { ok: false, error: String(e) };
      }
    },

    async event(kind, fmt) {
      try {
        const r = await fetch("/api/notifications/event", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ kind, fmt: fmt || {} }),
        });
        const data = await r.json();
        if (data.payload) await this.show(data.payload);
        return data;
      } catch (e) {
        return { ok: false };
      }
    },

    /** Keep local daily/evening schedule alive while the PWA is installed */
    startScheduleTicker() {
      if (this._tick) clearInterval(this._tick);
      const tick = async () => {
        if (!this.schedule) {
          const raw = localStorage.getItem("nf_push_schedule");
          if (raw) {
            try {
              this.schedule = JSON.parse(raw);
            } catch (_) {}
          }
        }
        if (!this.schedule || !this.schedule.enabled) return;
        if (this.registration && this.registration.active) {
          this.registration.active.postMessage({
            type: "schedule-check",
            schedule: this.schedule,
          });
        }
        // Also check in-page (covers some iOS cases)
        await this._localMinuteCheck();
      };
      // every 30s near minute boundary
      this._tick = setInterval(tick, 30000);
      setTimeout(tick, 2000);
    },

    async _localMinuteCheck() {
      const s = this.schedule;
      if (!s || !s.enabled) return;
      const now = new Date();
      const dayMap = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];
      const code = dayMap[now.getDay()];
      const check = async (slot) => {
        if (!slot || !slot.enabled) return;
        if (now.getHours() !== slot.hour || now.getMinutes() !== slot.minute) return;
        const key = `nf_local_${slot.id}_${now.toDateString()}`;
        if (localStorage.getItem(key)) return;
        const days = slot.days || [];
        if (days.length && !days.includes(code)) return;
        await this.show({
          title: slot.title,
          body: slot.body,
          tag: slot.id,
          sound: s.sound !== false,
        });
        localStorage.setItem(key, "1");
      };
      await check(s.daily);
      await check(s.evening);
    },

    statusLine() {
      const p = this.platform;
      const perm = Notification && Notification.permission;
      if (p === "ios" && !isStandalone()) {
        return "iPhone: Add to Home Screen for push, then Enable";
      }
      if (perm === "granted") return `Push ON · ${p}`;
      if (perm === "denied") return "Push blocked in system settings";
      return `Push ready · ${p} · tap Enable`;
    },
  };

  function detectPlatform() {
    const ua = navigator.userAgent || "";
    if (/iPhone|iPad|iPod/i.test(ua)) return "ios";
    if (/Android/i.test(ua)) return "android";
    // iPadOS 13+ desktop UA
    if (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1) return "ios";
    return "web";
  }

  function isStandalone() {
    return (
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true
    );
  }

  window.NFPush = NFPush;
})();
