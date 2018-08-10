import datetime

token = ''
test_user_id = 'user:123'
owner_user_id = 'user:234'
self_user_id = 'user:345'
test_chat_id = 'chat:123'


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H")


now = now()


def setup():
    import os
    # module = os.path.split(os.path.dirname(__file__))[0]#[-1]
#     # print(module)
#     # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(module))
#     import sys
#     sys.path.append(module)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
    import django
    django.setup()
