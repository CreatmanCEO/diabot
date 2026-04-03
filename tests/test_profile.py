"""Tests for profile calculation service."""

from services.profile import calculate_targets


def test_calculate_targets_female():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    # Female BMR = 10*58 + 6.25*165 - 5*27 - 161 = 1315.25
    # TDEE = round(1315.25 * 1.4) = 1841
    assert targets["calories"] == 1841


def test_calculate_targets_male():
    targets = calculate_targets(gender="male", height_cm=180, weight_kg=80, age=30)
    # Male BMR = 10*80 + 6.25*180 - 5*30 + 5 = 1780
    # TDEE = round(1780 * 1.4) = 2492
    assert targets["calories"] == 2492


def test_protein_is_1g_per_kg():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    assert targets["protein"] == 58


def test_fat_is_30_percent():
    targets = calculate_targets(gender="male", height_cm=180, weight_kg=80, age=30)
    assert targets["fat"] == round(2492 * 0.30 / 9)


def test_carbs_is_remainder():
    targets = calculate_targets(gender="female", height_cm=165, weight_kg=58, age=27)
    protein_cal = targets["protein"] * 4
    fat_cal = targets["fat"] * 9
    expected_carbs = round((targets["calories"] - protein_cal - fat_cal) / 4)
    assert targets["carbs"] == expected_carbs


def test_all_values_positive():
    targets = calculate_targets(gender="female", height_cm=150, weight_kg=45, age=60)
    assert all(v >= 0 for v in targets.values())
