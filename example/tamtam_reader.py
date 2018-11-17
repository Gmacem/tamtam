from .tamtam import TamTam
from .models import *
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import utc
from django.utils import timezone
# from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
import logging
import time
from requests.exceptions import ProxyError

logger = logging.getLogger(__name__)


class TamtamReader:

    channels = None
    i = 0

    def __init__(self):
        self.get_channels()

    def get_channels(self):
        if not self.channels:
            self.channels = settings.TAMTAM_TOKEN
        # print(self.channels)
        return self.channels

    def get_and_sync_channel(self, channel_code):
        channel, created = Channels.objects.get_or_create(type='TamTam', deleted_at__isnull=True, code=channel_code)
        if created:
            channel.save()
        return channel

    def update(self, force=False, msg=True, new_chat_read=True, *, read=True):
        # return
        self.i = 0
        for channel_code in self.channels:
            # print('channel:'+channel_code)
            channel = self.get_and_sync_channel(channel_code)
            if read:
                ttrc = TamtamReaderFromChannels(channel, self.channels[channel_code])
                self.i += ttrc.update(force, msg, new_chat_read)
        return self.i


class TamtamReaderFromChannels:

    channel = None
    i = 0
    tamtam = None
    me = None

    def __init__(self, channel: Channels, token: str):
        self.channel = channel
        self.tamtam = TamTam(token)
        self.me = self.tamtam.get_me()['user_id']

    force = False
    msg = True
    new_chat_read = True
    _data = None

    def read_tamtam(self):
        self.i = 0
        self._data = self.tamtam.get_chats_all()

    def update(self, force=False, msg=True, new_chat_read=False):
        self.force = force
        self.msg = msg
        self.new_chat_read = new_chat_read
        self.read_tamtam()
        # проверяем есть ли чат, если нет, то создаём, если есть обновляем
        for chat in self._data:
            self._update_chat(chat)
        # зачитываем юзеров
        if self.new_chat_read:
            for chat in self._data:
                if chat['obj'].readable or chat['obj'].ldap_control:
                    self.sync_user_in_chat(chat['obj'], chat)
        # читаем сообщения
        if self.msg:
            for chat in self._data:
                self.read_msgs(chat['obj'], chat)
        return self.i

    @staticmethod
    def timestamp2datetime(tm):
        return datetime.datetime.utcfromtimestamp(int(tm) / 1e3).replace(tzinfo=utc)

    def _update_chat(self, chat):
        chat['last_event_timeDT'] = self.timestamp2datetime(chat['last_event_time'])
        try:
            chat_obj = Chats.objects.get(chat_id=chat['chat_id'],
                                         channel=self.channel)
        except Chats.DoesNotExist:
            chat_obj = Chats(chat_id=chat['chat_id'],
                             channel=self.channel,
                             title=chat['title'] if 'title' in chat else chat['chat_id'],
                             type=chat['type'],
                             status=chat['status'],
                             code=chat['chat_id'])
            if chat_obj.type == 'DIALOG':
                chat_obj.title, chat_obj.parent_user = self.tamtam.get_dialog_title(chat_id=chat_obj.chat_id, chat=chat)
                chat_obj.readable = True
            chat_obj.save()
            self.i += 1000
        else:
            if chat_obj.type == 'DIALOG' and not chat_obj.parent_user:
                chat_obj.title, chat_obj.parent_user = self.tamtam.get_dialog_title(chat_id=chat_obj.chat_id, chat=chat)
                chat_obj.save()
        chat['obj'] = chat_obj

    def write_msg(self, msg, chat_obj):
        # это всё может измениться, если сообщение редактировали
        mid = msg['message']['mid']
        m = Messages.objects.filter(chat=chat_obj, message_id=mid).first()
        if not m:
            d = self.timestamp2datetime(msg['timestamp'])
            text = msg['message']['text'] if 'message' in msg and 'text' in msg['message'] else ''  # может не быть
            sender = msg['sender']['user_id']
            str_msg = str(msg)
            try:
                m = Messages(chat=chat_obj,
                             d=d,
                             message_id=mid,
                             sender=sender,
                             text=text,
                             msg=str_msg)
                if sender == self.me:
                    m.out_user = settings.ME_USER_ID
                body, type_msg, file = TamTam.get_attachments(msg)
                if body:
                    m.attachments = body
                    m.type = type_msg
                    if file:
                        m.text = file
                m.save()
                self.i += 1
            except EmptySignalsException:
                print('skip')
                m = None
        return m

    def read_msgs(self, chat_obj, chat):
        # читаем сообщения в чатах
        # и пишем в базу, то что удовлетворяет условию (придумать)
        # далее через сигналы обрабатываем те что нужно
        # ещё вариант - через Error - для всего, для чего не нашлось сигнала
        if settings.DEBUG_BOT != chat_obj.debug:
            return  # дата чтения не сдвигается - ведь чтения нет
        if chat_obj.validate < -20:
            return
        if not chat_obj.readable:
            return
        if self.force or not chat_obj.last_update or chat['last_event_timeDT'] > chat_obj.last_update:
            msgs = self.tamtam.get_messages(chat_obj.chat_id)
            try:
                for msg in reversed(msgs):
                    if not msg:
                        # В принципе такого быть не должно, но сейчас есть
                        print(str(chat_obj.chat_id) + ': msg is none')
                        continue
                    self.write_msg(msg, chat_obj)
                chat_obj.last_update = chat['last_event_timeDT']
                chat_obj.save()  # только если всё прочитали успешно, двигаем дату
            except EmptySignalsChatException:
                print('EmptySignalsChatException')
                pass  # чат сказал, что здесь его обрабатывать не нужно
        # print(len(msgs))

    def _update_user(self, user, force=False, update=False):
        if not user.pers_chat:
            user.pers_chat = Chats.objects.filter(channel=user.channel,
                                                  parent_user=user.origin,
                                                  deleted_at__isnull=True
                                                  ).first()
            update = True
        if not user.ldap_user and user.pers_chat and user.pers_chat.validate > 0:
            user.ldap_user = get_user_model().objects.filter(email__iexact=user.pers_chat.code).first()
            # logger.debug()
            print(user.ldap_user, user.pers_chat)
            update = True
        if force:
            if user.me != (user.origin == self.me):
                user.me = user.origin == self.me
                update = True
            if user.origin == self.me:
                if not user.ldap_user or user.ldap_user_id != settings.ME_USER_ID:
                    user.ldap_user_id = settings.ME_USER_ID
                    update = True

        if update:
            user.save()

    def _update_chat_user(self, chat_user, participant, force=False):
        update = False
        tm = self.timestamp2datetime(participant)
        if chat_user.user.me and chat_user.is_validate:
            chat_user.is_validate = True
            update = True
        if not chat_user.last_update or chat_user.last_update < tm:
            chat_user.last_update = tm
            update = True
        if force:
            pass
            update = True
        if update:
            chat_user.save()

    def _create_chat_user(self):
        pass

    def sync_user_in_chat(self, chat_obj, chat):
        participants = chat['participants']  # Список пользователей чата
        chat_users_all = ChatUsers.objects.filter(chat=chat_obj, deleted_at__isnull=True).prefetch_related('user')  # тоже в проме
        for chat_user in chat_users_all:
            # Если пользователь есть
            if chat_user.user.origin in participants:
                self._update_chat_user(chat_user, participants[chat_user.user.origin])
                participants.pop(chat_user.user.origin)
            # Если пользователя нет, то "удаляем" связь
            elif chat_user.is_blocked:
                pass
            else:
                chat_user.deleted_at = datetime.datetime.now()
        # разбираемся с новыми
        for user_origin in participants:
            new_chat_user = ChatUsers.objects.filter(chat=chat_obj, user__origin=user_origin).first()
            self.i += 1000000
            if new_chat_user:
                new_chat_user.deleted_at = None
                self._update_user(new_chat_user.user, force=True)
            else:
                user = Users.objects.filter(channel=chat_obj.channel, origin=user_origin).first()
                if not user:
                    user = Users(channel=chat_obj.channel, origin=user_origin)
                    self._update_user(user, force=True, update=True)
                new_chat_user = ChatUsers(user=user, chat=chat_obj)
                new_chat_user.save()
            self._update_chat_user(new_chat_user, participants[user_origin])


