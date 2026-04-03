# DiaBot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a self-hosted multi-user Telegram bot that recognizes food from photos, calculates KBJU/XE nutrition values, and maintains a food diary for people with type 1 diabetes.

**Architecture:** Monolith Python async app. python-telegram-bot handles Telegram I/O, litellm Router manages multi-provider LLM fallback (2 chains: vision and text), aiosqlite for persistence. ConversationHandler state machine drives the UX flow. i18n-ready with Russian default.

**Tech Stack:** Python 3.11+, python-telegram-bot 21+, litellm, google-genai (for Search grounding fallback), aiosqlite, python-dotenv

**Design doc:** `docs/plans/2026-04-03-diabot-design.md`

---

## Task 1: Update project foundation (requirements, .env, config)

**Files:**
- Modify: `requirements.txt`
- Modify: `.env.example`
- Create: `config.py`
- Create: `tests/test_config.py`

**Step 1: Update requirements.txt**

```
python-telegram-bot>=21.0
litellm>=1.40.0
google-genai>=1.0.0
aiosqlite>=0.20.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

**Step 2: Update .env.example**

```env
# Telegram
TELEGRAM_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321

# LLM Providers (priority order)
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
GROQ_API_KEY=your_groq_api_key

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

**Step 3: Write failing test for config**

```python
# tests/test_config.py
import os
import pytest
from config import Settings, load_settings


def test_load_settings_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("ADMIN_IDS", "111,222")
    monkeypatch.setenv("GEMINI_API_KEY", "gem-key")
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
    monkeypatch.setenv("GROQ_API_KEY", "groq-key")

    settings = load_settings()

    assert settings.telegram_token == "test-token"
    assert settings.admin_ids == {111, 222}
    assert settings.gemini_api_key == "gem-key"
    assert settings.openrouter_api_key == "or-key"
    assert settings.groq_api_key == "groq-key"
    assert settings.default_timezone == "Europe/Moscow"
    assert settings.default_he_grams == 12
    assert settings.default_language == "ru"
    assert settings.rate_limit_requests == 30
    assert settings.rate_limit_window == 3600
    assert settings.db_path == "data/diabot.db"


def test_load_settings_missing_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    with pytest.raises(ValueError, match="TELEGRAM_TOKEN"):
        load_settings()


def test_load_settings_no_llm_keys(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
    monkeypatch.setenv("ADMIN_IDS", "111")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="LLM"):
        load_settings()
```

**Step 4: Run tests to verify they fail**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'config'`

**Step 5: Implement config.py**

```python
# config.py
"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Application settings."""

    telegram_token: str
    admin_ids: set[int]
    gemini_api_key: str
    openrouter_api_key: str
    groq_api_key: str
    default_timezone: str = "Europe/Moscow"
    default_he_grams: int = 12
    default_language: str = "ru"
    rate_limit_requests: int = 30
    rate_limit_window: int = 3600
    db_path: str = "data/diabot.db"


def load_settings() -> Settings:
    """Load settings from environment variables.

    Raises:
        ValueError: If required variables are missing.
    """
    load_dotenv()

    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN environment variable is required")

    admin_ids_str = os.getenv("ADMIN_IDS", "")
    admin_ids = {int(x.strip()) for x in admin_ids_str.split(",") if x.strip()}

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if not any([gemini_key, openrouter_key, groq_key]):
        raise ValueError(
            "At least one LLM API key is required "
            "(GEMINI_API_KEY, OPENROUTER_API_KEY, or GROQ_API_KEY)"
        )

    return Settings(
        telegram_token=token,
        admin_ids=admin_ids,
        gemini_api_key=gemini_key,
        openrouter_api_key=openrouter_key,
        groq_api_key=groq_key,
        default_timezone=os.getenv("DEFAULT_TIMEZONE", "Europe/Moscow"),
        default_he_grams=int(os.getenv("DEFAULT_HE_GRAMS", "12")),
        default_language=os.getenv("DEFAULT_LANGUAGE", "ru"),
        rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "30")),
        rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600")),
        db_path=os.getenv("DB_PATH", "data/diabot.db"),
    )
```

**Step 6: Run tests to verify they pass**

Run: `pytest tests/test_config.py -v`
Expected: 3 passed

**Step 7: Commit**

```bash
git add requirements.txt .env.example config.py tests/test_config.py
git commit -m "feat: add config module with env validation and tests"
```

---

## Task 2: Localization system (locales)

**Files:**
- Create: `locales/__init__.py`
- Create: `locales/ru.py`
- Create: `locales/en.py`
- Create: `tests/test_locales.py`

**Step 1: Write failing test**

```python
# tests/test_locales.py
from locales import get_locale


def test_get_russian_locale():
    locale = get_locale("ru")
    assert locale.LANG == "ru"
    assert locale.BTN_TODAY  # not empty
    assert locale.RECOGNITION_PROMPT  # not empty
    assert locale.CALCULATION_PROMPT  # not empty


def test_get_english_locale():
    locale = get_locale("en")
    assert locale.LANG == "en"
    assert locale.BTN_TODAY
    assert locale.RECOGNITION_PROMPT


def test_unknown_locale_falls_back_to_russian():
    locale = get_locale("de")
    assert locale.LANG == "ru"


