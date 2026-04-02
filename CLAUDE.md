# CLAUDE.md

## О проекте

DiaBot — персональный Telegram-бот для человека с диабетом 1 типа. Фото еды → распознавание через Gemini AI → подтверждение пользователем → расчёт КБЖУ и ХЕ → запись в дневник. Бот для одного пользователя.

## Стек

- Python 3.11+, полный async/await
- `python-telegram-bot` (async, polling mode)
- `google-genai` (НЕ google-generativeai, НЕ vertexai) — Gemini 2.5 Flash
- `aiosqlite` — SQLite без ORM, простые SQL запросы
- `python-dotenv` — конфигурация через .env

## Команды

- Run: `python main.py`
- Install deps: `pip install -r requirements.txt`
- No test framework yet

## Стиль кода

- Type hints везде
- Docstrings для публичных функций
- Logging через модуль `logging` (INFO — действия, DEBUG — Gemini запросы/ответы)
- Никаких хардкод-строк — тексты сообщений в константах
- HTML parse mode для Telegram (не Markdown)
- JSON mode для Gemini (`response_mime_type: "application/json"`)

## Архитектура

- `handlers/` — Telegram хендлеры (start, photo, text, confirm, diary)
- `services/` — бизнес-логика (gemini, nutrition, database)
- `models/` — dataclasses/TypedDict
- `prompts/` — системные промпты для Gemini
- ConversationHandler с состояниями: IDLE → AWAITING_CONFIRM → IDLE
- Состояние в `context.user_data`

## Важно

- Точность углеводов критичнее калорий — от этого зависит доза инсулина
- 1 ХЕ = 12 г углеводов (конфигурируемо через HE_GRAMS)
- Один пользователь (ALLOWED_USER_ID), проверка во всех хендлерах
- Polling mode (не webhook)
- Фото не хранить на диске — только Telegram file_id
- Даты с учётом timezone пользователя
- Reference-проект: https://github.com/jokkebk/mealgram (вдохновение, не копировать)
