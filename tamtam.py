import requests
"""https://github.com/xvlady/tamtam"""


class TamTam:
    """
    Вам нужен аккаунт пользователя в ОК/ТамТам с привязанной почтой,
    который для вас будет являться тем ботом с которым будут общаться пользователи.

    Затем от имени этого аккаунта
    - Получить права разработчика по ссылке https://ok.ru/devaccess
    - После получения прав разработчика открыть раздел Игры, в левом меню выбрать “Мои загруженные”
    и нажать на “Добавить приложение”. Вписать название и «Сохранить»
    - На почту придёт ID приложения, который нужно сообщить

    После чего по этому ID выдам права на API  https://apiok.ru/dev/graph_api/bot_api
    (получение сообщений через вебхук и рассылка)

    Чтобы получить токен нужно зайти в приложение через раздел Игры - Мои загруженные,
    нажать «Изменить настройки приложения», затем ввести секретный ключ.
    В списке прав появится - Bot API.
    Далее нажимаете «Добавить платформу», прокручиваете страничку до низа (кнопки «Сохранить»)
    и там будет кнопка на получение токена,
    Нажимаете на неё и ок



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
        :return json:
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
        """Простой список
        :return json
        {'chat:123467890ABCD': 'Test chat 2018-07-22 23',
         'chat:23467890ABCDE': 'Test2',
         'chat:123456789': '',
         'chat:Ddcd6A41de': ''}
        """
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

    _me_id = None

    def get_dialog_title(self, chat_id, chat=None):
        """Находим по сообщениям чей это персоналльный чат"""
        msgs = self.get_messages(chat_id)
        if not self._me_id:
            self._me_id = self.get_me()['user_id']
        for m in msgs:
            if m['sender']['user_id'] != self._me_id:
                return m['sender']['name']
        if chat:
            z = [x for x in chat['participants'] if x != self._me_id]
            return z[0]
        return chat_id

    def set_icon_chat(self, chat_id, icon_url):
        """send icon from chat
        :param chat_id:
        :param icon_url: https://and.su/bots/icon128.png
        :return:
        >>> from test_config import token, test_chat_id
        >>> r = TamTam(token).set_icon_chat(test_chat_id, bots)
     bots r['message_id'].startswith('mid')
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
        [# редактированное сообщение
         {'edited': True,
          'message': {'mid': 'mid:C3f8698c84b26.165501eef0505cb',
                      'seq': 100574660475028939,
                      'text': 'Поправленное сообщение, оригинала в ответе нет'},
           'recipient': {'chat_id': 'chat:C3f8698c84b26'},
           'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
           'timestamp': 1534647529221},
         # в чат добавили юзера
         {'message': {'mid': 'mid:C3f8698c84b26.165502556403711',
                      'seq': 100574687976765201,
                      'text': '{"ai":562187610613,"pa":[573046260078],"ty":"USERS_ADDED"}'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1534647948864},
         #Атач и текст
         {'message': {'attachments': [{'payload': {'url': 'https://i.mycdn.me/image?id=87301517124329&t=3&plc=API&aid=126867243432&tkn=*hbp3XsOdrwerwer23s'},
                                       'type': 'IMAGE'}],
                      'mid': 'mid:C3f835b894b26.16565d7e487291b',
                      'seq': 100598544612141339,
                      'text': 'sdfsdfs'},
          'recipient': {'chat_id': 'chat:C3f835b894b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1535011972231},
         # фворвард (как прочитать, что прилетело - хз)
         {'message': {'mid': 'mid:C3f8698c84b26.165502454330d89',
                      'seq': 100574683647380873},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1534647882803},
         # ответ на сообщение
         {'message': {'mid': 'mid:C3f8698c84b26.165501ed16f1379',
                      'reply_to': 'mid:C3f8698c84b26.164fe22632210ef',
                      'seq': 100574659978662777,
                      'text': 'ssdfds'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1534647521647},
         # многострочное сообщение со смайликами
         {'message': {'mid': 'mid:C3f8698c84b26.164fe22632210ef',
                      'seq': 100475790818946187,
                      'text': 'b=31 04+22+15+20+156 08.01 05:39\n'
                              'd=59 07+39+42+49+255 08.01 05:12\n'
                              'https://megawiki.megafon.ru/pages/viewpage.action?pageId=189071575'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Елена Три', 'user_id': 'user:575522687955'},
          'timestamp': 1533138897994},
         # тема чата изменена
         {'message': {'mid': 'mid:C3f8698c84b26.164cf6206360163',
                      'seq': 100433111626940771,
                      'text': '{"ai":562187610613,"tn":"WoG '
                              'Log","ty":"THEME_CHANGED"}'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1532487665206},
         # смайл
         {'message': {'attachments': [{'payload': {'url': 'https://dsm.odnoklassniki.ru/getImage?smileId=cfadcda100'},
                                       'type': 'IMAGE'}],
                      'mid': 'mid:C3f8698c84b26.164a39ac33030f9',
                      'seq': 100384976803999993},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1531753186096},
         # новый смайл через ссылку
         {'message': {'mid': 'mid:C3f8698c84b26.164a2e46d663bbb',
                      'seq': 100384193680653243,
                      'text': '{"ui":575522687955,"ty":"JOIN_BY_LINK"}'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Елена Три', 'user_id': 'user:575522687955'},
          'timestamp': 1531741236582},
         # новая иконка чата
         {'message': {'mid': 'mid:C3f8698c84b26.164901c4eaa2d63',
                      'seq': 100363542962253155,
                      'text': '{"ai":562187610613,"ci":{"id":871613984757,"sw":640,"sh":640},"ty":"ICON_CHANGED"}'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1531426131626},
         # первое сообщение - чат создан
         {'message': {'mid': 'mid:C3f8698c84b26.1648ff870360efd',
                      'seq': 100363388906245885,
                      'text': '{"ai":562187610613,"pa":[577456123628,575478725594],"ty":"CHAT_CREATED"}'},
          'recipient': {'chat_id': 'chat:C3f8698c84b26'},
          'sender': {'name': 'Vlady X', 'user_id': 'user:562187610613'},
          'timestamp': 1531423780918}]
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

    @staticmethod
    def get_attachments(msg):
        if 'attachments' not in msg['message']:
            return None, 'TEXT'
        url = msg['message']['attachments']['payload']['url']
        rr = requests.get(url)
        rr.raise_for_status()
        if 'Content-Type' in rr.headers:
            type_msg = rr.headers['Content-Type']
        else:
            type_msg = msg['message']['attachments']['payload']['type']
        if 'Content-Disposition' in rr.headers:
            name = rr.headers['Content-Disposition'].split(';')[1].split('"')[1]
            # : 'attachment; filename="requirements.txt"; filename*=utf-8\'\'requirements.txt']
        else:
            name = None
        return rr.content, type_msg, name


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
