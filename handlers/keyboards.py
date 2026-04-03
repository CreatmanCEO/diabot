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


def gender_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline gender selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(locale.GENDER_FEMALE, callback_data="gender_female"),
            InlineKeyboardButton(locale.GENDER_MALE, callback_data="gender_male"),
        ],
        [InlineKeyboardButton(locale.BTN_CANCEL, callback_data="onboarding_cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def height_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline height selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(locale.HEIGHT_155, callback_data="height_155"),
            InlineKeyboardButton(locale.HEIGHT_160, callback_data="height_160"),
            InlineKeyboardButton(locale.HEIGHT_165, callback_data="height_165"),
        ],
        [
            InlineKeyboardButton(locale.HEIGHT_170, callback_data="height_170"),
            InlineKeyboardButton(locale.HEIGHT_175, callback_data="height_175"),
            InlineKeyboardButton(locale.HEIGHT_OTHER, callback_data="height_custom"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def targets_confirm_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline targets confirmation keyboard."""
    keyboard = [[
        InlineKeyboardButton(locale.TARGETS_CONFIRM, callback_data="targets_confirm"),
        InlineKeyboardButton(locale.TARGETS_EDIT, callback_data="targets_edit"),
    ]]
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard_inline(locale) -> InlineKeyboardMarkup:
    """Inline settings action keyboard."""
    keyboard = [[
        InlineKeyboardButton(locale.SETTINGS_EDIT_TARGETS, callback_data="settings_targets"),
        InlineKeyboardButton(locale.SETTINGS_EDIT_PROFILE, callback_data="settings_profile"),
    ]]
    return InlineKeyboardMarkup(keyboard)


def targets_setup_keyboard(locale) -> InlineKeyboardMarkup:
    """Inline targets setup prompt keyboard for migration."""
    keyboard = [[
        InlineKeyboardButton(locale.TARGETS_SETUP_NOW, callback_data="targets_setup_now"),
        InlineKeyboardButton(locale.TARGETS_SETUP_LATER, callback_data="targets_setup_later"),
    ]]
    return InlineKeyboardMarkup(keyboard)