def test_prompts_contain_language_instruction():
    ru = get_locale("ru")
    en = get_locale("en")
    assert "Russian" in ru.RECOGNITION_PROMPT or "Русский" in ru.RECOGNITION_PROMPT
    assert "English" in en.RECOGNITION_PROMPT
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_locales.py -v`
Expected: FAIL

**Step 3: Implement locales/ru.py**

```python
# locales/ru.py
"""Russian locale — bot messages and LLM prompts."""

LANG = "ru"
LANG_NAME = "Русский"

# --- Onboarding ---
START_WELCOME = (
    "👋 Привет! Я <b>DiaBot</b> — помощник для подсчёта "
    "углеводов и КБЖУ по фото еды.\n\n"
    "Я создан для людей с диабетом 1 типа.\n"
    "Отправь фото еды — я распознаю продукты, "
    "посчитаю углеводы и хлебные единицы.\n\n"
    "⚠️ Я не медицинское устройство. Всегда "
    "консультируйся с врачом по вопросам дозировки.\n\n"
    "Для работы мне нужно отправлять фото еды "
    "в AI-сервис. Подробнее: /privacy"
)
CONSENT_AGREE = "✅ Согласен и начинаем"
CONSENT_DETAILS = "📄 Подробнее"
CONSENT_DETAILS_TEXT = (
    "🔒 <b>Что я делаю с данными:</b>\n"
    "• Фото отправляются в AI для распознавания\n"
    "• Результаты хранятся на сервере бота\n"
    "• Данные не передаются третьим лицам\n"
    "• Ты можешь экспортировать или удалить свои данные\n\n"
    "Подробнее: /privacy"
)
ONBOARDING_TIMEZONE = "🌍 Какой у тебя часовой пояс?"
TZ_MOSCOW = "🇷🇺 Москва"
TZ_EUROPE = "🇪🇺 Европа"
TZ_OTHER = "Другой"
ONBOARDING_HE = (
    "⚙️ Сколько граммов углеводов в 1 ХЕ?\n"
    "(стандарт РФ — 12 г, в некоторых странах 10 г)"
)
HE_12 = "12 г (РФ)"
HE_10 = "10 г"
HE_OTHER = "Другое"
ONBOARDING_COMPLETE = (
    "✅ Готово! Вот что я умею:\n\n"
    "📸 Отправь фото еды — я распознаю и посчитаю КБЖУ\n"
    "✏️ Или напиши текстом что ела\n"
    "💉 «Сахар» — записать показание глюкозы\n"
    "📊 «Сегодня» — дневник за день\n\n"
    "Попробуй — отправь фото еды!"
)
ONBOARDING_HE_CUSTOM = "Введи количество граммов углеводов в 1 ХЕ (число):"
ONBOARDING_TZ_CUSTOM = "Введи часовой пояс (например Europe/Berlin):"

# --- Main menu buttons ---
BTN_TODAY = "📊 Сегодня"
BTN_WEEK = "📅 Неделя"
BTN_SUGAR = "💉 Сахар"
BTN_MENU = "⚙️ Меню"
BTN_HISTORY = "📋 История"
BTN_UNDO = "↩️ Отменить"
BTN_PRIVACY = "🔒 Приватность"
BTN_HELP = "❓ Помощь"
BTN_BACK = "◀️ Назад"

# --- Inline buttons ---
BTN_CONFIRM = "✅ Верно"
BTN_CANCEL = "❌ Отмена"

# --- Recognition ---
ANALYZING = "⏳ Анализирую..."
RECOGNITION_HEADER = "🔍 Я вижу:"
RECOGNITION_HEADER_TEXT = "🔍 Предполагаю:"
RECOGNITION_CONFIRM = "Всё верно? Нажми ✅ или напиши что исправить."
RECOGNITION_UPDATED = "🔍 Обновлённый список:"
RECOGNITION_NO_FOOD = "🤔 Не вижу еды на фото. Отправь фото тарелки или опиши что ела."
RECOGNITION_FAILED = "⚠️ Не удалось распознать, попробуй другое фото или опиши текстом."

# --- Calculation ---
CALCULATION_HEADER = "🍽 Расчёт КБЖУ:"
CALCULATION_SAVED = "📝 Записано!"
CALCULATION_TODAY_SUMMARY = "Сегодня: {calories} ккал | {he} ХЕ"

# --- Diary ---
DIARY_HEADER = "📊 Дневник за {date}:"
DIARY_EMPTY = "📭 За {date} записей нет."
DIARY_TOTAL = "ИТОГО за день:"
WEEK_HEADER = "📅 Статистика за неделю:"
WEEK_EMPTY = "📭 За последнюю неделю записей нет."
HISTORY_HEADER = "📋 Последние {n} записей:"
HISTORY_EMPTY = "📭 Записей пока нет."
UNDO_SUCCESS = "↩️ Последняя запись удалена."
UNDO_NOTHING = "📭 Нечего отменять."

# --- Glucose ---
GLUCOSE_PROMPT = "💉 Введи показание сахара (ммоль/л):"
GLUCOSE_SAVED = "💉 Записано: {value} ммоль/л"
GLUCOSE_INVALID = "⚠️ Введи число, например: 5.8"

# --- Privacy ---
PRIVACY_TEXT = (
    "🔒 <b>Приватность</b>\n\n"
    "• Фото еды отправляются в AI-сервис для распознавания\n"
    "• Результаты хранятся на сервере бота\n"
    "• Фото НЕ сохраняются на диск\n"
    "• Данные не передаются третьим лицам\n\n"
    "<b>Команды:</b>\n"
    "/export — скачать все свои данные\n"
    "/delete_my_data — удалить все данные"
)
EXPORT_EMPTY = "📭 Нет данных для экспорта."
DELETE_CONFIRM = "⚠️ Ты уверен? Это удалит ВСЕ твои данные безвозвратно."
DELETE_YES = "Да, удалить"
DELETE_NO = "Нет, отмена"
DELETE_DONE = "✅ Все данные удалены."

