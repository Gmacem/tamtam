import requests


class TamTam:
    """
    https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.chats
    >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now
    >>> token != ''
    True
    >>> test_chat_id != ''
    True
    >>> test_user_id != ''
    True
    >>> self_user_id != ''
    True
    >>> now != ''
    True
    """

    _url_root = 'https://api.ok.ru/graph/'
    _url = 'https://api.ok.ru/graph/me/'
    _headers = {
        'Content-Type': 'application/json',
        'charset': 'utf-8',
    }
    _token = ''

    def __init__(self, token):
        self._token = token

    def post_messages(self, data, ai=False):
        rr = requests.post(self._url + 'messages',
                           params={'access_token': self._token},
                           json=data,
                           headers=self._headers)
        rr.raise_for_status()
        z = rr.json()
        if not ai:
            if not z['message_id'].startswith('mid:'):
                raise MessageNotSendException(z)
        return z

    def send(self, chat_id, text):
        """send message into chat  полетело сообщение в заданный чат
        :param chat_id:
        :param text:
        :return:
        >>> from test_config import token, test_chat_id, now
        >>> tt=TamTam(token).send(test_chat_id, 'Hi! '+now)
        >>> tt['message_id'].startswith('mid:')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "message": {"text": text},
        }
        return self.post_messages(data=data)

    def send_img(self, chat_id, url):
        """
        Отравляем картинку
        :param chat_id:
        :param url: URL изображения в формате jpg или png
        :return:
        >>> from test_config import token, test_chat_id
        >>> tt=TamTam(token).send(test_chat_id, 'https://docs.djangoproject.com/s/img/small-fundraising-heart.d255f6e934e5.png')
        >>> tt['message_id'].startswith('mid:')
        True
        >>> tt=TamTam(token).send(test_chat_id, 'abrakatabra') #улетело простое сообщение
        >>> tt['message_id'].startswith('mid:')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "message": {
                "attachment": {
                    "type": "IMAGE",
                    "payload": {"url": url}
                }
            }
        }
        return self.post_messages(data=data)

    def send_file(self):
        """
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.fileUploadUrl/get
        :return:
        """
        pass

    def send_pers(self, user_id, text):
        """
        отправка персонального сообщения пользователю чата
        :param text:
        :param user_id:
        :return:
        >>> from test_config import token, test_user_id, now
        >>> r = TamTam(token).send_pers(test_user_id, 'DocTest Running '+now+'!')
        >>> r['message_id'].startswith('mid')
        True
        """
        data = {
            "recipient": {"user_id": user_id},
            "message": {"text": text},
        }
        return self.post_messages(data=data)

    def mark_seen(self, chat_id):
        """
        Все соообщения прочитаны
        :param chat_id: 
        :return:
        >>> from test_config import token, test_chat_id
        >>> r=TamTam(token).mark_seen(test_chat_id)
        >>> r=={'success': True}
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "sender_action": "mark_seen",
        }
        return self.post_messages(data=data, ai=True)

    def get_me(self):
        """Получение информации о текущем пользователе
        {'name': 'Елена Три', 'user_id': 'user:575522687955'}
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.info/get
        :return:json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat(test_chat_id)
        >>> tt['user_id'].startswith('user:')
        True
        """
        params = {'access_token': self._token}
        rr = requests.get(self._url + 'info', params=params)
        rr.raise_for_status()
        zz = rr.json()
        return zz

    def get_chat_list(self, count=100, marker=None):
        """list chat users-bot
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.chats/get
        :param count:
        :param marker:
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat_list()
        >>> len(tt) >=0
        True
        >>> tt[0]['chat_id'].startswith('chat:')
        True
        >>> z = [x for x in tt if(x['chat_id'] == test_chat_id)]
        >>> z[0]['owner_id'] == owner_user_id
        True
        """
        params = {'access_token': self._token, 'count': count}
        if marker is not None:
            params['marker'] = marker
        rr = requests.get(self._url + 'chats', params=params)
        rr.raise_for_status()
        zz = rr.json()
        return zz['chats']

    def get_chat_all(self):
        """
        Полный список чатов
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat_all()
        >>> len(tt) >=0
        True
        >>> tt[0]['chat_id'].startswith('chat:')
        True
        >>> z = [x for x in tt if(x['chat_id'] == test_chat_id)]
        >>> z[0]['owner_id'] == owner_user_id
        True
        """
        marker = None
        step = 0
        zz = []
        rr = []
        while (step == 0) or ((len(zz) == 100) and (step < 50)):
            zz = self.get_chat_list(count=100, marker=marker)
            rr = rr + zz
            step = step + 1
        return rr

    def get_flat_chat_list(self):
        json = self.get_chat_list()
        return get_result(json_data=json, key_key='chat_id', key_value='title')

    def get_chat(self, chat_id):
        """информация только об одном чате
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.chat/get
        :return:json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat(test_chat_id)
        >>> tt['title'].startswith('Test chat')
        True
        """
        params = {'access_token': self._token, 'chat_id': chat_id}
        rr = requests.get(self._url + 'chat', params=params)
        rr.raise_for_status()
        zz = rr.json()
        return zz

    def get_chat_url(self, chat_id):
        """Получение прямой ссылки на чат по его ID
        https://apiok.ru/dev/graph_api/methods/graph.chat/graph.chat.url/get
        :return:json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat(test_chat_id)
        >>> tt['url'].startswith('https://ok.ru/messages/g')
        True
        """
        params = {'access_token': self._token}
        rr = requests.get(self._url_root + chat_id + '/url', params=params)
        rr.raise_for_status()
        zz = rr.json()
        return zz

    def rename_chat(self, chat_id, name):
        """send message from rename chat
        :param chat_id:
        :param name: Новый заголовок
        :return:
        >>> from test_config import token, test_chat_id, now
        >>> r = TamTam(token).rename_chat(test_chat_id, 'Test chat '+now)
        >>> r['message_id'].startswith('mid')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "chat_control": {
                "title": name
            },
        }
        return self.post_messages(data=data)

    def set_icon_chat(self, chat_id, icon_url):
        """send icon from chat
        :param chat_id:
        :param icon_url: https://and.su/tamtam_bot/icon128.png
        :return:
        >>> from test_config import token, test_chat_id
        >>> r = TamTam(token).set_icon_chat(test_chat_id, tamtam_bot)
     tamtam_bot r['message_id'].startswith('mid')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "chat_control": {
                "icon": {"url": icon_url},
            },
        }
        return self.post_messages(data=data)

    def get_messages(self, chat_id):
        """
        Todo:from,to,count
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.messages/get
        :param chat_id: chat:C3f8698c84b26
        :return: json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now
        >>> r = TamTam(token).get_messages(chat_id=test_chat_id)
        >>> z = [x for x in r if (x['sender']['user_id'] == self_user_id) & (x['message']['text'].find("Hi") != -1)]
        >>> len(z)>0 #
        True
        """
        rr = requests.get(self._url + 'messages/' + chat_id, params={'access_token': self._token})
        rr.raise_for_status()
        zz = rr.json()
        return zz['messages']

    def get_messages_pers(self, user_id):
        """
        Список сообщений из личной беседы
        :param user_id:
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now
        >>> r = TamTam(token).get_messages_pers(test_user_id)
        >>> len(r)>0
        True
        >>> r = TamTam(token).get_messages_pers('user:124567')
        Traceback (most recent call last):
            ...
        UserDonTHaveChatException: user:124567
        """
        rr = self.get_chat_list()
        zz = [x for x in rr if((x['type'] == 'DIALOG') & (user_id in x['participants'].keys()))]
        if len(zz) == 0:
            raise UserDonTHaveChatException(user_id)
        chat_id = zz[0]['chat_id']  # по идее беседа одна
        return self.get_messages(chat_id=chat_id)


def get_result(json_data, key_key, key_value):
    """
    >>> get_result([{'a':'b1', 'x':'y1'}, {'a':'b2', 'x':'y2'}, {'a':'none'}],'a','x')
    {'b1': 'y1', 'b2': 'y2', 'none': ''}
    >>>  get_result([{'a':'b1', 'x':'y1'}, {'a':'b2', 'x':'y2'}, {'x':'none'}],'a','x')
    Traceback (most recent call last):
        ...
    IndentationError: unexpected indent
    """
    labels_list = {}
    for index in json_data:
        labels_list[index[key_key]] = index.get(key_value, '')
    return labels_list
    # [obj for obj in dict if(obj['type'] == 1)] -- фильтрация


class UserDonTHaveChatException(Exception):
    pass


class MessageNotSendException(Exception):
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
