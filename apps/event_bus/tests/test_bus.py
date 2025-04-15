import uuid
from django.test import TestCase
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from .. import interfaces
from .fake_modules import Payload, ListListener, BadListener


class BusTestCase(TestCase):
    def setUp(self) -> None:
        bootstrapper = Bootstrapper()
        self.service = bootstrapper.get_event_bus()
        self.listener1 = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="listener1",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='listener1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            match_string='*/*',
            listener=self.listener1,
        )
        self.listener2 = BadListener()
        self.service.subscribe(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="listener2",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='listener2',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            match_string='*/*',
            listener=self.listener2,
        )
        self.listener3 = ListListener()
        self.service.subscribe(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="listener3",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='listener3',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            match_string='*/*',
            listener=self.listener3,
        )

    def test_last_listener_receives_event_even_if_previous_listener_was_bad(self):
        self.service.emit(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event1', payload=Payload(data='u0 data')),
        )
        self.assertEqual(len(self.listener1.event_list), 1)
        self.assertEqual(len(self.listener3.event_list), 1)

    def test_idempotency(self):
        self.service.emit(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u0', event_type='event1', payload=Payload(data='u0 data')),
        )
        self.service.emit(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u1', event_type='event1', payload=Payload(data='u1 data')),
        )
        self.service.emit(
            caller=accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                 user_uid="emitter1",
                                                 user=accounts_interfaces.UserPublicInfo(
                                                     uid='emitter1',
                                                     is_identified=True,
                                                     full_name="abed abdi",
                                                     user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                 ),
            event_or_command=interfaces.EventOrCommand(uid='u1', event_type='event1', payload=Payload(data='u1 data')),
        )
        self.assertEqual(len(self.listener1.event_list), 2)
        self.assertEqual(len(self.listener3.event_list), 2)

    def test_event_or_command_equality(self):
        emitter = accounts_interfaces.UserClaim(uid=str(uuid.uuid4()),
                                                user_uid="emitter1",
                                                user=accounts_interfaces.UserPublicInfo(
                                                    uid='emitter1',
                                                    is_identified=True,
                                                    full_name="abed abdi",
                                                    user_type=accounts_interfaces.UserType.IRANIAN_ORDINARY)
                                                )
        event_or_command = interfaces.EventOrCommand(uid='u0', event_type='event1', payload=Payload(data='u0 data'))
        self.service.emit(
            caller=emitter,
            event_or_command=event_or_command,
        )
        received_event = self.listener1.event_list[0]
        self.assertEqual(received_event, {'emitter': emitter, 'event_or_command': event_or_command})
