# Daily Targets & User Profile — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add user physical profile, daily KBJU targets with Mifflin-St Jeor calculation, progress bars in diary and after meals, /settings command.

**Architecture:** Extend existing User model and DB schema with profile fields and target fields. New `services/profile.py` calculates defaults. Extended onboarding flow with 5 new states. Progress formatting in `services/nutrition.py`. New `/settings` handler. Compact progress after meals in `handlers/confirm.py`.

**Tech Stack:** Python 3.11+, aiosqlite, python-telegram-bot 21+

**Design doc:** `docs/plans/2026-04-03-daily-targets-design.md`

---

## Task 1: Profile calculation service

**Files:**
- Create: `services/profile.py`
- Create: `tests/test_profile.py`

**Step 1: Write failing tests**

```python
# tests/test_profile.py
"""Tests for profile calculation service."""

from services.profile import calculate_targets


def test_calculate_targets_female():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    assert targets["calories"] > 0
    assert targets["protein"] > 0
    assert targets["fat"] > 0
    assert targets["carbs"] > 0
    # Female BMR = 10*58 + 6.25*165 - 5*27 - 161 = 580 + 1031.25 - 135 - 161 = 1315.25
    # TDEE = 1315.25 * 1.4 = 1841
    assert targets["calories"] == 1841


def test_calculate_targets_male():
    targets = calculate_targets(gender="male", height_cm=180, weight_kg=80, age=30)
    # Male BMR = 10*80 + 6.25*180 - 5*30 + 5 = 800 + 1125 - 150 + 5 = 1780
    # TDEE = 1780 * 1.4 = 2492
    assert targets["calories"] == 2492


def test_protein_is_1g_per_kg():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    assert targets["protein"] == 58


def test_fat_is_30_percent():
    targets = calculate_targets(gender="male", height_cm=180, weight_kg=80, age=30)
    # fat = 30% of 2492 / 9 = 83
    assert targets["fat"] == 83


def test_carbs_is_remainder():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    # protein_cal = 58*4 = 232, fat_cal = targets["fat"]*9, carbs = (1841 - 232 - fat_cal) / 4
    protein_cal = targets["protein"] * 4
    fat_cal = targets["fat"] * 9
    expected_carbs = round((targets["calories"] - protein_cal - fat_cal) / 4)
    assert targets["carbs"] == expected_carbs
```

**Step 2: Run tests — expected FAIL**

**Step 3: Implement services/profile.py**

```python
# services/profile.py
"""User profile calculations — daily nutrition targets."""


def calculate_targets(
    gender: str,
    height_cm: int,
    weight_kg: float,
    age: int,
    activity_factor: float = 1.4,
) -> dict[str, int]:
    """Calculate daily nutrition targets using Mifflin-St Jeor formula.

    Args:
        gender: "male" or "female".
        height_cm: Height in centimeters.
        weight_kg: Weight in kilograms.
        age: Age in years.
        activity_factor: Activity multiplier (default 1.4 = light activity).

    Returns:
        Dict with calories, protein, fat, carbs (all integers).
    """
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    tdee = round(bmr * activity_factor)

    protein = round(weight_kg)  # 1g per kg
    fat = round(tdee * 0.30 / 9)  # 30% of calories from fat
    carbs = round((tdee - protein * 4 - fat * 9) / 4)  # remainder

    return {
        "calories": tdee,
        "protein": protein,
        "fat": fat,
        "carbs": max(carbs, 0),
    }
```

**Step 4: Run tests — expected PASS**

**Step 5: Commit**

```bash
git add services/profile.py tests/test_profile.py
git commit -m "feat: add profile calculation service (Mifflin-St Jeor)"
```

---

## Task 2: Database schema migration + User model update

**Files:**
- Modify: `services/database.py` — add columns, new methods
- Modify: `models/schemas.py` — add fields to User
- Modify: `tests/test_database.py` — add tests for new fields

**Step 1: Add new fields to User dataclass in models/schemas.py**

Add after `created_at`:
```python
    gender: str | None = None
    height_cm: int | None = None
    weight_kg: float | None = None
    age: int | None = None
    target_calories: int | None = None
    target_protein: int | None = None
    target_fat: int | None = None
    target_carbs: int | None = None
```

