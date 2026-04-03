"""Nutrition data formatting for Telegram messages."""

from models.schemas import (
    RecognitionResult,
    CalculationResult,
    NutritionTotals,
)


def format_recognition(
    result: RecognitionResult,
    header: str,
    confirm_msg: str = "",
    no_food_msg: str = "",
) -> str:
    """Format recognition result as numbered list for Telegram (HTML).

    Args:
        result: Recognition result from LLM.
        header: Header text (e.g. "I see:" or "Updated list:").
        confirm_msg: Confirmation prompt to append.
        no_food_msg: Message to show if no food detected.
    """
    if not result.is_food:
        return no_food_msg

    lines = [header, ""]
    for i, item in enumerate(result.items, 1):
        line = f"{i}. {item.name} — ~{item.weight_g} г"
        if item.note:
            line += f" ({item.note})"
        lines.append(line)

    if confirm_msg:
        lines.append("")
        lines.append(confirm_msg)

    return "\n".join(lines)


def format_calculation(result: CalculationResult) -> str:
    """Format KBJU calculation as monospace table for Telegram (HTML).

    Uses <pre> tags for aligned table output.
    """
    lines = []

    # Items table
    for item in result.items:
        name_weight = f"{item.name} {item.weight_g}г"
        line = f"{name_weight:<25} {item.calories:>5.0f} ккал | Б {item.protein:>5.1f} | Ж {item.fat:>5.1f} | У {item.carbs:>5.1f}"
        lines.append(line)

    # Separator
    lines.append("─" * 60)

    # Totals
    t = result.totals
    lines.append(
        f"{'ИТОГО':<25} {t.calories:>5.0f} ккал | Б {t.protein:>5.1f} | Ж {t.fat:>5.1f} | У {t.carbs:>5.1f}"
    )

    table = "\n".join(lines)
    return f"<pre>{table}</pre>"


def format_calculation_summary(totals: NutritionTotals) -> str:
    """Format the summary section below the table."""
    gi_map = {"low": "низкий", "medium": "средний", "high": "высокий"}
    gi_text = gi_map.get(totals.gi_overall, totals.gi_overall)

    lines = [
        f"🔸 Углеводы: {totals.carbs:.1f} г (клетчатка: {totals.fiber:.1f} г)",
        f"🔸 Усваиваемые углеводы: {totals.net_carbs:.1f} г",
        f"🔸 Хлебные единицы: {totals.he:.1f} ХЕ",
        f"🔸 ГИ: {gi_text}",
    ]
    return "\n".join(lines)


def format_daily_summary(calories: float, he: float, template: str) -> str:
    """Format daily summary using template string."""
    return template.format(calories=int(calories), he=f"{he:.1f}")


def format_diary_entry(meal: dict, index: int = 0) -> str:
    """Format a single diary entry.

    Args:
        meal: Meal dict from database (with timestamp, items_json, totals_json).
        index: Optional entry index for display.
    """
    import json
    from datetime import datetime

    timestamp = meal.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp)
        time_str = dt.strftime("%H:%M")
    except (ValueError, TypeError):
        time_str = "—"

    items = json.loads(meal.get("items_json", "[]"))
    totals = json.loads(meal.get("totals_json", "{}"))

    item_names = ", ".join(item.get("name", "") for item in items[:3])
    if len(items) > 3:
        item_names += "..."

    cal = totals.get("calories", 0)
    protein = totals.get("protein", 0)
    fat = totals.get("fat", 0)
    carbs = totals.get("carbs", 0)
    he = totals.get("he", 0)

    lines = [
        f"🕐 {time_str}",
        f"  {item_names}",
        f"  {int(cal)} ккал | Б {protein:.1f} | Ж {fat:.1f} | У {carbs:.1f} | {he:.1f} ХЕ",
    ]
    return "\n".join(lines)


