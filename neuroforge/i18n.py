"""
Multi-language support for NeuroForge.

Usage:
    from neuroforge.i18n import t, set_language, get_language, LANGUAGES

    set_language("es")
    label = t("home.train")
"""

from __future__ import annotations

from typing import Any

# code -> (native name, English name)
LANGUAGES: dict[str, tuple[str, str]] = {
    "en": ("English", "English"),
    "es": ("Español", "Spanish"),
    "fr": ("Français", "French"),
    "de": ("Deutsch", "German"),
    "pt": ("Português", "Portuguese"),
    "it": ("Italiano", "Italian"),
    "nl": ("Nederlands", "Dutch"),
    "pl": ("Polski", "Polish"),
    "ru": ("Русский", "Russian"),
    "uk": ("Українська", "Ukrainian"),
    "tr": ("Türkçe", "Turkish"),
    "sv": ("Svenska", "Swedish"),
    "no": ("Norsk", "Norwegian"),
    "da": ("Dansk", "Danish"),
    "fi": ("Suomi", "Finnish"),
    "el": ("Ελληνικά", "Greek"),
    "cs": ("Čeština", "Czech"),
    "ro": ("Română", "Romanian"),
    "hu": ("Magyar", "Hungarian"),
    "zh": ("中文", "Chinese"),
    "ja": ("日本語", "Japanese"),
    "ko": ("한국어", "Korean"),
    "hi": ("हिन्दी", "Hindi"),
    "bn": ("বাংলা", "Bengali"),
    "ta": ("தமிழ்", "Tamil"),
    "te": ("తెలుగు", "Telugu"),
    "mr": ("मराठी", "Marathi"),
    "gu": ("ગુજરાતી", "Gujarati"),
    "pa": ("ਪੰਜਾਬੀ", "Punjabi"),
    "ar": ("العربية", "Arabic"),
    "he": ("עברית", "Hebrew"),
    "fa": ("فارسی", "Persian"),
    "ur": ("اردو", "Urdu"),
    "id": ("Bahasa Indonesia", "Indonesian"),
    "ms": ("Bahasa Melayu", "Malay"),
    "th": ("ไทย", "Thai"),
    "vi": ("Tiếng Việt", "Vietnamese"),
    "tl": ("Tagalog", "Filipino"),
    "sw": ("Kiswahili", "Swahili"),
}

_current = "en"


def _merge_pack(base: dict[str, dict[str, str]], pack: dict[str, dict[str, str]]) -> None:
    """Overlay pack translations onto base (pack wins for each lang)."""
    for key, langs in pack.items():
        block = base.setdefault(key, {})
        block.update(langs)


