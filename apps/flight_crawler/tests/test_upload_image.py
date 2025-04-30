from django.test import TestCase
from apps.airlines import interfaces
from .fake_modules import FakeCacheService, FakeFileStorageService
from libs import dataclasses as lib_dataclasses
from runner.bootstrap import get_bootstrapper
from apps.flight_crawler.models import Website
from apps.flight_crawler import interfaces
class UploadImageTestCase(TestCase):
    def setUp(self) -> None:
        bootstrapper = get_bootstrapper(
            file_storage_service=FakeFileStorageService(),
            cache_service=FakeCacheService()
        )

        self.service = bootstrapper.get_flight_crawler_service()

        self.website1 = Website.objects.create(uid="website1", name="website1", name_fa="website1", logo=None, request_payload_structure={}, response_parsing_rules={}, is_active=True, base_url="https://example.com", redirect_url_template="https://example.com/redirect", one_adult_url_template=None, two_adult_url_template=None, redirect_url_config={})

    def test_happy(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.jpg"
        )

        request = interfaces.UploadImageRequest(
            uid=self.website1.uid,
            logo=test_file
        )

        self.service.upload_image(request)

        result = self.service.get_websites(interfaces.GetWebsitesRequest(uid_list=[self.website1.uid]))
        self.assertEqual(result[self.website1.uid].logo, f"https://example.com/{self.website1.uid}/test.jpg")
