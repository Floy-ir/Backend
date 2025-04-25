import uuid
from django.test import TestCase
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from .. import interfaces
from .fake_modules import Payload, ListListener


class MatchStringTestCase(TestCase):
    def setUp(self) -> None:
        bootstrapper = Bootstrapper()
        self.service = bootstrapper.get_event_bus()
        accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                      user_uid="listener_on_general",
                                      session_uid=str(uuid.uuid4()),
                                      user=accounts_interfaces.User(
                                          uid='listener_on_general',
                                          is_identified=True,
                                          full_name="abed abdi",
                                          user_type=accounts_interfaces.UserType.ORDINARY)
                                      )
        self.listener_on_exact = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="listener_on_exact",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='listener_on_exact',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            match_string='emitter1/event1',
            listener=self.listener_on_exact,
        )
        self.listener_on_event = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="listener_on_event",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='listener_on_event',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            match_string='*/event1',
            listener=self.listener_on_event,
        )
        self.listener_on_emitter = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="listener_on_emitter",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='listener_on_emitter',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            match_string='emitter1/*',
            listener=self.listener_on_emitter,
        )
        self.listener_on_general = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="listener_on_general",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='listener_on_general',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            match_string='*/*',
            listener=self.listener_on_general,
        )

    def test_different_event(self):
        self.service.emit(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event2', payload=Payload(data='u0 data')),
        )
        self.assertEqual(len(self.listener_on_event.event_list), 0)
        self.assertEqual(len(self.listener_on_exact.event_list), 0)
        self.assertEqual(len(self.listener_on_emitter.event_list), 1)
        self.assertEqual(len(self.listener_on_general.event_list), 1)

    def test_different_emitter(self):
        self.service.emit(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="emitter2",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='emitter2',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event1', payload=Payload(data='u0 data')),
        )
        self.assertEqual(len(self.listener_on_event.event_list), 1)
        self.assertEqual(len(self.listener_on_exact.event_list), 0)
        self.assertEqual(len(self.listener_on_emitter.event_list), 0)
        self.assertEqual(len(self.listener_on_general.event_list), 1)

    def test_different_emitter_and_event(self):
        self.service.emit(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="emitter2",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='emitter2',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event2', payload=Payload(data='u0 data')),
        )
        self.assertEqual(len(self.listener_on_event.event_list), 0)
        self.assertEqual(len(self.listener_on_exact.event_list), 0)
        self.assertEqual(len(self.listener_on_emitter.event_list), 0)
        self.assertEqual(len(self.listener_on_general.event_list), 1)

    def test_exact(self):
        self.service.emit(
            caller=accounts_interfaces.Session(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 session_uid=str(uuid.uuid4()),
                                                 user=accounts_interfaces.User(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event1', payload=Payload(data='u0 data')),
        )
        self.assertEqual(len(self.listener_on_event.event_list), 1)
        self.assertEqual(len(self.listener_on_exact.event_list), 1)
        self.assertEqual(len(self.listener_on_emitter.event_list), 1)
        self.assertEqual(len(self.listener_on_general.event_list), 1)