# UI strings: key -> {lang: text}
# English is the source; missing keys fall back to en.
# Full multi-language pack is merged below after STRINGS is defined.
STRINGS: dict[str, dict[str, str]] = {
    "app.title": {
        "en": "NeuroForge — Brain Training",
        "es": "NeuroForge — Entrenamiento cerebral",
        "fr": "NeuroForge — Entraînement cérébral",
        "de": "NeuroForge — Gehirntraining",
        "pt": "NeuroForge — Treino cerebral",
        "zh": "NeuroForge — 大脑训练",
        "ja": "NeuroForge — 脳トレ",
        "hi": "NeuroForge — मस्तिष्क प्रशिक्षण",
        "ar": "NeuroForge — تدريب الدماغ",
        "ko": "NeuroForge — 두뇌 훈련",
    },
    "home.tagline": {
        "en": "Rewire. Adapt. Grow.",
        "es": "Reconecta. Adapta. Crece.",
        "fr": "Recâblez. Adaptez. Grandissez.",
        "de": "Umverdrahten. Anpassen. Wachsen.",
        "pt": "Reconecte. Adapte. Cresça.",
        "zh": "重塑。适应。成长。",
        "ja": "再配線。適応。成長。",
        "hi": "रीवायर। अनुकूलित। बढ़ें।",
        "ar": "أعد التوصيل. تكيّف. انمُ.",
        "ko": "재배선. 적응. 성장.",
    },
    "home.subtitle": {
        "en": "{n} research drills · Adaptive Difficulty Engine",
        "es": "{n} ejercicios de investigación · Dificultad adaptativa",
        "fr": "{n} exercices de recherche · Difficulté adaptative",
        "de": "{n} Forschungsübungen · Adaptive Schwierigkeit",
        "pt": "{n} exercícios de pesquisa · Dificuldade adaptativa",
        "zh": "{n} 项研究训练 · 自适应难度",
        "ja": "{n} の研究ドリル · 適応難易度",
        "hi": "{n} शोध ड्रिल · अनुकूली कठिनाई",
        "ar": "{n} تمارين بحثية · صعوبة متكيفة",
        "ko": "{n}개 연구 드릴 · 적응형 난이도",
    },
    "home.daily": {
        "en": "▶  Daily Circuit  (5 modes)",
        "es": "▶  Circuito diario  (5 modos)",
        "fr": "▶  Circuit quotidien  (5 modes)",
        "de": "▶  Tägliche Runde  (5 Modi)",
        "pt": "▶  Circuito diário  (5 modos)",
        "zh": "▶  每日回路  (5 种模式)",
        "ja": "▶  デイリーサーキット  (5モード)",
        "hi": "▶  दैनिक सर्किट  (5 मोड)",
        "ar": "▶  الدائرة اليومية  (5 أوضاع)",
        "ko": "▶  일일 서킷  (5모드)",
    },
    "home.full_gym": {
        "en": "Full Gym  (all {n} modes)",
        "es": "Gimnasio completo  (los {n} modos)",
        "fr": "Salle complète  (tous les {n} modes)",
        "de": "Volles Gym  (alle {n} Modi)",
        "pt": "Academia completa  (todos os {n} modos)",
        "zh": "完整训练馆  (全部 {n} 模式)",
        "ja": "フルジム  (全{n}モード)",
        "hi": "पूर्ण जिम  (सभी {n} मोड)",
        "ar": "الصالة الكاملة  (كل {n} أوضاع)",
        "ko": "전체 체육관  (전체 {n}모드)",
    },
    "home.full_gym_pro": {
        "en": "Full Gym  (Pro)",
        "es": "Gimnasio completo  (Pro)",
        "fr": "Salle complète  (Pro)",
        "de": "Volles Gym  (Pro)",
        "pt": "Academia completa  (Pro)",
        "zh": "完整训练馆  (Pro)",
        "ja": "フルジム  (Pro)",
        "hi": "पूर्ण जिम  (Pro)",
        "ar": "الصالة الكاملة  (Pro)",
        "ko": "전체 체육관  (Pro)",
    },
    "home.train": {
        "en": "Train a single skill",
        "es": "Entrenar una habilidad",
        "fr": "Entraîner une compétence",
        "de": "Eine Fähigkeit trainieren",
        "pt": "Treinar uma habilidade",
        "zh": "训练单项技能",
        "ja": "単一スキルを鍛える",
        "hi": "एक कौशल प्रशिक्षित करें",
        "ar": "تدريب مهارة واحدة",
        "ko": "단일 기술 훈련",
    },
    "home.pro": {
        "en": "⭐  Go Pro  ·  Plans & pricing",
        "es": "⭐  Hazte Pro  ·  Planes y precios",
        "fr": "⭐  Passer Pro  ·  Formules et tarifs",
        "de": "⭐  Pro werden  ·  Pläne & Preise",
        "pt": "⭐  Seja Pro  ·  Planos e preços",
        "zh": "⭐  升级 Pro  ·  方案与价格",
        "ja": "⭐  Proにする  ·  プランと料金",
        "hi": "⭐  Pro बनें  ·  योजना और मूल्य",
        "ar": "⭐  انتقل إلى Pro  ·  الخطط والأسعار",
        "ko": "⭐  Pro 업그레이드  ·  요금제",
    },
    "home.progress": {
        "en": "Progress & science",
        "es": "Progreso y ciencia",
        "fr": "Progrès et science",
        "de": "Fortschritt & Wissenschaft",
        "pt": "Progresso e ciência",
        "zh": "进度与科学",
        "ja": "進捗と科学",
        "hi": "प्रगति और विज्ञान",
        "ar": "التقدم والعلم",
        "ko": "진행과 과학",
    },
    "home.sound_on": {
        "en": "Sound & haptics: ON",
        "es": "Sonido y háptica: ON",
        "fr": "Son et haptique : ON",
        "de": "Ton & Haptik: AN",
        "pt": "Som e háptica: ON",
        "zh": "声音与触感：开",
        "ja": "音と触覚：オン",
        "hi": "ध्वनि और हैप्टिक्स: चालू",
        "ar": "الصوت واللمس: تشغيل",
        "ko": "사운드 및 햅틱: 켜짐",
    },
    "home.sound_off": {
        "en": "Sound & haptics: OFF",
        "es": "Sonido y háptica: OFF",
        "fr": "Son et haptique : OFF",
        "de": "Ton & Haptik: AUS",
        "pt": "Som e háptica: OFF",
        "zh": "声音与触感：关",
        "ja": "音と触覚：オフ",
        "hi": "ध्वनि और हैप्टिक्स: बंद",
        "ar": "الصوت واللمس: إيقاف",
        "ko": "사운드 및 햅틱: 꺼짐",
    },
    "home.language": {
        "en": "Language",
        "es": "Idioma",
        "fr": "Langue",
        "de": "Sprache",
        "pt": "Idioma",
        "zh": "语言",
        "ja": "言語",
        "hi": "भाषा",
        "ar": "اللغة",
        "ko": "언어",
    },
    "home.notifications": {
        "en": "Notifications",
        "es": "Notificaciones",
        "fr": "Notifications",
        "de": "Benachrichtigungen",
        "pt": "Notificações",
        "zh": "通知",
        "ja": "通知",
        "hi": "सूचनाएं",
        "ar": "الإشعارات",
        "ko": "알림",
    },
    "home.settings": {
        "en": "Settings · Language & alerts",
        "es": "Ajustes · Idioma y alertas",
        "fr": "Réglages · Langue et alertes",
        "de": "Einstellungen · Sprache & Hinweise",
        "pt": "Definições · Idioma e alertas",
        "zh": "设置 · 语言与提醒",
        "ja": "設定 · 言語と通知",
        "hi": "सेटिंग्स · भाषा और अलर्ट",
        "ar": "الإعدادات · اللغة والتنبيهات",
        "ko": "설정 · 언어 및 알림",
    },
    "home.player": {
        "en": "Player: {name}  ·  v{version}",
        "es": "Jugador: {name}  ·  v{version}",
        "fr": "Joueur : {name}  ·  v{version}",
        "de": "Spieler: {name}  ·  v{version}",
        "pt": "Jogador: {name}  ·  v{version}",
        "zh": "玩家：{name}  ·  v{version}",
        "ja": "プレイヤー: {name}  ·  v{version}",
        "hi": "खिलाड़ी: {name}  ·  v{version}",
        "ar": "اللاعب: {name}  ·  v{version}",
        "ko": "플레이어: {name}  ·  v{version}",
    },
    "home.edit_name": {
        "en": "Edit name",
        "es": "Editar nombre",
        "fr": "Modifier le nom",
        "de": "Name ändern",
        "pt": "Editar nome",
        "zh": "编辑名称",
        "ja": "名前を編集",
        "hi": "नाम संपादित करें",
        "ar": "تعديل الاسم",
        "ko": "이름 수정",
    },
    "home.streak": {
        "en": "Streak {n} day(s)  ·  Best {best}  ·  {sessions} sessions",
        "es": "Racha {n} día(s)  ·  Mejor {best}  ·  {sessions} sesiones",
        "fr": "Série {n} jour(s)  ·  Record {best}  ·  {sessions} sessions",
        "de": "Serie {n} Tag(e)  ·  Best {best}  ·  {sessions} Sitzungen",
        "pt": "Sequência {n} dia(s)  ·  Melhor {best}  ·  {sessions} sessões",
        "zh": "连续 {n} 天  ·  最佳 {best}  ·  {sessions} 次训练",
        "ja": "連続 {n} 日  ·  最高 {best}  ·  {sessions} セッション",
        "hi": "स्ट्रीक {n} दिन  ·  सर्वश्रेष्ठ {best}  ·  {sessions} सत्र",
        "ar": "سلسلة {n} يوم  ·  الأفضل {best}  ·  {sessions} جلسة",
        "ko": "연속 {n}일  ·  최고 {best}  ·  {sessions}회",
    },
    "back": {
        "en": "← Back",
        "es": "← Atrás",
        "fr": "← Retour",
        "de": "← Zurück",
        "pt": "← Voltar",
        "zh": "← 返回",
        "ja": "← 戻る",
        "hi": "← वापस",
        "ar": "→ رجوع",
        "ko": "← 뒤로",
    },
    "start": {
        "en": "Start",
        "es": "Empezar",
        "fr": "Démarrer",
        "de": "Start",
        "pt": "Iniciar",
        "zh": "开始",
        "ja": "スタート",
        "hi": "शुरू",
        "ar": "ابدأ",
        "ko": "시작",
    },
    "unlock_pro": {
        "en": "Unlock with Pro",
        "es": "Desbloquear con Pro",
        "fr": "Débloquer avec Pro",
        "de": "Mit Pro freischalten",
        "pt": "Desbloquear com Pro",
        "zh": "用 Pro 解锁",
        "ja": "Proで解除",
        "hi": "Pro से अनलॉक",
        "ar": "فتح مع Pro",
        "ko": "Pro로 잠금 해제",
    },
    "choose_skill": {
        "en": "Choose a skill",
        "es": "Elige una habilidad",
        "fr": "Choisir une compétence",
        "de": "Fähigkeit wählen",
        "pt": "Escolha uma habilidade",
        "zh": "选择技能",
        "ja": "スキルを選択",
        "hi": "कौशल चुनें",
        "ar": "اختر مهارة",
        "ko": "기술 선택",
    },
    "lang.title": {
        "en": "Language",
        "es": "Idioma",
        "fr": "Langue",
        "de": "Sprache",
        "pt": "Idioma",
        "zh": "语言",
        "ja": "言語",
        "hi": "भाषा",
        "ar": "اللغة",
        "ko": "언어",
    },
    "lang.hint": {
        "en": "Select your language. The interface updates immediately.",
        "es": "Elige tu idioma. La interfaz se actualiza al instante.",
        "fr": "Choisissez votre langue. L’interface se met à jour aussitôt.",
        "de": "Sprache wählen. Die Oberfläche aktualisiert sich sofort.",
        "pt": "Escolha o idioma. A interface atualiza na hora.",
        "zh": "选择语言。界面会立即更新。",
        "ja": "言語を選択。画面はすぐに切り替わります。",
        "hi": "अपनी भाषा चुनें। इंटरफ़ेस तुरंत अपडेट होगा।",
        "ar": "اختر لغتك. تتحدث الواجهة فورًا.",
        "ko": "언어를 선택하세요. 인터페이스가 바로 바뀝니다.",
    },
    "notif.title": {
        "en": "Push notifications",
        "es": "Notificaciones push",
        "fr": "Notifications push",
        "de": "Push-Benachrichtigungen",
        "pt": "Notificações push",
        "zh": "推送通知",
        "ja": "プッシュ通知",
        "hi": "पुश सूचनाएं",
        "ar": "إشعارات الدفع",
        "ko": "푸시 알림",
    },
    "notif.enabled": {
        "en": "Reminders: ON",
        "es": "Recordatorios: ON",
        "fr": "Rappels : ON",
        "de": "Erinnerungen: AN",
        "pt": "Lembretes: ON",
        "zh": "提醒：开",
        "ja": "リマインダー：オン",
        "hi": "अनुस्मारक: चालू",
        "ar": "التذكيرات: تشغيل",
        "ko": "리마인더: 켜짐",
    },
    "notif.disabled": {
        "en": "Reminders: OFF",
        "es": "Recordatorios: OFF",
        "fr": "Rappels : OFF",
        "de": "Erinnerungen: AUS",
        "pt": "Lembretes: OFF",
        "zh": "提醒：关",
        "ja": "リマインダー：オフ",
        "hi": "अनुस्मारक: बंद",
        "ar": "التذكيرات: إيقاف",
        "ko": "리마인더: 꺼짐",
    },
    "notif.daily": {
        "en": "Daily training reminder",
        "es": "Recordatorio diario de entrenamiento",
        "fr": "Rappel d’entraînement quotidien",
        "de": "Tägliche Trainingserinnerung",
        "pt": "Lembrete diário de treino",
        "zh": "每日训练提醒",
        "ja": "毎日のトレーニング通知",
        "hi": "दैनिक प्रशिक्षण अनुस्मारक",
        "ar": "تذكير التدريب اليومي",
        "ko": "매일 훈련 알림",
    },
    "notif.streak": {
        "en": "Streak risk alerts",
        "es": "Alertas de racha en riesgo",
        "fr": "Alertes de série en danger",
        "de": "Serien-Warnungen",
        "pt": "Alertas de sequência em risco",
        "zh": "连续天数风险提醒",
        "ja": "連続記録の危機アラート",
        "hi": "स्ट्रीक जोखिम अलर्ट",
        "ar": "تنبيهات خطر السلسلة",
        "ko": "연속 기록 위험 알림",
    },
    "notif.test": {
        "en": "Send test notification",
        "es": "Enviar notificación de prueba",
        "fr": "Envoyer une notification test",
        "de": "Testbenachrichtigung senden",
        "pt": "Enviar notificação de teste",
        "zh": "发送测试通知",
        "ja": "テスト通知を送る",
        "hi": "परीक्षण सूचना भेजें",
        "ar": "إرسال إشعار تجريبي",
        "ko": "테스트 알림 보내기",
    },
    "notif.test_title": {
        "en": "NeuroForge",
        "es": "NeuroForge",
        "fr": "NeuroForge",
        "de": "NeuroForge",
        "pt": "NeuroForge",
        "zh": "NeuroForge",
        "ja": "NeuroForge",
        "hi": "NeuroForge",
        "ar": "NeuroForge",
        "ko": "NeuroForge",
    },
    "notif.test_body": {
        "en": "Notifications work! Time for a 2-minute brain drill?",
        "es": "¡Las notificaciones funcionan! ¿Un ejercicio de 2 minutos?",
        "fr": "Les notifications marchent ! Un exercice de 2 minutes ?",
        "de": "Benachrichtigungen funktionieren! 2-Minuten-Drill?",
        "pt": "As notificações funcionam! Um treino de 2 minutos?",
        "zh": "通知可用！来一次 2 分钟训练？",
        "ja": "通知は動作中！2分ドリルはどう？",
        "hi": "सूचनाएं काम कर रही हैं! 2 मिनट का ड्रिल?",
        "ar": "الإشعارات تعمل! تمرين لدقيقتين؟",
        "ko": "알림이 작동합니다! 2분 드릴 할까요?",
    },
    "notif.daily_title": {
        "en": "Daily brain training",
        "es": "Entrenamiento diario",
        "fr": "Entraînement quotidien",
        "de": "Tägliches Gehirntraining",
        "pt": "Treino cerebral diário",
        "zh": "每日大脑训练",
        "ja": "毎日の脳トレ",
        "hi": "दैनिक मस्तिष्क प्रशिक्षण",
        "ar": "التدريب اليومي للدماغ",
        "ko": "매일 두뇌 훈련",
    },
    "notif.daily_body": {
        "en": "Keep your streak alive — a short session builds plasticity.",
        "es": "Mantén tu racha — una sesión corta construye plasticidad.",
        "fr": "Gardez votre série — une courte session renforce la plasticité.",
        "de": "Serie halten — kurze Sessions stärken Plastizität.",
        "pt": "Mantenha a sequência — uma sessão curta ajuda a plasticidade.",
        "zh": "保持连续天数——短训练有助可塑性。",
        "ja": "連続を守ろう — 短いセッションが可塑性を育てます。",
        "hi": "अपनी स्ट्रीक बनाए रखें — छोटा सत्र प्लास्टिसिटी बढ़ाता है।",
        "ar": "حافظ على سلسلتك — جلسة قصيرة تبني اللدونة.",
        "ko": "연속 기록을 지키세요 — 짧은 세션이 가소성을 키웁니다.",
    },
    "notif.streak_title": {
        "en": "Streak at risk!",
        "es": "¡Racha en riesgo!",
        "fr": "Série en danger !",
        "de": "Serie in Gefahr!",
        "pt": "Sequência em risco!",
        "zh": "连续天数有风险！",
        "ja": "連続記録の危機！",
        "hi": "स्ट्रीक खतरे में!",
        "ar": "السلسلة في خطر!",
        "ko": "연속 기록이 위험합니다!",
    },
    "notif.streak_body": {
        "en": "You haven't trained today. One quick drill keeps your streak.",
        "es": "Hoy no has entrenado. Un ejercicio rápido salva tu racha.",
        "fr": "Pas d’entraînement aujourd’hui. Un drill rapide sauve la série.",
        "de": "Heute noch nicht trainiert. Ein Drill rettet die Serie.",
        "pt": "Ainda não treinou hoje. Um drill rápido salva a sequência.",
        "zh": "今天还没训练。一次快速练习可保住连续。",
        "ja": "今日は未トレーニング。短いドリルで連続を守れます。",
        "hi": "आज प्रशिक्षण नहीं हुआ। एक छोटा ड्रिल स्ट्रीक बचाएगा।",
        "ar": "لم تتدرب اليوم. تمرين سريع يحفظ سلسلتك.",
        "ko": "오늘 아직 훈련하지 않았습니다. 짧은 드릴로 연속을 지키세요.",
    },

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
    "session.complete": {
        "en": "Session complete",
        "es": "Sesión completada",
        "fr": "Session terminée",
        "de": "Sitzung beendet",
        "pt": "Sessão concluída",
        "zh": "训练完成",
        "ja": "セッション完了",
        "hi": "सत्र पूर्ण",
        "ar": "اكتملت الجلسة",
        "ko": "세션 완료",
    },
    "home": {
        "en": "Home",
        "es": "Inicio",
        "fr": "Accueil",
        "de": "Start",
        "pt": "Início",
        "zh": "主页",
        "ja": "ホーム",
        "hi": "होम",
        "ar": "الرئيسية",
        "ko": "홈",
    },
    "disclaimer": {
        "en": "Not a medical device. For entertainment & personal training only.",
        "es": "No es un dispositivo médico. Solo entretenimiento y entrenamiento personal.",
        "fr": "Pas un dispositif médical. Divertissement et entraînement personnel uniquement.",
        "de": "Kein Medizinprodukt. Nur Unterhaltung und persönliches Training.",
        "pt": "Não é dispositivo médico. Apenas entretenimento e treino pessoal.",
        "zh": "非医疗器械。仅供娱乐与个人训练。",
        "ja": "医療機器ではありません。娯楽・個人トレーニング用です。",
        "hi": "चिकित्सा उपकरण नहीं। केवल मनोरंजन और व्यक्तिगत प्रशिक्षण।",
        "ar": "ليس جهازًا طبيًا. للتسلية والتدريب الشخصي فقط.",
        "ko": "의료기기가 아닙니다. 오락 및 개인 훈련 전용입니다.",
    },
    "ad.banner": {
        "en": "  AD  ·  Free plan  ·  Upgrade to remove ads  ",
        "es": "  ANUNCIO  ·  Plan gratis  ·  Mejora para quitar anuncios  ",
        "fr": "  PUB  ·  Offre gratuite  ·  Passez Pro pour retirer les pubs  ",
        "de": "  WERBUNG  ·  Gratis  ·  Pro entfernt Werbung  ",
        "pt": "  ANÚNCIO  ·  Plano grátis  ·  Pro remove anúncios  ",
        "zh": "  广告  ·  免费版  ·  升级可去广告  ",
        "ja": "  広告  ·  無料  ·  Proで広告なし  ",
        "hi": "  विज्ञापन  ·  मुफ़्त  ·  Pro से विज्ञापन हटाएं  ",
        "ar": "  إعلان  ·  مجاني  ·  Pro لإزالة الإعلانات  ",
        "ko": "  광고  ·  무료  ·  Pro로 광고 제거  ",
    },
}