**Step 2: Update _create_tables in services/database.py**

Add new columns to the CREATE TABLE users statement:
```sql
gender TEXT,
height_cm INTEGER,
weight_kg REAL,
age INTEGER,
target_calories INTEGER,
target_protein INTEGER,
target_fat INTEGER,
target_carbs INTEGER
```

Also add a migration method that runs ALTER TABLE for existing databases:
```python
async def _migrate_tables(self) -> None:
    """Add new columns to existing tables (safe if already exist)."""
    new_columns = [
        ("users", "gender", "TEXT"),
        ("users", "height_cm", "INTEGER"),
        ("users", "weight_kg", "REAL"),
        ("users", "age", "INTEGER"),
        ("users", "target_calories", "INTEGER"),
        ("users", "target_protein", "INTEGER"),
        ("users", "target_fat", "INTEGER"),
        ("users", "target_carbs", "INTEGER"),
    ]
    for table, column, col_type in new_columns:
        try:
            await self._db.execute(
                f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"
            )
        except Exception:
            pass  # Column already exists
    await self._db.commit()
```

Call `_migrate_tables()` at the end of `init()`.

**Step 3: Update get_user to read new fields**

Add to the User construction in `get_user`:
```python
gender=row["gender"],
height_cm=row["height_cm"],
weight_kg=row["weight_kg"],
age=row["age"],
target_calories=row["target_calories"],
target_protein=row["target_protein"],
target_fat=row["target_fat"],
target_carbs=row["target_carbs"],
```

**Step 4: Add method get_day_totals**

```python
async def get_day_totals(self, user_id: int, date: str) -> dict:
    """Get aggregated nutrition totals for a day."""
    meals = await self.get_meals_by_date(user_id, date)
    totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "fiber": 0, "he": 0}
    for meal in meals:
        import json
        mt = json.loads(meal.get("totals_json", "{}"))
        for key in totals:
            totals[key] += mt.get(key, 0)
    return totals
```

**Step 5: Write tests for new DB functionality**

```python
@pytest.mark.asyncio
async def test_user_profile_fields(db):
    await db.create_user(user_id=123)
    await db.update_user(123, gender="female", height_cm=165, weight_kg=58, age=27)
    user = await db.get_user(123)
    assert user.gender == "female"
    assert user.height_cm == 165
    assert user.weight_kg == 58
    assert user.age == 27

@pytest.mark.asyncio
async def test_user_target_fields(db):
    await db.create_user(user_id=123)
    await db.update_user(123, target_calories=1800, target_protein=65, target_fat=60, target_carbs=225)
    user = await db.get_user(123)
    assert user.target_calories == 1800
    assert user.target_carbs == 225

@pytest.mark.asyncio
async def test_get_day_totals(db):
    await db.create_user(user_id=123)
    import json
    totals1 = json.dumps({"calories": 287, "protein": 8.2, "fat": 5.1, "carbs": 52.3, "fiber": 2.0, "he": 4.0})
    totals2 = json.dumps({"calories": 452, "protein": 45.0, "fat": 4.5, "carbs": 58.3, "fiber": 3.0, "he": 4.4})
    await db.save_meal(user_id=123, date="2026-04-03", items_json="[]", totals_json=totals1)
    await db.save_meal(user_id=123, date="2026-04-03", items_json="[]", totals_json=totals2)
    day = await db.get_day_totals(123, "2026-04-03")
    assert day["calories"] == 739
    assert day["he"] == 8.4
```

**Step 6: Run all tests — expected PASS**

**Step 7: Commit**

```bash
git add models/schemas.py services/database.py tests/test_database.py
git commit -m "feat: add user profile and target fields to DB schema"
```

---

## Task 3: Progress bar formatting

**Files:**
- Modify: `services/nutrition.py` — add progress bar functions
- Modify: `tests/test_nutrition.py` — add tests

**Step 1: Write failing tests**

