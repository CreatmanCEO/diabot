"""User profile calculations — daily nutrition targets."""


def calculate_targets(
    gender: str,
    height_cm: int,
    weight_kg: float,
    age: int,
    activity_factor: float = 1.4,
) -> dict[str, int]:
    """Calculate daily nutrition targets using Mifflin-St Jeor formula.

    Args:
        gender: "male" or "female".
        height_cm: Height in centimeters.
        weight_kg: Weight in kilograms.
        age: Age in years.
        activity_factor: Activity multiplier (default 1.4 = light activity).

    Returns:
        Dict with calories, protein, fat, carbs (all integers).
    """
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    tdee = round(bmr * activity_factor)

    protein = round(weight_kg)  # 1g per kg
    fat = round(tdee * 0.30 / 9)  # 30% of calories from fat
    carbs = round((tdee - protein * 4 - fat * 9) / 4)  # remainder

    return {
        "calories": tdee,
        "protein": protein,
        "fat": fat,
        "carbs": max(carbs, 0),
    }