# Merge full 39-language UI pack (home buttons, settings, etc.)
try:
    from neuroforge.i18n_pack import UI_PACK as _UI_PACK

    _merge_pack(STRINGS, _UI_PACK)
except Exception:
    try:
        from .i18n_pack import UI_PACK as _UI_PACK  # type: ignore

        _merge_pack(STRINGS, _UI_PACK)
    except Exception:
        pass

# Mode title translations (fallback: English MODE_META)
MODE_TITLES: dict[str, dict[str, str]] = {
    "focus": {
        "en": "Focus Pulse", "es": "Pulso de enfoque", "fr": "Impulsion focus",
        "de": "Fokus-Puls", "pt": "Pulso de foco", "zh": "专注脉冲",
        "ja": "フォーカスパルス", "hi": "फोकस पल्स", "ar": "نبضة التركيز", "ko": "포커스 펄스",
    },
    "memory": {
        "en": "Memory Lattice", "es": "Red de memoria", "fr": "Treillis mémoire",
        "de": "Gedächtnisgitter", "pt": "Rede de memória", "zh": "记忆网格",
        "ja": "メモリーラティス", "hi": "मेमोरी लैटिस", "ar": "شبكة الذاكرة", "ko": "메모리 격자",
    },
    "nback": {
        "en": "N-Back Lite", "es": "N-Back Lite", "fr": "N-Back Lite",
        "de": "N-Back Lite", "pt": "N-Back Lite", "zh": "N-Back 轻量",
        "ja": "N-Back Lite", "hi": "N-Back Lite", "ar": "N-Back Lite", "ko": "N-Back Lite",
    },
    "speed": {
        "en": "Speed Mirror", "es": "Espejo de velocidad", "fr": "Miroir vitesse",
        "de": "Geschwindigkeitsspiegel", "pt": "Espelho de velocidade", "zh": "速度镜像",
        "ja": "スピードミラー", "hi": "स्पीड मिरर", "ar": "مرآة السرعة", "ko": "스피드 미러",
    },
}


