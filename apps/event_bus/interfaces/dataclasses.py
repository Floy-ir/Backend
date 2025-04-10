from enum import Enum

from pydantic import BaseModel
import lib.data_classes as lib_data_classes


class EmissionType(str, Enum):
    EVENT_OR_COMMAND = 'event_or_command'
    EVENT = 'event'
    COMMAND = 'command'


class EventOrCommand(BaseModel):
    uid: str  # for duplicate emit prevention
    event_type: lib_data_classes.CustomStringValidator.max_length_string(128)  # usually upper case
    payload: BaseModel  # each event has its own payload. the emitter should document this.
    emission_type: EmissionType = EmissionType.EVENT_OR_COMMAND