# --- Admin ---
ADMIN_USER_ADDED = "✅ Пользователь {user_id} добавлен."
ADMIN_USER_REMOVED = "✅ Пользователь {user_id} удалён."
ADMIN_USER_LIST = "👥 Разрешённые пользователи:\n{users}"
ADMIN_USER_LIST_EMPTY = "📭 Список пуст (только админы)."
ADMIN_ONLY = "🔒 Команда только для администраторов."

# --- Errors ---
SERVICE_UNAVAILABLE = "⚠️ Сервис временно недоступен, попробуй через минуту."
RATE_LIMITED = "⏳ Слишком много запросов. Попробуй через {minutes} мин."
ACCESS_DENIED = "🔒 Этот бот персональный. Попроси админа добавить тебя."
UNSUPPORTED_MESSAGE = "📸 Отправь фото еды или напиши что ела."
CANCELLED = "❌ Отменено."

# --- Help ---
HELP_TEXT = (
    "❓ <b>Как пользоваться DiaBot</b>\n\n"
    "<b>Основное:</b>\n"
    "📸 Отправь фото еды — я распознаю и посчитаю КБЖУ\n"
    "✏️ Напиши текстом: «борщ с хлебом и компот»\n"
    "📸+✏️ Фото с подписью тоже работает\n\n"
    "<b>Команды:</b>\n"
    "/today — дневник за сегодня\n"
    "/week — статистика за неделю\n"
    "/history — последние записи\n"
    "/sugar — записать сахар\n"
    "/undo — удалить последнюю запись\n"
    "/privacy — приватность и данные\n"
    "/help — эта справка"
)

# --- LLM Prompts ---
RECOGNITION_PROMPT = """You are a nutritionist assistant for a person with type 1 diabetes.
Your task is to accurately recognize food in the photo (or from text description) and estimate portion sizes.

RULES:
1. List EACH visible product/dish on a separate line
2. Estimate weight in grams or volume in ml
3. If a dish is composite (e.g., soup, salad) — break it down into main components relevant for carbohydrates
4. If hard to determine precisely — indicate the most likely option
5. Do NOT calculate calories at this step, only recognition and weight
6. If the photo shows no food — report this politely
7. If the product is branded/packaged — specify exact product name and brand
8. If user provided a caption with the photo, use it as additional context for recognition

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {"name": "product name", "weight_g": 200, "note": ""},
    {"name": "product name", "weight_g": 150, "note": "additional detail"}
  ],
  "is_food": true,
  "confidence": "high"
}

confidence: "high" / "medium" / "low"
note: additional details if needed (cooking method, sauce, etc.)
If is_food = false, items must be empty.

IMPORTANT: All text values (name, note) MUST be in Русский language."""

CALCULATION_PROMPT = """You are a nutritionist calculator for a person with type 1 diabetes.
Calculate precise KBJU values for the given list of products.

RULES:
1. Use standard calorie tables (USDA, Russian FIC nutrition databases)
2. Account for cooking method (boiled, fried, raw)
3. For carbohydrates: specify TOTAL carbs and FIBER separately
4. Calculate bread units (XE/HE) using formula: (carbs_g - fiber_g) / {he_grams}
5. Estimate glycemic index (GI) of each product: low (<55), medium (55-70), high (>70)
6. Estimate overall GI of the meal
7. Be maximally accurate — insulin dosing depends on these numbers
8. If the product is branded/packaged — use exact KBJU values from packaging data in your knowledge. Indicate source: "manufacturer data"

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {
      "name": "product name",
      "weight_g": 200,
      "calories": 264,
      "protein": 9.5,
      "fat": 2.3,
      "carbs": 54.0,
      "fiber": 3.7,
      "gi": "medium",
      "source": ""
    }
  ],
  "totals": {
    "calories": 0,
    "protein": 0.0,
    "fat": 0.0,
    "carbs": 0.0,
    "fiber": 0.0,
    "net_carbs": 0.0,
    "he": 0.0,
    "gi_overall": "medium"
  }
}

net_carbs = carbs - fiber
he = net_carbs / {he_grams}
Round all values to 1 decimal place.
source: "manufacturer data" if branded, empty string otherwise.

IMPORTANT: All text values (name) MUST be in Русский language."""

CORRECTION_PROMPT = """You are a nutritionist assistant for a person with type 1 diabetes.
The user previously received a food recognition result and wants to make corrections.

Previous recognition result:
{previous_items}

User's correction: {correction_text}

Apply the user's correction to the list. Add, remove, or modify items as requested.
Keep unchanged items as they are. Re-estimate weights if the correction implies a change.

RESPONSE FORMAT (strictly JSON):
{
  "items": [
    {"name": "product name", "weight_g": 200, "note": ""}
  ],
  "is_food": true,
  "confidence": "high"
}

IMPORTANT: All text values (name, note) MUST be in Русский language."""
```

**Step 4: Implement locales/en.py**

Same structure as ru.py but with English strings. LLM prompts are identical except the final IMPORTANT line says "MUST be in English language."

**Step 5: Implement locales/__init__.py**

```python
# locales/__init__.py
"""Localization module — provides locale-specific strings and prompts."""

