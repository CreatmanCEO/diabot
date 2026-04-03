# CLAUDE.md

## About

DiaBot — open-source Telegram bot for people with type 1 diabetes. Food photo → AI recognition → user confirmation → KBJU/XE calculation → food diary. Multi-user, self-hosted, i18n-ready.

## Tech Stack

- Python 3.11+, full async/await
- `python-telegram-bot` 21+ (async, polling mode)
- `litellm` — multi-provider LLM routing (Gemini → OpenRouter → Groq)
- `google-genai` — Google Search grounding fallback for unknown products
- `aiosqlite` — SQLite, no ORM, plain SQL
- `python-dotenv` — configuration via .env

## Commands

- Run: `python main.py`
- Test: `python -m pytest tests/ -v`
- Install: `pip install -r requirements.txt`

## Code Style

- All code, comments, docstrings in **English**
- Type hints everywhere
- Docstrings for public functions
- Logging via `logging` module (INFO for actions, DEBUG for LLM requests)
- No hardcoded strings — all bot messages in `locales/` modules
- HTML parse_mode for Telegram (not Markdown)
- JSON mode for LLM responses (`response_format: json_object`)

## Architecture

```
main.py                    # Entry point, ConversationHandler wiring
config.py                  # Settings dataclass from .env
handlers/                  # Telegram handlers (thin, I/O only)
  start.py                 # /start, onboarding, /help
  photo.py                 # Food photo recognition
  text.py                  # Text food description + button routing
  confirm.py               # Confirmation, cancellation, corrections
  diary.py                 # /today, /week, /history, /undo
  glucose.py               # /sugar, glucose readings
  admin.py                 # /adduser, /removeuser, /listusers
  privacy.py               # /privacy, /export, /delete_my_data
  keyboards.py             # Keyboard factory functions
services/                  # Business logic
  llm.py                   # litellm Router with 2 chains (vision + text)
  nutrition.py             # KBJU formatting for Telegram
  database.py              # aiosqlite CRUD (users, meals, glucose)
  auth.py                  # Access control, rate limiting
models/schemas.py          # Dataclasses (MealItem, User, etc.)
locales/                   # i18n strings + LLM prompts
  ru.py                    # Russian (default)
  en.py                    # English
```

## State Machine

```
ONBOARDING_CONSENT → ONBOARDING_TIMEZONE → ONBOARDING_HE → IDLE
IDLE ↔ AWAITING_CONFIRM (food recognition flow)
IDLE ↔ AWAITING_GLUCOSE (glucose recording)
```

## Key Decisions

- Services stored in `context.bot_data` (db, llm, auth, settings)
- 2 LLM chains: vision (Gemini/OpenRouter) and text (+ Groq fallback)
- Google Search grounding for low-confidence branded products
- Photos never saved to disk — only Telegram file_id stored
- Admins from .env (ADMIN_IDS), additional users via /adduser commands
- User data isolation per user_id in all DB queries
- Carb accuracy > calorie accuracy (insulin dosing depends on it)
- 1 XE = 12g carbs default (configurable per user)

## Important

- LLM prompts in `locales/` (not separate prompts/ dir) — tied to language
- Reply keyboard for main navigation, inline keyboard for confirmation only
- All dates stored with user's timezone awareness
- GDPR: /export and /delete_my_data implemented
