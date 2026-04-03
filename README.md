# 🍽 DiaBot — AI Nutrition Assistant for Type 1 Diabetes

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4.svg)](https://core.telegram.org/bots/api)
[![Tests: 72](https://img.shields.io/badge/tests-72-brightgreen.svg)]()

[Русский](#русский) | [English](#english)

---

## Русский

### Проблема

Каждый приём пищи для человека с диабетом 1 типа — это математическая задача. Нужно оценить количество углеводов в тарелке, перевести их в хлебные единицы и рассчитать дозу инсулина. Ошибка в 1-2 ХЕ может привести к гипогликемии или гипергликемии — а это госпитализация, потеря сознания, кома. Люди делают это 4-6 раз в день, каждый день, всю жизнь.

### Решение

DiaBot превращает подсчёт углеводов в одно действие: **сфотографируй еду — получи результат**. Бот распознаёт продукты через AI, считает КБЖУ и хлебные единицы, ведёт дневник и показывает прогресс к дневным целям. Углеводы и ХЕ всегда на первом месте — потому что именно от них зависит доза инсулина.

### 📸 Как это работает

1. **Отправь фото** еды в чат (или опиши текстом)
2. **Бот распознаёт** продукты и порции через Gemini AI
3. **Подтверди или поправь** — бот показывает что распознал, ты корректируешь при необходимости
4. **Получи КБЖУ + ХЕ** — точный расчёт с акцентом на углеводы
5. **Следи за прогрессом** — дневник, статистика, прогресс-бары к дневным целям

### 🎯 Ключевые возможности

**Распознавание еды**
- 📷 Фото → AI распознавание продуктов и порций
- ✏️ Текстовое описание (без фото)
- 📷+✏️ Фото с подписью для уточнения
- 🏷 Распознавание брендовых продуктов (с Google Search для редких марок)

**Точный подсчёт**
- 🔢 Калории, белки, жиры, углеводы (КБЖУ)
- 🍞 Хлебные единицы (ХЕ) — с настраиваемым коэффициентом
- 🎯 Углеводы всегда выделены первыми (приоритет дозирования инсулина)
- ✅ Двухшаговый процесс: распознал → подтверди → сохрани

**Дневные цели и прогресс**
- 👤 Профиль: пол, рост, вес, возраст
- 📊 Автоматический расчёт норм по формуле Mifflin-St Jeor
- ✍️ Ручная настройка целей (рекомендации диетолога)
- 📈 Компактный прогресс после каждого приёма пищи
- ▓▓▓░░░ Визуальные прогресс-бары в дневнике

**Дневник питания**
- 📅 Дневник за сегодня с разбивкой по приёмам (`/today`)
- 📊 Недельная статистика (`/week`)
- 📜 История записей (`/history N`)
- ↩️ Отмена последней записи (`/undo`)
- 🩸 Учёт показаний глюкозы (`/sugar`)

**Конфиденциальность**
- 🔒 Согласие при первом запуске с описанием обработки данных
- 🚫 Фото НИКОГДА не сохраняются на диск (только Telegram file_id)
- 📦 Полный экспорт данных (`/export` — JSON)
- 🗑 Полное удаление данных (`/delete_my_data`)
- ✅ GDPR-совместимость

**Мультипользовательский режим**
- 👥 Self-hosted с системой одобрения доступа
- 📩 Пользователь запрашивает → админ получает уведомление с кнопками → пользователь получает ответ
- ⚡ Rate limiting для каждого пользователя

### Технологии

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+, полностью асинхронный |
| Telegram | python-telegram-bot 21+ |
| AI/LLM | litellm Router — Gemini 2.5 Flash, OpenRouter, Groq (Llama 4) |
| Поиск | Google Search grounding (google-genai) |
| База данных | SQLite через aiosqlite, без ORM |
| Деплой | systemd |
| Тесты | 72 автотеста (pytest) |

### Быстрый старт

```bash
git clone https://github.com/CreatmanCEO/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Заполни .env своими API-ключами
python main.py
```

**Переменные окружения:**

| Переменная | Описание | Обязательно |
|-----------|----------|:-----------:|
| `TELEGRAM_TOKEN` | Токен бота от @BotFather | да |
| `ADMIN_IDS` | Telegram ID админов через запятую | да |
| `GEMINI_API_KEY` | API ключ Google AI Studio | * |
| `OPENROUTER_API_KEY` | API ключ OpenRouter | * |
| `GROQ_API_KEY` | API ключ Groq | * |
| `DEFAULT_TIMEZONE` | Часовой пояс (Europe/Moscow) | нет |
| `DEFAULT_HE_GRAMS` | Граммов углеводов в 1 ХЕ (12) | нет |
| `DEFAULT_LANGUAGE` | Язык по умолчанию (ru) | нет |
| `RATE_LIMIT_REQUESTS` | Лимит запросов в час (30) | нет |
| `DB_PATH` | Путь к SQLite базе | нет |

\* Нужен хотя бы один LLM API ключ. Для распознавания фото нужен GEMINI или OPENROUTER.

### Деплой (systemd)

```bash
sudo useradd -r -s /bin/false diabot
sudo mkdir -p /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git /opt/diabot
cd /opt/diabot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env  # заполнить токены
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

---

## English

### The Problem

Every meal for a person with type 1 diabetes is a math problem. You need to estimate the carbohydrates on your plate, convert them to bread units, and calculate the insulin dose. An error of 1-2 XE can lead to hypoglycemia or hyperglycemia — hospitalization, loss of consciousness, coma. People do this 4-6 times a day, every day, for the rest of their lives.

### The Solution

DiaBot turns carb counting into a single action: **snap a photo — get the result**. The bot recognizes food via AI, calculates nutrition and bread units, keeps a food diary, and shows progress toward daily targets. Carbs and XE are always highlighted first — because insulin dosing depends on them.

### 📸 How It Works

1. **Send a photo** of your meal (or describe it in text)
2. **Bot recognizes** products and portions via Gemini AI
3. **Confirm or correct** — the bot shows what it found, you adjust if needed
4. **Get nutrition + XE** — precise calculation with carbs prioritized
5. **Track your progress** — diary, statistics, progress bars toward daily goals

### 🎯 Key Features

**Food Recognition**
- 📷 Photo → AI recognition of products and portions
- ✏️ Text-based food description (no photo needed)
- 📷+✏️ Photo with caption for extra context
- 🏷 Branded product recognition (with Google Search fallback for rare brands)

**Precise Calculation**
- 🔢 Calories, protein, fat, carbs (KBJU)
- 🍞 Bread units (XE/HE) — with configurable ratio
- 🎯 Carbs always highlighted first (insulin dosing priority)
- ✅ Two-step flow: recognize → confirm → save

**Daily Targets & Progress**
- 👤 Profile: gender, height, weight, age
- 📊 Automatic target calculation via Mifflin-St Jeor formula
- ✍️ Manual target override (for dietician recommendations)
- 📈 Compact progress after every meal
- ▓▓▓░░░ Visual progress bars in diary

**Food Diary**
- 📅 Today's diary with per-meal breakdown (`/today`)
- 📊 Weekly statistics (`/week`)
- 📜 Meal history (`/history N`)
- ↩️ Undo last entry (`/undo`)
- 🩸 Glucose readings tracking (`/sugar`)

**Privacy & Data**
- 🔒 Consent on first launch with data processing details
- 🚫 Photos are NEVER saved to disk (only Telegram file_id)
- 📦 Full data export (`/export` as JSON)
- 🗑 Complete data deletion (`/delete_my_data`)
- ✅ GDPR-style compliance

**Multi-User**
- 👥 Self-hosted with admin approval workflow
- 📩 User requests access → admin gets notification with approve/reject buttons → user notified
- ⚡ Per-user rate limiting

### Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+, fully async |
| Telegram | python-telegram-bot 21+ |
| AI/LLM | litellm Router — Gemini 2.5 Flash, OpenRouter, Groq (Llama 4) |
| Search | Google Search grounding (google-genai) |
| Database | SQLite via aiosqlite, no ORM |
| Deployment | systemd |
| Tests | 72 automated tests (pytest) |

### Quick Start

```bash
git clone https://github.com/CreatmanCEO/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python main.py
```

**Environment Variables:**

| Variable | Description | Required |
|----------|-------------|:--------:|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | yes |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | yes |
| `GEMINI_API_KEY` | Google AI Studio API key | * |
| `OPENROUTER_API_KEY` | OpenRouter API key | * |
| `GROQ_API_KEY` | Groq API key | * |
| `DEFAULT_TIMEZONE` | Default timezone (Europe/Moscow) | no |
| `DEFAULT_HE_GRAMS` | Grams of carbs per 1 XE (12) | no |
| `DEFAULT_LANGUAGE` | Default language (ru) | no |
| `RATE_LIMIT_REQUESTS` | Requests per hour limit (30) | no |
| `DB_PATH` | Path to SQLite database | no |

\* At least one LLM API key required. Photo recognition needs GEMINI or OPENROUTER.

### Deploy (systemd)

```bash
sudo useradd -r -s /bin/false diabot
sudo mkdir -p /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git /opt/diabot
cd /opt/diabot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env  # fill in tokens
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

---

## Architecture

```
main.py                     Entry point, ConversationHandler wiring
config.py                   Settings dataclass from .env (frozen, validated)

handlers/                   Telegram handlers (thin I/O layer)
  start.py                  /start, 5-step onboarding, /help
  photo.py                  Food photo recognition pipeline
  text.py                   Text food input + reply keyboard routing
  confirm.py                Confirmation, correction, cancellation
  diary.py                  /today, /week, /history, /undo
  glucose.py                /sugar — glucose readings
  settings.py               Profile/target editing, admin panel
  admin.py                  /adduser, /removeuser, /listusers, approval workflow
  privacy.py                /privacy, /export, /delete_my_data, consent
  keyboards.py              Keyboard factory (reply + inline)

services/                   Business logic (no Telegram dependencies)
  llm.py                    litellm Router: 2 chains (vision + text), failover
  nutrition.py              KBJU formatting, progress bars, XE calculation
  database.py               aiosqlite CRUD (users, meals, glucose, targets)
  auth.py                   Access control, rate limiting, approval queue

models/
  schemas.py                Dataclasses: MealItem, User, NutritionTarget, etc.

locales/                    i18n strings + LLM prompts (tied to language)
  ru.py                     Russian (default)
  en.py                     English
```

### Design Decisions

- **Handlers are thin** — all business logic lives in `services/`. Handlers only do I/O (Telegram API calls, user input parsing).
- **Two LLM chains** — Vision chain (Gemini/OpenRouter) for photos. Text chain adds Groq/Llama as a cheaper fallback. litellm Router handles automatic failover between providers.
- **Google Search grounding** — When the primary model returns low-confidence results for branded products, a separate `google-genai` call with Search grounding retrieves accurate nutrition data.
- **State machine** — `ConversationHandler` manages onboarding flow and food recognition flow. Services are injected via `context.bot_data`.
- **Carb accuracy over calorie accuracy** — Architectural decision reflected in prompts, formatting, and UI ordering. Insulin dosing depends on carb precision.
- **No ORM** — Plain SQL with aiosqlite. The schema is simple enough that an ORM would add complexity without benefit.
- **Photos never touch disk** — Only Telegram `file_id` is stored. The image is fetched on-demand from Telegram servers and passed directly to the LLM API as bytes.

### State Machine

```
ONBOARDING: consent → gender → height → weight → age → targets → IDLE
IDLE ↔ AWAITING_CONFIRM  (food recognition flow)
IDLE ↔ AWAITING_GLUCOSE   (glucose recording)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests for new functionality
4. Ensure all tests pass: `python -m pytest tests/ -v`
5. Submit a pull request

Code style:
- All code, comments, and docstrings in English
- Type hints on all function signatures
- Docstrings for public functions
- HTML parse_mode for Telegram messages (not Markdown)
- Bot-facing strings in `locales/` modules (never hardcoded)

## License

MIT License. Copyright (c) 2026 Creatman.

---

<sub>Built with care. Powered by AI.</sub>
