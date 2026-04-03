from models.schemas import MealItem, NutritionItem, NutritionTotals, RecognitionResult, CalculationResult, User


def test_meal_item_creation():
    item = MealItem(name="Buckwheat", weight_g=200, note="boiled")
    assert item.name == "Buckwheat"
    assert item.weight_g == 200
    assert item.note == "boiled"


def test_meal_item_default_note():
    item = MealItem(name="Chicken", weight_g=150)
    assert item.note == ""


def test_nutrition_totals():
    totals = NutritionTotals(
        calories=452, protein=45.0, fat=4.5, carbs=58.3,
        fiber=5.2, net_carbs=53.1, he=4.4, gi_overall="medium",
    )
    assert totals.he == 4.4


def test_recognition_result():
    items = [MealItem(name="Rice", weight_g=200)]
    result = RecognitionResult(items=items, is_food=True, confidence="high")
    assert result.is_food
    assert len(result.items) == 1


def test_recognition_result_from_dict():
    data = {
        "items": [{"name": "Rice", "weight_g": 200, "note": ""}],
        "is_food": True,
        "confidence": "high",
    }
    result = RecognitionResult.from_dict(data)
    assert result.items[0].name == "Rice"


def test_recognition_result_from_dict_missing_fields():
    data = {"items": [], "is_food": False}
    result = RecognitionResult.from_dict(data)
    assert result.confidence == "low"
    assert result.is_food is False


def test_calculation_result_from_dict():
    data = {
        "items": [
            {
                "name": "Rice", "weight_g": 200, "calories": 260,
                "protein": 5.0, "fat": 0.6, "carbs": 58.0,
                "fiber": 0.4, "gi": "high", "source": "",
            }
        ],
        "totals": {
            "calories": 260, "protein": 5.0, "fat": 0.6,
            "carbs": 58.0, "fiber": 0.4, "net_carbs": 57.6,
            "he": 4.8, "gi_overall": "high",
        },
    }
    result = CalculationResult.from_dict(data)
    assert result.totals.he == 4.8
    assert result.items[0].calories == 260


def test_user_defaults():
    user = User(user_id=123)
    assert user.timezone == "Europe/Moscow"
    assert user.he_grams == 12
    assert user.language == "ru"
    assert user.onboarding_completed is False
    assert user.consent_given_at is None
