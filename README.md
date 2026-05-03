# 🍽 DiaBot — non-commercial AI nutrition assistant for type 1 diabetes

[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial%201.0.0-9d6cff)](LICENSE)
[![Stars](https://img.shields.io/github/stars/CreatmanCEO/diabot?style=flat&color=yellow)](https://github.com/CreatmanCEO/diabot/stargazers)
[![Validate](https://github.com/CreatmanCEO/diabot/actions/workflows/validate.yml/badge.svg)](https://github.com/CreatmanCEO/diabot/actions/workflows/validate.yml)
[![Status](https://img.shields.io/badge/status-active%20development-22c55e)](#status--non-commercial-use-only)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-26A5E4.svg)](https://core.telegram.org/bots/api)

🇬🇧 English · [🇷🇺 Русский](README.ru.md)

**Open-source non-commercial Telegram bot for people with type 1 diabetes. Built for friends and family by a sibling-of-T1D developer, shared with the community. Active development — contributors welcome under non-commercial terms.**

---

## Why this exists

Every meal for a person with type 1 diabetes is a math problem. You estimate the carbohydrates on your plate, convert them to bread units (XE), and calculate the insulin dose. An error of 1–2 XE can cause hypoglycaemia or hyperglycaemia — hospitalisation, loss of consciousness, coma. People do this 4–6 times a day, every day, for the rest of their lives.

DiaBot turns carb counting into a single action: **send a photo — get the result.** AI recognises the food, the user confirms or corrects, the bot calculates KBJU and bread units, writes a diary entry, and shows progress against daily targets. Carbs and XE are always rendered first — because that is what insulin dose depends on.

## Status — non-commercial use only

This project is in **active development** and shared under the [PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0) licence. You may run it for yourself, your family, or a friends-and-family circle. **Commercial use — including hosting it as a paid service or bundling it into a paid product — is not permitted.** Contributors are welcome under the same terms.

The bot needs help with: tighter LLM prompting, more precise dietetic calculations, user-facing answer verification, integration with external KBJU databases (USDA, OpenFoodFacts, regional sources), and regional adaptation. See [Roadmap & known limitations](#roadmap--known-limitations) and [`CONTRIBUTING.md`](CONTRIBUTING.md) for the priority list.

## What it looks like

> UI shown in Russian (default locale). English locale also fully supported — language follows the user's Telegram preference.

<table>
  <tr>
    <td colspan="2" align="center"><img src="docs/screenshots/01-kbju-result.png" width="640" alt="Result after corrections — bot returns updated item list (multigrain bread 60 g, cheese 30 g, brisket 70 g), monospace KBJU table per item with Calories / Protein / Fat / Carbs columns, totals 419 kcal · carbs 24 g (fibre 3 g) · digestible carbs 21 g · 1.8 XE · low GI, plus daily progress 886 kcal / 7.6 XE / 96 of 351 g carbs (27%)"/></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><b>Final result — KBJU table + daily progress</b><br><sub>The whole loop in one screen: per-item nutrition, totals, carbs / digestible carbs / XE / GI separately highlighted, and daily progress bar against the user's targets.</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/02-photo-recognition.png" width="320" alt="Photo recognition step — user sent a photo of brisket on a wooden board with cheese and bread next to it, bot replied 'I can see: 1. Rye bread ~60 g, 2. Cheese ~30 g, 3. Meat (probably smoked turkey or beef brisket) ~70 g (thinly sliced)' followed by Confirm and Cancel inline buttons"/></td>
    <td align="center"><img src="docs/screenshots/03-daily-report.png" width="320" alt="Daily report — date header, list of three meals with timestamps and per-meal calories / carbs / XE, totals row, daily progress bars for calories / carbs / fat / protein with percentages"/></td>
  </tr>
  <tr>
    <td align="center"><b>Photo recognition</b><br><sub>Send a photo. The vision LLM names items and estimates portions in grams. Two-step confirmation is the safety mechanism — the user has the final word before insulin is dosed against these numbers.</sub></td>
    <td align="center"><b>Daily diary</b><br><sub><code>/today</code> shows every meal with timestamps and per-meal totals, plus daily progress bars. <code>/week</code> aggregates seven days. <code>/history N</code> walks back further.</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/04-onboarding-setup.png" width="320" alt="Onboarding setup — bot asks for gender, height, weight, age, automatically computes daily KBJU targets via the Mifflin-St Jeor formula, user can override manually if a dietician has prescribed different values"/></td>
    <td align="center"><img src="docs/screenshots/05-onboard-confirm.png" width="320" alt="Onboarding confirm step — bot summarises the entered profile and target values for review and waits for the user to confirm before going to IDLE state"/></td>
  </tr>
  <tr>
    <td align="center"><b>Onboarding</b><br><sub>Five-step setup: consent → gender → height → weight → age → targets. KBJU targets auto-computed via Mifflin-St Jeor; manual override is one tap away if a dietician has prescribed different values.</sub></td>
    <td align="center"><b>Profile confirmation</b><br><sub>Final review before the IDLE state. All inputs are stored locally in SQLite and visible to the user via <code>/export</code>; deletable via <code>/delete_my_data</code>.</sub></td>
  </tr>
</table>

## Architecture

![Recognition pipeline: Telegram → handlers → litellm Router with two chains (vision + text) → user confirmation → nutrition + database → daily progress; Google Search grounding for low-confidence branded products](docs/architecture.svg)

| Layer | Technology | Notes |
|---|---|---|
| Language | Python 3.11+, fully async | one event loop, no thread pools |
| Telegram | `python-telegram-bot` 21+ | polling mode, `ConversationHandler` for state |
| LLM router | `litellm` Router with two chains | vision (Gemini 2.5 Flash → OpenRouter Gemini) + text (Gemini → OpenRouter → Groq Llama 4) |
| Search grounding | `google-genai` | Google Search tool — fallback for low-confidence branded products |
| Database | SQLite via `aiosqlite` | no ORM, plain SQL, schema fits in one file |
| Config | `python-dotenv` | frozen `Settings` dataclass validated at start |
| Deployment | systemd unit included | runs as a non-privileged user under `/opt/diabot/` |
| Tests | 72 pytest cases | covers every handler and service |

## How it works

1. **Send a photo** of your meal (or describe it in text)
2. **Bot recognises** items and portions via the vision LLM
3. **Confirm or correct** — the bot prints what it saw, you adjust if anything is off
4. **Get KBJU + XE** — calculation with carbs prioritised
5. **Track progress** — diary, weekly stats, progress bars towards daily targets

## Key features

**Food recognition**
- 📷 Photo → AI recognition of products and portions
- ✏️ Text-based food description (no photo needed)
- 📷+✏️ Photo with caption for extra context
- 🏷 Branded-product recognition with Google Search grounding for rare brands

**Precise calculation**
- 🔢 Calories, protein, fat, carbohydrates (KBJU)
- 🍞 Bread units (XE / HE) — configurable ratio (default 1 XE = 12 g carbs)
- 🎯 Carbs always rendered first — insulin dosing priority
- ✅ Two-step flow: recognise → confirm → save

**Daily targets and progress**
- 👤 Profile: gender, height, weight, age
- 📊 Automatic target calculation via Mifflin-St Jeor
- ✍️ Manual target override (for dietician-prescribed values)
- 📈 Compact progress after every meal
- ▓▓▓░░░ Visual progress bars in the diary

**Food diary**
- 📅 Today's diary with per-meal breakdown (`/today`)
- 📊 Weekly statistics (`/week`)
- 📜 Meal history (`/history N`)
- ↩️ Undo last entry (`/undo`)
- 🩸 Glucose readings tracking (`/sugar`)

**Privacy and data**
- 🔒 Consent on first launch with data-processing details
- 🚫 Photos are NEVER saved to disk — only Telegram `file_id` is stored
- 📦 Full data export (`/export` as JSON)
- 🗑 Complete data deletion (`/delete_my_data`)
- ✅ GDPR-style compliance

**Multi-user**
- 👥 Self-hosted with admin approval workflow
- 📩 User requests access → admin gets notification → user is notified back
- ⚡ Per-user rate limiting

## Roadmap & known limitations

> **Safety disclaimer.** This is an assistance tool, **not a medical device**. Always cross-check critical carb counts before insulin dosing. The two-step recognise → confirm flow is safety-critical, not cosmetic — do not skip it. Not a substitute for an endocrinologist or a dietician.

### Active improvements (contributors welcome)

- **Tighter LLM prompting** — stricter JSON-schema validation, lower temperature, deterministic portion estimation
- **More precise dietetic calculations** — verified portion-size heuristics, glycaemic load, fibre subtraction in digestible carbs
- **User-facing answer verification** — confidence scores per item, explicit "double-check this" flag at low confidence
- **External KBJU databases** — [USDA FoodData Central](https://fdc.nal.usda.gov/), [OpenFoodFacts](https://world.openfoodfacts.org/), regional Russian / Eastern-European sources
- **Regional adaptation** — EU / US / RU / Asia food norms and cuisines, branded products, locally common dishes

### Current limits

- LLM may misidentify food (poor lighting, small portions, regional dishes, unusual angles). The two-step confirmation exists exactly because of this.
- No CGM integration yet
- Bilingual prompts mostly tested in RU; EN locale verification is ongoing
- Google Search grounding is available only for the Gemini chain — OpenRouter / Groq fallbacks do not support it yet
- Onboarding asks for body metrics in metric units only — imperial conversion is on the backlog

## Quick start

```bash
git clone https://github.com/CreatmanCEO/diabot.git
cd diabot
python -m venv venv
source venv/bin/activate              # Linux / macOS — on Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python main.py
```

### Environment variables

| Variable | Description | Required |
|---|---|:---:|
| `TELEGRAM_TOKEN` | Bot token from @BotFather | yes |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | yes |
| `GEMINI_API_KEY` | Google AI Studio API key | * |
| `OPENROUTER_API_KEY` | OpenRouter API key | * |
| `GROQ_API_KEY` | Groq API key | * |
| `DEFAULT_TIMEZONE` | Default timezone (`Europe/Moscow`) | no |
| `DEFAULT_HE_GRAMS` | Grams of carbs per 1 XE (`12`) | no |
| `DEFAULT_LANGUAGE` | Default language (`ru`) | no |
| `RATE_LIMIT_REQUESTS` | Per-user requests per hour (`30`) | no |
| `DB_PATH` | Path to SQLite database | no |

\* At least one LLM API key required. Photo recognition needs `GEMINI_API_KEY` or `OPENROUTER_API_KEY`.

### Deploy (systemd)

```bash
sudo useradd -r -s /bin/false diabot
sudo mkdir -p /opt/diabot
sudo git clone https://github.com/CreatmanCEO/diabot.git /opt/diabot
cd /opt/diabot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env                                # fill in tokens
sudo cp diabot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable diabot
sudo systemctl start diabot
```

## Project structure

```
diabot/
├── main.py                     # Entry point, ConversationHandler wiring
├── config.py                   # Settings dataclass from .env (frozen, validated)
├── handlers/                   # Telegram handlers (thin I/O, no business logic)
│   ├── start.py                # /start, 5-step onboarding, /help
│   ├── photo.py                # Food photo recognition pipeline
│   ├── text.py                 # Text food input + reply keyboard routing
│   ├── confirm.py              # Confirmation, correction, cancellation
│   ├── diary.py                # /today, /week, /history, /undo
│   ├── glucose.py              # /sugar — glucose readings
│   ├── settings.py             # Profile / target editing, admin panel
│   ├── admin.py                # /adduser, /removeuser, /listusers, approval workflow
│   ├── privacy.py              # /privacy, /export, /delete_my_data, consent
│   └── keyboards.py            # Keyboard factory (reply + inline)
├── services/                   # Business logic (no Telegram imports)
│   ├── llm.py                  # litellm Router, two chains, auto-failover
│   ├── nutrition.py            # KBJU formatting, progress bars, XE calculation
│   ├── database.py             # aiosqlite CRUD
│   └── auth.py                 # Access control, rate limiting, approval queue
├── models/schemas.py           # Dataclasses: MealItem, User, NutritionTarget, …
├── locales/                    # i18n strings + LLM prompts (tied to language)
│   ├── ru.py                   # Russian (default)
│   └── en.py                   # English
├── docs/
│   ├── architecture.svg        # this README's pipeline diagram
│   ├── plans/                  # design docs and implementation plans
│   └── screenshots/            # README assets
├── tests/                      # 72 automated tests (pytest)
├── diabot.service              # systemd unit
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CLAUDE.md                   # Claude Code project constitution
└── LICENSE                     # PolyForm Noncommercial 1.0.0
```

## State machine

```
ONBOARDING: consent → gender → height → weight → age → targets → IDLE
IDLE ↔ AWAITING_CONFIRM   (food recognition flow)
IDLE ↔ AWAITING_GLUCOSE    (glucose recording)
```

## Design decisions

- **Handlers are thin** — every business decision lives in `services/`. Handlers only do Telegram I/O.
- **Two LLM chains** — vision (Gemini → OpenRouter) for photos; text (Gemini → OpenRouter → Groq Llama 4) for descriptions. `litellm` Router handles automatic failover.
- **Google Search grounding** — when the primary model returns low confidence on a branded product, a separate `google-genai` call with the Search tool retrieves accurate KBJU.
- **Carb accuracy over calorie accuracy** — reflected in prompts, formatting, and UI ordering. Insulin dosing depends on carb precision; calories are secondary.
- **No ORM** — plain SQL with `aiosqlite`. The schema fits in one file; an ORM would add complexity without benefit.
- **Photos never touch disk** — only Telegram `file_id` is stored. Image bytes are fetched on demand and passed directly to the LLM API as bytes.
- **Two-step confirmation is a safety mechanism** — recognition → confirm. Without explicit confirmation no meal is saved and no insulin guidance is implied.

## Working on it

The project is configured for [Claude Code](https://code.claude.com) as the primary development driver — see [`CLAUDE.md`](CLAUDE.md) for the project constitution. The same author maintains a [Claude Code Anti-Regression Setup](https://github.com/CreatmanCEO/claude-code-antiregression-setup) — that pattern is what keeps the 72-test suite green during refactors.

Run tests:

```bash
python -m pytest tests/ -v
```

Per-iteration design docs live in `docs/plans/`. New work starts with a design doc, then code follows.

## Contributing

PRs are welcome under the same non-commercial terms as the project. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for priorities (LLM prompt-tightening, dietetic accuracy, answer verification, external KBJU databases, regional adaptation, native localisations beyond RU/EN).

## Related

- [Claude Code Anti-Regression Setup](https://github.com/CreatmanCEO/claude-code-antiregression-setup) — sister repo by the same author. The `.claude/` config + subagents + hooks pattern that keeps the 72-test suite green during refactors.
- [ai-context-hierarchy](https://github.com/CreatmanCEO/ai-context-hierarchy) — sister repo. Three-level context system used by Claude Code on this project.
- [claude-statusline](https://github.com/CreatmanCEO/claude-statusline) — sister repo. Statusline for Claude Code with VPS monitoring.
- [lingua-companion](https://github.com/CreatmanCEO/lingua-companion) — sister product from the same author — a voice-first English tutor for Russian-speaking IT professionals. Different domain, same engineering discipline.

## Author

**Nick Podolyak** — Python developer and digital architect at [CREATMAN](https://creatman.site)

- GitHub: [@CreatmanCEO](https://github.com/CreatmanCEO)
- Habr: [creatman](https://habr.com/ru/users/creatman/)
- dev.to: [@creatman](https://dev.to/creatman)

## License

[PolyForm Noncommercial 1.0.0](LICENSE) · Nick Podolyak. Non-commercial use only — see the [Status](#status--non-commercial-use-only) section.
