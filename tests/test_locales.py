from locales import get_locale, AVAILABLE_LANGUAGES


def test_get_russian_locale():
    locale = get_locale("ru")
    assert locale.LANG == "ru"
    assert locale.BTN_TODAY
    assert locale.RECOGNITION_PROMPT
    assert locale.CALCULATION_PROMPT


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
    assert "Русский" in ru.RECOGNITION_PROMPT
    assert "English" in en.RECOGNITION_PROMPT


def test_available_languages():
    assert "ru" in AVAILABLE_LANGUAGES
    assert "en" in AVAILABLE_LANGUAGES


def test_all_locales_have_same_keys():
    ru = get_locale("ru")
    en = get_locale("en")
    ru_keys = {k for k in dir(ru) if not k.startswith("_")}
    en_keys = {k for k in dir(en) if not k.startswith("_")}
    assert ru_keys == en_keys, f"Missing in en: {ru_keys - en_keys}, Extra in en: {en_keys - ru_keys}"
