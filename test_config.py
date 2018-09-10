import datetime

token = ''
test_user_id = 'user:123'
owner_user_id = 'user:234'
self_user_id = 'user:345'
test_chat_id = 'chat:123'


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H")


now = now()
