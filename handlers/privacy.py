"""Privacy, data export, and data deletion handlers."""

import io
import json
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, fmt
from handlers.keyboards import main_keyboard, delete_confirm_keyboard

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def handle_privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show privacy information."""
    user, locale = await get_user_and_locale(update, context)

    await update.message.reply_text(
        locale.PRIVACY_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Export all user data as a JSON file."""
    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    data = await db.export_user_data(update.effective_user.id)

    if not data.get("user") and not data.get("meals") and not data.get("glucose_readings"):
        await update.message.reply_text(
            locale.EXPORT_EMPTY, parse_mode=ParseMode.HTML
        )
        return

    json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    file_bytes = json_str.encode("utf-8")
    file_obj = io.BytesIO(file_bytes)
    file_obj.name = f"diabot_export_{update.effective_user.id}.json"

    await update.message.reply_document(
        document=file_obj,
        caption=f"DiaBot data export for user {update.effective_user.id}",
    )


async def handle_delete_data(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Show data deletion confirmation."""
    user, locale = await get_user_and_locale(update, context)

    await update.message.reply_text(
        locale.DELETE_CONFIRM,
        parse_mode=ParseMode.HTML,
        reply_markup=delete_confirm_keyboard(locale),
    )


async def handle_delete_confirm(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle data deletion confirmation callback."""
    query = update.callback_query
    await query.answer()

    user, locale = await get_user_and_locale(update, context)
    db = context.bot_data["db"]

    if query.data == "delete_yes":
        await db.delete_all_user_data(update.effective_user.id)
        await query.edit_message_text(
            locale.DELETE_DONE, parse_mode=ParseMode.HTML
        )
        return IDLE

    if query.data == "delete_no":
        await query.edit_message_text(
            locale.CANCELLED, parse_mode=ParseMode.HTML
        )
        return IDLE

    return IDLE
