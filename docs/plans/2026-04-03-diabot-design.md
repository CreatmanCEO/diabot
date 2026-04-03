# DiaBot Design Document

**Date:** 2026-04-03
**Status:** Approved

## Overview

DiaBot is a personal Telegram bot for people with type 1 diabetes. It recognizes food from photos using AI (Gemini), calculates nutrition values (KBJU) with emphasis on carbohydrates and bread units (XE/HE), and maintains a food diary.

**Target:** Open-source, self-hosted, multi-user per instance.

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Monolith with litellm Router | Simple, single process, easy to deploy on VPS |
| LLM Integration | litellm with 2 chains (vision/text) | Multi-provider fallback with priority ordering |
| Vision chain | Gemini AI Studio → OpenRouter/Gemini | Vision quality is critical for carb accuracy |
| Text chain | Gemini → OpenRouter → Groq/Llama 4 | Any model handles text KBJU calculation |
| Unknown products | LLM first, Google Search grounding if low confidence | Saves API calls, search only when needed |
| User access | Self-hosted hybrid: admins in .env, /adduser for others | No SSH needed to add users |
| Database | SQLite via aiosqlite, no ORM | Simple, portable, sufficient for personal deployments |
| Localization | i18n-ready, Russian default, EN included | Open-source friendly, prompts in user's language |
| Privacy | Full: consent on first launch, /export, /delete_my_data | Health data requires careful handling |
| Telegram UI | Reply keyboard (main menu) + Inline buttons (confirmation) | Convenient, no need to type /commands |
| Photo storage | Never on disk, only Telegram file_id in DB | Privacy, disk space |
| Code language | English only (comments, docstrings, variables) | Open-source standard |
| Deployment | VPS via systemd service | Simple, reliable |

## Project Structure

```
diabot/
├── main.py                    # Entry point, Application, handler registration
├── config.py                  # .env loading, validation, Settings dataclass
├── handlers/
│   ├── __init__.py
│   ├── start.py               # /start (with consent), /help
│   ├── photo.py               # Food photo handling (+ caption)
│   ├── text.py                # Text food description
│   ├── confirm.py             # ✅ confirmation / correction
│   ├── diary.py               # /today, /week, /history
│   ├── glucose.py             # /sugar <value>
│   ├── admin.py               # /adduser, /removeuser, /listusers
│   └── privacy.py             # /privacy, /export, /delete_my_data
├── services/
│   ├── __init__.py
│   ├── llm.py                 # litellm Router: vision_chain + text_chain
│   ├── nutrition.py           # Parse LLM JSON, format KBJU/XE output
│   ├── database.py            # aiosqlite: users, meals, glucose, CRUD
│   └── auth.py                # Access check, consent, rate limiting
├── models/
│   ├── __init__.py
│   └── schemas.py             # Dataclasses: MealItem, NutritionTotals, User, GlucoseReading
├── prompts/
│   └── system_prompt.py       # RECOGNITION_PROMPT, CALCULATION_PROMPT templates
├── locales/
│   ├── __init__.py            # get_locale(lang) helper
│   ├── ru.py                  # Russian: bot strings + LLM prompts
│   └── en.py                  # English: bot strings + LLM prompts
├── data/                      # Auto-created, in .gitignore
├── docs/plans/                # Design and implementation docs
├── requirements.txt
├── .env.example
├── diabot.service
├── LICENSE
└── README.md
```

## Database Schema

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    timezone TEXT DEFAULT 'Europe/Moscow',
    he_grams INTEGER DEFAULT 12,
    language TEXT DEFAULT 'ru',
    is_active BOOLEAN DEFAULT TRUE,
    onboarding_completed BOOLEAN DEFAULT FALSE,
    consent_given_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    items_json TEXT NOT NULL,
    totals_json TEXT NOT NULL,
    photo_file_id TEXT,
    original_text TEXT,
    timezone TEXT DEFAULT 'Europe/Moscow'
);

CREATE INDEX idx_meals_user_date ON meals(user_id, date);

CREATE TABLE glucose_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    value REAL NOT NULL,
    reading_type TEXT,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    note TEXT
);

CREATE INDEX idx_glucose_user_date ON glucose_readings(user_id, date);

