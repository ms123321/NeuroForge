/* NeuroForge Web — UI parity with desktop tkinter shell */
(() => {
  const $ = (s) => document.querySelector(s);
  const $$ = (s) => document.querySelectorAll(s);

  const views = ["home", "modes", "play", "result", "progress", "pro", "settings"];
  let state = {
    sessionId: null,
    mode: null,
    trial: null,
    lastMode: null,
    circuit: [],
    circuitLabel: "",
    modesCache: null,
    pro: false,
    sound: true,
    timers: [],
    lang: localStorage.getItem("nf_lang") || "en",
    i18n: {},
    sort: localStorage.getItem("nf_mode_sort") || "default",
  };

  function tr(key, fallback, vars) {
    let s = (state.i18n && state.i18n[key]) || fallback || key;
    if (vars) {
      Object.keys(vars).forEach((k) => {
        s = s.replace(new RegExp("\\{" + k + "\\}", "g"), String(vars[k]));
      });
    }
    return s;
  }

  function applyI18nDom() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (!key) return;
      // full_gym needs count — handled in loadHome for btnFull
      if (key === "home.full_gym" || key === "home.full_gym_pro") return;
      if (key === "home.sound_on" || key === "home.sound_off") return;
      const text = tr(key, el.textContent);
      if (text) el.textContent = text;
    });
    if (state.i18n["app.title"]) document.title = state.i18n["app.title"];
    document.documentElement.lang = state.lang || "en";
  }

  const LANGS = [
    ["en", "English  (English)"],
    ["es", "Español  (Spanish)"],
    ["fr", "Français  (French)"],
    ["de", "Deutsch  (German)"],
    ["pt", "Português  (Portuguese)"],
    ["it", "Italiano  (Italian)"],
    ["zh", "中文  (Chinese)"],
    ["ja", "日本語  (Japanese)"],
    ["ko", "한국어  (Korean)"],
    ["hi", "हिन्दी  (Hindi)"],
    ["ar", "العربية  (Arabic)"],
    ["ru", "Русский  (Russian)"],
    ["nl", "Nederlands  (Dutch)"],
    ["pl", "Polski  (Polish)"],
    ["tr", "Türkçe  (Turkish)"],
    ["vi", "Tiếng Việt  (Vietnamese)"],
    ["th", "ไทย  (Thai)"],
    ["id", "Bahasa Indonesia  (Indonesian)"],
    ["uk", "Українська  (Ukrainian)"],
    ["sv", "Svenska  (Swedish)"],
  ];

  function clearTimers() {
    state.timers.forEach((id) => clearTimeout(id));
    state.timers = [];
  }
  function later(ms, fn) {
    const id = setTimeout(fn, ms);
    state.timers.push(id);
    return id;
  }

  function show(name) {
    views.forEach((v) => {
      const el = $(`#view-${v}`);
      if (el) el.classList.toggle("hidden", v !== name);
    });
    window.scrollTo(0, 0);
  }

  async function api(path, opts = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
      cache: "no-store",
      ...opts,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = new Error(data.error || res.statusText);
      err.paywall = data.paywall;
      throw err;
    }
    return data;
  }

  function soundLabel() {
    return state.sound ? "Sound & haptics: ON" : "Sound & haptics: OFF";
  }
  function syncSoundButtons() {
    ["#btnSound", "#btnSound2"].forEach((sel) => {
      const el = $(sel);
      if (el) el.textContent = soundLabel();
    });
  }

  async function loadI18n(lang) {
    const code = lang || state.lang || "en";
    try {
      const data = await api(`/api/i18n?lang=${encodeURIComponent(code)}`);
      state.lang = data.lang || code;
      state.i18n = data.strings || {};
      localStorage.setItem("nf_lang", state.lang);
      if (data.languages && data.languages.length) {
        state.langList = data.languages;
      }
      applyI18nDom();
      return data;
    } catch (e) {
      state.i18n = state.i18n || {};
      return null;
    }
  }

  async function setLanguage(code) {
    if (!code) return;
    state.lang = code;
    localStorage.setItem("nf_lang", code);
    try {
      const data = await api("/api/language", {
        method: "POST",
        body: JSON.stringify({ lang: code }),
      });
      state.lang = data.lang || code;
      state.i18n = data.strings || {};
      if (data.languages) state.langList = data.languages;
      applyI18nDom();
    } catch (e) {
      await loadI18n(code);
    }
    // Refresh screens so mode titles / buttons use new language
    state.modesCache = null;
    await loadHome();
  }

  function fillLangSelects() {
    const list =
      state.langList ||
      LANGS.map(([code, label]) => ({ code, label }));
    ["#langSelect", "#langSelect2"].forEach((sel) => {
      const el = $(sel);
      if (!el) return;
      const prev = el.value || state.lang || "en";
      el.innerHTML = "";
      list.forEach((item) => {
        const code = item.code || item[0];
        const label = item.label || item[1];
        const o = document.createElement("option");
        o.value = code;
        o.textContent = label;
        el.appendChild(o);
      });
      el.value = state.lang || prev || "en";
      el.onchange = () => {
        setLanguage(el.value).catch((err) => alert(err.message || "Language failed"));
      };
    });
  }

  async function loadHome() {
    try {
      if (!state.i18n || !Object.keys(state.i18n).length) {
        await loadI18n(state.lang);
      }
      fillLangSelects();
      applyI18nDom();

      const langQ = encodeURIComponent(state.lang || "en");
      const sortQ = encodeURIComponent(state.sort || "default");
      const modes = await api(`/api/modes?lang=${langQ}&sort=${sortQ}`);
      const prog = await api("/api/progress");
      state.modesCache = modes;
      state.pro = !!modes.pro;
      state.sound = prog.sound !== false;
      if (localStorage.getItem("nf_sound") === "0") state.sound = false;
      if (localStorage.getItem("nf_sound") === "1") state.sound = true;
      syncSoundButtons();

      const n = modes.modes.length;
      $("#homeSub").textContent =
        tr("home.subtitle", "{n} research drills · Adaptive Difficulty Engine", { n }) +
        "\n" +
        (modes.status || "");
      $("#growthTitle").textContent = prog.title || "Trainee";
      $("#growthPts").textContent = `${prog.growth || 0} GP`;
      $("#streakLine").textContent = tr(
        "home.streak",
        `Streak ${prog.streak || 0} day(s)  ·  Best ${prog.best_streak || 0}  ·  ${prog.sessions || 0} sessions`,
        {
          n: prog.streak || 0,
          best: prog.best_streak || 0,
          sessions: prog.sessions || 0,
        }
      );
      const fill = Math.min(1, ((prog.growth || 0) % 200) / 200) || 0.05;
      $("#growthBar").style.width = `${fill * 100}%`;
      $("#btnFull").textContent = modes.pro
        ? tr("home.full_gym", `Full Gym  (all ${n} modes)`, { n })
        : tr("home.full_gym_pro", "Full Gym  (Pro)");
      $("#btnDaily").textContent = tr("home.daily", "▶  Daily Circuit  (5 modes)");
      $("#btnModes").textContent = tr("home.train", "Train a single skill");
      $("#btnPro").textContent = tr("home.pro", "⭐  Go Pro  ·  Plans & pricing");
      $("#btnProgress").textContent = tr("home.progress", "Progress & science");
      $("#btnSettings").textContent = tr("home.settings", "Settings · Language & alerts");
      $("#adBanner").classList.toggle("hidden", !!modes.pro);
      $("#playerLine").textContent = tr(
        "home.player",
        `Player: ${prog.name || "Trainee"}  ·  v${modes.version || "1.8"}`,
        { name: prog.name || "Trainee", version: modes.version || "1.8" }
      );
    } catch (e) {
      $("#homeSub").textContent =
        "Server offline — check Render logs or Start Web App.bat";
    }
    show("home");
  }

  async function loadModes() {
    const langQ = encodeURIComponent(state.lang || "en");
    const sortQ = encodeURIComponent(state.sort || "default");
    const data = await api(`/api/modes?lang=${langQ}&sort=${sortQ}`);
    state.modesCache = data;

    const sortEl = $("#modeSort");
    if (sortEl) {
      // populate labels from API when present
      if (data.sort_options && data.sort_options.length) {
        const cur = state.sort || "default";
        sortEl.innerHTML = "";
        data.sort_options.forEach((opt) => {
          const o = document.createElement("option");
          o.value = opt.id;
          o.textContent = opt.label;
          sortEl.appendChild(o);
        });
        sortEl.value = cur;
      } else {
        sortEl.value = state.sort || "default";
      }
      sortEl.onchange = () => {
        state.sort = sortEl.value || "default";
        localStorage.setItem("nf_mode_sort", state.sort);
        loadModes().catch((e) => alert(e.message));
      };
    }

    $("#modesHint").textContent = data.pro
      ? `${data.modes.length} · Pro: all modes unlocked · no ads`
      : `${data.modes.length} · Free: ${(data.free_keys || []).length} modes · locked need Pro`;
    const list = $("#modeList");
    list.innerHTML = "";
    data.modes.forEach((m) => {
      const el = document.createElement("div");
      el.className = "mode-card";
      el.style.borderLeftColor = m.color;
      el.innerHTML = `
        <div class="meta-row">
          <h3 style="color:${m.color}">${m.title}${m.locked ? "  🔒" : ""}</h3>
          <span class="gold small">Lv ${m.level || 1}</span>
        </div>
        <p>${m.subtitle || ""}</p>
        <div class="blurb">${m.domain ? m.domain + " · " : ""}${m.blurb || ""}</div>
        <div class="start-wrap"></div>`;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = m.locked ? "btn gold" : "btn primary";
      btn.style.background = m.locked ? "" : m.color;
      btn.style.color = m.locked ? "" : "#0b1020";
      btn.textContent = m.locked
        ? tr("unlock_pro", "Unlock with Pro")
        : tr("start", "Start");
      btn.onclick = () => {
        if (m.locked) {
          loadPro();
          return;
        }
        state.circuit = [];
        state.circuitLabel = "";
        startPlay(m.key, m.title, m.level);
      };
      el.querySelector(".start-wrap").appendChild(btn);
      list.appendChild(el);
    });
    show("modes");
  }

  async function loadProgress() {
    const p = await api("/api/progress");
    const data = state.modesCache || (await api("/api/modes"));
    $("#progressSummary").innerHTML = `
      <div class="teal">Your growth</div>
      <div style="margin-top:8px;font-weight:700">${p.title}  ·  ${p.growth} growth points</div>
      <div class="muted small" style="margin-top:6px">
        Streak: ${p.streak} days (best ${p.best_streak})<br>
        Sessions: ${p.sessions}
      </div>`;
    const box = $("#progressModes");
    box.innerHTML = "";
    (data.modes || []).forEach((m) => {
      const st = (p.modes || {})[m.key];
      if (!st || !st.sessions) return;
      const el = document.createElement("div");
      el.className = "mode-card";
      el.style.borderLeftColor = m.color;
      el.innerHTML = `<h3 style="color:${m.color}">${m.title}</h3>
        <p>Level ${st.level} · High ${st.high} · Acc ${Math.round((st.accuracy || 0) * 100)}% · ${st.sessions} plays</p>`;
      box.appendChild(el);
    });
    if (!box.children.length) {
      box.innerHTML = `<div class="muted small">No sessions yet — try Daily Circuit.</div>`;
    }
    show("progress");
  }

  function loadPro() {
    const m = state.modesCache;
    $("#proStatus").textContent = m ? m.status : "";
    $("#planFreeCurrent").textContent = m && !m.pro ? "✓ Current plan" : "";
    show("pro");
  }

  async function buy(plan) {
    // In Despia: open native App Store / Play paywall (RevenueCat)
    if (window.NFDespia && NFDespia.isDespia && plan !== "restore") {
      await NFDespia.openPaywall("default");
      // Entitlement callback may unlock Pro; refresh shortly
      setTimeout(async () => {
        if (NFDespia.checkEntitlements) await NFDespia.checkEntitlements();
        state.modesCache = null;
        await loadHome();
      }, 1500);
      return;
    }
    if (window.NFDespia && NFDespia.isDespia && plan === "restore") {
      await NFDespia.restorePurchases();
      state.modesCache = null;
      await loadHome();
      return;
    }
    try {
      const r = await api("/api/pro/buy", {
        method: "POST",
        body: JSON.stringify({ plan }),
      });
      alert(r.message || "OK");
      state.modesCache = null;
      await loadHome();
    } catch (e) {
      alert(e.message);
    }
  }

  async function toggleSound() {
    state.sound = !state.sound;
    localStorage.setItem("nf_sound", state.sound ? "1" : "0");
    syncSoundButtons();
    try {
      await api("/api/settings", {
        method: "POST",
        body: JSON.stringify({ sound: state.sound }),
      });
    } catch (_) { /* offline ok */ }
  }

  async function renamePlayer() {
    const name = prompt("What should we call you?", ($("#playerLine").textContent.match(/Player:\s*([^·]+)/) || [])[1]?.trim() || "Trainee");
    if (!name || !name.trim()) return;
    try {
      await api("/api/player", {
        method: "POST",
        body: JSON.stringify({ name: name.trim().slice(0, 24) }),
      });
      await loadHome();
    } catch (e) {
      alert(e.message);
    }
  }

  function startDaily() {
    const daily = (state.modesCache && state.modesCache.daily) || [
      "focus", "memory", "switch", "speed", "nback",
    ];
    const free = (state.modesCache && state.modesCache.free_keys) || daily;
    const pro = state.modesCache && state.modesCache.pro;
    const order = pro ? daily.slice() : daily.filter((k) => free.includes(k));
    if (!order.length) {
      loadPro();
      return;
    }
    state.circuit = order.slice(1);
    state.circuitLabel = "Daily Circuit";
    const first = order[0];
    const meta = (state.modesCache.modes || []).find((m) => m.key === first);
    startPlay(first, meta ? meta.title : first, meta && meta.level);
  }

  function startFull() {
    if (!state.modesCache || !state.modesCache.pro) {
      loadPro();
      return;
    }
    const order = state.modesCache.modes.map((m) => m.key);
    state.circuit = order.slice(1);
    state.circuitLabel = "Full Gym";
    const first = order[0];
    const meta = state.modesCache.modes[0];
    startPlay(first, meta.title, meta.level);
  }

  async function startPlay(modeKey, title, level) {
    clearTimers();
    try {
      const data = await api("/api/play/start", {
        method: "POST",
        body: JSON.stringify({ mode: modeKey, level: level || 1 }),
      });
      state.sessionId = data.session_id;
      state.mode = modeKey;
      state.lastMode = modeKey;
      $("#playTitle").textContent = data.title || title;
      $("#playLevel").textContent = `Lv ${data.level || 1}`;
      updateHud(data);
      setFeedback(null);
      renderTrial(data.trial);
      show("play");
    } catch (e) {
      if (e.paywall) {
        alert(e.message);
        loadPro();
      } else alert(e.message || "Could not start");
    }
  }

  function updateHud(data) {
    const rounds = data.rounds ?? "?";
    $("#playScore").textContent = `Score  ${data.score ?? 0}`;
    const r = Math.min((data.round ?? 0) + 1, data.rounds || 1);
    $("#playRound").textContent = `${r} / ${rounds}`;
    const pct = data.rounds ? Math.min(100, ((data.round || 0) / data.rounds) * 100) : 0;
    $("#playBar").style.width = `${pct}%`;
  }

  function setFeedback(ev) {
    const fb = $("#playFeedback");
    if (!ev) {
      fb.textContent = " ";
      fb.className = "feedback";
      return;
    }
    fb.textContent = ev.message || (ev.good ? "Correct ✓" : "Miss ✗");
    fb.className = "feedback " + (ev.good ? "ok" : "bad");
  }

  function fillActions(list) {
    const actions = $("#playActions");
    actions.innerHTML = "";
    (list || []).forEach((a) => {
      const b = document.createElement("button");
      b.type = "button";
      let cls = "btn primary";
      if (/no|hold|diff|absent|false|new/i.test(a.label)) cls = "btn coral";
      else if (/yes|match|same|tap|got/i.test(a.label)) cls = "btn teal";
      b.className = cls;
      b.textContent = a.label;
      b.onclick = () => sendAnswer(a.id);
      actions.appendChild(b);
    });
  }

  async function sendAnswer(action, extra = {}) {
    if (!state.sessionId) return null;
    clearTimers();
    const body = { session_id: state.sessionId, action, ...extra };
    try {
      const data = await api("/api/play/answer", {
        method: "POST",
        body: JSON.stringify(body),
      });
      setFeedback(data.event);
      updateHud(data);
      if (window.NFDespia && NFDespia.isDespia && data.event) {
        NFDespia.haptic(data.event.good ? "correct" : "wrong");
      }
      if (data.done) {
        showResult(data);
        return data;
      }
      if (data.partial && extra.keepUI) return data;
      if (data.partial) return data;
      if (data.trial) later(320, () => renderTrial(data.trial));
      return data;
    } catch (e) {
      alert(e.message || "Error");
      return null;
    }
  }

  function showResult(data) {
    clearTimers();
    $("#resultTitle").textContent = data.title || state.mode;
    $("#resultScore").textContent = data.score ?? 0;
    const acc = data.accuracy != null ? Math.round(data.accuracy * 100) : 0;
    const entry = data.entry || {};
    let levelNote = `Level holds at ${entry.level_after ?? data.level ?? 1}`;
    if (entry.level_delta > 0) levelNote = `Level UP → ${entry.level_after} ⬆`;
    else if (entry.level_delta < 0) levelNote = `Level eased → ${entry.level_after} ⬇`;
    $("#resultDetail").innerHTML =
      `Accuracy  ${acc}%   (${data.correct}/${data.attempts})<br>` +
      `${levelNote}<br>+${entry.growth_gained || 0} growth points`;
    let tip = "Solid work. Stay consistent; small daily gains compound.";
    if (acc >= 85) tip = "Strong session. Difficulty will edge up — plasticity sweet spot.";
    else if (acc < 60) tip = "Tough round — struggle is information. Level may ease.";
    $("#resultTip").textContent = tip;

    const nextBtn = $("#btnNextCircuit");
    if (state.circuit && state.circuit.length) {
      nextBtn.style.display = "block";
      const nxt = state.circuit[0];
      const meta = (state.modesCache.modes || []).find((m) => m.key === nxt);
      nextBtn.textContent = `Next: ${meta ? meta.title : nxt}`;
      nextBtn.onclick = () => {
        state.circuit = state.circuit.slice(1);
        startPlay(nxt, meta ? meta.title : nxt, meta && meta.level);
      };
    } else {
      nextBtn.style.display = "none";
      if (state.circuitLabel) {
        $("#resultTip").textContent = `${state.circuitLabel} complete 🎉  ` + tip;
        state.circuitLabel = "";
      }
    }
    // Mobile push: session complete (+ level-up)
    if (window.NFPush) {
      NFPush.event("session", { score: data.score ?? 0, acc: `${acc}` });
      if (entry.level_delta > 0) {
        NFPush.event("level", { level: entry.level_after });
      }
    }
    if (window.NFDespia && NFDespia.isDespia) {
      NFDespia.haptic(entry.level_delta > 0 ? "level" : "success");
    }
    show("result");
  }

  /* ── Mobile push settings ───────────────────────────────── */
  const DAY_CODES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
  const DAY_LABELS = { mon: "Mo", tue: "Tu", wed: "We", thu: "Th", fri: "Fr", sat: "Sa", sun: "Su" };
  let notifDays = Object.fromEntries(DAY_CODES.map((d) => [d, true]));

  function pad2(n) {
    return String(n).padStart(2, "0");
  }

  function renderDayChips() {
    const row = $("#dayRow");
    if (!row) return;
    row.innerHTML = "";
    DAY_CODES.forEach((code) => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "day-chip" + (notifDays[code] ? " on" : "");
      b.textContent = DAY_LABELS[code];
      b.onclick = () => {
        notifDays[code] = !notifDays[code];
        renderDayChips();
      };
      row.appendChild(b);
    });
  }

  function setCheck(id, val) {
    const el = $(id);
    if (el) el.checked = !!val;
  }
  function getCheck(id) {
    const el = $(id);
    return el ? !!el.checked : false;
  }

  async function loadNotifSettings() {
    renderDayChips();
    try {
      const data = await api("/api/notifications");
      const p = data.prefs || {};
      setCheck("#n_enabled", p.enabled !== false);
      setCheck("#n_daily", p.daily_reminder !== false);
      setCheck("#n_evening", p.evening_reminder);
      setCheck("#n_streak", p.streak_alerts !== false);
      setCheck("#n_session", p.session_complete !== false);
      setCheck("#n_level", p.level_up !== false);
      setCheck("#n_weekly", p.weekly_summary !== false);
      setCheck("#n_motiv", p.motivational);
      setCheck("#n_sound", p.sound !== false);
      setCheck("#n_quiet", p.quiet_hours);
      $("#n_daily_time").value = `${pad2(p.daily_hour ?? 9)}:${pad2(p.daily_minute ?? 0)}`;
      $("#n_evening_time").value = `${pad2(p.evening_hour ?? 18)}:${pad2(p.evening_minute ?? 0)}`;
      $("#n_quiet_start").value = p.quiet_start_hour ?? 22;
      $("#n_quiet_end").value = p.quiet_end_hour ?? 7;
      if (p.days) notifDays = { ...notifDays, ...p.days };
      renderDayChips();
      $("#quietRow").classList.toggle("hidden", !p.quiet_hours);
      if (window.NFDespia && NFDespia.isDespia) {
        $("#pushStatus").textContent = NFDespia.isIOS
          ? "Despia iOS · OneSignal / APNs ready"
          : NFDespia.isAndroid
            ? "Despia Android · OneSignal / FCM ready"
            : "Despia native · push ready";
        $("#pushHint").textContent =
          "Running inside Despia. Enable OneSignal in Despia Integrations for remote push.";
      } else if (window.NFPush) {
        NFPush.prefs = p;
        NFPush.schedule = data.schedule;
        $("#pushStatus").textContent = NFPush.statusLine();
        const plat = NFPush.platform;
        $("#pushHint").textContent =
          plat === "ios"
            ? "iPhone uses APNs / Home Screen Web Push — not Windows toast."
            : plat === "android"
              ? "Android uses FCM / Chrome notifications — not Windows toast."
              : "This browser can use Web Push. On a phone, install as an app for best results.";
      }
    } catch (e) {
      $("#pushStatus").textContent = "Could not load notification prefs";
    }
  }

  async function saveNotifSettings() {
    const [dh, dm] = ($("#n_daily_time").value || "09:00").split(":").map(Number);
    const [eh, em] = ($("#n_evening_time").value || "18:00").split(":").map(Number);
    const body = {
      enabled: getCheck("#n_enabled"),
      daily_reminder: getCheck("#n_daily"),
      evening_reminder: getCheck("#n_evening"),
      streak_alerts: getCheck("#n_streak"),
      session_complete: getCheck("#n_session"),
      level_up: getCheck("#n_level"),
      weekly_summary: getCheck("#n_weekly"),
      motivational: getCheck("#n_motiv"),
      sound: getCheck("#n_sound"),
      quiet_hours: getCheck("#n_quiet"),
      daily_hour: dh,
      daily_minute: dm,
      evening_hour: eh,
      evening_minute: em,
      quiet_start_hour: parseInt($("#n_quiet_start").value, 10) || 22,
      quiet_end_hour: parseInt($("#n_quiet_end").value, 10) || 7,
      days: notifDays,
      platform: (window.NFPush && NFPush.platform) || "web",
    };
    if (body.platform === "desktop") body.platform = "web";
    try {
      const data = await api("/api/notifications", {
        method: "POST",
        body: JSON.stringify(body),
      });
      if (window.NFPush) {
        NFPush.prefs = data.prefs;
        NFPush.schedule = data.schedule;
        localStorage.setItem("nf_push_schedule", JSON.stringify(data.schedule || {}));
        NFPush.startScheduleTicker();
      }
      alert("Schedule saved for phone push");
      await loadNotifSettings();
    } catch (e) {
      alert(e.message || "Save failed");
    }
  }

  async function enablePush() {
    // Prefer Despia native (OneSignal) when inside the app shell
    if (window.NFDespia && NFDespia.isDespia) {
      const r = await NFDespia.enablePush();
      if (r.ok) alert(r.message || "Phone push enabled (Despia)");
      else alert(r.reason || "Could not enable Despia push");
      await loadNotifSettings();
      return;
    }
    if (!window.NFPush) {
      alert("Push module not loaded");
      return;
    }
    const r = await NFPush.enable();
    if (r.reason === "ios_add_to_home") {
      alert(r.message);
    } else if (!r.ok) {
      alert(r.message || r.reason || "Could not enable push");
    } else {
      alert("Phone push enabled");
    }
    await loadNotifSettings();
  }

  async function testPush() {
    if (window.NFDespia && NFDespia.isDespia) {
      await NFDespia.testPush();
      return;
    }
    if (!window.NFPush) return;
    if (Notification.permission !== "granted") {
      const r = await NFPush.enable();
      if (!r.ok) {
        alert(r.message || "Allow notifications first");
        return;
      }
    }
    await NFPush.test();
  }

  /* ── Trial renderers (desktop-like visuals for Daily Circuit) ─ */
  function renderTrial(trial) {
    clearTimers();
    state.trial = trial;
    const prompt = $("#playPrompt");
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    prompt.textContent = trial.prompt || "";
    display.textContent = trial.display || "";
    display.className = "display";
    display.style.color = trial.ink || "";
    display.style.fontSize = "";
    display.style.whiteSpace = "";
    stage.innerHTML = "";
    actions.innerHTML = "";
    const ui = trial.ui || "generic";

    // Focus Pulse — green circle / red square (tkinter match)
    if (ui === "go_nogo" && trial.mode === "focus") {
      playFocus(trial);
      return;
    }
    // N-Back letter circle
    if (ui === "match" || (ui === "nback")) {
      playNback(trial);
      return;
    }
    // Switch Path — colored shape cards
    if (ui === "switch" || (trial.mode === "switch" && trial.options_rich)) {
      playSwitch(trial);
      return;
    }
    // Speed Mirror — symbol grid
    if (ui === "speed" || (trial.mode === "speed" && trial.options)) {
      playSpeed(trial);
      return;
    }

    if (ui === "go_nogo") {
      // SART / oddball fallback buttons
      if (trial.display) display.textContent = trial.display;
      fillActions(trial.actions);
      if (trial.stimulus_ms) {
        later(trial.stimulus_ms, () => sendAnswer("hold"));
      }
      return;
    }

    if (ui === "rsvp" && trial.stream) {
      display.textContent = "…";
      let i = 0;
      const tick = () => {
        if (i >= trial.stream.length) {
          display.textContent = "?";
          fillActions(trial.actions);
          return;
        }
        display.textContent = trial.stream[i++];
        later(trial.soa_ms || 120, tick);
      };
      tick();
      return;
    }
    if (ui === "matrix" && trial.grid) {
      display.textContent = "";
      const g = document.createElement("div");
      g.className = "matrix";
      trial.grid.forEach((cell) => {
        const d = document.createElement("div");
        d.textContent = cell;
        g.appendChild(d);
      });
      stage.appendChild(g);
      fillActions(trial.actions);
      return;
    }
    if (ui === "loci" && trial.pairs) {
      display.style.fontSize = "15px";
      display.style.whiteSpace = "pre-line";
      display.textContent = trial.pairs.join("\n");
      later(trial.study_ms || 2500, () => {
        display.style.fontSize = "28px";
        display.textContent = trial.cue || "?";
        fillActions(trial.actions);
      });
      return;
    }
    if (ui === "sequence" && trial.sequence) {
      playMemory(trial);
      return;
    }
    if ((ui === "blocks" || ui === "digits") && (trial.sequence || trial.forward)) {
      const seq = trial.forward || trial.sequence;
      display.textContent = "Watch…";
      if (ui === "digits") {
        let i = 0;
        const show = () => {
          if (i >= seq.length) {
            display.textContent = "?";
            const pad = document.createElement("div");
            pad.className = "actions";
            for (let d = 0; d < 10; d++) {
              const b = document.createElement("button");
              b.type = "button";
              b.className = "btn elev";
              b.textContent = String(d);
              b.onclick = () => sendAnswer(String(d), { keepUI: true });
              pad.appendChild(b);
            }
            stage.appendChild(pad);
            return;
          }
          display.textContent = String(seq[i++]);
          later(trial.flash_ms || 600, () => {
            display.textContent = "";
            later(120, show);
          });
        };
        show();
        return;
      }
      const grid = document.createElement("div");
      grid.className = "blocks";
      const btns = [];
      for (let i = 0; i < 9; i++) {
        const b = document.createElement("button");
        b.type = "button";
        b.disabled = true;
        b.onclick = () => sendAnswer(String(i), { keepUI: true });
        grid.appendChild(b);
        btns.push(b);
      }
      stage.appendChild(grid);
      let step = 0;
      const flash = () => {
        if (step >= seq.length) {
          display.textContent = trial.reverse ? "Reverse order" : "Your turn";
          btns.forEach((b) => (b.disabled = false));
          return;
        }
        const idx = seq[step++];
        btns[idx].classList.add("flash");
        later(trial.flash_ms || 500, () => {
          btns[idx].classList.remove("flash");
          later(120, flash);
        });
      };
      later(400, flash);
      return;
    }
    if (ui === "cancel" && trial.items) {
      display.textContent = `Target: ${trial.target}`;
      const g = document.createElement("div");
      g.className = "grid";
      g.style.gridTemplateColumns = `repeat(${trial.cols || 5}, 40px)`;
      trial.items.forEach((sym, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = sym;
        b.onclick = () =>
          sendAnswer(String(i), { keepUI: true }).then((res) => {
            if (res && res.partial) b.classList.add("hit");
          });
        g.appendChild(b);
      });
      stage.appendChild(g);
      return;
    }
    if (ui === "odd" || ui === "grid") {
      const g = document.createElement("div");
      g.className = "grid";
      g.style.gridTemplateColumns = `repeat(${trial.cols || 3}, 48px)`;
      (trial.items || []).forEach((sym, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = sym;
        b.onclick = () => sendAnswer(String(i));
        g.appendChild(b);
      });
      stage.appendChild(g);
      return;
    }
    if (ui === "wordlist") {
      display.style.fontSize = "15px";
      display.textContent = (trial.study || []).join(" · ");
      later(trial.study_ms || 3000, () => {
        display.textContent = "Recall the list";
        display.style.fontSize = "22px";
        const g = document.createElement("div");
        g.className = "actions";
        (trial.pool || []).forEach((w) => {
          const b = document.createElement("button");
          b.type = "button";
          b.className = "btn elev";
          b.textContent = w;
          b.onclick = () => sendAnswer(w, { keepUI: true });
          g.appendChild(b);
        });
        stage.appendChild(g);
        const done = document.createElement("button");
        done.type = "button";
        done.className = "btn primary";
        done.textContent = "I'm done recalling";
        done.onclick = () => sendAnswer("done");
        actions.appendChild(done);
      });
      return;
    }
    if (ui === "running") {
      let i = 0;
      const stream = trial.stream || [];
      const tick = () => {
        if (i >= stream.length) {
          display.textContent = `Last ${trial.target?.length || "?"} letters`;
          const pad = document.createElement("div");
          pad.className = "actions";
          "FHJKLNPQRSTY".split("").forEach((L) => {
            const b = document.createElement("button");
            b.type = "button";
            b.className = "btn elev";
            b.textContent = L;
            b.onclick = () => sendAnswer(L, { keepUI: true });
            pad.appendChild(b);
          });
          stage.appendChild(pad);
          return;
        }
        display.textContent = stream[i++];
        later(trial.flash_ms || 500, tick);
      };
      tick();
      return;
    }
    if (ui === "trail") {
      display.textContent = "Tap in order";
      const g = document.createElement("div");
      g.className = "grid";
      g.style.gridTemplateColumns = `repeat(${trial.cols || 3}, 52px)`;
      (trial.labels || []).forEach((lab) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = lab;
        b.onclick = () =>
          sendAnswer(lab, { keepUI: true }).then((res) => {
            if (res && res.partial && res.event && res.event.good !== false) {
              b.classList.add("hit");
              b.disabled = true;
            }
          });
        g.appendChild(b);
      });
      stage.appendChild(g);
      return;
    }
    if (ui === "tower") {
      display.style.fontSize = "14px";
      display.textContent = "From peg → To peg";
      stage.innerHTML = `<pre style="color:#8b9bb8;font-size:11px;text-align:left">NOW ${JSON.stringify(
        trial.start
      )}\nGOAL ${JSON.stringify(trial.goal)}</pre>`;
      let from = null;
      [0, 1, 2].forEach((peg) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn elev";
        b.textContent = `Peg ${peg + 1}`;
        b.onclick = () => {
          if (from === null) {
            from = peg;
            setFeedback({ good: true, message: `From ${peg + 1} → pick destination` });
          } else sendAnswer("move", { from, to: peg });
        };
        actions.appendChild(b);
      });
      return;
    }
    if (ui === "dual") {
      display.textContent = trial.letter;
      const grid = document.createElement("div");
      grid.className = "blocks";
      for (let i = 0; i < 9; i++) {
        const b = document.createElement("button");
        b.type = "button";
        if (i === trial.position) b.classList.add("flash");
        grid.appendChild(b);
      }
      stage.appendChild(grid);
      let letterOn = false,
        posOn = false;
      const lb = document.createElement("button");
      lb.type = "button";
      lb.className = "btn elev";
      lb.textContent = "Letter: NO";
      lb.onclick = () => {
        letterOn = !letterOn;
        lb.textContent = letterOn ? "Letter: YES" : "Letter: NO";
        lb.className = letterOn ? "btn teal" : "btn elev";
      };
      const pb = document.createElement("button");
      pb.type = "button";
      pb.className = "btn elev";
      pb.textContent = "Position: NO";
      pb.onclick = () => {
        posOn = !posOn;
        pb.textContent = posOn ? "Position: YES" : "Position: NO";
        pb.className = posOn ? "btn teal" : "btn elev";
      };
      const sub = document.createElement("button");
      sub.type = "button";
      sub.className = "btn primary";
      sub.textContent = "Submit";
      sub.onclick = () => sendAnswer("submit", { letter: letterOn, position: posOn });
      actions.append(lb, pb, sub);
      return;
    }
    if (ui === "dualtask") {
      display.textContent = `${trial.letter}   ${trial.digit}`;
      fillActions([
        { id: "same", label: "SAME letter" },
        { id: "new", label: "NEW letter" },
      ]);
      return;
    }
    if (ui === "opspan") {
      playOpspan(trial);
      return;
    }
    if (ui === "track") {
      playTrack(trial);
      return;
    }
    if (ui === "brownpeterson") {
      display.textContent = trial.trigram;
      later(trial.encode_ms || 900, () => {
        let i = 0;
        const dist = () => {
          if (i >= (trial.distractors || []).length) {
            display.textContent = "Recall the 3 letters";
            fillActions((trial.options || []).map((o) => ({ id: o, label: o })));
            return;
          }
          display.textContent = trial.distractors[i++];
          later((trial.distract_ms || 2000) / Math.max(1, trial.distractors.length), dist);
        };
        dist();
      });
      return;
    }
    if (ui === "partial") {
      display.textContent = "";
      const g = document.createElement("div");
      g.className = "grid";
      g.style.gridTemplateColumns = `repeat(${trial.cols}, 40px)`;
      (trial.grid || []).forEach((ch) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = ch;
        b.disabled = true;
        g.appendChild(b);
      });
      stage.appendChild(g);
      later(trial.encode_ms || 200, () => {
        stage.querySelectorAll("button").forEach((b, idx) => {
          const r = Math.floor(idx / trial.cols);
          b.textContent = "·";
          if (r === trial.cue_row) b.style.outline = "2px solid #f5c542";
        });
        display.textContent = `Row ${trial.cue_row + 1}`;
        const pad = document.createElement("div");
        pad.className = "actions";
        "BCDFGHJKLMNPRSTVWXZ".split("").slice(0, 18).forEach((L) => {
          const b = document.createElement("button");
          b.type = "button";
          b.className = "btn elev";
          b.textContent = L;
          b.onclick = () => sendAnswer(L, { keepUI: true });
          pad.appendChild(b);
        });
        actions.appendChild(pad);
      });
      return;
    }
    if (ui === "conjunction") {
      const g = document.createElement("div");
      g.className = "grid";
      g.style.gridTemplateColumns = `repeat(${trial.cols || 4}, 48px)`;
      (trial.items || []).forEach((it, i) => {
        const b = document.createElement("button");
        b.type = "button";
        b.textContent = it.shape;
        b.style.color = it.color;
        b.onclick = () => sendAnswer(String(i));
        g.appendChild(b);
      });
      stage.appendChild(g);
      const ab = document.createElement("button");
      ab.type = "button";
      ab.className = "btn coral";
      ab.textContent = "NOT PRESENT";
      ab.onclick = () => sendAnswer("absent");
      actions.appendChild(ab);
      return;
    }
    // multi / left_right / stroop / yes_no / same_diff generic
    if (ui === "multi" || ui === "left_right" || ui === "stroop" || ui === "yes_no" || ui === "same_diff") {
      fillActions(trial.actions || []);
      return;
    }
    fillActions(trial.actions || [{ id: "ok", label: "OK" }]);
  }

  function playFocus(trial) {
    const prompt = $("#playPrompt");
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    display.className = "display quiet";
    display.textContent = "";
    actions.innerHTML = "";
    prompt.textContent = "Watch…";
    stage.innerHTML = `<div class="focus-fix">+</div>`;
    let responded = false;

    const finish = (action) => {
      if (responded) return;
      responded = true;
      clearTimers();
      sendAnswer(action);
    };

    later(trial.isi_ms || 500, () => {
      if (responded) return;
      const go = !!trial.is_go;
      prompt.textContent = "TAP green · HOLD on red";
      stage.innerHTML = "";
      const stim = document.createElement("div");
      stim.className = "focus-stim " + (go ? "go" : "nogo");
      stim.textContent = go ? "●" : "■";
      stim.onclick = () => finish("tap");
      stage.appendChild(stim);
      // keyboard like desktop
      const onKey = (e) => {
        if (e.code === "Space" || e.code === "Enter") {
          e.preventDefault();
          finish("tap");
        }
      };
      window.addEventListener("keydown", onKey, { once: true });
      later(trial.stimulus_ms || 800, () => finish(go ? "timeout" : "hold"));
    });
  }

  function playNback(trial) {
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    display.className = "display quiet";
    display.textContent = "";
    stage.innerHTML = "";
    const card = document.createElement("div");
    card.className = "nback-card";
    card.textContent = trial.display || trial.letter || "?";
    stage.appendChild(card);
    if (trial.history && trial.history.length > 1 && (trial.n || 2) <= 3) {
      const trail = document.createElement("div");
      trail.className = "muted small";
      trail.style.marginTop = "8px";
      trail.textContent = "Recent: " + trial.history.slice(-(trial.n + 2)).join(" → ");
      stage.appendChild(trail);
    }
    fillActions([
      { id: "match", label: "MATCH" },
      { id: "nomatch", label: "NO MATCH" },
    ]);
    if (trial.stim_ms) {
      later(trial.stim_ms, () => sendAnswer("timeout"));
    }
  }

  function playSwitch(trial) {
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    display.className = "display quiet";
    display.textContent = `Target  ${trial.target_shape || ""}   ${trial.target_color_name || ""}`;
    stage.innerHTML = "";
    const chip = document.createElement("div");
    chip.className = "target-chip";
    chip.style.background = trial.target_color || "#6c8cff";
    chip.textContent = trial.target_shape || "●";
    stage.appendChild(chip);
    const grid = document.createElement("div");
    grid.className = "option-grid";
    const opts = trial.options_rich || [];
    if (opts.length) {
      opts.forEach((o, i) => {
        const card = document.createElement("button");
        card.type = "button";
        card.className = "opt-card";
        card.innerHTML = `<div class="dot" style="background:${o.color}">${o.shape}</div><div class="lbl">${o.name || ""}</div>`;
        card.onclick = () => sendAnswer(String(i));
        grid.appendChild(card);
      });
      stage.appendChild(grid);
    } else {
      fillActions(trial.actions || []);
    }
  }

  function playSpeed(trial) {
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    const t0 = performance.now();
    display.className = "display quiet";
    display.textContent = "Find this symbol";
    stage.innerHTML = "";
    actions.innerHTML = "";
    const chip = document.createElement("div");
    chip.className = "target-chip sym";
    chip.textContent = trial.display || trial.target || "?";
    stage.appendChild(chip);
    const opts = trial.options || (trial.actions || []).map((a) => a.id);
    const grid = document.createElement("div");
    grid.className = "option-grid" + (opts.length > 4 ? " cols3" : "");
    opts.forEach((sym) => {
      const s = typeof sym === "string" ? sym : sym.label || sym.id;
      const card = document.createElement("button");
      card.type = "button";
      card.className = "opt-card";
      card.innerHTML = `<div class="dot" style="background:#243052;color:#e8eef9;border-radius:12px;font-size:28px">${s}</div>`;
      card.onclick = () => {
        const elapsed = (performance.now() - t0) / 1000;
        sendAnswer(s, { elapsed });
      };
      grid.appendChild(card);
    });
    stage.appendChild(grid);
    const limit = (trial.time_limit || 2.5) * 1000;
    later(limit, () => sendAnswer("", { elapsed: trial.time_limit || 2.5 }));
  }

  function playMemory(trial) {
    const display = $("#playDisplay");
    const stage = $("#playStage");
    display.textContent = "Watch the pattern…";
    stage.innerHTML = "";
    const tiles = document.createElement("div");
    tiles.className = "seq-tiles";
    const btns = [];
    const n = trial.n_tiles || (trial.tiles && trial.tiles.length) || 4;
    for (let i = 0; i < n; i++) {
      const b = document.createElement("button");
      b.type = "button";
      const color = (trial.tiles && trial.tiles[i] && trial.tiles[i].color) || "#6C8CFF";
      b.style.background = color;
      b.textContent = String(i + 1);
      b.disabled = true;
      b.onclick = () => {
        b.classList.add("flash");
        later(120, () => b.classList.remove("flash"));
        sendAnswer(String(i), { keepUI: true }).then((res) => {
          if (res && !res.partial && res.trial) {
            later(280, () => renderTrial(res.trial));
          } else if (res && res.done) {
            showResult(res);
          }
        });
      };
      tiles.appendChild(b);
      btns.push(b);
    }
    stage.appendChild(tiles);
    let step = 0;
    const flash = () => {
      if (step >= trial.sequence.length) {
        display.textContent = "Your turn — tap the order";
        btns.forEach((b) => (b.disabled = false));
        return;
      }
      const idx = trial.sequence[step++];
      btns[idx].classList.add("flash");
      later(trial.flash_ms || 500, () => {
        btns[idx].classList.remove("flash");
        later(180, flash);
      });
    };
    later(600, flash);
  }

  async function playOpspan(trial) {
    const items = trial.items || [];
    let i = 0;
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    const nextMath = async () => {
      if (i >= items.length) {
        display.textContent = "Recall letters in order";
        stage.innerHTML = "";
        actions.innerHTML = "";
        const picked = [];
        const pool = Array.from(
          new Set([...(trial.target_letters || []), ..."FHJKLNPQRSTY".split("")])
        ).slice(0, 12);
        pool.forEach((L) => {
          const b = document.createElement("button");
          b.type = "button";
          b.className = "btn elev";
          b.textContent = L;
          b.onclick = async () => {
            picked.push(L);
            setFeedback({ good: true, message: picked.join(" ") });
            if (picked.length >= (trial.target_letters || []).length) {
              const data = await api("/api/play/answer", {
                method: "POST",
                body: JSON.stringify({
                  session_id: state.sessionId,
                  phase: "recall",
                  data: picked,
                  action: "recall",
                }),
              });
              setFeedback(data.event);
              updateHud(data);
              if (data.done) showResult(data);
              else if (data.trial) later(400, () => renderTrial(data.trial));
            }
          };
          actions.appendChild(b);
        });
        return;
      }
      const it = items[i];
      display.textContent = it.expression;
      stage.innerHTML = "";
      actions.innerHTML = "";
      it.options.forEach((o) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn primary";
        b.textContent = String(o);
        b.onclick = async () => {
          await api("/api/play/answer", {
            method: "POST",
            body: JSON.stringify({
              session_id: state.sessionId,
              phase: "math",
              action: String(o),
            }),
          });
          display.textContent = it.letter;
          actions.innerHTML = "";
          later(800, async () => {
            await api("/api/play/answer", {
              method: "POST",
              body: JSON.stringify({
                session_id: state.sessionId,
                phase: "letter",
                action: "ack",
              }),
            });
            i++;
            nextMath();
          });
        };
        actions.appendChild(b);
      });
    };
    nextMath();
  }

  function playTrack(trial) {
    const display = $("#playDisplay");
    const stage = $("#playStage");
    const actions = $("#playActions");
    display.textContent = "Watch targets…";
    stage.innerHTML = "";
    actions.innerHTML = "";
    const canvas = document.createElement("canvas");
    canvas.width = 300;
    canvas.height = 260;
    canvas.style.background = "#1c2540";
    canvas.style.borderRadius = "12px";
    canvas.style.width = "100%";
    stage.appendChild(canvas);
    const ctx = canvas.getContext("2d");
    const n = trial.n_objects || 4;
    const targets = new Set(trial.targets || []);
    const paths = trial.paths || [];
    let step = 0;
    const maxStep = trial.move_steps || 6;
    function draw(highlight) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let i = 0; i < n; i++) {
        const path = paths[i] || [[0.5, 0.5]];
        const pt = path[Math.min(step, path.length - 1)];
        const x = pt[0] * canvas.width;
        const y = pt[1] * canvas.height;
        ctx.beginPath();
        ctx.arc(x, y, 12, 0, Math.PI * 2);
        ctx.fillStyle = highlight && targets.has(i) ? "#f5c542" : "#8fa6ff";
        ctx.fill();
      }
    }
    draw(true);
    later(trial.flash_ms || 800, () => {
      display.textContent = "Tracking…";
      const iv = setInterval(() => {
        step++;
        draw(false);
        if (step >= maxStep) {
          clearInterval(iv);
          display.textContent = "Tap targets, then Submit";
          const selected = new Set();
          canvas.onclick = (ev) => {
            const rect = canvas.getBoundingClientRect();
            const mx = ((ev.clientX - rect.left) / rect.width) * canvas.width;
            const my = ((ev.clientY - rect.top) / rect.height) * canvas.height;
            for (let i = 0; i < n; i++) {
              const path = paths[i] || [[0.5, 0.5]];
              const pt = path[path.length - 1];
              const x = pt[0] * canvas.width;
              const y = pt[1] * canvas.height;
              if ((mx - x) ** 2 + (my - y) ** 2 < 400) {
                if (selected.has(i)) selected.delete(i);
                else selected.add(i);
              }
            }
            draw(false);
            for (let i of selected) {
              const path = paths[i] || [[0.5, 0.5]];
              const pt = path[path.length - 1];
              ctx.beginPath();
              ctx.arc(pt[0] * canvas.width, pt[1] * canvas.height, 12, 0, Math.PI * 2);
              ctx.fillStyle = "#f5c542";
              ctx.fill();
            }
          };
          const sub = document.createElement("button");
          sub.type = "button";
          sub.className = "btn primary";
          sub.textContent = "Submit";
          sub.onclick = () =>
            sendAnswer("submit", {
              data: Array.from(selected),
              selected: Array.from(selected),
            });
          actions.appendChild(sub);
        }
      }, trial.step_ms || 200);
      state.timers.push(iv);
    });
  }

  // Wire navigation
  $("#btnDaily").onclick = () => startDaily();
  $("#btnFull").onclick = () => startFull();
  $("#btnModes").onclick = () => loadModes().catch((e) => alert(e.message));
  $("#btnProgress").onclick = () => loadProgress().catch((e) => alert(e.message));
  $("#btnPro").onclick = () => loadPro();
  $("#btnSettings").onclick = () => {
    syncSoundButtons();
    loadNotifSettings();
    show("settings");
  };
  if ($("#btnPushEnable")) $("#btnPushEnable").onclick = () => enablePush();
  if ($("#btnPushTest")) $("#btnPushTest").onclick = () => testPush();
  if ($("#btnSaveNotif")) $("#btnSaveNotif").onclick = () => saveNotifSettings();
  if ($("#n_quiet")) {
    $("#n_quiet").onchange = () => {
      $("#quietRow").classList.toggle("hidden", !$("#n_quiet").checked);
    };
  }
  $("#btnSound").onclick = () => toggleSound();
  $("#btnSound2").onclick = () => toggleSound();
  $("#btnRename").onclick = () => renamePlayer();
  $("#btnQuitPlay").onclick = () => {
    clearTimers();
    state.sessionId = null;
    state.circuit = [];
    loadHome();
  };
  $("#btnAgain").onclick = () => {
    if (state.lastMode) {
      const meta = (state.modesCache?.modes || []).find((m) => m.key === state.lastMode);
      startPlay(state.lastMode, meta?.title || state.lastMode, meta?.level);
    }
  };
  $("#buyMonth").onclick = () => buy("monthly");
  $("#buyYear").onclick = () => buy("yearly");
  $("#buyLife").onclick = () => buy("lifetime");
  $("#btnRestore").onclick = () => buy("restore");
  $$("[data-go]").forEach((b) => {
    b.onclick = () => {
      const dest = b.getAttribute("data-go");
      if (dest === "home") loadHome();
      else show(dest);
    };
  });

  // Boot: language → home
  (async () => {
    try {
      await loadI18n(state.lang);
      fillLangSelects();
    } catch (_) {}
    await loadHome();
  })();
  // Mobile-first push (iPhone / Android / PWA)
  if (window.NFPush) {
    NFPush.init().then(() => {
      /* ready */
    });
  }
})();
