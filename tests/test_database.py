"""Tests for database service."""

import json
import pytest
import pytest_asyncio
from services.database import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    database = Database(str(tmp_path / "test.db"))
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_init_creates_tables(db):
    tables = await db.execute_fetchall(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    names = [row[0] for row in tables]
    assert "users" in names
    assert "meals" in names
    assert "glucose_readings" in names
    assert "allowed_users" in names


@pytest.mark.asyncio
async def test_create_and_get_user(db):
    await db.create_user(user_id=123, username="testuser")
    user = await db.get_user(123)
    assert user is not None
    assert user.user_id == 123
    assert user.username == "testuser"
    assert user.onboarding_completed is False


@pytest.mark.asyncio
async def test_get_nonexistent_user(db):
    user = await db.get_user(999)
    assert user is None


@pytest.mark.asyncio
async def test_update_user(db):
    await db.create_user(user_id=123)
    await db.update_user(123, timezone="Europe/Berlin", he_grams=10)
    user = await db.get_user(123)
    assert user.timezone == "Europe/Berlin"
    assert user.he_grams == 10


@pytest.mark.asyncio
async def test_complete_onboarding(db):
    await db.create_user(user_id=123)
    await db.complete_onboarding(123)
    user = await db.get_user(123)
    assert user.onboarding_completed is True
    assert user.consent_given_at is not None


@pytest.mark.asyncio
async def test_save_and_get_meals(db):
    await db.create_user(user_id=123)
    items_json = json.dumps([{"name": "Rice", "weight_g": 200}])
    totals_json = json.dumps({"calories": 260, "he": 4.8})
    await db.save_meal(
        user_id=123, date="2026-04-03",
        items_json=items_json, totals_json=totals_json,
        photo_file_id="abc123", timezone="Europe/Moscow",
    )
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 1
    assert meals[0]["photo_file_id"] == "abc123"


@pytest.mark.asyncio
async def test_delete_last_meal(db):
    await db.create_user(user_id=123)
    items = json.dumps([])
    totals = json.dumps({})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    deleted = await db.delete_last_meal(123)
    assert deleted is True
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 1


@pytest.mark.asyncio
async def test_delete_last_meal_empty(db):
    deleted = await db.delete_last_meal(999)
    assert deleted is False


@pytest.mark.asyncio
async def test_save_glucose_reading(db):
    await db.create_user(user_id=123)
    await db.save_glucose(user_id=123, value=5.8, date="2026-04-03")
    readings = await db.get_glucose_by_date(123, "2026-04-03")
    assert len(readings) == 1
    assert readings[0]["value"] == 5.8


@pytest.mark.asyncio
async def test_allowed_users(db):
    await db.add_allowed_user(user_id=456, added_by=123)
    assert await db.is_user_allowed(456) is True
    assert await db.is_user_allowed(789) is False
    await db.remove_allowed_user(456)
    assert await db.is_user_allowed(456) is False


@pytest.mark.asyncio
async def test_get_all_allowed_users(db):
    await db.add_allowed_user(456, added_by=123)
    await db.add_allowed_user(789, added_by=123)
    users = await db.get_allowed_users()
    assert len(users) == 2


@pytest.mark.asyncio
async def test_delete_all_user_data(db):
    await db.create_user(user_id=123)
    items = json.dumps([])
    totals = json.dumps({})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    await db.save_glucose(user_id=123, value=5.8, date="2026-04-03")
    await db.delete_all_user_data(123)
    user = await db.get_user(123)
    assert user is None
    meals = await db.get_meals_by_date(123, "2026-04-03")
    assert len(meals) == 0


@pytest.mark.asyncio
async def test_export_user_data(db):
    await db.create_user(user_id=123, username="test")
    items = json.dumps([{"name": "Rice"}])
    totals = json.dumps({"calories": 260})
    await db.save_meal(user_id=123, date="2026-04-03", items_json=items, totals_json=totals)
    data = await db.export_user_data(123)
    assert "user" in data
    assert "meals" in data
    assert "glucose_readings" in data
    assert data["user"]["user_id"] == 123
    assert len(data["meals"]) == 1


@pytest.mark.asyncio
async def test_meals_history(db):
    await db.create_user(user_id=123)
    items = json.dumps([])
    totals = json.dumps({})
    for i in range(10):
        await db.save_meal(user_id=123, date=f"2026-04-{i+1:02d}", items_json=items, totals_json=totals)
    history = await db.get_meals_history(123, limit=3)
    assert len(history) == 3


@pytest.mark.asyncio
async def test_user_profile_fields(db):
    await db.create_user(user_id=123)
    await db.update_user(123, gender="female", height_cm=165, weight_kg=58.0, age=27)
    user = await db.get_user(123)
    assert user.gender == "female"
    assert user.height_cm == 165
    assert user.weight_kg == 58.0
    assert user.age == 27


@pytest.mark.asyncio
async def test_user_target_fields(db):
    await db.create_user(user_id=123)
    await db.update_user(123, target_calories=1800, target_protein=65, target_fat=60, target_carbs=225)
    user = await db.get_user(123)
    assert user.target_calories == 1800
    assert user.target_carbs == 225


@pytest.mark.asyncio
async def test_get_day_totals(db):
    await db.create_user(user_id=123)
    import json
    totals1 = json.dumps({"calories": 287, "protein": 8.2, "fat": 5.1, "carbs": 52.3, "fiber": 2.0, "he": 4.0})
    totals2 = json.dumps({"calories": 452, "protein": 45.0, "fat": 4.5, "carbs": 58.3, "fiber": 3.0, "he": 4.4})
    await db.save_meal(user_id=123, date="2026-04-03", items_json="[]", totals_json=totals1)
    await db.save_meal(user_id=123, date="2026-04-03", items_json="[]", totals_json=totals2)
    day = await db.get_day_totals(123, "2026-04-03")
    assert day["calories"] == 739
    assert abs(day["he"] - 8.4) < 0.01


@pytest.mark.asyncio
async def test_get_day_totals_empty(db):
    await db.create_user(user_id=123)
    day = await db.get_day_totals(123, "2026-04-03")
    assert day["calories"] == 0
