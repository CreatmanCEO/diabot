"""Settings handler — view and edit profile and targets."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, ONBOARDING_GENDER, fmt
from handlers.keyboards import settings_keyboard_inline, main_keyboard, gender_keyboard
from services.profile import calculate_targets

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def handle_settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show current settings."""
    user, locale = await get_user_and_locale(update, context)
    if not user:
        return IDLE

    gender_display = {
        "male": locale.GENDER_DISPLAY_MALE,
        "female": locale.GENDER_DISPLAY_FEMALE,
    }.get(user.gender, locale.GENDER_DISPLAY_NONE)

    text = locale.SETTINGS_HEADER.replace("{timezone}", user.timezone or "—")
    text = text.replace("{he_grams}", str(user.he_grams or 12))
    text = text.replace("{gender}", gender_display)
    text = text.replace("{height}", str(user.height_cm or "—"))
    text = text.replace("{weight}", str(user.weight_kg or "—"))
    text = text.replace("{age}", str(user.age or "—"))
    text = text.replace("{calories}", str(user.target_calories or "—"))
    text = text.replace("{protein}", str(user.target_protein or "—"))
    text = text.replace("{fat}", str(user.target_fat or "—"))
    text = text.replace("{carbs}", str(user.target_carbs or "—"))

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=settings_keyboard_inline(locale),
    )
    return IDLE


async def handle_settings_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle settings inline button callbacks."""
    query = update.callback_query
    await query.answer()
    user, locale = await get_user_and_locale(update, context)

    if query.data == "settings_targets":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_TARGETS_EDIT, parse_mode=ParseMode.HTML
        )
        # Store flag so text handler knows we're editing targets
        context.user_data["editing_targets"] = True
        return IDLE

    if query.data == "settings_profile":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            fmt(locale.ONBOARDING_GENDER, update),
            parse_mode=ParseMode.HTML,
            reply_markup=gender_keyboard(locale),
        )
        return ONBOARDING_GENDER

    return IDLE


async def handle_targets_text_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle target editing from settings (4 numbers)."""
    if not context.user_data.get("editing_targets"):
        return None  # Not editing, let other handlers handle

    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    try:
        parts = update.message.text.strip().split()
        if len(parts) != 4:
            raise ValueError
        calories, protein, fat, carbs = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_TARGETS_INVALID, parse_mode=ParseMode.HTML
        )
        return IDLE

    await db.update_user(
        update.effective_user.id,
        target_calories=calories, target_protein=protein,
        target_fat=fat, target_carbs=carbs,
    )
    context.user_data.pop("editing_targets", None)

    await update.message.reply_text(
        locale.SETTINGS_SAVED,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_targets_setup_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle migration prompt — setup now or later."""
    query = update.callback_query
    await query.answer()
    locale = get_locale(context.bot_data["settings"].default_language)

    if query.data == "targets_setup_now":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            fmt(locale.ONBOARDING_GENDER, update),
            parse_mode=ParseMode.HTML,
            reply_markup=gender_keyboard(locale),
        )
        return ONBOARDING_GENDER

    # targets_setup_later
    await query.edit_message_reply_markup(reply_markup=None)
    return IDLE
