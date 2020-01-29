from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler
from config import BOT_TOKEN, LOGGING_FORMAT, LOGGING_LEVEL
from app.db_persistence import DBPersistence
from app import callback, states
import logging


logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)
updater = Updater(BOT_TOKEN, use_context=True, persistence=DBPersistence())
dp = updater.dispatcher


def start_bot():
    startup_settings_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback.StartupSettings.display_menu, pattern="continue")],

        states={
            states.ENTERING_TOKEN: [MessageHandler(Filters.text, callback.StartupSettings.token_received)],
            states.PASS_MESSAGES: [CallbackQueryHandler(callback.StartupSettings.pass_messages, pattern=r"(?!return)")],
            states.START_POLLING: [CallbackQueryHandler(callback.StartupSettings.start_polling, pattern=r"yes|no")]
        },

        fallbacks=[
            CallbackQueryHandler(callback.StartupSettings.prev_menu, pattern="return")
        ],

        map_to_parent={
            states.SELECTING_ACTIONS: states.SELECTING_ACTIONS
        },

        allow_reentry=False,
        name="startup_settings",
        persistent=True
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', callback.start)],

        states={
            states.STARTUP_SETTINGS: [CallbackQueryHandler(callback.end_conversation, pattern="cancel"),
                                      startup_settings_handler],
            states.SELECTING_ACTIONS: []
        },

        fallbacks=[],

        allow_reentry=False,
        name="main",
        persistent=True
    )

    dp.add_error_handler(callback.error)
    dp.add_handler(conv_handler)
    startup_settings_handler.persistence = conv_handler.persistence
    startup_settings_handler.conversations = \
        startup_settings_handler.persistence.get_conversations(startup_settings_handler.name)

    for user in dp.user_data:
        if dp.user_data[user].get('is_job_set'):
            dp.job_queue.run_repeating(callback=callback.handle_fh_updates, interval=60, first=0,
                                       context=dp.user_data[user], name=str(user))

    updater.start_polling()
    updater.idle()
