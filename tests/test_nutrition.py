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


from services.nutrition import format_progress_bar, format_compact_progress, format_full_progress


def test_format_progress_bar_half():
    bar = format_progress_bar(50, 100, width=10)
    assert "▓" * 5 in bar
    assert "░" * 5 in bar
    assert "50%" in bar


def test_format_progress_bar_zero():
    bar = format_progress_bar(0, 100, width=10)
    assert "0%" in bar
    assert "░" * 10 in bar


def test_format_progress_bar_full():
    bar = format_progress_bar(100, 100, width=10)
    assert "▓" * 10 in bar
    assert "100%" in bar


def test_format_progress_bar_over():
    bar = format_progress_bar(150, 100, width=10)
    assert "150%" in bar
    assert "▓" * 10 in bar  # capped at width


def test_format_progress_bar_no_target():
    assert format_progress_bar(50, None) == ""
    assert format_progress_bar(50, 0) == ""


def test_format_compact_progress():
    day_totals = {"calories": 440, "protein": 24, "fat": 10, "carbs": 105, "he": 8.8}
    targets = {"calories": 1800, "protein": 65, "fat": 60, "carbs": 225}
    text = format_compact_progress(day_totals, targets, he_target=18.8)
    assert "🔸" in text
    assert "🔹" in text
    assert "105/225" in text
    assert "8.8/18.8" in text


def test_format_full_progress():
    day_totals = {"calories": 739, "protein": 53.2, "fat": 9.6, "carbs": 110, "he": 8.4}
    targets = {"calories": 1800, "protein": 65, "fat": 60, "carbs": 225}
    text = format_full_progress(day_totals, targets, he_target=18.8)
    assert "▓" in text
    assert "Углеводы" in text
    assert "ХЕ" in text
    assert "<pre>" in text
