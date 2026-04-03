"""Access request handlers — unauthorized user approval workflow."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale
from handlers import IDLE, fmt
from handlers.keyboards import access_request_keyboard, admin_review_keyboard

logger = logging.getLogger(__name__)


async def handle_access_denied(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show access denied with request button for unauthorized users."""
    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)
    user_id = update.effective_user.id

    has_pending = await db.has_pending_request(user_id)
    if has_pending:
        await update.effective_message.reply_text(
            locale.ACCESS_REQUEST_PENDING, parse_mode=ParseMode.HTML
        )
        return

    await update.effective_message.reply_text(
        fmt(locale.ACCESS_REQUEST_WELCOME, update),
        parse_mode=ParseMode.HTML,
        reply_markup=access_request_keyboard(locale),
    )


async def handle_access_request_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle 'Request access' button press."""
    query = update.callback_query
    await query.answer()

    db = context.bot_data["db"]
    settings = context.bot_data["settings"]
    locale = get_locale(settings.default_language)
    tg_user = update.effective_user

    # Create request
    request_id = await db.create_access_request(
        user_id=tg_user.id,
        username=tg_user.username,
        first_name=tg_user.first_name,
    )

    await query.edit_message_reply_markup(reply_markup=None)
    await query.message.reply_text(
        locale.ACCESS_REQUEST_SENT, parse_mode=ParseMode.HTML
    )

    # Notify all admins
    admin_text = locale.ADMIN_NEW_REQUEST.format(
        first_name=tg_user.first_name or "\u2014",
        username=tg_user.username or "\u2014",
        user_id=str(tg_user.id),
    )

    for admin_id in settings.admin_ids:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_text,
                parse_mode=ParseMode.HTML,
                reply_markup=admin_review_keyboard(locale, request_id),
            )
        except Exception:
            logger.warning("Failed to notify admin %s", admin_id)

    return IDLE


async def handle_review_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle admin approve/reject callback."""
    query = update.callback_query
    await query.answer()

    auth = context.bot_data["auth"]
    if not auth.is_admin(update.effective_user.id):
        return IDLE

    db = context.bot_data["db"]
    locale = get_locale(context.bot_data["settings"].default_language)

    # Parse callback: "review_approve_123" or "review_reject_123"
    parts = query.data.split("_")
    action = parts[1]  # approve or reject
    request_id = int(parts[2])

    if action == "approve":
        request = await db.approve_request(request_id, reviewed_by=update.effective_user.id)
        if not request:
            await query.edit_message_text(
                locale.ADMIN_REQUEST_ALREADY_HANDLED, parse_mode=ParseMode.HTML
            )
            return IDLE

        await query.edit_message_text(
            locale.ADMIN_REQUEST_APPROVED.format(
                first_name=request.get("first_name") or "\u2014",
                user_id=str(request["user_id"]),
            ),
            parse_mode=ParseMode.HTML,
        )

        # Notify user
        try:
            user_locale = get_locale(context.bot_data["settings"].default_language)
            await context.bot.send_message(
                chat_id=request["user_id"],
                text=user_locale.ACCESS_REQUEST_APPROVED.format(
                    name=request.get("first_name") or ""
                ),
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.warning("Failed to notify user %s", request["user_id"])

    elif action == "reject":
        request = await db.reject_request(request_id, reviewed_by=update.effective_user.id)
        if not request:
            await query.edit_message_text(
                locale.ADMIN_REQUEST_ALREADY_HANDLED, parse_mode=ParseMode.HTML
            )
            return IDLE

        await query.edit_message_text(
            locale.ADMIN_REQUEST_REJECTED.format(
                first_name=request.get("first_name") or "\u2014",
                user_id=str(request["user_id"]),
            ),
            parse_mode=ParseMode.HTML,
        )

        # Notify user
        try:
            user_locale = get_locale(context.bot_data["settings"].default_language)
            await context.bot.send_message(
                chat_id=request["user_id"],
                text=user_locale.ACCESS_REQUEST_REJECTED,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            logger.warning("Failed to notify user %s", request["user_id"])

    return IDLE