```python
from services.nutrition import format_progress_bar, format_compact_progress, format_full_progress

def test_format_progress_bar():
    bar = format_progress_bar(50, 100, width=15)
    assert "▓" in bar
    assert "░" in bar
    assert "50%" in bar

def test_format_progress_bar_zero():
    bar = format_progress_bar(0, 100, width=15)
    assert "0%" in bar

def test_format_progress_bar_over_100():
    bar = format_progress_bar(120, 100, width=15)
    assert "120%" in bar

def test_format_progress_bar_no_target():
    bar = format_progress_bar(50, None, width=15)
    assert bar == ""

def test_format_compact_progress():
    day_totals = {"calories": 440, "protein": 24, "fat": 10, "carbs": 105, "he": 8.8}
    targets = {"calories": 1800, "protein": 65, "fat": 60, "carbs": 225}
    he_target = 225 / 12  # 18.75
    text = format_compact_progress(day_totals, targets, he_target)
    assert "105/225" in text
    assert "🔸" in text  # carbs accent
    assert "🔹" in text  # rest

def test_format_full_progress():
    day_totals = {"calories": 739, "protein": 53.2, "fat": 9.6, "carbs": 110, "he": 8.4}
    targets = {"calories": 1800, "protein": 65, "fat": 60, "carbs": 225}
    he_target = 18.8
    text = format_full_progress(day_totals, targets, he_target)
    assert "▓" in text
    assert "Углеводы" in text or "Carbs" in text
```

**Step 2: Implement functions in services/nutrition.py**

```python
def format_progress_bar(current: float, target: float | None, width: int = 15) -> str:
    """Format a text progress bar."""
    if target is None or target <= 0:
        return ""
    pct = current / target * 100
    filled = min(round(pct / 100 * width), width)
    bar = "▓" * filled + "░" * (width - filled)
    return f"{bar} {pct:.0f}%"


def format_compact_progress(
    day_totals: dict,
    targets: dict,
    he_target: float,
) -> str:
    """Format compact progress line shown after each meal."""
    carbs = day_totals.get("carbs", 0)
    he = day_totals.get("he", 0)
    cal = day_totals.get("calories", 0)
    protein = day_totals.get("protein", 0)
    fat = day_totals.get("fat", 0)

    t_carbs = targets.get("carbs", 0)
    t_cal = targets.get("calories", 0)
    t_protein = targets.get("protein", 0)
    t_fat = targets.get("fat", 0)

    carb_pct = round(carbs / t_carbs * 100) if t_carbs else 0
    he_str = f"{he:.1f}/{he_target:.1f}" if he_target else f"{he:.1f}"
    cal_pct = round(cal / t_cal * 100) if t_cal else 0
    p_pct = round(protein / t_protein * 100) if t_protein else 0
    f_pct = round(fat / t_fat * 100) if t_fat else 0

    lines = [
        f"🔸 У: {carbs:.0f}/{t_carbs}г ({carb_pct}%) | ХЕ: {he_str}",
        f"🔹 К: {cal:.0f}/{t_cal} ({cal_pct}%) | Б: {protein:.0f}/{t_protein}г ({p_pct}%) | Ж: {fat:.0f}/{t_fat}г ({f_pct}%)",
    ]
    return "\n".join(lines)


def format_full_progress(
    day_totals: dict,
    targets: dict,
    he_target: float,
    width: int = 15,
) -> str:
    """Format full progress bars for /today diary."""
    carbs = day_totals.get("carbs", 0)
    he = day_totals.get("he", 0)
    cal = day_totals.get("calories", 0)
    protein = day_totals.get("protein", 0)
    fat = day_totals.get("fat", 0)

    t = targets
    lines = []

    # Carbs and XE first (diabetes accent)
    bar = format_progress_bar(carbs, t.get("carbs"), width)
    lines.append(f"Углеводы: {bar} ({carbs:.0f}/{t.get('carbs', 0)}г)")

    bar = format_progress_bar(he, he_target, width)
    lines.append(f"ХЕ:       {bar} ({he:.1f}/{he_target:.1f})")

    bar = format_progress_bar(cal, t.get("calories"), width)
    lines.append(f"Калории:  {bar} ({cal:.0f}/{t.get('calories', 0)})")

    bar = format_progress_bar(protein, t.get("protein"), width)
    lines.append(f"Белок:    {bar} ({protein:.0f}/{t.get('protein', 0)}г)")

    bar = format_progress_bar(fat, t.get("fat"), width)
    lines.append(f"Жиры:     {bar} ({fat:.0f}/{t.get('fat', 0)}г)")

    return "<pre>" + "\n".join(lines) + "</pre>"
```