from typing import Any

from locales import ru, en

_LOCALES: dict[str, Any] = {
    "ru": ru,
    "en": en,
}

AVAILABLE_LANGUAGES = list(_LOCALES.keys())
DEFAULT_LANGUAGE = "ru"


def get_locale(lang: str) -> Any:
    """Get locale module by language code. Falls back to Russian."""
    return _LOCALES.get(lang, _LOCALES[DEFAULT_LANGUAGE])
```

**Step 6: Run tests**

Run: `pytest tests/test_locales.py -v`
Expected: 4 passed

**Step 7: Commit**

```bash
git add locales/ tests/test_locales.py
git commit -m "feat: add i18n localization system with ru/en locales and LLM prompts"
```

---

## Task 3: Data models (schemas)

**Files:**
- Create: `models/schemas.py`
- Create: `tests/test_schemas.py`

**Step 1: Write failing test**

```python
# tests/test_schemas.py
from models.schemas import MealItem, NutritionTotals, RecognitionResult, CalculationResult, User


def test_meal_item_creation():
    item = MealItem(name="Buckwheat", weight_g=200, note="boiled")
    assert item.name == "Buckwheat"
    assert item.weight_g == 200
    assert item.note == "boiled"


def test_meal_item_default_note():
    item = MealItem(name="Chicken", weight_g=150)
    assert item.note == ""


def test_nutrition_totals():
    totals = NutritionTotals(
        calories=452, protein=45.0, fat=4.5, carbs=58.3,
        fiber=5.2, net_carbs=53.1, he=4.4, gi_overall="medium",
    )
    assert totals.he == 4.4


def test_recognition_result():
    items = [MealItem(name="Rice", weight_g=200)]
    result = RecognitionResult(items=items, is_food=True, confidence="high")
    assert result.is_food
    assert len(result.items) == 1


def test_recognition_result_from_dict():
    data = {
        "items": [{"name": "Rice", "weight_g": 200, "note": ""}],
        "is_food": True,
        "confidence": "high",
    }
    result = RecognitionResult.from_dict(data)
    assert result.items[0].name == "Rice"


def test_calculation_result_from_dict():
    data = {
        "items": [
            {
                "name": "Rice", "weight_g": 200, "calories": 260,
                "protein": 5.0, "fat": 0.6, "carbs": 58.0,
                "fiber": 0.4, "gi": "high", "source": "",
            }
        ],
        "totals": {
            "calories": 260, "protein": 5.0, "fat": 0.6,
            "carbs": 58.0, "fiber": 0.4, "net_carbs": 57.6,
            "he": 4.8, "gi_overall": "high",
        },
    }
    result = CalculationResult.from_dict(data)
    assert result.totals.he == 4.8
    assert result.items[0].calories == 260
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement models/schemas.py**

```python
# models/schemas.py
"""Data models for DiaBot."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MealItem:
    """A single recognized food item."""

    name: str
    weight_g: int
    note: str = ""


@dataclass
class NutritionItem:
    """A food item with full nutrition data."""

    name: str
    weight_g: int
    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    gi: str = "medium"
    source: str = ""


@dataclass
class NutritionTotals:
    """Aggregated nutrition totals for a meal."""

    calories: float
    protein: float
    fat: float
    carbs: float
    fiber: float
    net_carbs: float
    he: float
    gi_overall: str = "medium"


@dataclass
class RecognitionResult:
    """Result of food recognition (Step 1)."""

    items: list[MealItem]
    is_food: bool
    confidence: str

    @classmethod
    def from_dict(cls, data: dict) -> RecognitionResult:
        items = [MealItem(**item) for item in data.get("items", [])]
        return cls(
            items=items,
            is_food=data.get("is_food", False),
            confidence=data.get("confidence", "low"),
        )


@dataclass
class CalculationResult:
    """Result of nutrition calculation (Step 2)."""

    items: list[NutritionItem]
    totals: NutritionTotals

    @classmethod
    def from_dict(cls, data: dict) -> CalculationResult:
        items = [NutritionItem(**item) for item in data.get("items", [])]
        totals = NutritionTotals(**data.get("totals", {}))
        return cls(items=items, totals=totals)


@dataclass
class User:
    """User profile from database."""

    user_id: int
    username: str | None = None
    timezone: str = "Europe/Moscow"
    he_grams: int = 12
    language: str = "ru"
    is_active: bool = True
    onboarding_completed: bool = False
    consent_given_at: str | None = None
    created_at: str | None = None
```

**Step 4: Run tests — expected 6 passed**

**Step 5: Commit**

```bash
git add models/schemas.py tests/test_schemas.py
git commit -m "feat: add data models for meals, nutrition, recognition, users"
```

---

## Task 4: Database service

**Files:**
- Create: `services/database.py`
- Create: `tests/test_database.py`

**Step 1: Write failing tests**

```python
# tests/test_database.py
import json
import pytest
import pytest_asyncio
from services.database import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_init_creates_tables(db):
    """Tables should exist after init."""
    tables = await db.execute_fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    names = [row[0] for row in tables]
    assert "users" in names
    assert "meals" in names
    assert "glucose_readings" in names
    assert "allowed_users" in names


@pytest.mark.asyncio
async def test_create_and_get_user(db):
    await db.create_user(user_id=123, username="testuser")
    user = await db.get_user(123)
    assert user is not None
    assert user.user_id == 123
    assert user.username == "testuser"
    assert user.onboarding_completed is False


@pytest.mark.asyncio
async def test_get_nonexistent_user(db):
    user = await db.get_user(999)
    assert user is None


@pytest.mark.asyncio
async def test_update_user(db):
    await db.create_user(user_id=123)
    await db.update_user(123, timezone="Europe/Berlin", he_grams=10)
    user = await db.get_user(123)
    assert user.timezone == "Europe/Berlin"
    assert user.he_grams == 10


@pytest.mark.asyncio
async def test_complete_onboarding(db):
    await db.create_user(user_id=123)
    await db.complete_onboarding(123)
    user = await db.get_user(123)
    assert user.onboarding_completed is True
    assert user.consent_given_at is not None


@pytest.mark.asyncio
async def test_save_and_get_meals(db):
    await db.create_user(user_id=123)
    items_json = json.dumps([{"name": "Rice", "weight_g": 200}])
    totals_json = json.dumps({"calories": 260, "he": 4.8})
    await db.save_meal(
        user_id=123, date="2026-04-03",
        items_json=items_json, totals_json=totals_json,
        photo_file_id="abc123", timezone="Europe/Moscow",
    )
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 1
    assert meals[0]["photo_file_id"] == "abc123"


@pytest.mark.asyncio
async def test_delete_last_meal(db):
    await db.create_user(user_id=123)
    items = json.dumps([])
    totals = json.dumps({})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    deleted = await db.delete_last_meal(123)
    assert deleted is True
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 1


@pytest.mark.asyncio
async def test_save_glucose_reading(db):
    await db.create_user(user_id=123)
    await db.save_glucose(user_id=123, value=5.8, date="2026-04-03")
    readings = await db.get_glucose_by_date(123, "2026-04-03")
    assert len(readings) == 1
    assert readings[0]["value"] == 5.8


@pytest.mark.asyncio
async def test_allowed_users(db):
    await db.add_allowed_user(user_id=456, added_by=123)
    assert await db.is_user_allowed(456) is True
    assert await db.is_user_allowed(789) is False
    await db.remove_allowed_user(456)
    assert await db.is_user_allowed(456) is False


@pytest.mark.asyncio
async def test_get_all_allowed_users(db):
    await db.add_allowed_user(456, added_by=123)
    await db.add_allowed_user(789, added_by=123)
    users = await db.get_allowed_users()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_delete_all_user_data(db):
    await db.create_user(user_id=123)
    items = json.dumps([])
    totals = json.dumps({})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    await db.save_glucose(user_id=123, value=5.8, date="2026-04-03")
    await db.delete_all_user_data(123)
    user = await db.get_user(123)
    assert user is None
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 0


@pytest.mark.asyncio
async def test_export_user_data(db):
    await db.create_user(user_id=123, username="test")
    items = json.dumps([{"name": "Rice"}])
    totals = json.dumps({"calories": 260})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    data = await db.export_user_data(123)
    assert "user" in data
    assert "meals" in data
    assert "glucose_readings" in data
    assert data["user"]["user_id"] == 123
    assert len(data["meals"]) == 1
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement services/database.py**

Full async Database class with:
- `init()` — create tables and indexes
- `create_user()`, `get_user()`, `update_user()`, `complete_onboarding()`
- `save_meal()`, `get_meals_by_date()`, `get_meals_week()`, `get_meals_history()`, `delete_last_meal()`
- `save_glucose()`, `get_glucose_by_date()`
- `add_allowed_user()`, `remove_allowed_user()`, `is_user_allowed()`, `get_allowed_users()`
- `delete_all_user_data()`, `export_user_data()`
- `execute_fetchall()` — low-level helper
- `close()`

All queries use parameterized SQL. User model returned as `User` dataclass. Meals and glucose returned as dicts.

**Step 4: Run tests — expected all passed**

**Step 5: Commit**

```bash
git add services/database.py tests/test_database.py
git commit -m "feat: add async database service with full CRUD for users, meals, glucose"
```

---

## Task 5: Auth service (access control, consent, rate limiting)

**Files:**
- Create: `services/auth.py`
- Create: `tests/test_auth.py`

**Step 1: Write failing tests**

```python
# tests/test_auth.py
import pytest
from unittest.mock import AsyncMock
from services.auth import AuthService


@pytest.fixture
def auth():
    db = AsyncMock()
    return AuthService(db=db, admin_ids={100, 200}, rate_limit_requests=3, rate_limit_window=60)


def test_admin_is_always_allowed(auth):
    assert auth.is_admin(100) is True
    assert auth.is_admin(999) is False


@pytest.mark.asyncio
async def test_allowed_user(auth):
    auth.db.is_user_allowed = AsyncMock(return_value=True)
    assert await auth.is_allowed(300) is True


@pytest.mark.asyncio
async def test_admin_always_allowed(auth):
    assert await auth.is_allowed(100) is True
    auth.db.is_user_allowed.assert_not_called()


@pytest.mark.asyncio
async def test_unknown_user_denied(auth):
    auth.db.is_user_allowed = AsyncMock(return_value=False)
    assert await auth.is_allowed(999) is False


def test_rate_limiting(auth):
    for _ in range(3):
        allowed, _ = auth.check_rate_limit(300)
        assert allowed is True
    allowed, wait = auth.check_rate_limit(300)
    assert allowed is False
    assert wait > 0


