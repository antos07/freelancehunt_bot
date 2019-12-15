from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from app import states, fhapi
from app.utils import ask_token, prepare_feed
from logging import getLogger
from config import PARSE_MODE


logger = getLogger(__name__)


def error(upd: Update, context: CallbackContext):
    logger.error("In update %s caught \"%s\"", upd,  context.error)


def send_feed(context):
    bot = context.bot
    context = context.job.context
    feed = prepare_feed(context['token'])
    for msg in feed:
        bot.send_message(context['user_id'], msg, disable_web_page_preview=True, parse_mode=PARSE_MODE)


def start(upd: Update, context: CallbackContext):
    user_data = context.user_data
    token = user_data.get('token')
    if token is None:
        buttons = [InlineKeyboardButton(text="Отменить", callback_data="cancel"),
                   InlineKeyboardButton(text="Продолжить", callback_data="continue")]
        reply_markup = InlineKeyboardMarkup.from_row(buttons)
        upd.effective_message.reply_text('Данный бот является неофициальным. Сообщая ему личные данные, '
                                         'вы соглашаетесь на их дальнейшее использование и обработку.',
                                         reply_markup=reply_markup)
        return states.STARTUP_SETTINGS
    elif not user_data.get('is_job_set'):
        user_data['is_job_set'] = True
        context.job_queue.run_repeating(send_feed, interval=60, first=0, name=str(upd.effective_user.id),
                                        context=user_data)
        upd.effective_message.reply_text('Активировано')
    else:
        upd.effective_message.reply_text('Информирование уже активно')
    return states.SELECTING_ACTIONS


def token_received(upd: Update, context: CallbackContext):
    token = upd.effective_message.text
    if not fhapi.validate(token):
        upd.effective_message.reply_text('Введенный токен некоректен. Повторите попытку')
        return states.ENTERING_TOKEN
    context.user_data['token'] = token
    upd.effective_message.reply_text('Токен установлен. Пропишите /start чтобы запустить информирование')
    return states.SELECTING_ACTIONS


def stop(upd: Update, context: CallbackContext):
    user_data = context.user_data
    if user_data.get('token') is None or not user_data.get('is_job_set'):
        upd.effective_message.reply_text('Информирое неактивно')
    else:
        job = context.job_queue.get_jobs_by_name(str(upd.effective_user.id))[0]
        job.schedule_removal()
        del job
        user_data['is_job_set'] = False
        upd.effective_message.reply_text('Информирое отключено')
    return states.SELECTING_ACTIONS


def status(upd: Update, context: CallbackContext):
    user_data = context.user_data
    if user_data.get('is_job_set'):
        upd.effective_message.reply_text('Информирое активно')
    else:
        upd.effective_message.reply_text('Информирое отключено')
    return states.SELECTING_ACTIONS


def end_conversation(upd: Update, context: CallbackContext):
    upd.callback_query.edit_message_text('Отменено. Пропишите /start, чтобы запустить бота.')
    return states.END


def ()
