"""Confirmation handlers for AWAITING_CONFIRM state."""

import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, AWAITING_CONFIRM
from handlers.keyboards import confirm_keyboard, main_keyboard
from models.schemas import RecognitionResult
from services.nutrition import (
    format_recognition,
    format_calculation,
    format_calculation_summary,
    format_daily_summary,
)

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


def _clear_pending(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear all pending data from user_data."""
    for key in (
        "pending_items",
        "pending_photo_file_id",
        "pending_photo_bytes",
        "pending_text",
        "correction_history",
    ):
        context.user_data.pop(key, None)


async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle confirm callback — calculate nutrition and save meal."""
    query = update.callback_query
    await query.answer()

    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]
    llm = context.bot_data["llm"]

    pending_items = context.user_data.get("pending_items")
    if not pending_items:
        await query.edit_message_text(
            locale.CANCELLED, parse_mode=ParseMode.HTML
        )
        _clear_pending(context)
        return IDLE

    # Remove inline keyboard from recognition message
    await query.edit_message_reply_markup(reply_markup=None)

    try:
        calc_prompt = locale.CALCULATION_PROMPT.format(he_grams=user.he_grams)
        result = await llm.calculate_nutrition(pending_items, calc_prompt)
    except Exception:
        logger.exception("Nutrition calculation failed")
        await query.message.reply_text(
            locale.SERVICE_UNAVAILABLE, parse_mode=ParseMode.HTML
        )
        _clear_pending(context)
        return IDLE

    # Calculate user's local date
    user_tz = ZoneInfo(user.timezone)
    now = datetime.now(user_tz)
    local_date = now.strftime("%Y-%m-%d")

    # Save meal to DB
    items_json = json.dumps(pending_items, ensure_ascii=False)
    totals_dict = {
        "calories": result.totals.calories,
        "protein": result.totals.protein,
        "fat": result.totals.fat,
        "carbs": result.totals.carbs,
        "fiber": result.totals.fiber,
        "net_carbs": result.totals.net_carbs,
        "he": result.totals.he,
        "gi_overall": result.totals.gi_overall,
    }
    totals_json = json.dumps(totals_dict, ensure_ascii=False)

    photo_file_id = context.user_data.get("pending_photo_file_id")
    original_text = context.user_data.get("pending_text")

    await db.save_meal(
        user_id=user.user_id,
        date=local_date,
        items_json=items_json,
        totals_json=totals_json,
        photo_file_id=photo_file_id,
        original_text=original_text,
        timezone=user.timezone,
    )

    # Format response
    table = format_calculation(result)
    summary = format_calculation_summary(result.totals)

    # Get today's totals for daily summary
    today_meals = await db.get_meals_by_date(user.user_id, local_date)
    day_calories = 0.0
    day_he = 0.0
    for meal in today_meals:
        t = json.loads(meal.get("totals_json", "{}"))
        day_calories += t.get("calories", 0)
        day_he += t.get("he", 0)

    daily_summary = format_daily_summary(
        day_calories, day_he, locale.CALCULATION_TODAY_SUMMARY
    )

    text = (
        f"{locale.CALCULATION_HEADER}\n\n"
        f"{table}\n\n"
        f"{summary}\n\n"
        f"{locale.CALCULATION_SAVED}\n"
        f"{daily_summary}"
    )

    await query.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )

    _clear_pending(context)
    return IDLE


async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle cancel callback — discard pending recognition."""
    query = update.callback_query
    await query.answer()

    user, locale = await get_user_and_locale(update, context)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        locale.CANCELLED,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )

    _clear_pending(context)
    return IDLE


async def handle_correction_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle text in AWAITING_CONFIRM — treat as correction to pending items."""
    user, locale = await get_user_and_locale(update, context)
    llm = context.bot_data["llm"]

    pending_items = context.user_data.get("pending_items")
    if not pending_items:
        await update.message.reply_text(
            locale.CANCELLED, parse_mode=ParseMode.HTML
        )
        _clear_pending(context)
        return IDLE

    correction_text = update.message.text.strip()
    pending_photo_bytes = context.user_data.get("pending_photo_bytes")

    status_msg = await update.message.reply_text(
        locale.ANALYZING, parse_mode=ParseMode.HTML
    )

    try:
        result = await llm.correct_recognition(
            previous_items=pending_items,
            correction=correction_text,
            prompt=locale.CORRECTION_PROMPT,
            image_bytes=pending_photo_bytes,
        )
    except Exception:
        logger.exception("Correction failed")
        await status_msg.edit_text(
            locale.SERVICE_UNAVAILABLE, parse_mode=ParseMode.HTML
        )
        return AWAITING_CONFIRM

    # Update pending items
    context.user_data["pending_items"] = [
        {"name": item.name, "weight_g": item.weight_g, "note": item.note}
        for item in result.items
    ]

    # Track correction history
    history = context.user_data.get("correction_history", [])
    history.append(correction_text)
    context.user_data["correction_history"] = history

    text = format_recognition(
        result,
        header=locale.RECOGNITION_UPDATED,
        confirm_msg=locale.RECOGNITION_CONFIRM,
        no_food_msg=locale.RECOGNITION_NO_FOOD,
    )

    await status_msg.edit_text(
        text, parse_mode=ParseMode.HTML, reply_markup=confirm_keyboard(locale)
    )
    return AWAITING_CONFIRM