def test_rate_limit_per_user(auth):
    for _ in range(3):
        auth.check_rate_limit(300)
    # Different user should not be limited
    allowed, _ = auth.check_rate_limit(400)
    assert allowed is True
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement services/auth.py**

AuthService class with:
- `is_admin(user_id)` — check admin_ids set
- `is_allowed(user_id)` — admin check first, then db.is_user_allowed
- `check_rate_limit(user_id)` — in-memory sliding window per user

**Step 4: Run tests — expected all passed**

**Step 5: Commit**

```bash
git add services/auth.py tests/test_auth.py
git commit -m "feat: add auth service with access control and rate limiting"
```

---

## Task 6: LLM service (litellm Router + Google Search fallback)

**Files:**
- Create: `services/llm.py`
- Create: `tests/test_llm.py`

**Step 1: Write failing tests**

```python
# tests/test_llm.py
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from services.llm import LLMService
from models.schemas import RecognitionResult, CalculationResult


@pytest.fixture
def llm_service():
    return LLMService(
        gemini_api_key="test-gemini",
        openrouter_api_key="test-or",
        groq_api_key="test-groq",
    )


def test_service_creates_two_routers(llm_service):
    assert llm_service.vision_router is not None
    assert llm_service.text_router is not None


@pytest.mark.asyncio
async def test_recognize_food_returns_recognition_result(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "items": [{"name": "Rice", "weight_g": 200, "note": ""}],
        "is_food": True,
        "confidence": "high",
    })

    with patch.object(llm_service.vision_router, "acompletion", return_value=mock_response):
        result = await llm_service.recognize_food(
            image_bytes=b"fake-image",
            prompt="test prompt",
            caption=None,
        )

    assert isinstance(result, RecognitionResult)
    assert result.is_food is True
    assert result.items[0].name == "Rice"


@pytest.mark.asyncio
async def test_recognize_food_text(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "items": [{"name": "Soup", "weight_g": 300, "note": ""}],
        "is_food": True,
        "confidence": "medium",
    })

    with patch.object(llm_service.text_router, "acompletion", return_value=mock_response):
        result = await llm_service.recognize_food_text(
            text="soup with bread",
            prompt="test prompt",
        )

    assert result.items[0].name == "Soup"


@pytest.mark.asyncio
async def test_calculate_nutrition(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "items": [{
            "name": "Rice", "weight_g": 200, "calories": 260,
            "protein": 5.0, "fat": 0.6, "carbs": 58.0,
            "fiber": 0.4, "gi": "high", "source": "",
        }],
        "totals": {
            "calories": 260, "protein": 5.0, "fat": 0.6,
            "carbs": 58.0, "fiber": 0.4, "net_carbs": 57.6,
            "he": 4.8, "gi_overall": "high",
        },
    })

    with patch.object(llm_service.text_router, "acompletion", return_value=mock_response):
        result = await llm_service.calculate_nutrition(
            items=[{"name": "Rice", "weight_g": 200}],
            prompt="test prompt",
        )

    assert isinstance(result, CalculationResult)
    assert result.totals.he == 4.8


@pytest.mark.asyncio
async def test_invalid_json_retries(llm_service):
    bad_response = MagicMock()
    bad_response.choices = [MagicMock()]
    bad_response.choices[0].message.content = "not json"

    good_response = MagicMock()
    good_response.choices = [MagicMock()]
    good_response.choices[0].message.content = json.dumps({
        "items": [], "is_food": False, "confidence": "low",
    })

    with patch.object(
        llm_service.text_router, "acompletion",
        side_effect=[bad_response, good_response],
    ):
        result = await llm_service.recognize_food_text(text="test", prompt="test")
        assert result.is_food is False
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement services/llm.py**

LLMService class with:
- `__init__` — creates `vision_router` (Gemini + OpenRouter) and `text_router` (+ Groq)
- `recognize_food(image_bytes, prompt, caption)` — vision chain, returns RecognitionResult
- `recognize_food_text(text, prompt)` — text chain, returns RecognitionResult
- `correct_recognition(previous_items, correction, prompt, image_bytes)` — vision or text chain
- `calculate_nutrition(items, prompt)` — text chain, returns CalculationResult
- `_search_grounding(query)` — Google Search via native google-genai (called when confidence=low)
- `_parse_json(content)` — parse JSON with retry on failure
- Image bytes converted to base64 data URI for litellm message format

**Step 4: Run tests — expected all passed**

**Step 5: Commit**

```bash
git add services/llm.py tests/test_llm.py
git commit -m "feat: add LLM service with litellm Router, vision/text chains, JSON parsing"
```

---

## Task 7: Nutrition formatting service

**Files:**
- Create: `services/nutrition.py`
- Create: `tests/test_nutrition.py`

**Step 1: Write failing tests**

```python
# tests/test_nutrition.py
from models.schemas import MealItem, NutritionItem, NutritionTotals, RecognitionResult, CalculationResult
from services.nutrition import format_recognition, format_calculation, format_daily_summary


def test_format_recognition():
    items = [
        MealItem(name="Гречка", weight_g=200),
        MealItem(name="Курица", weight_g=150, note="варёная"),
    ]
    result = RecognitionResult(items=items, is_food=True, confidence="high")
    text = format_recognition(result, header="🔍 Я вижу:")
    assert "Гречка" in text
    assert "200" in text
    assert "Курица" in text
    assert "варёная" in text


def test_format_recognition_no_food():
    result = RecognitionResult(items=[], is_food=False, confidence="low")
    text = format_recognition(result, header="🔍 Я вижу:", no_food_msg="No food")
    assert text == "No food"