**Step 3: Run tests — expected PASS**

**Step 4: Commit**

```bash
git add services/nutrition.py tests/test_nutrition.py
git commit -m "feat: add progress bar and compact progress formatting"
```

---

## Task 4: New locale strings

**Files:**
- Modify: `locales/ru.py` — add onboarding, settings, progress strings
- Modify: `locales/en.py` — same strings in English

**Step 1: Add strings to ru.py**

```python
# --- Onboarding profile ---
ONBOARDING_GENDER = "👤 {name}, какой у тебя пол?"
GENDER_FEMALE = "👩 Женский"
GENDER_MALE = "👨 Мужской"
ONBOARDING_HEIGHT = "📏 Какой у тебя рост (см)?"
HEIGHT_155 = "155"
HEIGHT_160 = "160"
HEIGHT_165 = "165"
HEIGHT_170 = "170"
HEIGHT_175 = "175"
HEIGHT_OTHER = "Другой"
ONBOARDING_WEIGHT = "⚖️ {name}, введи свой вес в кг:"
ONBOARDING_AGE = "🎂 Сколько тебе лет?"
ONBOARDING_TARGETS_SHOW = (
    "📊 {name}, на основе твоих данных, твои суточные нормы:\n\n"
    "  Калории: {calories} ккал\n"
    "  Белок: {protein} г\n"
    "  Жиры: {fat} г\n"
    "  Углеводы: {carbs} г ({he} ХЕ)\n\n"
    "Всё верно?"
)
TARGETS_CONFIRM = "✅ Подтвердить"
TARGETS_EDIT = "✏️ Изменить"
ONBOARDING_TARGETS_EDIT = (
    "Введи свои нормы в формате:\n"
    "<code>калории белок жиры углеводы</code>\n"
    "Например: <code>1800 65 60 225</code>"
)
ONBOARDING_TARGETS_INVALID = "⚠️ Введи 4 числа через пробел: калории белок жиры углеводы"

# --- Settings ---
SETTINGS_HEADER = (
    "⚙️ <b>Настройки</b>\n\n"
    "Часовой пояс: {timezone}\n"
    "ХЕ: {he_grams} г\n"
    "Пол: {gender} | Рост: {height} | Вес: {weight} | Возраст: {age}\n\n"
    "<b>Суточные нормы:</b>\n"
    "  Калории: {calories} ккал\n"
    "  Белок: {protein} г\n"
    "  Жиры: {fat} г\n"
    "  Углеводы: {carbs} г"
)
SETTINGS_EDIT_TARGETS = "✏️ Изменить нормы"
SETTINGS_EDIT_PROFILE = "📏 Изменить данные"
SETTINGS_SAVED = "✅ Настройки сохранены!"
GENDER_DISPLAY_MALE = "Муж"
GENDER_DISPLAY_FEMALE = "Жен"
GENDER_DISPLAY_NONE = "—"

# --- Migration prompt for existing users ---
TARGETS_SETUP_PROMPT = (
    "{name}, я добавил отслеживание суточных норм!\n"
    "Хочешь настроить? Это займёт минуту."
)
TARGETS_SETUP_NOW = "📏 Настроить"
TARGETS_SETUP_LATER = "⏭ Потом"
```

**Step 2: Add equivalent strings to en.py**

Same constant names, English translations.

**Step 3: Run locale key parity test**

Run: `python -m pytest tests/test_locales.py::test_all_locales_have_same_keys -v`
Expected: PASS

**Step 4: Commit**

```bash
git add locales/ru.py locales/en.py
git commit -m "feat: add locale strings for profile, targets, settings, progress"
```

---

## Task 5: Onboarding extension (new states + handlers)

