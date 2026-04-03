"""DiaBot entry point — Telegram bot for carb/KBJU tracking."""

import logging
import os
import sys

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from config import load_settings
from handlers import (
    ONBOARDING_CONSENT,
    ONBOARDING_GENDER,
    ONBOARDING_HEIGHT,
    ONBOARDING_WEIGHT,
    ONBOARDING_AGE,
    ONBOARDING_TARGETS_CONFIRM,
    IDLE,
    AWAITING_CONFIRM,
    AWAITING_GLUCOSE,
)
from handlers.start import (
    handle_start,
    handle_consent_callback,
    handle_help,
    handle_gender_callback,
    handle_height_callback,
    handle_height_text,
    handle_weight_text,
    handle_age_text,
    handle_targets_confirm_callback,
    handle_targets_edit_text,
    handle_onboarding_cancel,
)
from handlers.photo import handle_photo
from handlers.text import handle_text
from handlers.confirm import handle_confirm, handle_cancel, handle_correction_text
from handlers.diary import handle_today, handle_week, handle_history, handle_undo
from handlers.glucose import handle_sugar_button, handle_glucose_value
from handlers.admin import handle_adduser, handle_removeuser, handle_listusers
from handlers.privacy import (
    handle_privacy,
    handle_export,
    handle_delete_data,
    handle_delete_confirm,
)
from handlers.settings import (
    handle_settings, handle_settings_callback,
    handle_targets_setup_callback, handle_admin_callback,
)
from handlers.access import handle_access_request_callback, handle_review_callback
from services.database import Database
from services.llm import LLMService
from services.auth import AuthService

logger = logging.getLogger(__name__)


def main() -> None:
    """Initialize and run the bot."""
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    # Suppress noisy litellm logs
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    logging.getLogger("litellm").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        settings = load_settings()
    except ValueError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)

    # Build services
    db = Database(settings.db_path)
    llm = LLMService(
        gemini_api_key=settings.gemini_api_key,
        openrouter_api_key=settings.openrouter_api_key,
        groq_api_key=settings.groq_api_key,
    )
    auth = AuthService(
        db=db,
        admin_ids=settings.admin_ids,
        rate_limit_requests=settings.rate_limit_requests,
        rate_limit_window=settings.rate_limit_window,
    )

    # Build application with persistence
    persistence_path = os.path.join(
        os.path.dirname(settings.db_path) or "data", "bot_persistence.pickle"
    )
    from telegram.ext import PicklePersistence
    persistence = PicklePersistence(filepath=persistence_path)
    app = (
        Application.builder()
        .token(settings.telegram_token)
        .persistence(persistence)
        .build()
    )

    # Store services in bot_data for handler access
    app.bot_data["db"] = db
    app.bot_data["llm"] = llm
    app.bot_data["auth"] = auth
    app.bot_data["settings"] = settings

    # --- Conversation Handler ---
    # Entry points include text/photo so the bot works even without /start
    # (e.g., after restart when persistence fails or for returning users)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handle_start),
            MessageHandler(filters.PHOTO, handle_photo),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
            CommandHandler("today", handle_today),
            CommandHandler("week", handle_week),
            CommandHandler("history", handle_history),
            CommandHandler("undo", handle_undo),
            CommandHandler("sugar", handle_sugar_button),
            CommandHandler("help", handle_help),
            CommandHandler("settings", handle_settings),
            CommandHandler("privacy", handle_privacy),
            CommandHandler("export", handle_export),
            CommandHandler("delete_my_data", handle_delete_data),
            CommandHandler("adduser", handle_adduser),
            CommandHandler("removeuser", handle_removeuser),
            CommandHandler("listusers", handle_listusers),
        ],
        states={
            # Onboarding flow
            ONBOARDING_CONSENT: [
                CallbackQueryHandler(handle_consent_callback, pattern="^consent_"),
            ],
            ONBOARDING_GENDER: [
                CallbackQueryHandler(handle_onboarding_cancel, pattern="^onboarding_cancel$"),
                CallbackQueryHandler(handle_gender_callback, pattern="^gender_"),
            ],
            ONBOARDING_HEIGHT: [
                CallbackQueryHandler(handle_onboarding_cancel, pattern="^onboarding_cancel$"),
                CallbackQueryHandler(handle_height_callback, pattern="^height_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_height_text),
            ],
            ONBOARDING_WEIGHT: [
                CallbackQueryHandler(handle_onboarding_cancel, pattern="^onboarding_cancel$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weight_text),
            ],
            ONBOARDING_AGE: [
                CallbackQueryHandler(handle_onboarding_cancel, pattern="^onboarding_cancel$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_age_text),
            ],
            ONBOARDING_TARGETS_CONFIRM: [
                CallbackQueryHandler(handle_targets_confirm_callback, pattern="^targets_(confirm|edit)$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_targets_edit_text),
            ],
            # Main idle state
            IDLE: [
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text),
                CommandHandler("today", handle_today),
                CommandHandler("week", handle_week),
                CommandHandler("history", handle_history),
                CommandHandler("undo", handle_undo),
                CommandHandler("sugar", handle_sugar_button),
                CommandHandler("help", handle_help),
                CommandHandler("settings", handle_settings),
                CommandHandler("privacy", handle_privacy),
                CommandHandler("export", handle_export),
                CommandHandler("delete_my_data", handle_delete_data),
                CommandHandler("adduser", handle_adduser),
                CommandHandler("removeuser", handle_removeuser),
                CommandHandler("listusers", handle_listusers),
                CallbackQueryHandler(handle_delete_confirm, pattern="^delete_"),
                CallbackQueryHandler(handle_settings_callback, pattern="^settings_"),
                CallbackQueryHandler(handle_admin_callback, pattern="^admin_"),
                CallbackQueryHandler(handle_targets_setup_callback, pattern="^targets_setup_"),
            ],
            # Awaiting food confirmation
            AWAITING_CONFIRM: [
                CallbackQueryHandler(handle_confirm, pattern="^confirm$"),
                CallbackQueryHandler(handle_cancel, pattern="^cancel$"),
                MessageHandler(filters.PHOTO, handle_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_correction_text),
            ],
            # Awaiting glucose value
            AWAITING_GLUCOSE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_glucose_value),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handle_cancel),
            CommandHandler("start", handle_start),
        ],
        allow_reentry=True,
        persistent=True,
        name="diabot_conversation",
    )

    app.add_handler(conv_handler)

    # Standalone handlers for callbacks that may arrive outside conversation context
    app.add_handler(CallbackQueryHandler(handle_review_callback, pattern=r"^review_(approve|reject)_\d+$"))
    app.add_handler(CallbackQueryHandler(handle_access_request_callback, pattern=r"^access_request$"))

    # --- Lifecycle hooks ---
    async def post_init(application: Application) -> None:
        """Initialize database on startup."""
        db_dir = os.path.dirname(settings.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        await db.init()
        logger.info("DiaBot started. Admins: %s", settings.admin_ids)

    async def post_shutdown(application: Application) -> None:
        """Clean up on shutdown."""
        await db.close()
        logger.info("DiaBot stopped.")

    app.post_init = post_init
    app.post_shutdown = post_shutdown

    # Run polling
    logger.info("Starting DiaBot polling...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
