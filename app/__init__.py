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
        entry_points=[CallbackQueryHandler(callback.end_conversation, pattern="cancel")],

        states={
            states.ENTERING_TOKEN
        },

        fallbacks=[],

        map_to_parent={
            states.END: states.END
        },

        allow_reentry=False,
        name="startup_settings",
        persistent=True
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', callback.start)],

        states={
            states.STARTUP_SETTINGS: [startup_settings_handler],
            states.SELECTING_ACTIONS: [CommandHandler('start', callback.start), CommandHandler('stop', callback.stop),
                                       CommandHandler('status', callback.status)]
        },

        fallbacks=[],

        allow_reentry=False,
        name="main",
        persistent=True
    )

    dp.add_error_handler(callback.error)
    dp.add_handler(conv_handler)

    for user in dp.user_data:
        if dp.user_data[user].get('is_job_set'):
            dp.job_queue.run_repeating(callback.send_feed, interval=60, first=0, name=str(user),
                                       context=dp.user_data[user])

    updater.start_polling()
    updater.idle()
