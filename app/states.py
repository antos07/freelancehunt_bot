from telegram.ext import ConversationHandler

END = ConversationHandler.END
STOPPING = -4
ENTERING_TOKEN, PASS_MESSAGES, START_POLLING = range(3)
STARTUP_SETTINGS, SELECTING_ACTIONS = range(100, 102)