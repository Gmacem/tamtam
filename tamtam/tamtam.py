import requests
import json

"""https://github.com/xvlady/tamtam"""


class TamTam:
    """
    Вам нужен аккаунт пользователя в ТамТам,
    который для вас будет являться тем ботом с которым будут общаться пользователи.

    *** тут пока магия получения прав и токена ***

    место куда отправляются файлики:
    https://fu.mycdn.me/

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

    _url = 'https://botapi.tamtam.chat/'
    _headers = {
        'Content-Type': 'application/json',
        'charset': 'utf-8',
    }
    _token = ''

    def __init__(self, token):
        self._token = token

    def _post_messages(self, data, ai=False, params=None):
        if not params:
            params = {}
        params['access_token'] = self._token
        rr = requests.post(self._url + 'me/messages',
                           params=params,
                           json=data,
                           headers=self._headers)
        rr.raise_for_status()
        try:
            z = rr.json()
        except TypeError:
            raise TypeError(rr.text)
        if not ai:
            if not z['message_id'].startswith('mid.'):
                raise MessageNotSendException(z)
        return z

    def _get(self, url: str, params=None, json=True):
        if not params:
            params = {}
        params['access_token'] = self._token
        rr = requests.get(self._url + url, params=params)
        rr.raise_for_status()
        if json:
            z = rr.json()
        else:
            z = rr.content.decode('utf-8')
        return z

    def send(self, chat_id: int, text: str):
        """send message into chat  полетело сообщение в заданный чат
        :param chat_id:
        :param text:
        :return json:
        >>> from test_config import token, test_chat_id, now
        >>> tt=TamTam(token).send(test_chat_id, 'Hi! '+now)
        >>> tt['message_id'].startswith('mid.')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "message": {"text": text},
        }
        return self._post_messages(data=data)

    def send_img(self, chat_id: int, url: str):
        """
        Отравляем картинку
        :param chat_id:
        :param url: URL изображения в формате jpg или png
        :return:
        >>> from test_config import token, test_chat_id
        >>> tt=TamTam(token).send(test_chat_id, 'https://docs.djangoproject.com/s/img/small-fundraising-heart.d255f6e934e5.png')
        >>> tt['message_id'].startswith('mid.')
        True
        >>> tt=TamTam(token).send(test_chat_id, 'abrakatabra') #улетело простое сообщение
        >>> tt['message_id'].startswith('mid.')
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
        return self._post_messages(data=data)

    def _get_post(self, url, params, data=None, json=None):
        params['access_token'] = self._token
        rr = requests.post(self._url + url,
                           params=params,
                           data=data,
                           json=json,
                           headers=self._headers)
        rr.raise_for_status()
        return rr.json()

    ATTACH_TYPE = ['PHOTO', 'VIDEO', 'AUDIO', 'FILE']

    def send_file(self, chat_id: int, file_name: str, file_data, attach_type='FILE', text=None):
        """
        1 Получить URL на загрузку аттача отправв POST запрос в формате JSON
        на https://botapi.tamtam.chat/me/upload?access_token=TOKEN&type=ATTACH_TYPE
        где ATTACH_TYPE = PHOTO | VIDEO | AUDIO | FILE
        2. Загрузить контент по полученному URL - в результате вернётся json, который будет являться payload
        3. Передать этот payload в  POST /me/messages
        {
            "recipient": {
                "chat_id" : …
            },
            "message": {
                "text":"…",
                "attachments": [{
                        "type": <ATTACH_TYPE>,
                        "payload": <то, что вернулось на втором шаге>
                }]
            }
        }
        :return: json
        test > test_tamtam.py (test_send_file)
        """
        if attach_type not in self.ATTACH_TYPE:
            raise ValueError(attach_type+' not in '+str(self.ATTACH_TYPE))

        url = self._get_post('me/upload', params={'access_token': self._token, 'type': attach_type})['url']
        data = {'file': (file_name, file_data, 'application/x-www-form-urlencoded')}
        req = requests.post(url, files=data).json()
        payload = {
            "recipient": {
                "chat_id": chat_id
            },
            "message": {
                "attachments": [{
                    "type": attach_type,
                    "payload": req
                }]
            }
        }
        if text:
            payload["message"]["text"] = text

        send = self._get_post('me/messages', params={'access_token': self._token, 'type': attach_type},
                              json=payload)
        return send

    def send_pers(self, user_id: int, text: str):
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
        return self._post_messages(data=data)

    def mark_seen(self, chat_id: int):
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
        return self._post_messages(data=data, ai=True)

    def get_me(self):
        """Получение информации о текущем пользователе
        {'name': 'Елена Три', 'user_id': 'user:575522687955'}
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.info/get
        :return:json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_me()
        >>> tt['user_id']==self_user_id
        True
        """
        return self._get(url='me/info')

    def get_chats(self, count=100, marker=None):
        """list chat users-bot
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.chats/get
        :param count:
        :param marker:
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt, x=TamTam(token).get_chats()
        >>> len(tt) >=0
        True
        >>> type(tt[0]['chat_id']) is int
        True
        >>> z = [x for x in tt if(x['chat_id'] == test_chat_id)]
        >>> len(z)
        1
        """
        params = {'count': count}
        if marker:
            params['marker'] = marker
        zz = self._get(url='me/chats', params=params)
        return zz['chats'], zz['marker'] if 'marker' in zz else None

    def get_chats_all(self):
        """
        Полный список чатов
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chats_all()
        >>> len(tt) >=0
        True
        >>> type(tt[0]['chat_id']) is int
        True
        >>> z = [x for x in tt if(x['chat_id'] == test_chat_id)]
        >>> len(z)
        1
        """
        marker = None
        step = 0
        zz = []
        rr = []
        while (step == 0) or ((len(zz) == 100) and (step < 50)):
            zz, marker = self.get_chats(count=100, marker=marker)
            rr = rr + zz
            step = step + 1
        return rr

    def get_flat_chats(self):
        """Простой список
        :return json
        {-12346789: 'Test chat 2018-07-22 23',
         -23467890: 'Test2',
         123456789: '',
         132133223: ''}
        """
        json = self.get_chats_all()
        return get_result(json_data=json, key_key='chat_id', key_value='title')

    def get_chat(self, chat_id: int):
        """информация только об одном чате
        https://apiok.ru/dev/graph_api/methods/graph.user/graph.user.chat/get
        :return:json
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
        >>> tt=TamTam(token).get_chat(test_chat_id)
        >>> tt['title'].startswith('Test chat')
        True
        """
        params = {'chat_id': chat_id}
        zz = self._get(url='me/chat', params=params)
        if 'error_code' in zz:
            raise ChatNotFondException(zz['error_msg'])
        return zz

    # def get_chat_url(self, chat_id):
    #     """Получение прямой ссылки на чат по его ID
    #     https://apiok.ru/dev/graph_api/methods/graph.chat/graph.chat.url/get
    #     :return:json
    #     >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now, owner_user_id
    #     >>> tt=TamTam(token).get_chat(test_chat_id)
    #     >>> tt['url'].startswith('https://ok.ru/messages/g')
    #     True
    #     """
    #     return self.get(url=str(chat_id)+'/url')

    def rename_chat(self, chat_id: int, name: str):
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
        return self._post_messages(data=data)

    # Добавление пользователей в чат
    def add_members(self, chat_id: int, users_id: list):
        x = [{'user_id': x} for x in users_id]
        data = {
            "recipient": {"chat_id": chat_id},
            "chat_control": {
                "add_members": x
            },
        }
        return self._post_messages(data=data)

    # Удаление пользователя из чата
    def remove_member(self, chat_id: int, user_id: int):
        data = {
            "recipient": {"chat_id": chat_id},
            "chat_control": {
                "remove_member": {"user_id": user_id},  # Удалять можно только по одному пользователю
            },
        }
        # print(data)
        return self._post_messages(data=data)

    _me_id = None

    def get_dialog_title(self, chat_id: int, chat=None):
        """Находим по сообщениям чей это персоналльный чат"""
        msgs = self.get_messages(chat_id)
        if not self._me_id:
            self._me_id = self.get_me()['user_id']
        for m in msgs:
            if m['sender']['user_id'] != self._me_id:
                return m['sender']['name'], m['sender']['user_id']
        if chat:
            z = [x for x in chat['participants'] if x != self._me_id]
            return z[0], z[0]
        return chat_id, None

    def set_icon_chat(self, chat_id: int, icon_url: str):
        """send icon from chat
        :param chat_id:
        :param icon_url: https://and.su/bots/icon128.png
        :return:
        >>> from test_config import token, test_chat_id
        >>> r = TamTam(token).set_icon_chat(test_chat_id, 'https://i.mycdn.me/image?id=855366207587&t=35&plc=WEB&tkn=*i9oVtm3Onz3BLXUaEx0DBQTz6F0')
        >>> r['message_id'].startswith('mid')
        True
        """
        data = {
            "recipient": {"chat_id": chat_id},
            "chat_control": {
                "icon": {"url": icon_url},
            },
        }
        return self._post_messages(data=data)

    def get_messages(self, chat_id: int):
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
         {'message': {'attachments': [{'payload': {'url': 'https://i.mycdn.me/image?id=873015171829&t=3&plc=API&aid=1268677632&tkn=*hbp3XsOdKhvu9D5Tv7qE3HEqRbs'},
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
        >>> z = [x for x in r if (x['sender']['user_id'] == self_user_id) and (x['message'].get('text','').find("Hi") != -1)]
        >>> len(z)>0 #
        True
        """
        zz = self._get(url='me/messages', params={'chat_id': chat_id})
        return zz['messages']

    def get_messages_pers(self, user_id: int):
        """
        Список сообщений из личной беседы
        :param user_id:
        :return:
        >>> from test_config import token, test_chat_id, test_user_id, self_user_id, now
        >>> r = TamTam(token).get_messages_pers(test_user_id)
        >>> len(r)>0
        True
        >>> r = TamTam(token).get_messages_pers(124567)
        Traceback (most recent call last):
            ...
        UserDonTHaveChatException: 124567
        """
        rr = self.get_chats_all()
        zz = [x for x in rr if x['type'] == 'DIALOG' and user_id in x['participants'].keys()]
        if len(zz) == 0:
            raise UserDonTHaveChatException(user_id)
        chat_id = zz[0]['chat_id']  # по идее беседа одна
        return self.get_messages(chat_id=chat_id)

    @staticmethod
    def get_attachments(msg):
        if 'attachments' not in msg['message'] or not msg['message']['attachments']:
            return None, 'TEXT', None
        try:
            url = msg['message']['attachments'][0]['payload']['url']
        except TypeError:
            raise TypeError(str(msg))
        rr = requests.get(url)
        rr.raise_for_status()
        if 'Content-Type' in rr.headers:
            type_msg = rr.headers['Content-Type']
        else:
            type_msg = msg['message']['attachments']['payload']['type']
        if 'Content-Disposition' in rr.headers:
            name = rr.headers['Content-Disposition'].split(';')[1].split('"')[1]
        else:
            name = None
        return rr.content, type_msg, name

"""
Управление подписками на Webhooks
Механизм Webhooks позволяет боту получать сообщения по HTTP протоколу на указанный URL. Webhooks нужны только для приёма
сообщений. Отправлять сообщения через Bot API можно и без них.
Зарегистрировать новый Webhook
POST запрос на https://botapi.tamtam.chat/me/subscribe?access_token=TOKEN
{
"url":"https://example.com/mywebhook.php", /* http: или https: URL, куда будут доставляться сообщения боту,
которому выдан указанный TOKEN */
}
Отписаться от получения сообщений через Webhook
POST запрос на https://botapi.tamtam.chat/me/unsubscribe?access_token=TOKEN
{
"url":"https://example.com/mywebhook.php" /* http: или https: URL, указанный при регистрации Webhook */
}
Посмотреть все Webhook подписки
GET запрос на https://botapi.tamtam.chat/me/subscriptions?access_token=TOKEN
В ответ придёт список подписок в формате JSON.
{
"subscriptions":[
{"time":1481046252897,"url":"https://example.com/mywebhook.php"},
{"time":1481056345678,"url":"https://webhooks.example.com/secondhook"}
]
}
Получение сообщений
На зарегистрированные Webhook URL будут отправляться уведомления о входящих сообщениях методом POST в формате JSON.
{
"sender":{
"user_id":585110908962, /* ID пользователя, отправившего сообщение */
"name":"Иван Петров" /* Имя и фамилия отправителя */
},
"recipient":{"chat_id":970560697714}, /* ID чата или диалога */
"message":{
"mid":"mid.000000e1f9ecf572015825a32b7a3100", /* Уникальный идентификатор сообщения */
"text":"Привет", /* Текст сообщения */
"seq":96868774727790848 /* Возрастающий счётчик */
},
"timestamp":1478100200314 /* Время отправки сообщения в формате Java timestamp */
}
На каждый такой запрос скрипт должен в течение максимум 5 секунд вернуть HTTP ответ со статусом 200 OK. Если отправка
уведомления не удалась, или если скрипт вернул ответ со статусом, отличным от 200, через некоторое время будет предпринята
попытка повторной отправки уведомления. Если в течение 8 часов от скрипта не было получено положительного ответа, регистрация
указанного Webhook может быть автоматически отменена.
"""


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


class ChatNotFondException(Exception):
    pass


class UserDonTHaveChatException(Exception):
    pass


class MessageNotSendException(Exception):
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()
