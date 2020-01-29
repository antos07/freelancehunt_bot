from requests import get
import requests.exceptions
import logging
from time import sleep
import re


API_URL = "https://api.freelancehunt.com/v2"
EVENT_TEMPLATE = '{type} <b>{login}</b> {message}'
OK, NETWORK_ERROR, TOKEN_ERROR, TOO_MANY_REQUESTS = range(4)
logger = logging.getLogger(__name__)


def _api_get(token, rel_url="/"):
    return get(API_URL + rel_url, headers={'Authorization': f'Bearer {token}'})


def validate(token):
    try:
        response = _api_get(token)
    except requests.exceptions.RequestException as error:
        return NETWORK_ERROR
    res = response.json()
    if 'error' in res and response.status_code != 404:
        if response.status_code == 429:
            logger.warning("Server returned 'Too Many Requests' for validation query for user with token %s...",
                           token[:len(token) // 2])
            return TOO_MANY_REQUESTS
        logger.warning("Received error '%s' for token %s...", res['error'], token[:len(token) // 2])
        return TOKEN_ERROR
    else:
        return OK


def _get_feed(token):
    try:
        response = _api_get(token, "/my/feed")
    except requests.exceptions.RequestException as error:
        logger.critical("Request raised error '%s'. Returned 'NETWORK_ERROR'", error)
        return NETWORK_ERROR
    feed = response.json()
    if 'error' in feed and response.status_code != 404:
        if response.status_code == 429:
            logger.warning("Server returned 'Too Many Requests' for validation query for user with token %s...",
                           token[:len(token) // 2])
            return TOO_MANY_REQUESTS
        logger.warning("Received error '%s' for token %s...", feed['error'], token[:len(token) // 2])
        return TOKEN_ERROR
    return _prepare_feed(feed)


def _prepare_event_msg(text):
    msg = re.sub(r"<img.*/?>", "", text)
    msg = re.sub(r'<a.* href="(.*?)".*?>', lambda m: f'<a href="{m.group(1)}">', msg)
    return msg


def _prepare_feed(feed):
    events = []
    for i in feed['data']:
        attrs = i['attributes']
        if not attrs['is_new']:
            break
        from_type = "закачкик" if attrs['from']['type'] == "employer" else "исполнитель"
        login = attrs['from']['login']
        msg = _prepare_event_msg(attrs['message'])
        event = EVENT_TEMPLATE.format(type=from_type, login=login, message=msg)
        events.append(event)
    return events[::-1]


def _get_threads(token):
    try:
        response = _api_get(token, "/threads")
    except requests.exceptions.RequestException as error:
        logger.critical("Request raised error '%s'. Returned 'NETWORK_ERROR'", error)
        return NETWORK_ERROR
    threads = response.json()
    if 'error' in threads and response.status_code != 404:
        if response.status_code == 429:
            logger.warning("Server returned 'Too Many Requests' for validation query for user with token %s...",
                           token[:len(token) // 2])
            return TOO_MANY_REQUESTS
        logger.warning("Received error '%s' for token %s...", msgs['error'], token[:len(token) // 2])
        return TOKEN_ERROR
    return threads['data']


def _get_message(token):
    return "some text"


def _get_messages(token):
    threads = _get_threads(token)
    msgs = []
    for thread in threads:
        attrs = thread['attributes']
        if not attrs['is_unread']:
            continue



def get_updates(settings):
    token = settings['token']
    logger.debug("Starting 'get_updates' for token %s...", token[:len(token) // 2])
    validation = validate(token)
    if validation == TOO_MANY_REQUESTS:
        sleep(20)
        return get_updates(settings)
    elif validation != OK:
        return validation

    feed = _get_feed(token)
    if not isinstance(feed, list):
        return feed
    return feed


if __name__ == "__main__":
    TEST_TOKEN = "a10207aff6d23d9d735bcd6e36eefa9f2ba2a0d0"
    TEST_SETTINGS = {
        'token': TEST_TOKEN
    }
    TEST_MSG = 'От закачкика freelancehunt:\nИтоги 2019 года Freelancehunt: <a href="https://freelancehunt.com/blog/itoghi-ghoda/?utm_source=freelancehunt&utm_medium=feed&utm_campaign=blog-teaser" target="_blank">рекорды в цифрах!</a> <img src="https://freelancehunt.com/static/images/fugu/new-text.png" width="16" height="16"/>'
    #print(get_updates(TEST_SETTINGS))
    #print(_get_feed(TEST_TOKEN))
    print(_get_threads(TEST_TOKEN))
    #print(_prepare_msg(TEST_MSG))