def test_format_calculation():
    items = [
        NutritionItem(name="Гречка", weight_g=200, calories=264, protein=9.5, fat=2.3, carbs=54.0, fiber=3.7, gi="medium"),
    ]
    totals = NutritionTotals(calories=264, protein=9.5, fat=2.3, carbs=54.0, fiber=3.7, net_carbs=50.3, he=4.2, gi_overall="medium")
    result = CalculationResult(items=items, totals=totals)
    text = format_calculation(result)
    assert "264" in text
    assert "4.2" in text  # HE
    assert "ИТОГО" in text or "TOTAL" in text


def test_format_daily_summary():
    text = format_daily_summary(calories=1420, he=13.0, template="Today: {calories} kcal | {he} XE")
    assert "1420" in text
    assert "13.0" in text
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement services/nutrition.py**

Functions:
- `format_recognition(result, header, confirm_msg, no_food_msg)` — format Step 1 output as numbered list
- `format_calculation(result)` — format Step 2 as monospace table with totals, XE, GI
- `format_daily_summary(calories, he, template)` — format daily summary line
- `format_diary_entry(meal, time_format)` — format single diary entry
- `format_diary_day(meals, date, header, empty_msg, total_label)` — format full day diary

All formatting uses HTML tags for Telegram.

**Step 4: Run tests — expected all passed**

**Step 5: Commit**

```bash
git add services/nutrition.py tests/test_nutrition.py
git commit -m "feat: add nutrition formatting service for recognition and calculation output"
```

---

## Task 8: Telegram handlers — start, onboarding, help

**Files:**
- Create: `handlers/start.py`
- Create: `handlers/keyboards.py`
- Create: `tests/test_handlers_start.py`

**Step 1: Implement handlers/keyboards.py**

Keyboard factory functions:
- `main_keyboard(locale)` — Reply keyboard: Today, Week, Sugar, Menu
- `settings_keyboard(locale)` — Reply keyboard: History, Undo, Privacy, Help, Back
- `confirm_keyboard(locale)` — Inline keyboard: Confirm, Cancel
- `consent_keyboard(locale)` — Inline keyboard: Agree, Details
- `timezone_keyboard(locale)` — Inline keyboard: Moscow, Europe, Other
- `he_keyboard(locale)` — Inline keyboard: 12g, 10g, Other
- `delete_confirm_keyboard(locale)` — Inline keyboard: Yes delete, No cancel

All button labels from locale module.

**Step 2: Implement handlers/start.py**

Handlers:
- `start_command(update, context)` — check if onboarded, show welcome or brief help
- `consent_callback(update, context)` — handle Agree/Details inline buttons
- `timezone_callback(update, context)` — handle timezone selection
- `he_callback(update, context)` — handle HE grams selection
- `help_command(update, context)` — show help text

Returns ConversationHandler states for onboarding flow.

**Step 3: Write tests for handler logic**

Test that correct messages are sent and states are returned. Mock Update and Context objects.

**Step 4: Run tests — expected all passed**

**Step 5: Commit**

```bash
git add handlers/start.py handlers/keyboards.py tests/test_handlers_start.py
git commit -m "feat: add start/onboarding/help handlers with keyboard factory"
```

---

## Task 9: Telegram handlers — photo, text, confirm (main flow)

**Files:**
- Create: `handlers/photo.py`
- Create: `handlers/text.py`
- Create: `handlers/confirm.py`
- Create: `tests/test_handlers_flow.py`

**Step 1: Implement handlers/photo.py**

- `handle_photo(update, context)` — download photo bytes, call llm.recognize_food, store in user_data, send recognition with inline confirm keyboard, return AWAITING_CONFIRM

**Step 2: Implement handlers/text.py**

- `handle_text(update, context)` — filter out button presses (delegate to button handler), call llm.recognize_food_text, store in user_data, return AWAITING_CONFIRM

**Step 3: Implement handlers/confirm.py**

- `handle_confirm_callback(update, context)` — ✅ button: call llm.calculate_nutrition, save meal to db, clear user_data, show result, return IDLE
- `handle_cancel_callback(update, context)` — ❌ button: clear user_data, return IDLE
- `handle_correction_text(update, context)` — text correction: call llm.correct_recognition with context, update user_data, show updated recognition, stay AWAITING_CONFIRM

**Step 4: Write tests**

Test each handler with mocked LLM service, database, and Telegram objects. Verify:
- Correct state transitions
- user_data populated/cleared correctly
- Messages sent with correct format

**Step 5: Run tests — expected all passed**

**Step 6: Commit**

```bash
git add handlers/photo.py handlers/text.py handlers/confirm.py tests/test_handlers_flow.py
git commit -m "feat: add photo/text/confirm handlers implementing main food recognition flow"
```

---

## Task 10: Telegram handlers — diary, glucose, admin, privacy

**Files:**
- Create: `handlers/diary.py`
- Create: `handlers/glucose.py`
- Create: `handlers/admin.py`
- Create: `handlers/privacy.py`
- Create: `tests/test_handlers_diary.py`
- Create: `tests/test_handlers_admin.py`

**Step 1: Implement handlers/diary.py**

- `handle_today(update, context)` — get meals by today's date, format diary
- `handle_week(update, context)` — get meals for last 7 days, format weekly stats
- `handle_history(update, context)` — get last N meals, format list
- `handle_undo(update, context)` — delete last meal, confirm