**Files:**
- Modify: `handlers/__init__.py` — add new states
- Modify: `handlers/start.py` — add gender/height/weight/age/targets handlers
- Modify: `handlers/keyboards.py` — add new keyboards
- Modify: `main.py` — register new states

**Step 1: Add states to handlers/__init__.py**

```python
ONBOARDING_GENDER = 6
ONBOARDING_HEIGHT = 7
ONBOARDING_WEIGHT = 8
ONBOARDING_AGE = 9
ONBOARDING_TARGETS_CONFIRM = 10
```

**Step 2: Add keyboards to handlers/keyboards.py**

```python
def gender_keyboard(locale) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(locale.GENDER_FEMALE, callback_data="gender_female"),
        InlineKeyboardButton(locale.GENDER_MALE, callback_data="gender_male"),
    ]]
    return InlineKeyboardMarkup(keyboard)

def height_keyboard(locale) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(locale.HEIGHT_155, callback_data="height_155"),
            InlineKeyboardButton(locale.HEIGHT_160, callback_data="height_160"),
            InlineKeyboardButton(locale.HEIGHT_165, callback_data="height_165"),
        ],
        [
            InlineKeyboardButton(locale.HEIGHT_170, callback_data="height_170"),
            InlineKeyboardButton(locale.HEIGHT_175, callback_data="height_175"),
            InlineKeyboardButton(locale.HEIGHT_OTHER, callback_data="height_custom"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def targets_confirm_keyboard(locale) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(locale.TARGETS_CONFIRM, callback_data="targets_confirm"),
        InlineKeyboardButton(locale.TARGETS_EDIT, callback_data="targets_edit"),
    ]]
    return InlineKeyboardMarkup(keyboard)

def settings_keyboard_inline(locale) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(locale.SETTINGS_EDIT_TARGETS, callback_data="settings_targets"),
        InlineKeyboardButton(locale.SETTINGS_EDIT_PROFILE, callback_data="settings_profile"),
    ]]
    return InlineKeyboardMarkup(keyboard)

def targets_setup_keyboard(locale) -> InlineKeyboardMarkup:
    keyboard = [[
        InlineKeyboardButton(locale.TARGETS_SETUP_NOW, callback_data="targets_setup_now"),
        InlineKeyboardButton(locale.TARGETS_SETUP_LATER, callback_data="targets_setup_later"),
    ]]
    return InlineKeyboardMarkup(keyboard)
```

**Step 3: Add handler functions to handlers/start.py**

After the existing HE handlers, add:

- `handle_he_callback` and `handle_he_text` — change return to `ONBOARDING_GENDER` instead of IDLE (and don't call `complete_onboarding` yet)
- `handle_gender_callback` — save gender, ask height → `ONBOARDING_HEIGHT`
- `handle_height_callback` — save height, ask weight → `ONBOARDING_WEIGHT`
- `handle_height_text` — custom height input
- `handle_weight_text` — save weight, ask age → `ONBOARDING_AGE`
- `handle_age_text` — save age, calculate targets, show summary → `ONBOARDING_TARGETS_CONFIRM`
- `handle_targets_confirm_callback` — save targets, complete onboarding → IDLE
- `handle_targets_edit_text` — parse "cal protein fat carbs", save, complete → IDLE

**Step 4: Update main.py ConversationHandler with new states**

Add states for ONBOARDING_GENDER through ONBOARDING_TARGETS_CONFIRM.

**Step 5: Test manually — full onboarding flow**

**Step 6: Commit**

```bash
git add handlers/__init__.py handlers/start.py handlers/keyboards.py main.py
git commit -m "feat: extend onboarding with profile and daily targets"
```

---

## Task 6: Compact progress after meals

**Files:**
- Modify: `handlers/confirm.py` — add progress after meal save
- Modify: `services/nutrition.py` — ensure format_compact_progress handles locales

**Step 1: In handle_confirm, after saving meal, add progress**

After the meal is saved and formatted, before sending the response:
```python
# Get day totals for progress
day_totals = await db.get_day_totals(user.user_id, local_date)

# Show progress if targets are set
progress_text = ""
if user.target_calories:
    targets = {
        "calories": user.target_calories,
        "protein": user.target_protein,
        "fat": user.target_fat,
        "carbs": user.target_carbs,
    }
    he_target = user.target_carbs / user.he_grams if user.target_carbs else 0
    progress_text = "\n" + format_compact_progress(day_totals, targets, he_target)
```

Append `progress_text` to the final message.

**Step 2: Test manually — confirm meal, see progress**

**Step 3: Commit**

```bash
git add handlers/confirm.py
git commit -m "feat: show compact progress after each meal"
```

---

## Task 7: Full progress in /today

**Files:**
- Modify: `handlers/diary.py` — add progress bars to /today output

**Step 1: In handle_today, after formatting meals, add progress bars**

After the diary text is built, if user has targets:
```python
if user.target_calories:
    day_totals = await db.get_day_totals(user.user_id, local_date)
    targets = {
        "calories": user.target_calories,
        "protein": user.target_protein,
        "fat": user.target_fat,
        "carbs": user.target_carbs,
    }
    he_target = user.target_carbs / user.he_grams if user.target_carbs else 0
    diary_text += "\n\n" + format_full_progress(day_totals, targets, he_target)
```

**Step 2: Test manually**

**Step 3: Commit**

```bash
git add handlers/diary.py
git commit -m "feat: add progress bars to /today diary"
```

---

## Task 8: Settings handler

**Files:**
- Create: `handlers/settings.py`
- Modify: `handlers/text.py` — route settings button
- Modify: `main.py` — register settings handlers

**Step 1: Create handlers/settings.py**

```python
# Show settings with current profile and targets
# Handle "Edit targets" → prompt for 4 numbers
# Handle "Edit profile" → restart gender/height/weight/age flow
# Handle settings_targets/settings_profile callbacks
```

**Step 2: Add BTN_MENU routing to /settings in handlers/text.py**

Change the BTN_MENU handler to call handle_settings instead of showing HELP_TEXT with settings_keyboard.

**Step 3: Register in main.py**

Add settings callbacks to IDLE state.

**Step 4: Test manually**

**Step 5: Commit**

```bash
git add handlers/settings.py handlers/text.py main.py
git commit -m "feat: add /settings command with profile and target editing"
```

---

## Task 9: Existing user migration prompt

**Files:**
- Modify: `handlers/diary.py` — check for null targets on /today

**Step 1: At the start of handle_today, check if targets are set**

```python
if user and user.onboarding_completed and user.target_calories is None:
    # Show setup prompt
    await update.message.reply_text(
        fmt(locale.TARGETS_SETUP_PROMPT, update),
        parse_mode=ParseMode.HTML,
        reply_markup=targets_setup_keyboard(locale),
    )
    # Still show the diary below (without progress bars)
```

**Step 2: Handle targets_setup_now callback → redirect to gender step**

**Step 3: Handle targets_setup_later callback → dismiss**

**Step 4: Test manually with existing user (delete target fields)**

**Step 5: Commit**

```bash
git add handlers/diary.py
git commit -m "feat: prompt existing users to set up daily targets"
```

---

## Task 10: Deploy and test

**Step 1: Run all tests**

```bash
python -m pytest tests/ -v
```

**Step 2: Push to GitHub**

```bash
git push origin master
```

**Step 3: Deploy to VPS**

```bash
ssh root@95.85.234.200 "cd /opt/diabot && git pull && systemctl restart diabot"
```

**Step 4: Test full flow in Telegram**

- New user: full onboarding with profile
- /today with progress bars
- /settings — view and edit
- Photo → confirm → compact progress

**Step 5: Commit any fixes**

---

## Task Dependencies

```
Task 1 (profile calc) ──┐
Task 2 (DB schema) ─────┼──► Task 4 (locale strings) ──► Task 5 (onboarding) ──┐
Task 3 (progress bars) ──┘                                                       │
                                                         Task 6 (compact) ◄──────┤
                                                         Task 7 (/today) ◄───────┤
                                                         Task 8 (settings) ◄─────┤
                                                         Task 9 (migration) ◄────┘
                                                         Task 10 (deploy)
```

Tasks 1-3 can be parallelized. Task 4 depends on knowing the full scope. Tasks 5-9 are sequential. Task 10 is final.
