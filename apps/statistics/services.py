from uuid import uuid4
from .models import Statistic
from . import interfaces

class StatisticsService(interfaces.AbstractStatisticsService):
    
    def increase_redirect(self, request: interfaces.IncreaseRedirectNumberRequest):
        statistic,is_create = Statistic.objects.get_or_create(provider=request.provider,defaults={
            "uid" : str(uuid4()),
            "redirect_number": 1
        })
        if not is_create:
            statistic.redirect_number += 1
            statistic.save()
        return
    
    def get_providers(self) -> interfaces.GetProvidersInfo:
        statistics = Statistic.objects.all()
        return interfaces.GetProvidersInfo(
            count=statistics.count(),
            results=[self._convert_statistic_to_dataclass(statistic=statistic) for statistic in statistics]
        )
    

    def _convert_statistic_to_dataclass(self, statistic: Statistic) -> interfaces.Statistic:
        return interfaces.Statistic(
            uid=statistic.uid,
            provider=statistic.provider,
            redirect_number=statistic.redirect_number
        )