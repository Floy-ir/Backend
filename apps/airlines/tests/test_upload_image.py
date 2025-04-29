from django.test import TestCase
from apps.airlines import interfaces
from .fake_modules import FakeCacheService, FakeFileStorageService
from libs import dataclasses as lib_dataclasses
from runner.bootstrap import get_bootstrapper

class UploadImageTestCase(TestCase):
    def setUp(self) -> None:
        bootstrapper = get_bootstrapper(
            file_storage_service=FakeFileStorageService(),
            cache_service=FakeCacheService()
        )

        self.service = bootstrapper.get_airlines_service()

        self.airline1 = self.service.get_airline_by_name(name="airline1")

    def test_happy(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.jpg"
        )

        request = interfaces.UploadImageReq(
            uid=self.airline1.uid,
            image=test_file
        )

        result = self.service.upload_image(request)

        self.assertEqual(result.uid, self.airline1.uid)
        self.assertEqual(result.image, f"https://example.com/{self.airline1.uid}/test.jpg")
