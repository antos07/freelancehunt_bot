from os import environ
import logging
from telegram import ParseMode


DEBUG = True

# logging config
LOGGING_FORMAT = "%(asctime)s - %(levelname)s - %(module)s:%(lineno)d - %(funcName)s - %(message)s"
LOGGING_LEVEL = logging.DEBUG


# bot config
BOT_TOKEN = environ.get("BOT_TOKEN")
PARSE_MODE = ParseMode.MARKDOWN


# persistence settings
STORE_USER_DATA = True
STORE_CHAT_DATA = False


# database config
DATABASE_URL = environ.get("DATABASE_URL")
