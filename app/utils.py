from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from app.fhapi import get_feed


def ask_token(chat):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Получить токен", url="https://freelancehunt.com/my/api2")]
    ])
    chat.send_message("Введите токен", reply_markup=buttons)


def tuple_from_key(key: str):
    key = key[1: -1]
    return tuple(map(int, key.split(', ')))


def prepare_feed(token):
    return ["test"]
