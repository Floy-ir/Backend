from uuid import uuid4
from . import interfaces
from utils.date_time import interfaces as date_time_interfaces
from .models import User, Session
import logging

logger = logging.getLogger(__name__)


class AccountService(interfaces.AbstractAccountService):
    def __init__(self,
                 claim: interfaces.Session,
                 session_life_time_in_second: int = 24 * 60 * 60
                 ):
        self.claim = claim
        self.session_life_time_in_second = session_life_time_in_second
