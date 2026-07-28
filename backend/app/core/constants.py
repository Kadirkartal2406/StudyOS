"""
StudyOS — Uygulama Sabitleri
Kod içinde sihirli sayı (magic number) kullanımını önlemek için tüm sabit
değerler burada toplanır. Bkz. docs/project/ai-rules.md §3.2.4
"""

from datetime import date

# ── Dashboard ─────────────────────────────────────────────────
# Student profili (Sprint-3.0) yoksa veya günlük hedef boşsa varsayılan.
DEFAULT_DAILY_STUDY_GOAL_MINUTES = 120

# ── Study Plan ────────────────────────────────────────────────
# İlk plan kaleminin order_index başlangıç değeri; sonraki kalemler
# mevcut en yüksek order_index + 1 olarak atanır.
STUDY_PLAN_INITIAL_ORDER_INDEX = 0

# ── Study Session (Pomodoro) ──────────────────────────────────
# Hazır süre paketleri (odak / mola, dakika). Flutter UI ile senkron tutulur.
POMODORO_PRESET_DURATIONS = (
    (25, 5),
    (50, 10),
    (90, 15),
)
# Planlı odak süresi sınırları (dakika).
STUDY_SESSION_MIN_DURATION_MINUTES = 1
STUDY_SESSION_MAX_DURATION_MINUTES = 240
# Mola süresi sınırları (dakika); 0 = mola yok.
STUDY_SESSION_MIN_BREAK_MINUTES = 0
STUDY_SESSION_MAX_BREAK_MINUTES = 60
# Geçmiş / istatistik sayfalama varsayılanları.
STUDY_SESSION_HISTORY_DEFAULT_PAGE_SIZE = 20
STUDY_SESSION_HISTORY_MAX_PAGE_SIZE = 100

# ── Statistics ────────────────────────────────────────────────
# Plansız (serbest) Pomodoro oturumlarının ders/konu etiketleri.
STATISTICS_FREE_LABEL = "Serbest"
# Heatmap ve son aktivite penceresi (gün).
STATISTICS_HEATMAP_DAYS = 30
# Subject/topic dağılımında dönecek maksimum satır.
STATISTICS_DISTRIBUTION_LIMIT = 20

# ── Activity / Dashboard (Sprint-1.7) ─────────────────────────
DASHBOARD_RECENT_ACTIVITIES_LIMIT = 10

# ── Question Records (Sprint-1.9) ─────────────────────────────
QUESTION_RECORD_DEFAULT_PAGE_SIZE = 20
QUESTION_RECORD_MAX_PAGE_SIZE = 100
# YKS tarzı net cezası: net = correct − wrong × penalty
QUESTION_NET_WRONG_PENALTY = 0.25

# ── AI Insights / Rule Engine (Sprint-2.0) ────────────────────
AI_IDLE_DAYS_THRESHOLD = 3
AI_LOW_ACCURACY_THRESHOLD = 55.0
AI_STUDY_DROP_PCT_THRESHOLD = 20.0
AI_SUBJECT_NEGLECT_ENABLED = True

# ── Goals / Goal Engine (Sprint-2.1) ──────────────────────────
GOAL_MILESTONE_PERCENTS = (25, 50, 75, 100)

# ── AI Chat (Sprint-2.2 / 2.4) ────────────────────────────────
AI_CONTEXT_VERSION = "3"
AI_SYSTEM_PROMPT_VERSION = "v1"
AI_CONTEXT_RECENT_ACTIVITIES = 5
AI_CONTEXT_ACTIVE_GOALS = 5
AI_CONTEXT_HISTORY_MESSAGES = 20
AI_CONTEXT_TODAY_PLANS = 5
AI_CONTEXT_TODAY_SESSIONS = 5
AI_CHAT_TITLE_MAX_LEN = 80

# ── AI Memory (Sprint-2.3) ────────────────────────────────────
AI_CONTEXT_MEMORIES = 8

# ── Exam Tracking (Sprint-2.6) ────────────────────────────────
EXAM_MILESTONE_FIRST = 1
EXAM_MILESTONE_TENTH = 10
AI_CONTEXT_EXAMS = 5

# ── Adaptive Planner (Sprint-2.7) ─────────────────────────────
# Legacy generic fallback — ASLA doğrudan kullanma; exam-aware helper kullan.
PLANNER_FALLBACK_SUBJECTS = ("Matematik", "Türkçe", "Fen", "Sosyal")
PLANNER_FALLBACK_BY_EXAM: dict[str, tuple[str, ...]] = {
    "kpss": (
        "Türkçe",
        "Matematik",
        "Tarih",
        "Coğrafya",
        "Vatandaşlık",
        "Güncel Bilgiler",
    ),
    "yks": (
        "Türkçe",
        "Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Tarih",
        "Coğrafya",
    ),
    "tyt": (
        "Türkçe",
        "Matematik",
        "Geometri",
        "Fizik",
        "Kimya",
        "Biyoloji",
        "Tarih",
        "Coğrafya",
    ),
    "ayt": ("Matematik", "Geometri", "Fizik", "Kimya", "Biyoloji"),
    "lgs": (
        "Türkçe",
        "Matematik",
        "Fen Bilimleri",
        "İnkılap Tarihi",
        "Din Kültürü",
        "İngilizce",
    ),
    "ales": ("Sözel", "Sayısal"),
    "yds": ("Kelime", "Gramer", "Okuma", "Çeviri"),
    "dgs": ("Türkçe", "Matematik"),
    "ags": (
        "Türkçe",
        "Matematik",
        "Tarih",
        "Coğrafya",
        "Vatandaşlık",
        "Güncel Bilgiler",
    ),
}
PLANNER_MIN_MINUTES_PER_BLOCK = 30
PLANNER_QUESTIONS_PER_HOUR = 40
# Seviye testi ortak paket tarihi (günlük kitapçıktan ayırmak için)
LEVEL_TEST_PACK_DATE = date(2099, 1, 1)
PLANNER_MAX_RESOURCES_PER_ITEM = 2

# ── Revision / Spaced Repetition (Sprint-2.8) ─────────────────
REVISION_DEFAULT_EASE = 2.5
REVISION_MIN_EASE = 1.3
REVISION_MAX_EASE = 3.0
REVISION_DEFAULT_DIFFICULTY = 3
REVISION_MIN_DIFFICULTY = 1
REVISION_MAX_DIFFICULTY = 5
REVISION_HEATMAP_DAYS = 84
REVISION_GENERATE_MAX_ITEMS = 12
# Subject-normalized: subject_net / subject_question_count (not total exam net)
REVISION_EXAM_WEAK_NET_RATIO = 0.7
REVISION_EXAM_STRONG_NET_RATIO = 0.85
REVISION_EXAM_MIN_QUESTIONS = 5
REVISION_QUESTION_WEAK_RATE = 55.0
AI_CONTEXT_REVISIONS = 8
AI_CONTEXT_ACHIEVEMENTS = 5

# ── AI Provider defaults (Sprint-2.4) ─────────────────────────
# gemini-2.0-flash free-tier kotası sık doluyor; flash-latest daha stabil.
AI_DEFAULT_MODELS = {
    "gemini": "gemini-flash-latest",
    "openai": "gpt-4o-mini",
    "claude": "claude-3-5-haiku-latest",
}
AI_GEMINI_MODEL_FALLBACKS = (
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
)
