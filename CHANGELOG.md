# Changelog

All notable changes to this project will be documented in this file.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · [SemVer](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-05-03

### Changed

- **License changed from MIT → PolyForm Noncommercial 1.0.0.** This project is non-commercial: it was built for friends and family by a sibling-of-T1D developer and is shared with the community for personal / family use only. Commercial use — including hosting it as a paid service or bundling it into a paid product — is not permitted.

### Added

- `LICENSE` is now the official PolyForm Noncommercial 1.0.0 text (replacing the previous MIT license)
- `README.ru.md` — full Russian version mirroring the new English structure (the previous bilingual inline format has been split into two locale files for consistency with sister repos and easier translation maintenance)
- Hero `Status — non-commercial use only` callout linking to the license and the contributor priorities
- `Roadmap & known limitations` section grouping safety disclaimer, active improvements (LLM prompt-tightening, dietetic accuracy, user-facing answer verification, external KBJU databases, regional adaptation), and current limits (LLM misidentification edge cases, no CGM integration, EN-locale verification ongoing, grounding only on Gemini chain, metric units only)
- Hero screenshot `docs/screenshots/01-kbju-result.png` — final KBJU table + daily progress
- Four supporting screenshots — `02-photo-recognition`, `03-daily-report`, `04-onboarding-setup`, `05-onboard-confirm` — arranged in a 2-column gallery with captions
- `docs/architecture.svg` — pipeline diagram (Telegram → handlers → litellm Router with two chains → user confirmation gate → nutrition + database → daily progress, with Google Search grounding sidecar)
- `CHANGELOG.md` (this file) — earlier history reconstructed below from `git log` / commit messages
- `CONTRIBUTING.md` with explicit non-commercial clause and a concrete priority list
- `.github/workflows/validate.yml` — runs the 72-test pytest suite on push and PR, plus `python -m py_compile` on every `.py`, SVG well-formed XML, internal Markdown links resolve, presence of `LICENSE` and `CHANGELOG.md`
- "Stars" and "Validate CI" badges; static `Tests: 72` badge replaced with the dynamic Validate badge
- "Related" section cross-linking to all sister Claude Code repos by the same author (anti-regression-setup, ai-context-hierarchy, claude-statusline, lingua-companion)
- Author signature expanded with full name and Habr / dev.to profile links
- Local `tests/manual screenshots/` paths and any deployment URLs are deliberately omitted from the public README per author instruction

### Notes

- Topics on GitHub applied separately via `gh api` after merge.
- Default branch remains `master` for now; rename to `main` deferred to a separate change because it would invalidate any external bookmarks / CI badges pointing at `master`.

## [0.2.0] — 2026-04-03

### Added — initial portfolio-quality README & live fixes
- Bilingual inline RU/EN `README.md` rewritten as a portfolio piece (commit `f0745f0`)
- `CLAUDE.md` aligned with the README (same commit)
- `PicklePersistence` for `python-telegram-bot` so the bot survives systemd restarts without losing in-flight conversations (commit `eceebf4`)
- All command handlers added as `entry_points` so the bot works even if a user types `/today` before `/start` (commit `41acab9`)
- Service injection in `post_init` after persistence restore — fixes a race where the database service was unavailable to the conversation handler on cold start (commit `ecb735d`)
- Correction-prompt always returns `is_food=true` and falls back to the original items when the LLM produces an empty correction — prevents silent food deletion on edit (commit `59c1a30`)
- `allow_reentry=False` on `entry_points` to prevent the user from accidentally re-entering onboarding while in the middle of a correction (commit `2619043`)
- LLM response handler tolerates unexpected fields like `volume_ml` that some providers add (commit `fb9811b`)
- Access check moved to before onboarding; database reference fix in settings (commit `0f638e1`)

### Architecture (as of this version)

- Two LLM chains via `litellm` Router with auto-failover: vision (Gemini 2.5 Flash → OpenRouter Gemini) for photos, text (Gemini → OpenRouter → Groq Llama 4) for descriptions
- Google Search grounding via `google-genai` for low-confidence branded products
- 72 pytest cases covering every handler and service
- `diabot.service` systemd unit for production
- Privacy-first: photos never written to disk (only Telegram `file_id`), `/export`, `/delete_my_data`, GDPR-style consent on first launch
- Multi-user with admin approval workflow (admins from `.env`, additional users via `/adduser` / approval queue)

## [0.1.0] — earlier

### Added
- Initial implementation: photo → recognition → confirm → KBJU + XE → diary
- Onboarding state machine: consent → gender → height → weight → age → targets
- Daily KBJU targets via the Mifflin-St Jeor formula with manual override
- Reply keyboard for navigation, inline keyboard for confirmation
- SQLite via `aiosqlite` for users / meals / glucose / targets
- Bilingual i18n (RU default, EN fully supported) with prompts living next to the locale strings in `locales/`
- 1 XE = 12 g carbs default, configurable per user
