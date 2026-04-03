"""Telegram bot handlers."""

from telegram import Update

# ConversationHandler states
ONBOARDING_CONSENT = 0
ONBOARDING_TIMEZONE = 1
ONBOARDING_HE = 2
IDLE = 3
AWAITING_CONFIRM = 4
AWAITING_GLUCOSE = 5


def get_first_name(update: Update) -> str:
    """Get user's first name for personalized messages."""
    return update.effective_user.first_name or ""


def fmt(template: str, update: Update, **kwargs) -> str:
    """Format a locale string with user's name and extra kwargs.

    Safely handles templates that don't contain {name}.
    """
    return template.format(name=get_first_name(update), **kwargs)