**Step 2: Implement handlers/glucose.py**

- `handle_sugar_button(update, context)` — send prompt, return AWAITING_GLUCOSE
- `handle_glucose_value(update, context)` — parse number, save, return IDLE

**Step 3: Implement handlers/admin.py**

- `handle_adduser(update, context)` — parse user_id, add to allowed_users
- `handle_removeuser(update, context)` — remove from allowed_users
- `handle_listusers(update, context)` — list all allowed users
- Admin check decorator

**Step 4: Implement handlers/privacy.py**

- `handle_privacy(update, context)` — show privacy text
- `handle_export(update, context)` — export data as JSON file
- `handle_delete_data(update, context)` — confirm + delete all user data

**Step 5: Write tests for diary and admin handlers**

**Step 6: Run tests — expected all passed**

**Step 7: Commit**

```bash
git add handlers/diary.py handlers/glucose.py handlers/admin.py handlers/privacy.py tests/test_handlers_diary.py tests/test_handlers_admin.py
git commit -m "feat: add diary, glucose, admin, and privacy handlers"
```

---

## Task 11: Main entry point — wire everything together

**Files:**
- Create: `main.py`
- Modify: `handlers/__init__.py`
- Modify: `services/__init__.py`

**Step 1: Implement main.py**

```python
# main.py — structure outline
"""DiaBot entry point."""

import asyncio
import logging
import os
import signal
import sys

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import load_settings
from services.database import Database
from services.llm import LLMService
from services.auth import AuthService
# ... import all handlers


def main():
    """Initialize and run the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    settings = load_settings()

    # Init services
    db = Database(settings.db_path)
    llm = LLMService(
        gemini_api_key=settings.gemini_api_key,
        openrouter_api_key=settings.openrouter_api_key,
        groq_api_key=settings.groq_api_key,
    )
    auth = AuthService(
        db=db,
        admin_ids=settings.admin_ids,
        rate_limit_requests=settings.rate_limit_requests,
        rate_limit_window=settings.rate_limit_window,
    )

    # Build application
    app = Application.builder().token(settings.telegram_token).build()

    # Store services in bot_data for handler access
    app.bot_data["db"] = db
    app.bot_data["llm"] = llm
    app.bot_data["auth"] = auth
    app.bot_data["settings"] = settings

    # Register ConversationHandler with all states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_command)],
        states={
            # ONBOARDING_CONSENT, ONBOARDING_TIMEZONE, ONBOARDING_HE
            # IDLE — photo, text, buttons, commands
            # AWAITING_CONFIRM — confirm/cancel/correction
            # AWAITING_GLUCOSE — glucose value
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)

    # post_init — initialize database
    async def post_init(application):
        os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
        await db.init()

    async def post_shutdown(application):
        await db.close()

    app.post_init = post_init
    app.post_shutdown = post_shutdown

    # Run polling
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
```

**Step 2: Test manually — bot starts, responds to /start**

Run: `python main.py`
Expected: Bot starts polling, responds to /start with onboarding

**Step 3: Commit**

```bash
git add main.py handlers/__init__.py services/__init__.py
git commit -m "feat: add main entry point, wire all handlers and services together"
```

---

## Task 12: Update CLAUDE.md, README.md, push to GitHub

**Files:**
- Modify: `CLAUDE.md`
- Modify: `README.md`

**Step 1: Update CLAUDE.md with actual commands and architecture**

Reflect final structure: litellm, multi-user, locales, all commands.

**Step 2: Update README.md**

Bilingual (RU + EN). Updated .env variables, commands, deployment instructions.

**Step 3: Commit and push**

```bash
git add CLAUDE.md README.md
git commit -m "docs: update README (bilingual) and CLAUDE.md with final architecture"
git push origin master
```

---

## Task 13: Deploy to VPS "main"

**Files:**
- Modify: `diabot.service` (if needed)

**Step 1: Connect to VPS, create directory**

```bash
ssh main
sudo mkdir -p /opt/diabot
sudo useradd -r -s /bin/false diabot || true
```

**Step 2: Clone repo, setup venv**

```bash
cd /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git .
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

**Step 3: Create .env with real credentials**

```bash
sudo nano /opt/diabot/.env
# Fill in real tokens and keys
```

**Step 4: Install and start systemd service**

```bash
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
sudo systemctl status diabot
```

**Step 5: Verify bot responds in Telegram**

Send /start to the bot, complete onboarding, test photo recognition.

**Step 6: Commit any deploy fixes**

---

## Task Order & Dependencies

```
Task 1 (config) ─────────┐
Task 2 (locales) ─────────┤
Task 3 (schemas) ─────────┼──► Task 6 (LLM) ──┐
                           │                     │
Task 4 (database) ────────┤                     ├──► Task 8 (start handlers) ──┐
Task 5 (auth) ────────────┘                     │                               │
                                                 ├──► Task 9 (main flow) ───────┤
Task 7 (nutrition format) ──────────────────────┘                               │
                                                                                 │
                                           Task 10 (diary/admin/privacy) ───────┤
                                                                                 │
                                           Task 11 (main.py wiring) ◄───────────┘
                                                    │
                                           Task 12 (docs) ◄─────────────────────┘
                                                    │
                                           Task 13 (deploy VPS)
```

Tasks 1-5 can be parallelized. Tasks 6-7 depend on 1-5. Tasks 8-10 depend on 6-7. Task 11 depends on 8-10.
