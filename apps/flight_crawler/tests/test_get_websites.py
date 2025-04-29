from django.test import TestCase
from apps.flight_crawler import interfaces
from .fake_modules import FakeCacheService, FakeFileStorageService
from runner.bootstrap import get_bootstrapper
from apps.flight_crawler.models import Website

class GetWebsitesTestCase(TestCase):
    def setUp(self) -> None:
        self.cache_service = FakeCacheService()
        self.file_storage_service = FakeFileStorageService()
        
        bootstrapper = get_bootstrapper(
            file_storage_service=self.file_storage_service,
            cache_service=self.cache_service
        )

        self.service = bootstrapper.get_flight_crawler_service()

        self.website1 = Website.objects.create(uid="website1", name="website1", name_fa="website1", logo=None, request_payload_structure={}, response_parsing_rules={}, is_active=True, base_url="https://example.com", redirect_url_template="https://example.com/redirect", one_adult_url_template=None, two_adult_url_template=None, redirect_url_config={})
        self.website2 = Website.objects.create(uid="website2", name="website2", name_fa="website2", logo=None, request_payload_structure={}, response_parsing_rules={}, is_active=True, base_url="https://example.com", redirect_url_template="https://example.com/redirect", one_adult_url_template=None, two_adult_url_template=None, redirect_url_config={})
        self.website3 = Website.objects.create(uid="website3", name="website3", name_fa="website3", logo=None, request_payload_structure={}, response_parsing_rules={}, is_active=True, base_url="https://example.com", redirect_url_template="https://example.com/redirect", one_adult_url_template=None, two_adult_url_template=None, redirect_url_config={})

    def test_happy(self):
        result = self.service.get_websites(interfaces.GetWebsitesRequest(uid_list=[self.website1.uid, self.website2.uid]))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[self.website1.uid].name, self.website1.name)
        self.assertEqual(result[self.website2.uid].name, self.website2.name)
        self.assertIsNone(result[self.website1.uid].logo)
        self.assertIsNone(result[self.website2.uid].logo)
        
    def test_mixed_from_cache_and_db(self):
        result = self.service.get_websites(interfaces.GetWebsitesRequest(uid_list=[self.website1.uid, self.website3.uid]))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[self.website1.uid].name, self.website1.name)
        self.assertEqual(result[self.website3.uid].name, self.website3.name)
        self.assertIsNone(result[self.website1.uid].logo)
        self.assertIsNone(result[self.website3.uid].logo)
