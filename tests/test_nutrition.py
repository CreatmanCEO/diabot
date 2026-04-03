"""Tests for nutrition formatting service."""

import json
from models.schemas import (
    MealItem, NutritionItem, NutritionTotals,
    RecognitionResult, CalculationResult,
)
from services.nutrition import (
    format_recognition, format_calculation, format_calculation_summary,
    format_daily_summary, format_diary_entry, format_diary_day,
)


def test_format_recognition():
    items = [
        MealItem(name="Гречка", weight_g=200),
        MealItem(name="Курица", weight_g=150, note="варёная"),
    ]
    result = RecognitionResult(items=items, is_food=True, confidence="high")
    text = format_recognition(result, header="🔍 Я вижу:", confirm_msg="Верно?")
    assert "Гречка" in text
    assert "200" in text
    assert "Курица" in text
    assert "варёная" in text
    assert "Верно?" in text


def test_format_recognition_no_food():
    result = RecognitionResult(items=[], is_food=False, confidence="low")
    text = format_recognition(result, header="Header", no_food_msg="No food here")
    assert text == "No food here"


def test_format_calculation():
    items = [
        NutritionItem(name="Гречка", weight_g=200, calories=264, protein=9.5, fat=2.3, carbs=54.0, fiber=3.7, gi="medium"),
    ]
    totals = NutritionTotals(calories=264, protein=9.5, fat=2.3, carbs=54.0, fiber=3.7, net_carbs=50.3, he=4.2, gi_overall="medium")
    result = CalculationResult(items=items, totals=totals)
    text = format_calculation(result)
    assert "264" in text
    assert "<pre>" in text
    assert "ИТОГО" in text


def test_format_calculation_summary():
    totals = NutritionTotals(calories=264, protein=9.5, fat=2.3, carbs=54.0, fiber=3.7, net_carbs=50.3, he=4.2, gi_overall="medium")
    text = format_calculation_summary(totals)
    assert "4.2 ХЕ" in text
    assert "50.3" in text
    assert "средний" in text


def test_format_daily_summary():
    text = format_daily_summary(calories=1420, he=13.0, template="Today: {calories} kcal | {he} XE")
    assert "1420" in text
    assert "13.0" in text


def test_format_diary_entry():
    meal = {
        "timestamp": "2026-04-03T13:15:00",
        "items_json": json.dumps([{"name": "Гречка"}, {"name": "Курица"}]),
        "totals_json": json.dumps({"calories": 452, "protein": 45.0, "fat": 4.5, "carbs": 58.3, "he": 4.4}),
    }
    text = format_diary_entry(meal)
    assert "13:15" in text
    assert "Гречка" in text
    assert "452" in text


def test_format_diary_day():
    meals = [
        {
            "timestamp": "2026-04-03T08:30:00",
            "items_json": json.dumps([{"name": "Овсянка"}]),
            "totals_json": json.dumps({"calories": 287, "protein": 8.2, "fat": 5.1, "carbs": 52.3, "he": 4.0}),
        },
        {
            "timestamp": "2026-04-03T13:15:00",
            "items_json": json.dumps([{"name": "Гречка"}, {"name": "Курица"}]),
            "totals_json": json.dumps({"calories": 452, "protein": 45.0, "fat": 4.5, "carbs": 58.3, "he": 4.4}),
        },
    ]
    text = format_diary_day(
        meals, date="3 апреля 2026",
        header_template="📊 Дневник за {date}:",
        empty_template="📭 За {date} записей нет.",
        total_label="ИТОГО за день:",
    )
    assert "3 апреля 2026" in text
    assert "Овсянка" in text
    assert "ИТОГО за день:" in text
    assert "8.4" in text  # total HE = 4.0 + 4.4


def test_format_diary_day_empty():
    text = format_diary_day(
        [], date="3 апреля 2026",
        header_template="📊 Дневник за {date}:",
        empty_template="📭 За {date} записей нет.",
        total_label="ИТОГО:",
    )
    assert "записей нет" in text
