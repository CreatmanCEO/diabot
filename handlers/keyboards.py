"""Telegram keyboard factories."""

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


def main_keyboard(locale) -> ReplyKeyboardMarkup:
    """Main menu reply keyboard."""
    keyboard = [
        [locale.BTN_TODAY, locale.BTN_WEEK],
        [locale.BTN_SUGAR, locale.BTN_MENU],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def settings_keyboard(locale) -> ReplyKeyboardMarkup:
    """Settings menu reply keyboard."""
    keyboard = [
        [locale.BTN_HISTORY, locale.BTN_UNDO],
        [locale.BTN_PRIVACY, locale.BTN_HELP],
        [locale.BTN_BACK],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def confirm_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline confirmation keyboard for food recognition."""
    keyboard = [
        [
            InlineKeyboardButton(locale.BTN_CONFIRM, callback_data="confirm"),
            InlineKeyboardButton(locale.BTN_CANCEL, callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def consent_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline consent keyboard for onboarding."""
    keyboard = [
        [
            InlineKeyboardButton(locale.CONSENT_AGREE, callback_data="consent_agree"),
            InlineKeyboardButton(locale.CONSENT_DETAILS, callback_data="consent_details"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def timezone_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline timezone selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(locale.TZ_MOSCOW, callback_data="tz_europe/moscow"),
            InlineKeyboardButton(locale.TZ_EUROPE, callback_data="tz_europe/berlin"),
        ],
        [InlineKeyboardButton(locale.TZ_OTHER, callback_data="tz_custom")],
    ]
    return InlineKeyboardMarkup(keyboard)


def he_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline HE grams selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(locale.HE_12, callback_data="he_12"),
            InlineKeyboardButton(locale.HE_10, callback_data="he_10"),
        ],
        [InlineKeyboardButton(locale.HE_OTHER, callback_data="he_custom")],
    ]
    return InlineKeyboardMarkup(keyboard)


def delete_confirm_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline data deletion confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(locale.DELETE_YES, callback_data="delete_yes"),
            InlineKeyboardButton(locale.DELETE_NO, callback_data="delete_no"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
