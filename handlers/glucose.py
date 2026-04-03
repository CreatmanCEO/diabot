"""Glucose recording handlers."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, AWAITING_GLUCOSE, fmt
from handlers.keyboards import main_keyboard

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def handle_sugar_button(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle sugar button/command — prompt for glucose value."""
    user, locale = await get_user_and_locale(update, context)

    await update.message.reply_text(
        fmt(locale.GLUCOSE_PROMPT, update),
        parse_mode=ParseMode.HTML,
    )
    return AWAITING_GLUCOSE


async def handle_glucose_value(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle glucose value input in AWAITING_GLUCOSE state."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    text = update.message.text.strip().replace(",", ".")

    try:
        value = float(text)
        if value <= 0 or value > 40:
            raise ValueError("out of range")
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.GLUCOSE_INVALID,
            parse_mode=ParseMode.HTML,
        )
        return AWAITING_GLUCOSE

    # Save glucose reading with user's local date
    user_tz = ZoneInfo(user.timezone)
    now = datetime.now(user_tz)
    local_date = now.strftime("%Y-%m-%d")

    await db.save_glucose(
        user_id=user.user_id,
        value=value,
        date=local_date,
    )

    await update.message.reply_text(
        fmt(locale.GLUCOSE_SAVED, update, value=value),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE
