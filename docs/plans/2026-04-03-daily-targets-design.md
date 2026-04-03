# Daily Targets & User Profile — Design Document

**Date:** 2026-04-03
**Status:** Approved

## Overview

Add user physical profile (gender, height, weight, age) and daily nutrition targets (calories, protein, fat, carbs). Calculate defaults via Mifflin-St Jeor formula, allow manual override. Show progress after each meal and in daily diary.

## Key Decisions

| Decision | Choice |
|----------|--------|
| Target source | Hybrid: calculated from profile, user can override |
| Tracked targets | Full KBJU: calories, protein, fat, carbs (+ XE derived) |
| Visual accent | Carbs/XE first (diabetes focus), rest secondary |
| Progress display | After meal: compact format. /today: full progress bars |
| Data collection | In onboarding (new users) + /settings (existing/changes) |
| Existing users | Prompt at first /today if targets not set |

## Database Changes

```sql
ALTER TABLE users ADD COLUMN gender TEXT;           -- male/female
ALTER TABLE users ADD COLUMN height_cm INTEGER;
ALTER TABLE users ADD COLUMN weight_kg REAL;
ALTER TABLE users ADD COLUMN age INTEGER;
ALTER TABLE users ADD COLUMN target_calories INTEGER;
ALTER TABLE users ADD COLUMN target_protein INTEGER;
ALTER TABLE users ADD COLUMN target_fat INTEGER;
ALTER TABLE users ADD COLUMN target_carbs INTEGER;
```

## Mifflin-St Jeor Formula

```
Male:   BMR = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
Female: BMR = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
TDEE = BMR * 1.4 (light activity default)

Protein: 1g per kg body weight
Fat: 30% of TDEE / 9
Carbs: (TDEE - protein*4 - fat*9) / 4
XE target: carbs / he_grams
```

## Onboarding (new steps after HE)

```
ONBOARDING_GENDER = 6
ONBOARDING_HEIGHT = 7
ONBOARDING_WEIGHT = 8
ONBOARDING_AGE = 9
ONBOARDING_TARGETS_CONFIRM = 10
```

Flow:
```
[after HE] → Gender: [Female] [Male]
→ Height: [155] [160] [165] [170] [175] [Other]
→ Weight: text input "Enter weight in kg:"
→ Age: text input "How old are you?"
→ Show calculated targets:
  "Based on your data, {name}, your daily targets:
   Calories: 1800 kcal
   Protein: 65g
   Fat: 60g
   Carbs: 225g (18.8 XE)

   All correct?"
   [✅ Confirm] [✏️ Edit]
→ Complete onboarding
```

## After Meal (compact progress, format B)

```
📝 Saved, {name}!
🔸 Carbs: 105/225g (47%) | XE: 8.8/18.8
🔹 Cal: 440/1800 (24%) | P: 24/65g (37%) | F: 10/60g (17%)
```

Carbs/XE on first line with 🔸 (diabetes accent). Rest with 🔹 compact.

## /today (full progress bars)

```
📊 Diary for April 3, {name}:

🕐 08:30 — Oatmeal, banana, coffee
  287 kcal | P 8.2 | F 5.1 | C 52.3 | 4.0 XE

🕐 13:15 — Buckwheat, chicken, salad
  452 kcal | P 45.0 | F 4.5 | C 58.3 | 4.4 XE

━━━━━━━━━━━━━━━━━━━
Carbs:    ▓▓▓▓▓▓▓░░░░░░░░ 49% (110/225g)
XE:       ▓▓▓▓▓▓▓░░░░░░░░ 45% (8.4/18.8)
Calories: ▓▓▓▓▓░░░░░░░░░░ 41% (739/1800)
Protein:  ▓▓▓▓▓▓▓▓▓▓▓░░░░ 82% (53.2/65g)
Fat:      ▓▓░░░░░░░░░░░░░ 16% (9.6/60g)
```

## /settings command

```
⚙️ Settings:

Timezone: Europe/Moscow
XE: 12g
Gender: Female | Height: 165 | Weight: 58 | Age: 27

Daily targets:
  Calories: 1800 kcal
  Protein: 65g
  Fat: 60g
  Carbs: 225g

[✏️ Edit targets] [📏 Edit profile]
```

## Existing Users Migration

On first /today after update, if target_calories IS NULL:
```
"{name}, I've added daily target tracking!
Want to set up? Takes a minute."
[📏 Set up] [⏭ Later]
```

If user skips, show diary without progress bars. Targets = NULL means "not configured".

## New Locale Strings

- Onboarding: gender prompt, height prompt, weight prompt, age prompt, targets summary, edit targets
- Progress: compact format template, full progress bar format
- Settings: settings display, edit prompts
- Migration: setup prompt for existing users

## Files Affected

- `services/database.py` — ALTER TABLE, new update methods
- `models/schemas.py` — add fields to User dataclass
- `services/nutrition.py` — add progress bar formatting, compact progress
- `services/profile.py` (new) — Mifflin-St Jeor calculation
- `handlers/__init__.py` — new states
- `handlers/start.py` — new onboarding steps
- `handlers/settings.py` (new) — /settings command
- `handlers/confirm.py` — add compact progress after meal
- `handlers/diary.py` — add progress bars to /today
- `handlers/text.py` — route settings button
- `handlers/keyboards.py` — new keyboards for onboarding steps, settings
- `locales/ru.py`, `locales/en.py` — new strings
- `main.py` — register new states and handlers
