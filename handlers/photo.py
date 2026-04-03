"""Photo handler — recognize food from photo in IDLE state."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, AWAITING_CONFIRM, fmt
from handlers.keyboards import confirm_keyboard
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
        from handlers.access import handle_access_denied
        await handle_access_denied(update, context)
        return False
    return True


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle photo message — recognize food items."""
    if not await check_access(update, context):
        return IDLE

    user, locale = await get_user_and_locale(update, context)
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

    # Download photo
    photo = update.message.photo[-1]
    caption = update.message.caption

    status_msg = await update.message.reply_text(
        fmt(locale.ANALYZING, update), parse_mode=ParseMode.HTML
    )

    try:
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()

        result = await llm.recognize_food(
            bytes(photo_bytes), locale.RECOGNITION_PROMPT, caption
        )
    except Exception:
        logger.exception("Food recognition failed")
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
    context.user_data["pending_photo_file_id"] = photo.file_id
    context.user_data["pending_photo_bytes"] = bytes(photo_bytes)
    context.user_data["pending_text"] = None
    context.user_data["correction_history"] = []

    text = format_recognition(
        result,
        header=fmt(locale.RECOGNITION_HEADER, update),
        confirm_msg=locale.RECOGNITION_CONFIRM,
        no_food_msg=locale.RECOGNITION_NO_FOOD,
    )

    await status_msg.edit_text(
        text, parse_mode=ParseMode.HTML, reply_markup=confirm_keyboard(locale)
    )
    return AWAITING_CONFIRM