def get_language() -> str:
    return _current


def set_language(code: str) -> str:
    global _current
    if code not in LANGUAGES:
        code = "en"
    _current = code
    return _current


def t(key: str, **kwargs: Any) -> str:
    """Translate key for current language; fall back to English."""
    block = STRINGS.get(key) or {}
    text = block.get(_current) or block.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def _ensure_mode_titles() -> None:
    """Ensure every MODE_META key has a title for every language (en + pack)."""
    try:
        from neuroforge.modes.meta import MODE_META
    except Exception:
        try:
            from .modes.meta import MODE_META  # type: ignore
        except Exception:
            return
    for key, meta in MODE_META.items():
        en = (meta or {}).get("title") or key
        block = MODE_TITLES.setdefault(key, {})
        if "en" not in block:
            block["en"] = en
        # Fill missing languages with English so selection never "fails"
        for code in LANGUAGES:
            block.setdefault(code, block.get("en") or en)


_ensure_mode_titles()


def mode_title(mode_key: str, fallback: str = "") -> str:
    block = MODE_TITLES.get(mode_key) or {}
    return block.get(_current) or block.get("en") or fallback or mode_key


def coverage_report() -> dict[str, Any]:
    """Return per-language completeness for web UI keys (for tests)."""
    web_keys = [
        "home.tagline",
        "home.subtitle",
        "home.daily",
        "home.full_gym",
        "home.full_gym_pro",
        "home.train",
        "home.pro",
        "home.progress",
        "home.sound_on",
        "home.sound_off",
        "home.language",
        "home.settings",
        "home.player",
        "home.streak",
        "choose_skill",
        "start",
        "unlock_pro",
    ]
    report: dict[str, Any] = {"languages": {}, "keys": web_keys}
    for code in LANGUAGES:
        missing = []
        for k in web_keys:
            block = STRINGS.get(k) or {}
            if code not in block:
                missing.append(k)
        report["languages"][code] = {
            "native": LANGUAGES[code][0],
            "complete": len(missing) == 0,
            "missing": missing,
            "sample_tagline": (STRINGS.get("home.tagline") or {}).get(code, ""),
        }
    report["all_complete"] = all(v["complete"] for v in report["languages"].values())
    return report


def language_bar_labels() -> list[tuple[str, str]]:
    """Return (code, short label) for the language selection bar."""
    return [(code, names[0]) for code, names in LANGUAGES.items()]


def language_dropdown_choices() -> list[str]:
    """Labels for a Combobox: 'English (English)', 'Español (Spanish)', …"""
    return [f"{native}  ({en})" for _code, (native, en) in LANGUAGES.items()]


def language_code_from_dropdown(label: str) -> str:
    """Map dropdown label back to language code."""
    label = (label or "").strip()
    for code, (native, en) in LANGUAGES.items():
        if label == f"{native}  ({en})" or label == native or label.startswith(native):
            return code
    # partial match on English name
    low = label.lower()
    for code, (native, en) in LANGUAGES.items():
        if en.lower() in low or native.lower() in low:
            return code
    return "en"


def language_dropdown_label(code: str | None = None) -> str:
    code = code or _current
    native, en = LANGUAGES.get(code, LANGUAGES["en"])
    return f"{native}  ({en})"
