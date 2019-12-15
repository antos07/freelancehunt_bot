from requests import get
from json import loads


API_URL = "https://api.freelancehunt.com/v2"


def validate(token):
    return get(API_URL, headers={'Authorization': f'Bearer {token}'}).status_code == 404


def get_feed(token):
    url = API_URL + "/my/feed/"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    request = get(url, headers=headers)
    return loads(request.text)


if __name__ == "__main__":
    TEST_TOKEN = "a10207aff6d23d9d735bcd6e36eefa9f2ba2a0d0"
    print(get_feed(TEST_TOKEN)['data'][5])
