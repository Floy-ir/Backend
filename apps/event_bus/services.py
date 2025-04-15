import logging

from utils.date_time import interfaces as date_time_interfaces

from apps.accounts.interfaces import Session
from . import interfaces

logger = logging.getLogger(__name__)


class EventBus(interfaces.AbstractEventBus):
    def __init__(
            self,
            claim: Session,
            date_time_utils: date_time_interfaces.AbstractDateTimeUtils,
    ):
        self.claim = claim
        self.date_time_utils = date_time_utils
        self.subscribers = []

    def emit(self, caller: Session, event_or_command: interfaces.EventOrCommand):
        if event_or_command.emission_type == interfaces.EmissionType.EVENT:
            raise NotImplementedError
        logger.info(f'\n\ncaller: {caller}, event_or_command: {event_or_command}')
        try:
            for subscriber in self.subscribers:
                logger.debug(f"subscriber: {subscriber}")
                self._push_if_matched(subscriber, caller, event_or_command)
        except Exception as e:
            logger.warning(f'an exception occurred during emission: {e}')
            if event_or_command.emission_type == interfaces.EmissionType.COMMAND:
                raise e

    def subscribe(self, caller: Session, match_string: str, listener: interfaces.AbstractEventListener):
        logger.info(f'caller: {caller}, match_string: {match_string}, listener: {listener}')
        # TODO: validate match_string format
        self.subscribers.append({
            'match_string': match_string,
            'listener': listener,
        })

    def _push_if_matched(self, subscriber, emitter_claim: Session, event_or_command: interfaces.EventOrCommand):
        is_matched = self._is_matched(subscriber['match_string'], emitter_claim.user_uid, event_or_command.event_type)
        logger.info(f'matched: {is_matched}')
        if is_matched:
            try:
                subscriber['listener'].on_event_or_command(emitter_claim, event_or_command)
            except Exception as e:
                logger.warning(f'an exception occurred during push: {e}')
                if event_or_command.emission_type == interfaces.EmissionType.COMMAND:
                    raise e

    def _is_matched(self, match_string: str, emitter_uid: str, event_type: str) -> bool:
        sp = match_string.split('/')
        if sp[0] != '*' and sp[0] != emitter_uid:
            return False
        if sp[1] != '*' and sp[1] != event_type:
            return False
        return True
