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