def format_diary_day(
    meals: list[dict],
    date: str,
    header_template: str,
    empty_template: str,
    total_label: str,
) -> str:
    """Format a full day's diary.

    Args:
        meals: List of meal dicts from database.
        date: Display date string.
        header_template: Header with {date} placeholder.
        empty_template: Empty message with {date} placeholder.
        total_label: Label for totals row.
    """
    if not meals:
        return empty_template.format(date=date)

    import json

    lines = [header_template.format(date=date), ""]

    total_cal = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0
    total_he = 0

    for meal in meals:
        lines.append(format_diary_entry(meal))
        lines.append("")
        totals = json.loads(meal.get("totals_json", "{}"))
        total_cal += totals.get("calories", 0)
        total_protein += totals.get("protein", 0)
        total_fat += totals.get("fat", 0)
        total_carbs += totals.get("carbs", 0)
        total_he += totals.get("he", 0)

    lines.append("━" * 20)
    lines.append(f"{total_label}")
    lines.append(f"  {int(total_cal)} ккал | Б {total_protein:.1f} | Ж {total_fat:.1f} | У {total_carbs:.1f}")
    lines.append(f"  🔸 ХЕ за день: {total_he:.1f}")

    return "\n".join(lines)


def format_progress_bar(current: float, target: float | None, width: int = 15) -> str:
    """Format a single text progress bar.

    Returns empty string if target is None or <= 0.
    """
    if target is None or target <= 0:
        return ""
    pct = current / target * 100
    filled = min(round(pct / 100 * width), width)
    bar = "▓" * filled + "░" * (width - filled)
    return f"{bar} {pct:.0f}%"


def format_compact_progress(
    day_totals: dict,
    targets: dict,
    he_target: float,
) -> str:
    """Format compact progress shown after each meal.

    Line 1 (🔸): Carbs and XE (diabetes accent)
    Line 2 (🔹): Calories, protein, fat
    """
    carbs = day_totals.get("carbs", 0)
    he = day_totals.get("he", 0)
    cal = day_totals.get("calories", 0)
    protein = day_totals.get("protein", 0)
    fat = day_totals.get("fat", 0)

    t_carbs = targets.get("carbs") or 0
    t_cal = targets.get("calories") or 0
    t_protein = targets.get("protein") or 0
    t_fat = targets.get("fat") or 0

    carb_pct = round(carbs / t_carbs * 100) if t_carbs else 0
    he_str = f"{he:.1f}/{he_target:.1f}" if he_target else f"{he:.1f}"
    cal_pct = round(cal / t_cal * 100) if t_cal else 0
    p_pct = round(protein / t_protein * 100) if t_protein else 0
    f_pct = round(fat / t_fat * 100) if t_fat else 0

    lines = [
        f"🔸 У: {carbs:.0f}/{t_carbs}г ({carb_pct}%) | ХЕ: {he_str}",
        f"🔹 К: {cal:.0f}/{t_cal} ({cal_pct}%) | Б: {protein:.0f}/{t_protein}г ({p_pct}%) | Ж: {fat:.0f}/{t_fat}г ({f_pct}%)",
    ]
    return "\n".join(lines)


def format_full_progress(
    day_totals: dict,
    targets: dict,
    he_target: float,
    width: int = 15,
) -> str:
    """Format full progress bars for /today diary (HTML <pre> block).

    Carbs and XE shown first (diabetes focus).
    """
    carbs = day_totals.get("carbs", 0)
    he = day_totals.get("he", 0)
    cal = day_totals.get("calories", 0)
    protein = day_totals.get("protein", 0)
    fat = day_totals.get("fat", 0)

    t = targets
    lines = []

    bar = format_progress_bar(carbs, t.get("carbs"), width)
    lines.append(f"Углеводы: {bar} ({carbs:.0f}/{t.get('carbs', 0)}г)")

    bar = format_progress_bar(he, he_target, width)
    lines.append(f"ХЕ:       {bar} ({he:.1f}/{he_target:.1f})")

    bar = format_progress_bar(cal, t.get("calories"), width)
    lines.append(f"Калории:  {bar} ({cal:.0f}/{t.get('calories', 0)})")

    bar = format_progress_bar(protein, t.get("protein"), width)
    lines.append(f"Белок:    {bar} ({protein:.0f}/{t.get('protein', 0)}г)")

    bar = format_progress_bar(fat, t.get("fat"), width)
    lines.append(f"Жиры:     {bar} ({fat:.0f}/{t.get('fat', 0)}г)")

    return "<pre>" + "\n".join(lines) + "</pre>"
