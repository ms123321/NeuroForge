/* NeuroForge ↔ Despia native bridge
 * Docs: https://setup.despia.com
 * Only active when user-agent contains "despia".
 */
(() => {
  const ua = (navigator.userAgent || "").toLowerCase();
  const isDespia = ua.includes("despia");
  const isIOS = isDespia && (ua.includes("iphone") || ua.includes("ipad"));
  const isAndroid = isDespia && ua.includes("android");

  function hasSdk() {
    return typeof window.despia === "function" || typeof window.despia === "string";
  }

  async function call(scheme, vars) {
    if (!isDespia) return null;
    try {
      // CDN UMD may expose global despia()
      const fn =
        typeof window.despia === "function"
          ? window.despia
          : typeof despia === "function"
            ? despia
            : null;
      if (!fn) {
        // Fallback: set location scheme (native intercept)
        window.location.href = scheme;
        return null;
      }
      if (vars && vars.length) return await fn(scheme, vars);
      return await fn(scheme);
    } catch (e) {
      console.warn("despia call failed", scheme, e);
      return null;
    }
  }

  const NFDespia = {
    isDespia,
    isIOS,
    isAndroid,

    async init() {
      if (!isDespia) return { ok: false, reason: "not_despia" };
      document.documentElement.classList.add("despia");
      document.body.classList.add("despia");

      // Fullscreen chrome
      await call("hidebars://on");
      await call("statusbarcolor://{11, 16, 32}"); // #0B1020
      await call("spinneroff://");

      // Stable device id for push / purchases
      let uuid = localStorage.getItem("nf_despia_uuid");
      try {
        const dev = await call("get-uuid://", ["uuid"]);
        if (dev && dev.uuid) {
          uuid = dev.uuid;
          localStorage.setItem("nf_despia_uuid", uuid);
        }
      } catch (_) {}
      if (!uuid) {
        uuid = localStorage.getItem("nf_device_id") || String(Date.now());
        localStorage.setItem("nf_despia_uuid", uuid);
      }

      // Map to OneSignal external user (if OneSignal enabled in Despia)
      try {
        await call(`setonesignalplayerid://?user_id=${encodeURIComponent(uuid)}`);
      } catch (_) {}

      // Register with NeuroForge backend
      try {
        await fetch("/api/notifications/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            token: uuid,
            platform: isIOS ? "ios" : isAndroid ? "android" : "web",
            label: "despia-" + (isIOS ? "ios" : isAndroid ? "android" : "app"),
          }),
        });
        await fetch("/api/notifications", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            enabled: true,
            platform: isIOS ? "ios" : isAndroid ? "android" : "web",
          }),
        });
      } catch (_) {}

      // Check RevenueCat entitlements (Pro)
      this.checkEntitlements().catch(() => {});

      window.onRevenueCatPurchase = () => {
        this.checkEntitlements().catch(() => {});
      };

      return { ok: true, uuid, isIOS, isAndroid };
    },

    haptic(kind) {
      if (!isDespia) return;
      const map = {
        light: "lighthaptic://",
        heavy: "heavyhaptic://",
        success: "successhaptic://",
        warning: "warninghaptic://",
        error: "errorhaptic://",
        correct: "successhaptic://",
        wrong: "errorhaptic://",
        level: "heavyhaptic://",
        tap: "lighthaptic://",
      };
      call(map[kind] || "lighthaptic://");
    },

    spinner(on) {
      call(on ? "spinneron://" : "spinneroff://");
    },

    async enablePush() {
      if (!isDespia) return { ok: false, reason: "not_despia" };
      const uuid = localStorage.getItem("nf_despia_uuid") || "user";
      await call(`setonesignalplayerid://?user_id=${encodeURIComponent(uuid)}`);
      // Open OS settings if user needs to re-grant
      // await call("settingsapp://");
      this.haptic("success");
      return { ok: true, message: "Push registered with Despia / OneSignal" };
    },

    async testPush() {
      // Local system notification style via web Notification if allowed,
      // plus haptic success to confirm native bridge works
      this.haptic("success");
      if (window.NFPush && NFPush.show) {
        await NFPush.show({
          title: "NeuroForge push OK",
          body: "Despia native bridge is working on this device.",
          tag: "test",
        });
      }
      return { ok: true };
    },

    async openPaywall(offering) {
      if (!isDespia) return { ok: false, reason: "not_despia" };
      const uuid =
        localStorage.getItem("nf_despia_uuid") ||
        localStorage.getItem("nf_device_id") ||
        "guest";
      const off = offering || "default";
      await call(
        `revenuecat://launchPaywall?external_id=${encodeURIComponent(uuid)}&offering=${encodeURIComponent(off)}`
      );
      return { ok: true };
    },

    async checkEntitlements() {
      if (!isDespia) return { pro: false };
      try {
        const data = await call("getpurchasehistory://", ["restoredData"]);
        const active = (data && data.restoredData ? data.restoredData : []).filter(
          (p) => p.isActive
        );
        const pro = active.some(
          (p) =>
            String(p.entitlementId || "").toLowerCase().includes("pro") ||
            String(p.entitlementId || "").toLowerCase().includes("premium") ||
            String(p.productId || "").toLowerCase().includes("pro")
        );
        if (pro) {
          // Mirror unlock on backend (demo entitlement for server gates)
          try {
            await fetch("/api/pro/buy", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ plan: "lifetime" }),
            });
          } catch (_) {}
        }
        return { pro, active };
      } catch (e) {
        return { pro: false };
      }
    },

    async restorePurchases() {
      await this.checkEntitlements();
      this.haptic("success");
    },

    openAppSettings() {
      call("settingsapp://");
    },
  };

  window.NFDespia = NFDespia;

  // Auto-init when in Despia runtime
  if (isDespia) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => NFDespia.init());
    } else {
      NFDespia.init();
    }
  }
})();
