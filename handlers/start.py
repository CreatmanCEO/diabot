"""Onboarding flow: /start -> consent -> timezone -> HE -> gender -> height -> weight -> age -> targets -> complete."""

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
    ONBOARDING_GENDER,
    ONBOARDING_HEIGHT,
    ONBOARDING_WEIGHT,
    ONBOARDING_AGE,
    ONBOARDING_TARGETS_CONFIRM,
    IDLE,
    fmt,
)
from handlers.keyboards import (
    main_keyboard,
    consent_keyboard,
    timezone_keyboard,
    he_keyboard,
    gender_keyboard,
    height_keyboard,
    targets_confirm_keyboard,
)
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

    locale = get_locale(context.bot_data["settings"].default_language)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        fmt(locale.ONBOARDING_GENDER, update),
        parse_mode=ParseMode.HTML,
        reply_markup=gender_keyboard(locale),
    )
    return ONBOARDING_GENDER


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

    await update.message.reply_text(
        fmt(locale.ONBOARDING_GENDER, update),
        parse_mode=ParseMode.HTML,
        reply_markup=gender_keyboard(locale),
    )
    return ONBOARDING_GENDER


async def handle_gender_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle gender selection."""
    query = update.callback_query
    await query.answer()
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    gender = query.data.split("_")[1]  # "gender_female" -> "female"
    await db.update_user(update.effective_user.id, gender=gender)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        locale.ONBOARDING_HEIGHT,
        parse_mode=ParseMode.HTML,
        reply_markup=height_keyboard(locale),
    )
    return ONBOARDING_HEIGHT


async def handle_height_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle height selection."""
    query = update.callback_query
    await query.answer()
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    if query.data == "height_custom":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_HEIGHT_CUSTOM, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_HEIGHT

    height = int(query.data.split("_")[1])  # "height_165" -> 165
    await db.update_user(update.effective_user.id, height_cm=height)

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        fmt(locale.ONBOARDING_WEIGHT, update), parse_mode=ParseMode.HTML
    )
    return ONBOARDING_WEIGHT


async def handle_height_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle custom height text input."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    try:
        height = int(update.message.text.strip())
        if height < 100 or height > 250:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_HEIGHT_CUSTOM, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_HEIGHT

    await db.update_user(update.effective_user.id, height_cm=height)
    await update.message.reply_text(
        fmt(locale.ONBOARDING_WEIGHT, update), parse_mode=ParseMode.HTML
    )
    return ONBOARDING_WEIGHT


async def handle_weight_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle weight text input."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    try:
        text = update.message.text.strip().replace(",", ".")
        weight = float(text)
        if weight < 30 or weight > 300:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_WEIGHT_INVALID, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_WEIGHT

    await db.update_user(update.effective_user.id, weight_kg=weight)
    await update.message.reply_text(
        locale.ONBOARDING_AGE, parse_mode=ParseMode.HTML
    )
    return ONBOARDING_AGE


async def handle_age_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle age text input, calculate targets, show summary."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    try:
        age = int(update.message.text.strip())
        if age < 10 or age > 120:
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_AGE_INVALID, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_AGE

    await db.update_user(update.effective_user.id, age=age)

    # Get updated user and calculate targets
    user = await db.get_user(update.effective_user.id)
    targets = calculate_targets(
        gender=user.gender or "female",
        height_cm=user.height_cm or 165,
        weight_kg=user.weight_kg or 60,
        age=age,
    )

    # Save calculated targets
    await db.update_user(
        update.effective_user.id,
        target_calories=targets["calories"],
        target_protein=targets["protein"],
        target_fat=targets["fat"],
        target_carbs=targets["carbs"],
    )

    he_target = round(targets["carbs"] / user.he_grams, 1) if user.he_grams else 0
    text = fmt(
        locale.ONBOARDING_TARGETS_SHOW, update,
        calories=targets["calories"], protein=targets["protein"],
        fat=targets["fat"], carbs=targets["carbs"], he=he_target,
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=targets_confirm_keyboard(locale),
    )
    return ONBOARDING_TARGETS_CONFIRM


async def handle_targets_confirm_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle targets confirmation or edit request."""
    query = update.callback_query
    await query.answer()
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    if query.data == "targets_edit":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ONBOARDING_TARGETS_EDIT, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_TARGETS_CONFIRM

    # targets_confirm
    await db.complete_onboarding(update.effective_user.id)
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(user.language if user else "ru")

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        fmt(locale.ONBOARDING_COMPLETE, update),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_targets_edit_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle manual target entry: 'calories protein fat carbs'."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    try:
        parts = update.message.text.strip().split()
        if len(parts) != 4:
            raise ValueError
        calories, protein, fat, carbs = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        if any(v < 0 for v in [calories, protein, fat, carbs]):
            raise ValueError
    except (ValueError, TypeError):
        await update.message.reply_text(
            locale.ONBOARDING_TARGETS_INVALID, parse_mode=ParseMode.HTML
        )
        return ONBOARDING_TARGETS_CONFIRM

    await db.update_user(
        update.effective_user.id,
        target_calories=calories, target_protein=protein,
        target_fat=fat, target_carbs=carbs,
    )
    await db.complete_onboarding(update.effective_user.id)

    user = await db.get_user(update.effective_user.id)
    locale = get_locale(user.language if user else "ru")

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
