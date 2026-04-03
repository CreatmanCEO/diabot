"""Onboarding flow: /start -> consent -> timezone -> HE -> complete."""

import logging
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import (
    ONBOARDING_CONSENT,
    ONBOARDING_TIMEZONE,
    ONBOARDING_HE,
    IDLE,
    fmt,
)
from handlers.keyboards import (
    main_keyboard,
    consent_keyboard,
    timezone_keyboard,
    he_keyboard,
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


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command — begin onboarding or show help."""
    db = context.bot_data["db"]
    tg_user = update.effective_user
    user = await db.get_user(tg_user.id)

    if user and user.onboarding_completed:
        locale = get_locale(user.language)
        await update.message.reply_text(
            fmt(locale.HELP_TEXT, update),
            parse_mode=ParseMode.HTML,
            reply_markup=main_keyboard(locale),
        )
        return IDLE

    # New user — create record and start onboarding
    if not user:
        await db.create_user(tg_user.id, username=tg_user.username)

    locale = get_locale(context.bot_data["settings"].default_language)
    await update.message.reply_text(
        fmt(locale.START_WELCOME, update),
        parse_mode=ParseMode.HTML,
        reply_markup=consent_keyboard(locale),
    )
    return ONBOARDING_CONSENT


async def handle_consent_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle consent inline buttons."""
    query = update.callback_query
    await query.answer()

    locale = get_locale(context.bot_data["settings"].default_language)

    if query.data == "consent_agree":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_TIMEZONE,
            parse_mode=ParseMode.HTML,
            reply_markup=timezone_keyboard(locale),
        )
        return ONBOARDING_TIMEZONE

    if query.data == "consent_details":
        await query.answer()
        await query.edit_message_text(
            text=locale.CONSENT_DETAILS_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=consent_keyboard(locale),
        )
        return ONBOARDING_CONSENT

    return ONBOARDING_CONSENT


async def handle_timezone_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle timezone selection inline buttons."""
    query = update.callback_query
    await query.answer()

    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    if query.data == "tz_custom":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_TZ_CUSTOM,
            parse_mode=ParseMode.HTML,
        )
        # Stay in ONBOARDING_TIMEZONE — next text message will be parsed as tz
        return ONBOARDING_TIMEZONE

    # Extract timezone from callback data: "tz_europe/moscow" -> "Europe/Moscow"
    tz_raw = query.data[3:]  # strip "tz_"
    # Capitalize parts: "europe/moscow" -> "Europe/Moscow"
    tz_str = "/".join(part.capitalize() for part in tz_raw.split("/"))

    try:
        ZoneInfo(tz_str)
    except (KeyError, ValueError):
        tz_str = context.bot_data["settings"].default_timezone

    await db.update_user(update.effective_user.id, timezone=tz_str)
    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        locale.ONBOARDING_HE,
        parse_mode=ParseMode.HTML,
        reply_markup=he_keyboard(locale),
    )
    return ONBOARDING_HE


async def handle_timezone_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle custom timezone text input during onboarding."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)
    tz_str = update.message.text.strip()

    try:
        ZoneInfo(tz_str)
    except (KeyError, ValueError):
        await update.message.reply_text(
            locale.ONBOARDING_TZ_CUSTOM,
            parse_mode=ParseMode.HTML,
        )
        return ONBOARDING_TIMEZONE

    await db.update_user(update.effective_user.id, timezone=tz_str)
    await update.message.reply_text(
        locale.ONBOARDING_HE,
        parse_mode=ParseMode.HTML,
        reply_markup=he_keyboard(locale),
    )
    return ONBOARDING_HE


async def handle_he_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle HE grams selection inline buttons."""
    query = update.callback_query
    await query.answer()

    db = context.bot_data["db"]

    if query.data == "he_custom":
        locale = get_locale(context.bot_data["settings"].default_language)
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_HE_CUSTOM,
            parse_mode=ParseMode.HTML,
        )
        # Stay in ONBOARDING_HE — next text message will be parsed as number
        return ONBOARDING_HE

    # Parse HE value: "he_12" -> 12, "he_10" -> 10
    he_grams = int(query.data.split("_")[1])
    await db.update_user(update.effective_user.id, he_grams=he_grams)
    await db.complete_onboarding(update.effective_user.id)

    user = await db.get_user(update.effective_user.id)
    locale = get_locale(user.language)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        fmt(locale.ONBOARDING_COMPLETE, update),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_he_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle custom HE grams text input during onboarding."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    try:
        he_grams = int(update.message.text.strip())
        if he_grams < 1 or he_grams > 50:
            raise ValueError("out of range")
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_HE_CUSTOM,
            parse_mode=ParseMode.HTML,
        )
        return ONBOARDING_HE

    await db.update_user(update.effective_user.id, he_grams=he_grams)
    await db.complete_onboarding(update.effective_user.id)

    user = await db.get_user(update.effective_user.id)
    locale = get_locale(user.language)

    await update.message.reply_text(
        fmt(locale.ONBOARDING_COMPLETE, update),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /help command."""
    user, locale = await get_user_and_locale(update, context)
    await update.message.reply_text(
        fmt(locale.HELP_TEXT, update),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale) if user and user.onboarding_completed else None,
    )
    return IDLE if user and user.onboarding_completed else ONBOARDING_CONSENT
