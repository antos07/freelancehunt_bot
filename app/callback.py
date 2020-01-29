from telegram.ext import CallbackContext
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from app import states, fhapi
from logging import getLogger
from config import PARSE_MODE


logger = getLogger(__name__)


def error(upd: Update, context: CallbackContext):
    logger.error("In update %s caught \"%s\"", upd,  context.error)


def start(upd: Update, context: CallbackContext):
    context.user_data['chat'] = upd.effective_chat
    buttons = [InlineKeyboardButton(text="Отменить", callback_data="cancel"),
               InlineKeyboardButton(text="Продолжить", callback_data="continue")]
    reply_markup = InlineKeyboardMarkup.from_row(buttons)
    upd.effective_message.reply_text('Данный бот является неофициальным. Сообщая ему личные данные, '
                                     'вы соглашаетесь на их дальнейшее использование и обработку.',
                                     reply_markup=reply_markup)
    return states.STARTUP_SETTINGS


def handle_fh_updates(context: CallbackContext):
    user_data = context.job.context
    logger.debug("'handle_fh_updates' was called with user_data '%s'", user_data)
    events = fhapi.get_updates(user_data['settings'])
    for event in events:
        user_data['chat'].send_message(event, parse_mode=PARSE_MODE)


def end_conversation(upd: Update, context: CallbackContext):
    upd.callback_query.edit_message_text('Отменено. Пропишите /start, чтобы запустить бота.')
    return states.END


class StartupSettings:
    @staticmethod
    def display_menu(upd: Update, context: CallbackContext):
        user_data = context.user_data
        upd.callback_query.answer()
        user_data['startup_settings'] = {
            'message': upd.effective_message.edit_text('Введите токен'),
            'lvl': 0
        }
        user_data['settings'] = {}
        logger.debug("Displayed startup settings menu for user %s", upd.effective_user.id)
        return states.ENTERING_TOKEN

    @staticmethod
    def prev_menu(upd: Update, context: CallbackContext):
        context.user_data['startup_settings']['lvl'] -= 1
        lvl = context.user_data['startup_settings']['lvl']
        if lvl > 2:
            logger.critical("'lvl > 2' for user' %s", upd.effective_user.id)
            exit(0)
        logger.debug('prev_menu called for user %s on lvl %s', upd.effective_user.id, lvl)
        upd.callback_query.answer()
        if lvl == 0:
            context.user_data['startup_settings']['message'].edit_text('Введите токен')
        elif lvl == 1:
            buttons = [
                [InlineKeyboardButton('Да', callback_data="yes"), InlineKeyboardButton('Нет', callback_data="no")],
                [InlineKeyboardButton('Назад', callback_data="return")]]
            reply_markup = InlineKeyboardMarkup(buttons)
            context.user_data['startup_settings']['message'].edit_text('Присылать входящие сообщения?',
                                                                       reply_markup=reply_markup)
        return lvl

    @staticmethod
    def token_received(upd: Update, context: CallbackContext):
        logger.debug('Token has been received for user %s', upd.effective_user.id)
        token = upd.message.text
        user_data = context.user_data
        validation = fhapi.validate(token)
        if validation != fhapi.OK:
            if validation == fhapi.NETWORK_ERROR:
                error_text = "api.freelancehunt.com временно не доступен. Повторите попытку позже"
            elif validation == fhapi.TOKEN_ERROR:
                error_text = "Введенный токен некоректен. Повторите попытку"
            elif validation == fhapi.TOO_MANY_REQUESTS:
                error_text = "Было превышено кол-во запросов. Повторите попытку через минуту"
            else:
                error_text = "Неизвестная ошибка"
            user_data['startup_settings']['message'].edit_text(error_text)
            return states.ENTERING_TOKEN
        user_data['settings']['token'] = token
        buttons = [[InlineKeyboardButton('Да', callback_data="yes"), InlineKeyboardButton('Нет', callback_data="no")],
                   [InlineKeyboardButton('Назад', callback_data="return")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        user_data['startup_settings']['message'].edit_text('Токен установлен.\nПрисылать входящие сообщения?',
                                                           reply_markup=reply_markup)
        user_data['startup_settings']['lvl'] += 1
        logger.debug('Token has been set for user %s', upd.effective_user.id)
        return states.PASS_MESSAGES

    @staticmethod
    def pass_messages(upd: Update, context: CallbackContext):
        res = upd.callback_query.data
        upd.callback_query.answer()
        t = context.user_data['settings']['pass_messages'] = (res == 'yes')
        logger.debug("'settings.pass_messages = %s' for user %s", t, upd.effective_user.id)
        buttons = [[InlineKeyboardButton('Да', callback_data="yes"), InlineKeyboardButton('Нет', callback_data="no")],
                   [InlineKeyboardButton('Назад', callback_data="return")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.user_data['startup_settings']['message'].edit_text('Активировать получение обновлений?',
                                                                   reply_markup=reply_markup)
        upd.callback_query.answer()
        context.user_data['startup_settings']['lvl'] += 1
        logger.debug("'start_polling' menu has been sent for user %s", upd.effective_user.id)
        return states.START_POLLING

    @staticmethod
    def start_polling(upd: Update, context: CallbackContext):
        res = upd.callback_query.data
        if res == 'yes':
            context.job_queue.run_repeating(callback=handle_fh_updates, interval=60, first=0, context=context.user_data,
                                            name=str(upd.effective_user.id))
            context.user_data['is_job_set'] = True
            logger.debug('job has been set for user %s', upd.effective_user.id)
        context.user_data['startup_settings']['message'].edit_text('Настройка завершена')
        upd.callback_query.answer()
        del context.user_data['startup_settings']
        logger.debug("'StartupSettings' ended for user %s", upd.effective_user.id)
        return states.SELECTING_ACTIONS
