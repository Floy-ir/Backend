from enum import Enum

from pydantic import BaseModel
import libs.dataclasses as lib_data_classes


class EmissionType(str, Enum):
    EVENT_OR_COMMAND = 'event_or_command'
    EVENT = 'event'
    COMMAND = 'command'


class EventOrCommand(BaseModel):
    uid: str  # for duplicate emit prevention
    event_type: str
    payload: BaseModel  # each event has its own payload. the emitter should document this.
    emission_type: EmissionType = EmissionType.EVENT_OR_COMMAND
