# CLAUDE.md

## About

DiaBot — open-source Telegram bot for people with type 1 diabetes. Food photo → AI recognition → user confirmation → KBJU/XE calculation → food diary. Multi-user, self-hosted, bilingual (RU/EN).

## Tech Stack

- Python 3.11+, full async/await
- `python-telegram-bot` 21+ (async, polling mode)
- `litellm` — multi-provider LLM routing with 2 chains:
  - Vision: Google AI Studio (Gemini 2.5 Flash) → OpenRouter (Gemini)
  - Text: Google AI Studio → OpenRouter → Groq (Llama 4)
- `google-genai` — Google Search grounding fallback for unknown/branded products
- `aiosqlite` — SQLite, no ORM, plain SQL
- `python-dotenv` — configuration via .env

## Commands

- Run: `python main.py`
- Test: `python -m pytest tests/ -v` (72 tests)
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
config.py                  # Settings dataclass from .env (frozen, validated)
handlers/                  # Telegram handlers (thin I/O layer, no business logic)
  start.py                 # /start, 5-step onboarding, /help
  photo.py                 # Food photo recognition pipeline
  text.py                  # Text food input + reply keyboard routing
  confirm.py               # Confirmation, correction, cancellation
  diary.py                 # /today, /week, /history, /undo
  glucose.py               # /sugar — glucose readings
  settings.py              # Profile/target editing, admin panel
  admin.py                 # /adduser, /removeuser, /listusers, approval workflow
  privacy.py               # /privacy, /export, /delete_my_data, consent
  keyboards.py             # Keyboard factory (reply + inline)
services/                  # Business logic (no Telegram imports)
  llm.py                   # litellm Router: 2 chains (vision + text), auto-failover
  nutrition.py             # KBJU formatting, progress bars, XE calculation
  database.py              # aiosqlite CRUD (users, meals, glucose, targets)
  auth.py                  # Access control, rate limiting, approval queue
models/schemas.py          # Dataclasses: MealItem, User, NutritionTarget, etc.
locales/                   # i18n strings + LLM prompts (tied to language)
  ru.py                    # Russian (default)
  en.py                    # English
tests/                     # 72 automated tests (pytest)
```

## State Machine

```
ONBOARDING: consent → gender → height → weight → age → targets → IDLE
IDLE ↔ AWAITING_CONFIRM  (food recognition flow)
IDLE ↔ AWAITING_GLUCOSE   (glucose recording)
```

## Key Decisions

- Handlers are thin I/O only — all business logic in `services/`
- Services stored in `context.bot_data` (db, llm, auth, settings)
- 2 LLM chains: vision (Gemini/OpenRouter) and text (+ Groq/Llama fallback)
- Google Search grounding for low-confidence branded products
- Photos never saved to disk — only Telegram file_id stored, bytes passed directly to LLM
- Admins from .env (ADMIN_IDS), additional users via approval workflow
- User data isolation per user_id in all DB queries
- Carb accuracy > calorie accuracy (insulin dosing depends on it)
- 1 XE = 12g carbs default (configurable per user)
- Mifflin-St Jeor formula for automatic KBJU target calculation
- Reply keyboard for main navigation, inline keyboard for confirmation only
- All dates stored with user's timezone awareness
- GDPR: /export and /delete_my_data implemented

## Important

- LLM prompts live in `locales/` (not separate prompts/ dir) — tied to language
- JSON mode for all LLM responses with retry logic for invalid JSON
- Bot messages use HTML parse_mode (not Markdown)
- Onboarding is 5 steps: gender → height → weight → age → targets
- Daily targets: auto-calculated or manually overridden
- Progress display: carbs/XE always first (insulin dosing priority)
