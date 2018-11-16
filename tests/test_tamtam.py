from django.test import TestCase
from tamtam import TamTam
from django.conf import settings
from requests.exceptions import HTTPError
import responses
import pprint


class TestTamTam(TestCase):

    tt = None
    test_chat_id = None
    pp = None

    def setUp(self):
        self.tt = TamTam(settings.TAMTAM_TOKEN['test'])
        self.test_chat_id = settings.TAMTAM_TEST_CHAT
        self.pp = pprint.PrettyPrinter(4)

    def test_send(self):
        s = self.tt.send(text='dds', chat_id=self.test_chat_id)
        self.assertTrue(s['message_id'].startswith('mid'), s)

    @responses.activate
    def test_negative(self):
        s = self.tt
        fuck_url = s._url + 'me/chats?count=100&access_token=' + s._token
        # self.assertEqual(fuck_url, '')
        responses.add(responses.GET,
                      fuck_url,
                      json={'error': 'not found'},
                      status=404)
        with self.assertRaises(HTTPError):
            s.get_chats()

    json_get_chat_list = {'chats': [
        {'chat_id': 32892385902485942,
         'icon': {
             'url': 'https://i.mycdn.me/image?id=871613929205&t=20&plc=API&aid=1268677632&tkn=*30kENi7C51SaV1XitrUugaHAV-M'},
         'last_event_time': 1531740045562,
         'owner_id': 'user:562187610613',
         'participants': {'user:160422175977': 1531739991174,
                          'user:442860378754': 1531739731585,
                          'user:592044717335': 1531740051469},
         'status': 'ACTIVE',
         'title': 'Эпсилон',
         'type': 'CHAT'},
        {'chat_id': 243802384320,
         'last_event_time': 1531740030819,
         'owner_id': 575522687955,
         'participants': {'user:573046260078': 1531740086703,
                          'user:575522687955': 1531740030819},
         'status': 'ACTIVE',
         'type': 'DIALOG'},
        {'chat_id': 'chat:C3f8699eee026',
         'icon': {
             'url': 'https://i.mycdn.me/image?id=871613209845&t=20&plc=API&aid=1268677632&tkn=*GoFRnxnME-kUrdjlhIsbR78PTJo'},
         'last_event_time': 1531739816117,
         'owner_id': 562187610613,
         'participants': {'user:147778830196': 1531733263505,
                          'user:160422175977': 1531739998678,
                          'user:31909466606': 1531482772043,
                          'user:592044717335': 1531739979585,
                          'user:714927777': 0},
         'status': 'ACTIVE',
         'title': 'Ню',
         'type': 'CHAT'},
        {'chat_id': -45456456456,
         'last_event_time': 1531739751730,
         'owner_id': 575522687955,
         'participants': {'user:571854766708': 1531740073391,
                          'user:575522687955': 1531739751730},
         'status': 'ACTIVE',
         'type': 'DIALOG'}]}

    def test_get_me(self):
        me = self.tt.get_me()['user_id']
        self.assertEqual(me, settings.TAMTAM_TEST_USER)

    def test_get_chat_list(self):
        tt = self.tt.get_chats_all()
        self.assertTrue(len(tt) >= 0, tt)
        self.assertTrue(type(tt[0]['chat_id']) is int, tt[0]['chat_id'])
        z = [x for x in tt if(x['chat_id'] == self.test_chat_id)]
        self.assertEqual(len(z), 1, z)

    def test_send_file(self):
        file = open('TamTam.png', 'rb').read()
        r = self.tt.send_file(self.test_chat_id, 'TamTam.png', file, "PHOTO")
        self.pp.pprint(r)
        self.assertEqual(True, False)
