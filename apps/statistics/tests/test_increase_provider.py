from uuid import uuid4
from django.test import TestCase
from runner.bootstrap import Bootstrapper
from .. import interfaces as interfaces

class IncreaseProviderTests(TestCase):
    def setUp(self) -> None:
        self.bootstrapper = Bootstrapper()
        self.service = self.bootstrapper.get_statistic_service()

    def test_happy1(self):
        for i in range(0,10):
            self.service.increase_redirect(
                request=interfaces.IncreaseRedirectNumberRequest(
                    provider="provider"
                ))
            statistics = self.service.get_providers()
        
        self.assertEqual(statistics.count,1)
        self.assertEqual(statistics.results[0].provider,'provider')
        self.assertEqual(statistics.results[0].redirect_number,10)

    def test_happy2(self):
        for j in range(0,10):
            self.service.increase_redirect(
                request=interfaces.IncreaseRedirectNumberRequest(
                    provider=f"{j}"
                ))
            statistics = self.service.get_providers()

            self.assertEqual(statistics.count,j+1)
            self.assertEqual(statistics.results[j].provider,f'{j}')
            self.assertEqual(statistics.results[j].redirect_number,1)