# Contributing

Thanks for considering a contribution. **Important: this project is licensed under [PolyForm Noncommercial 1.0.0](LICENSE).** Contributions are welcome under the same terms — code you submit becomes part of a non-commercial project, and you agree that you (and downstream users) are not allowed to use it commercially. If you need a commercial licence, contact the author first.

DiaBot is in active development. The core flow works end to end — but several layers need genuine improvement. **Contributors with diabetes / dietetics / endocrinology backgrounds are especially welcome** because the gaps below are domain-knowledge gaps, not just engineering gaps.

## Priorities (highest impact first)

1. **Tighter LLM prompting & schema validation.** The vision chain currently estimates portions in a relatively loose way. PRs welcome to: lower temperature, add explicit JSON-schema constraints, validate units more strictly, return confidence per item, retry on schema violations with a tighter follow-up prompt. Files to look at: `services/llm.py`, `locales/ru.py` and `locales/en.py` (prompts live in the locale files because they are language-tied).
2. **More precise dietetic calculations.** Verified portion-size heuristics, glycaemic load (not just GI label), fibre subtraction in digestible carbs, lactose handling, protein-impact-on-glucose for high-protein meals. Files: `services/nutrition.py`, `models/schemas.py`.
3. **User-facing answer verification.** Add an explicit confidence score per recognised item, render it in the confirmation card, surface a "double-check this" flag at low confidence, prompt the user to weigh portions when the LLM is uncertain. Files: `services/llm.py` (return structured confidence), `handlers/confirm.py` (render).
4. **External KBJU database integration.** Today the bot relies entirely on the LLM for KBJU values. Adding [USDA FoodData Central](https://fdc.nal.usda.gov/), [OpenFoodFacts](https://world.openfoodfacts.org/), or regional Russian / Eastern-European sources as a verification layer would make values much more reliable. Sketch: after recognition, look up each item in the external DB, fall back to LLM only on miss.
5. **Regional adaptation.** Food norms and cuisines differ between EU / US / RU / Asia. Branded products differ. Locally common dishes are recognised unevenly. Roadmap: locale-specific prompt addenda, locale-specific external DB priority, optional locale flag in the user profile.
6. **Native localisations beyond RU / EN.** New locale files in `locales/<code>.py` mirroring the structure of `ru.py` / `en.py`. Translation must include both UI strings and LLM prompts (they are tied to language).

## What we will not merge

- Anything that bypasses the two-step confirmation flow. The `recognise → confirm` step is safety-critical; do not "optimise" it away even if it adds a tap.
- Changes that expose more LLM raw output to the user without confirmation. The bot's response always passes through human review.
- Anything that stores food photos to disk. Only Telegram `file_id` is stored; bytes are streamed and discarded.
- Hard dependencies on a single LLM provider. The whole point of the `litellm` Router is auto-failover; do not collapse the chain.
- Commercial-use forks or features that gate functionality behind a paywall. The licence forbids commercial use.

## Pull request checklist

- [ ] `python -m pytest tests/ -v` — all 72 tests pass (and any new tests you added pass)
- [ ] `python -m py_compile $(git ls-files '*.py')` clean
- [ ] If you touched a handler: thin I/O only — business logic moved into `services/`
- [ ] If you touched LLM prompts: both `locales/ru.py` and `locales/en.py` updated
- [ ] If user-visible behaviour changed: both `README.md` and `README.ru.md` mirrored
- [ ] `CHANGELOG.md` entry added under a new minor / patch version
- [ ] No new file written to disk for user data without an explicit `/export` / `/delete_my_data` path
- [ ] Adheres to the existing code style (English code / comments / docstrings, type hints everywhere, HTML parse_mode for Telegram, no hardcoded user-facing strings)

## Style

- All code, comments, docstrings in **English**. Bot-facing strings only in `locales/`.
- Logging via `logging` (INFO for actions, DEBUG for LLM requests). No `print()`.
- Telegram messages use HTML parse_mode (not Markdown). Existing helpers handle escaping.
- LLM responses use JSON mode (`response_format: json_object`) with retry on invalid JSON.
- One feature per PR. Stack PRs if you have multiple.

## Author / maintainer

[@CreatmanCEO](https://github.com/CreatmanCEO) — Nick Podolyak. Open an issue first for anything larger than a single fix or a single locale.
