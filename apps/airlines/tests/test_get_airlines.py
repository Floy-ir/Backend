from django.test import TestCase
from apps.airlines import interfaces
from apps.airlines.models import Airline
from .fake_modules import FakeCacheService, FakeFileStorageService
from runner.bootstrap import get_bootstrapper


class GetAirlinesTestCase(TestCase):
    def setUp(self) -> None:
        self.cache_service = FakeCacheService()
        self.file_storage_service = FakeFileStorageService()
        
        bootstrapper = get_bootstrapper(
            file_storage_service=self.file_storage_service,
            cache_service=self.cache_service
        )

        self.service = bootstrapper.get_airlines_service()

        self.airline1 = self.service.get_airline_by_name(name="airline1")
        self.airline2 = self.service.get_airline_by_name(name="airline2")
        self.airline3 = self.service.get_airline_by_name(name="airline3")

    def test_happy(self):
        request = interfaces.AirlineListReq(
            uid_list=[self.airline1.uid, self.airline2.uid]
        )
        result = self.service.get_airlines(request)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[self.airline1.uid].name, self.airline1.name)
        self.assertEqual(result[self.airline2.uid].name, self.airline2.name)
        self.assertIsNone(result[self.airline1.uid].image)
        self.assertIsNone(result[self.airline2.uid].image)


    def test_mixed_from_cache_and_db(self):
        request = interfaces.AirlineListReq(
            uid_list=[self.airline1.uid, self.airline2.uid]
        )

        self.service.get_airlines(request)


        request = interfaces.AirlineListReq(
            uid_list=[self.airline1.uid, self.airline3.uid]
        )

        result = self.service.get_airlines(request)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[self.airline1.uid].name, self.airline1.name)
        self.assertEqual(result[self.airline3.uid].name, self.airline3.name)
        self.assertIsNone(result[self.airline1.uid].image)
        self.assertIsNone(result[self.airline3.uid].image)
        
