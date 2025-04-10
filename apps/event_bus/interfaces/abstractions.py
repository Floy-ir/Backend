import abc
from apps.accounts import interfaces as accounts_interfaces
from .dataclasses import EventOrCommand


class AbstractEventListener(abc.ABC):
    def on_event_or_command(self, emitter_claim: accounts_interfaces.UserClaim, event_or_command: EventOrCommand):
        """the listener will receive events with this method

        Args:
            emitter_claim (UserClaim): the original emitter
            event_or_command (EventOrCommand): the event
        """
        raise NotImplementedError


class AbstractEventBus(abc.ABC):

    def emit(self, caller: accounts_interfaces.UserClaim, event_or_command: EventOrCommand):
        """an internal app uses this method to emit a event or to trigger a delayed command

        Args:
            caller (UserClaim): the emitter internal app.
            event_or_command (EventOrCommand): the event to be emitted

        """
        raise NotImplementedError

    def subscribe(self, caller: accounts_interfaces.UserClaim, match_string: str, listener: AbstractEventListener) -> object:
        """an internal app uses this method to subscribe for an event or for multiple events

        Args:
            caller (UserClaim): the subscriber internal app
            match_string (str): with for of 'emitter/event_type' use * for generalization. for example '*/*' will subscribe for all events and commands.
            listener (AbstractEventListener): the listener stub

        """
        pass
