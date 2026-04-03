"""Diary handlers — today, week, history, undo."""

import json
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, fmt
from handlers.keyboards import main_keyboard
from services.nutrition import format_diary_day, format_diary_entry, format_full_progress

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def handle_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show diary for today."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    user_tz = ZoneInfo(user.timezone)
    now = datetime.now(user_tz)
    local_date = now.strftime("%Y-%m-%d")

    meals = await db.get_meals_by_date(user.user_id, local_date)

    text = format_diary_day(
        meals=meals,
        date=local_date,
        header_template=locale.DIARY_HEADER,
        empty_template=locale.DIARY_EMPTY,
        total_label=locale.DIARY_TOTAL,
    )

    # Add progress bars if user has targets
    if user.target_calories:
        day_totals = await db.get_day_totals(user.user_id, local_date)
        targets = {
            "calories": user.target_calories,
            "protein": user.target_protein,
            "fat": user.target_fat,
            "carbs": user.target_carbs,
        }
        he_target = user.target_carbs / user.he_grams if user.target_carbs and user.he_grams else 0
        text += "\n\n" + format_full_progress(day_totals, targets, he_target)

    # Add glucose readings for today
    glucose_readings = await db.get_glucose_by_date(user.user_id, local_date)
    if glucose_readings:
        glucose_lines = ["\n\n💉 <b>Glucose:</b>"]
        for reading in glucose_readings:
            ts = reading.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(ts)
                time_str = dt.strftime("%H:%M")
            except (ValueError, TypeError):
                time_str = "—"
            glucose_lines.append(f"  {time_str} — {reading['value']} mmol/L")
        text += "\n".join(glucose_lines)

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show weekly summary."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    user_tz = ZoneInfo(user.timezone)
    now = datetime.now(user_tz)

    dates = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    dates.reverse()

    meals = await db.get_meals_week(user.user_id, dates)

    if not meals:
        await update.message.reply_text(
            locale.WEEK_EMPTY,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(locale),
        )
        return IDLE

    # Group meals by date
    by_date: dict[str, list[dict]] = {}
    for meal in meals:
        d = meal.get("date", "")
        by_date.setdefault(d, []).append(meal)

    lines = [locale.WEEK_HEADER, ""]
    for date_str in dates:
        day_meals = by_date.get(date_str, [])
        if not day_meals:
            continue

        total_cal = 0.0
        total_he = 0.0
        for meal in day_meals:
            totals = json.loads(meal.get("totals_json", "{}"))
            total_cal += totals.get("calories", 0)
            total_he += totals.get("he", 0)

        lines.append(
            f"📅 {date_str}: {int(total_cal)} kcal | {total_he:.1f} HE "
            f"({len(day_meals)} meals)"
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show last N meals."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    # Parse count from command args
    n = 5
    if context.args:
        try:
            n = int(context.args[0])
            n = max(1, min(n, 20))
        except (ValueError, IndexError):
            pass

    meals = await db.get_meals_history(user.user_id, limit=n)

    if not meals:
        await update.message.reply_text(
            locale.HISTORY_EMPTY,
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(locale),
        )
        return IDLE

    lines = [locale.HISTORY_HEADER.format(n=len(meals)), ""]
    for meal in meals:
        lines.append(format_diary_entry(meal))
        lines.append("")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_undo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Delete the last meal entry."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    deleted = await db.delete_last_meal(user.user_id)

    text = fmt(locale.UNDO_SUCCESS, update) if deleted else fmt(locale.UNDO_NOTHING, update)
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE
