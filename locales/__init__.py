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
