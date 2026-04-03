"""Tests for LLM service."""

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


def test_vision_router_none_without_key():
    service = LLMService(groq_api_key="only-groq")
    assert service.vision_router is None


def test_text_router_accepts_groq_only():
    service = LLMService(groq_api_key="groq-key")
    assert service.text_router is not None


@pytest.mark.asyncio
async def test_recognize_food_returns_result(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "items": [{"name": "Rice", "weight_g": 200, "note": ""}],
        "is_food": True,
        "confidence": "high",
    })

    with patch.object(llm_service.vision_router, "acompletion", return_value=mock_response):
        result = await llm_service.recognize_food(
            image_bytes=b"fake-image", prompt="test prompt", caption=None,
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
        result = await llm_service.recognize_food_text(text="soup with bread", prompt="test prompt")

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
            items=[{"name": "Rice", "weight_g": 200}], prompt="test prompt",
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


@pytest.mark.asyncio
async def test_correct_recognition_with_photo(llm_service):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "items": [{"name": "Rice", "weight_g": 150, "note": "corrected"}],
        "is_food": True,
        "confidence": "high",
    })

    prompt = "Previous: {previous_items}\nCorrection: {correction_text}"
    with patch.object(llm_service.vision_router, "acompletion", return_value=mock_response):
        result = await llm_service.correct_recognition(
            previous_items=[{"name": "Rice", "weight_g": 200}],
            correction="less rice, about 150g",
            prompt=prompt,
            image_bytes=b"fake-image",
        )

    assert result.items[0].weight_g == 150


def test_parse_json_from_code_block():
    content = '```json\n{"items": [], "is_food": false, "confidence": "low"}\n```'
    result = LLMService._parse_json(content)
    assert result["is_food"] is False