class TamtamReaderException(Exception):
    pass


def run_tamtam_reader(request):
    force = 'force' in request.GET
    msg = 'skipmsg' not in request.GET
    one = 'one' in request.GET
    x = None
    try:
        tr = TamtamReader()
        tt = timezone.now()
        sec = 10
        # x = tr.update(force=force, msg=msg, new_chat_read=True)
        dt = timezone.now() - tt
        while dt.total_seconds() < 57:
            x = tr.update(force=force, msg=msg, new_chat_read=False)
            if one:
                break
            t = timezone.now()
            if not x or x == '0':
                d = timezone.now() - t
                if d.total_seconds() < sec:
                    time.sleep(sec - d.total_seconds())
            dt = timezone.now() - tt
    except ProxyError as e:
        logger.warning(e)
    except Exception as e:
        logger.exception(str(x))
        return HttpResponseBadRequest(str(x)+str(e))
    return HttpResponse(str(x))


def run_tamtam_users(request):
    x = None
    try:
        tr = TamtamReader()
        x = tr.update(force=False, msg=False, new_chat_read=True)
    except Exception as e:
        logger.exception(str(x))
        return HttpResponseBadRequest(str(x)+str(e))
    return HttpResponse(str(x))


def task_tamtam_reader(force=False, msg=True):
    return str(TamtamReader().update(force, msg))

# if __name__ == "__main__":
#     import timeit
#     start_time = timeit.default_timer()
#     import test_config
#     test_config.setup()
#     t = TamtamReader()
#     x = t.update_chat_list()
#     import pprint
#     pp = pprint.PrettyPrinter(indent=4)
#     # pp.pprint(t.get_runs())
#     # cl = t.get_chats()
#     pp.pprint(x)
#     print(timeit.default_timer() - start_time)