CREATE TABLE allowed_users (
    user_id INTEGER PRIMARY KEY,
    added_by INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## LLM Service

### Two Chains (litellm Router)

**Vision chain** (food photo recognition):
1. `gemini/gemini-2.5-flash` (Google AI Studio)
2. `openrouter/google/gemini-2.5-flash` (OpenRouter)

**Text chain** (KBJU calculation, corrections without photo):
1. `gemini/gemini-2.5-flash` (Google AI Studio)
2. `openrouter/google/gemini-2.5-flash` (OpenRouter)
3. `groq/meta-llama/llama-4-scout-17b-16e-instruct` (Groq)

### Public Interface (services/llm.py)

```python
async def recognize_food(image_bytes: bytes, caption: str | None) -> dict
async def recognize_food_text(text: str) -> dict
async def correct_recognition(previous_items: list, correction: str, image_bytes: bytes | None) -> dict
async def calculate_nutrition(items: list, he_grams: int) -> dict
```

### Error Handling

1. litellm Router: 2 retries per model → fallback to next
2. Invalid JSON from LLM → retry once
3. All providers down → user message "Service temporarily unavailable"
4. Before each LLM call → send "Analyzing..." to user

### Google Search Grounding

Two-level approach for branded/packaged products:
1. First call: standard LLM (no search)
2. If response has `confidence: "low"` or unknown product → second call via native `google-genai` with Google Search tool enabled
3. Fallback only for difficult cases, saves API calls

### Prompts

- Prompt body in English (LLM understands instructions better in EN)
- Final instruction: `IMPORTANT: Respond in {language_name}`
- JSON keys always English (`name`, `weight_g`, `calories`)
- Values (`name` of product) in user's language
- Branded products instruction: use exact KBJU from packaging knowledge

## State Machine

```
States:
  ONBOARDING_CONSENT = 0
  ONBOARDING_TIMEZONE = 1
  ONBOARDING_HE = 2
  IDLE = 3
  AWAITING_CONFIRM = 4
  AWAITING_GLUCOSE = 5
```

### Transitions

```
/start → ONBOARDING_CONSENT (new user) or IDLE (existing)
ONBOARDING_CONSENT → consent given → ONBOARDING_TIMEZONE
ONBOARDING_TIMEZONE → timezone set → ONBOARDING_HE
ONBOARDING_HE → HE set → IDLE

IDLE:
  photo/text → Step 1 (recognize) → AWAITING_CONFIRM
  menu buttons → execute command → IDLE
  /sugar or Sugar button → AWAITING_GLUCOSE

AWAITING_CONFIRM:
  ✅ inline button / "да"/"ок" → Step 2 (calculate) → save to DB → IDLE
  text correction → re-run Step 1 with context → AWAITING_CONFIRM
  ❌ inline button / /cancel → clear pending → IDLE
  new photo → restart with new photo → AWAITING_CONFIRM

AWAITING_GLUCOSE:
  number → save reading → IDLE
  /cancel → IDLE
```

### context.user_data (AWAITING_CONFIRM)

```python
{
    "pending_items": [...],
    "pending_photo_file_id": "...",
    "pending_photo_bytes": b"...",   # RAM only, cleared after save/cancel
    "pending_text": "...",
    "correction_history": [...]
}
```

## UX: Keyboards

### Reply Keyboard (persistent, bottom of screen)

Main menu:
```
[ 📊 Today ] [ 📅 Week   ]
[ 💉 Sugar ] [ ⚙️ Menu   ]
```

Settings menu (on "Menu" press):
```
[ 📋 History  ] [ ↩️ Undo     ]
[ 🔒 Privacy  ] [ ❓ Help     ]
[ ◀️ Back     ]
```

### Inline Keyboard (contextual, under messages)

After recognition (Step 1):
```
[ ✅ Correct ] [ ❌ Cancel ]
```

Consent (first /start):
```
[ ✅ I agree ] [ 📄 Details ]
```

## Onboarding Flow

```
/start → Welcome message + disclaimer → [✅ Agree] [📄 Details]
  → Details → privacy info → [✅ Agree] [◀️ Back]
  → Agree → Timezone selection → [Moscow] [Europe] [Other]
  → Timezone → HE grams selection → [12g (RU)] [10g] [Other]
  → HE → Setup complete message + main keyboard → IDLE
```

Returning users: `/start` shows brief help + main keyboard, no re-onboarding.

## Commands & Entry Points

| Action | Slash command | Button | State |
|--------|-------------|--------|-------|
| Start/help | `/start`, `/help` | ❓ Help | IDLE |
| Food photo | — | (send photo) | IDLE → AWAITING_CONFIRM |
| Food text | — | (send text) | IDLE → AWAITING_CONFIRM |
| Confirm | — | ✅ Correct (inline) | AWAITING_CONFIRM → IDLE |
| Cancel | `/cancel` | ❌ Cancel (inline) | AWAITING_CONFIRM → IDLE |
| Diary | `/today` | 📊 Today | IDLE |
| Week | `/week` | 📅 Week | IDLE |
| Sugar | `/sugar 5.8` | 💉 Sugar | IDLE → AWAITING_GLUCOSE |
| History | `/history N` | 📋 History | IDLE |
| Undo | `/undo` | ↩️ Undo | IDLE |
| Privacy | `/privacy` | 🔒 Privacy | IDLE |
| Export | `/export` | — | IDLE |
| Delete data | `/delete_my_data` | — | IDLE |
| Add user | `/adduser <id>` | — | IDLE (admin) |
| Remove user | `/removeuser <id>` | — | IDLE (admin) |
| List users | `/listusers` | — | IDLE (admin) |

## Configuration (.env)

```env
# Telegram
TELEGRAM_TOKEN=xxx
ADMIN_IDS=338930874,792567660

# LLM Providers (priority order)
GEMINI_API_KEY=xxx
OPENROUTER_API_KEY=xxx
GROQ_API_KEY=xxx

# Defaults
DEFAULT_TIMEZONE=Europe/Moscow
DEFAULT_HE_GRAMS=12
DEFAULT_LANGUAGE=ru

# Rate limiting
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW=3600

# Database
DB_PATH=data/diabot.db
```

## Privacy & Compliance

- Consent required before first use (stored in DB with timestamp)
- `/privacy` — detailed data handling description
- `/export` — export all user data as JSON
- `/delete_my_data` — complete data deletion
- Photos never saved to disk (only Telegram file_id in DB)
- Disclaimer: bot is not a medical device
- AI provider notice: food data sent to third-party AI services

## Deployment

- VPS "main" via systemd service
- Polling mode (not webhook)
- Graceful SIGTERM shutdown
- Auto-create data/ directory and DB tables on startup
