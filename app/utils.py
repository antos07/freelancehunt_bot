from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def tuple_from_key(key: str):
    key = key[1: -1]
    return tuple(map(int, key.split(', ')))
