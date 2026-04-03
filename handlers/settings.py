"""Settings handler — view and edit profile and targets."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, ONBOARDING_GENDER, fmt
from handlers.keyboards import settings_keyboard_inline, main_keyboard, gender_keyboard
from services.profile import calculate_targets
from services.auth import AuthService

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

    auth: AuthService = context.bot_data["auth"]
    db = context.bot_data["db"]
    is_admin = auth.is_admin(update.effective_user.id)

    pending_count = 0
    if is_admin:
        pending = await db.get_pending_requests()
        pending_count = len(pending)

    await update.effective_message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=settings_keyboard_inline(locale, is_admin=is_admin, pending_count=pending_count),
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


async def handle_admin_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle admin inline button callbacks from settings."""
    query = update.callback_query
    await query.answer()

    auth: AuthService = context.bot_data["auth"]
    if not auth.is_admin(update.effective_user.id):
        return IDLE

    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    if query.data == "admin_listusers":
        await query.edit_message_reply_markup(reply_markup=None)
        allowed = await db.get_allowed_users()
        if not allowed:
            await query.message.reply_text(
                locale.ADMIN_USER_LIST_EMPTY, parse_mode=ParseMode.HTML
            )
        else:
            lines = []
            for e in allowed:
                u = await db.get_user(e["user_id"])
                name = u.username if u and u.username else str(e["user_id"])
                lines.append(f"\u2022 {name} (ID: {e['user_id']})")
            await query.message.reply_text(
                locale.ADMIN_USERS_HEADER + "\n".join(lines),
                parse_mode=ParseMode.HTML,
            )
        return IDLE

    if query.data == "admin_pending":
        await query.edit_message_reply_markup(reply_markup=None)
        pending = await db.get_pending_requests()
        if not pending:
            await query.message.reply_text(
                locale.ADMIN_PENDING_EMPTY, parse_mode=ParseMode.HTML
            )
        else:
            from handlers.keyboards import admin_review_keyboard
            for req in pending:
                text = locale.ADMIN_NEW_REQUEST.format(
                    first_name=req.get("first_name") or "\u2014",
                    username=req.get("username") or "\u2014",
                    user_id=str(req["user_id"]),
                )
                await query.message.reply_text(
                    text, parse_mode=ParseMode.HTML,
                    reply_markup=admin_review_keyboard(locale, req["id"]),
                )
        return IDLE

    if query.data == "admin_adduser":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            locale.ADMIN_ADD_PROMPT, parse_mode=ParseMode.HTML
        )
        context.user_data["admin_adding_user"] = True
        return IDLE

    return IDLE


async def handle_admin_add_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | None:
    """Handle admin user ID input for adding users.

    Returns None if not in admin-add mode.
    """
    if not context.user_data.get("admin_adding_user"):
        return None

    auth: AuthService = context.bot_data["auth"]
    if not auth.is_admin(update.effective_user.id):
        context.user_data.pop("admin_adding_user", None)
        return None

    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    try:
        target_id = int(update.message.text.strip())
    except (ValueError, TypeError):
        context.user_data.pop("admin_adding_user", None)
        return None

    await db.add_allowed_user(target_id, added_by=update.effective_user.id)
    context.user_data.pop("admin_adding_user", None)

    await update.message.reply_text(
        locale.ADMIN_USER_ADDED.format(user_id=target_id),
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(locale),
    )
    return IDLE


async def handle_targets_text_edit(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | None:
    """Handle target editing from settings (4 numbers).

    Returns None if not editing or input doesn't parse as targets,
    so text.py can fall through to food recognition.
    """
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
        # Not valid targets input — clear flag and let food recognition handle it
        context.user_data.pop("editing_targets", None)
        return None

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
    context.user_data["targets_prompt_dismissed"] = True
    await query.edit_message_reply_markup(reply_markup=None)
    return IDLE
