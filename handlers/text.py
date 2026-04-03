"""Text handler — route button presses or recognize food from text in IDLE state."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, AWAITING_CONFIRM, AWAITING_GLUCOSE, fmt
from handlers.keyboards import confirm_keyboard, main_keyboard, settings_keyboard
from handlers.diary import handle_today, handle_week, handle_history, handle_undo
from handlers.glucose import handle_sugar_button
from handlers.privacy import handle_privacy
from handlers.settings import handle_settings, handle_targets_text_edit, handle_admin_add_text
from services.nutrition import format_recognition

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is allowed to use the bot."""
    auth = context.bot_data["auth"]
    if not await auth.is_allowed(update.effective_user.id):
        locale = get_locale(context.bot_data["settings"].default_language)
        await update.effective_message.reply_text(
            locale.ACCESS_DENIED, parse_mode=ParseMode.HTML
        )
        return False
    return True


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle text message in IDLE state — button press or food description."""
    user, locale = await get_user_and_locale(update, context)
    text = update.message.text.strip()

    # Check button presses
    if text == locale.BTN_TODAY:
        return await handle_today(update, context)

    if text == locale.BTN_WEEK:
        return await handle_week(update, context)

    if text == locale.BTN_SUGAR:
        return await handle_sugar_button(update, context)

    if text == locale.BTN_MENU:
        return await handle_settings(update, context)

    if text == locale.BTN_HISTORY:
        return await handle_history(update, context)

    if text == locale.BTN_UNDO:
        return await handle_undo(update, context)

    if text == locale.BTN_PRIVACY:
        return await handle_privacy(update, context)

    if text == locale.BTN_HELP:
        await update.message.reply_text(
            fmt(locale.HELP_TEXT, update),
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(locale),
        )
        return IDLE

    if text == locale.BTN_BACK:
        await update.message.reply_text(
            fmt(locale.HELP_TEXT, update),
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(locale),
        )
        return IDLE

    # Check if user is editing targets from settings
    result = await handle_targets_text_edit(update, context)
    if result is not None:
        return result

    # Check if admin is adding a user
    result = await handle_admin_add_text(update, context)
    if result is not None:
        return result

    # Not a button — treat as food description
    if not await check_access(update, context):
        return IDLE

    auth = context.bot_data["auth"]
    llm = context.bot_data["llm"]

    # Rate limit check
    allowed, wait_seconds = auth.check_rate_limit(update.effective_user.id)
    if not allowed:
        minutes = max(1, wait_seconds // 60)
        await update.message.reply_text(
            fmt(locale.RATE_LIMITED, update, minutes=minutes),
            parse_mode=ParseMode.HTML,
        )
        return IDLE

    status_msg = await update.message.reply_text(
        fmt(locale.ANALYZING, update), parse_mode=ParseMode.HTML
    )

    try:
        result = await llm.recognize_food_text(text, locale.RECOGNITION_PROMPT)
    except Exception:
        logger.exception("Text food recognition failed")
        await status_msg.edit_text(
            locale.SERVICE_UNAVAILABLE, parse_mode=ParseMode.HTML
        )
        return IDLE

    if not result.is_food:
        await status_msg.edit_text(
            fmt(locale.RECOGNITION_NO_FOOD, update), parse_mode=ParseMode.HTML
        )
        return IDLE

    # Store pending data for confirmation
    context.user_data["pending_items"] = [
        {"name": item.name, "weight_g": item.weight_g, "note": item.note}
        for item in result.items
    ]
    context.user_data["pending_photo_file_id"] = None
    context.user_data["pending_photo_bytes"] = None
    context.user_data["pending_text"] = text
    context.user_data["correction_history"] = []

    formatted = format_recognition(
        result,
        header=fmt(locale.RECOGNITION_HEADER_TEXT, update),
        confirm_msg=locale.RECOGNITION_CONFIRM,
        no_food_msg=locale.RECOGNITION_NO_FOOD,
    )

    await status_msg.edit_text(
        formatted, parse_mode=ParseMode.HTML, reply_markup=confirm_keyboard(locale)
    )
    return AWAITING_CONFIRM
