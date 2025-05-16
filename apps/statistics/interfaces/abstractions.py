from .dataclasses import *
from abc import ABC, abstractmethod
from typing import List

class AbstractStatisticsService(ABC):
    

    @abstractmethod
    def increase_redirect(self, request:IncreaseRedirectNumberRequest) :

        raise NotImplementedError