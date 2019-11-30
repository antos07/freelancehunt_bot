from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler
from telegram.ext.filters import Filters
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Chat, ReplyKeyboardRemove
from app import db, fhapi, utils
from os import environ


BOT_TOKEN = environ['BOT_TOKEN']


def ask_token(chat: Chat):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Получить токен", url="https://freelancehunt.com/my/api2")]
    ])
    chat.send_message("Введите токен", reply_markup=buttons)


def start(upd: Update, context: CallbackContext):
    user_id = upd.effective_user.id
    token = db.get_token(user_id)
    if token is None or token[0] is None:
        ask_token(upd.effective_chat)
        db.insert_user(user_id)
    elif db.get_status(user_id) is False:
        db.set_active(user_id)
        context.user_data['job'] = context.job_queue.run_repeating(send_feed, 60, first=0, context=user_id)
        upd.message.reply_text('Информирование включено')
    else:
        upd.message.reply_text('Информироание уже запущено')


def update_token(upd: Update, context: CallbackContext):
    buttons = ReplyKeyboardMarkup([
        ["Да", "Нет"]
    ], one_time_keyboard=True)
    upd.message.reply_text("Хотите обновить токен?", reply_markup=buttons)
    db.save_status(upd.effective_user.id)
    if db.get_status(upd.effective_user.id):
        db.set_inactive(upd.effective_user.id)
        context.user_data['job'].schedule_removal()
        del context.user_data['job']


def answer(upd: Update, context: CallbackContext):
    user_id = upd.effective_user.id
    if upd.message.text == 'Да' and db.get_status(user_id) is False:
        db.set_token(user_id, None)
        upd.message.reply_text('Ок', reply_markup=ReplyKeyboardRemove())
        ask_token(upd.effective_chat)
    else:
        token = db.get_token(user_id)
        if token is None or not fhapi.validate(token[0]):
            upd.message.reply_text('Ваш токен некоректен - обновите его', reply_markup=ReplyKeyboardRemove())
        else:
            db.restore_status(user_id)
            if db.get_status(user_id):
                context.user_data['job'] = context.job_queue.run_repeating(send_feed, 60, first=0, context=user_id)
            upd.message.reply_text('Отменено', reply_markup=ReplyKeyboardRemove())


def token_received(upd: Update, context: CallbackContext):
    token = upd.message.text
    if db.get_token(upd.effective_user.id)[0] is not None:
        return
    if not fhapi.validate(token):
        upd.message.reply_text('Введенный токен некоректен')
    else:
        db.set_token(upd.effective_user.id, token)
        upd.message.reply_text('Токен установлен')
        db.set_active(upd.effective_user.id)
        context.user_data['job'] = context.job_queue.run_repeating(send_feed, 60, first=0, context=upd.effective_user.id)


def send_feed(context: CallbackContext):
    user_id = context.job.context
    token = db.get_token(user_id)[0]
    feed = fhapi.get_feed(token)
    if 'data' not in feed:
        db.set_inactive(user_id)
        context.bot.send_message(user_id, 'Ваш токен некоректен/устарел. Обновите токен используя команду /new_token')
        context.job.schedule_removal()
        del context.user_data['job']
        return
    feed = feed['data']
    for event in feed:
        atr = event['attributes']
        if atr['is_new']:
            text = f"<b>From {atr['from']['type']} {atr['from']['first_name']} {atr['from']['last_name']}</b>" \
                   f"\n{utils.prepare_text(atr['message'])}"
            context.bot.send_message(user_id, text, parse_mode="HTML", disable_web_page_preview=True)


def stop(upd: Update, context: CallbackContext):
    if db.get_status(upd.effective_user.id):
        db.set_inactive(upd.effective_user.id)
        context.user_data['job'].schedule_removal()
        del context.user_data['job']
    upd.message.reply_text('Информирование отключено')


def status(upd: Update, context: CallbackContext):
    if db.get_status(upd.effective_user.id):
        upd.message.reply_text('Информирование активно')
    else:
        upd.message.reply_text('Информирование отключено')


def error(upd: Update, context: CallbackContext):
    print('In update\n{}\n error "{}"'.format(upd, context.error))


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    active_jobs = db.get_active_jobs()
    for user_id in active_jobs:
        dp.user_data[user_id[0]]['job'] = dp.job_queue.run_repeating(send_feed, 60, first=0, context=user_id[0])

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('stop', stop))
    dp.add_handler(CommandHandler('new_token', update_token))
    dp.add_handler(CommandHandler('status', status))
    dp.add_handler(MessageHandler(Filters.regex(r'Да') | Filters.regex(r'Нет'), answer))
    dp.add_handler(MessageHandler(Filters.text, token_received))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
