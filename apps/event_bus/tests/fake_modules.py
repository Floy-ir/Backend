from typing import Any
from pydantic import BaseModel
from apps.accounts import interfaces as accounts_interfaces
from .. import interfaces


class Payload(BaseModel):
    data: Any


class ListListener(interfaces.AbstractEventListener):
    def __init__(self):
        self.event_list = []

    def on_event_or_command(self, emitter_claim: accounts_interfaces.Session,
                            event_or_command: interfaces.EventOrCommand):
        self.event_list.append({'emitter': emitter_claim, 'event_or_command': event_or_command})


class BadListener(interfaces.AbstractEventListener):

    def on_event_or_command(self, emitter_claim: accounts_interfaces.Session,
                            event_or_command: interfaces.EventOrCommand):
        raise Exception("i'm bad")
