"""Admin-only handlers for user management."""

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from locales import get_locale

logger = logging.getLogger(__name__)


async def get_user_and_locale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user from DB and matching locale module."""
    db = context.bot_data["db"]
    user = await db.get_user(update.effective_user.id)
    locale = get_locale(
        user.language if user else context.bot_data["settings"].default_language
    )
    return user, locale


async def handle_adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a user to the allowed list. Admin only."""
    auth = context.bot_data["auth"]
    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    if not auth.is_admin(update.effective_user.id):
        await update.message.reply_text(
            locale.ADMIN_ONLY, parse_mode=ParseMode.HTML
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /adduser &lt;user_id&gt;", parse_mode=ParseMode.HTML
        )
        return

    try:
        target_id = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Usage: /adduser &lt;user_id&gt;", parse_mode=ParseMode.HTML
        )
        return

    await db.add_allowed_user(target_id, added_by=update.effective_user.id)
    await update.message.reply_text(
        locale.ADMIN_USER_ADDED.format(user_id=target_id),
        parse_mode=ParseMode.HTML,
    )


async def handle_removeuser(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Remove a user from the allowed list. Admin only."""
    auth = context.bot_data["auth"]
    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    if not auth.is_admin(update.effective_user.id):
        await update.message.reply_text(
            locale.ADMIN_ONLY, parse_mode=ParseMode.HTML
        )
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /removeuser &lt;user_id&gt;", parse_mode=ParseMode.HTML
        )
        return

    try:
        target_id = int(context.args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(
            "Usage: /removeuser &lt;user_id&gt;", parse_mode=ParseMode.HTML
        )
        return

    await db.remove_allowed_user(target_id)
    await update.message.reply_text(
        locale.ADMIN_USER_REMOVED.format(user_id=target_id),
        parse_mode=ParseMode.HTML,
    )


async def handle_listusers(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """List all allowed users. Admin only."""
    auth = context.bot_data["auth"]
    db = context.bot_data["db"]
    user, locale = await get_user_and_locale(update, context)

    if not auth.is_admin(update.effective_user.id):
        await update.message.reply_text(
            locale.ADMIN_ONLY, parse_mode=ParseMode.HTML
        )
        return

    allowed = await db.get_allowed_users()

    if not allowed:
        await update.message.reply_text(
            locale.ADMIN_USER_LIST_EMPTY, parse_mode=ParseMode.HTML
        )
        return

    user_lines = []
    for entry in allowed:
        user_lines.append(
            f"• {entry['user_id']} (added by {entry['added_by']})"
        )

    await update.message.reply_text(
        locale.ADMIN_USER_LIST.format(users="\n".join(user_lines)),
        parse_mode=ParseMode.HTML,
    )
