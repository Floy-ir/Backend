import uuid
from django.test import TestCase
from libs import dataclasses as lib_dataclasses
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from .. import interfaces
from ..models import UploadMetadata, FileMetadata
from .fake_modules import FakeS3ClientFactory, ConstantDateTimeUtils


class GetImagesLinkTestCase(TestCase):
    def setUp(self) -> None:
        self.app_session = accounts_interfaces.Session(
            session_uid=str(uuid.uuid4()),
            user_uid=str(uuid.uuid4()),
            user=accounts_interfaces.User(
                uid=str(uuid.uuid4()),
                is_identified=True,
                full_name="app session",
                user_type=accounts_interfaces.UserType.ADMIN,
            ),
        )

        self.current_time = 10
        self.date_time = ConstantDateTimeUtils(self.current_time)
        self.s3_client_factory = FakeS3ClientFactory()
        
        self.service = Bootstrapper(
            date_time_utils=self.date_time,
            s3_client_factory=self.s3_client_factory,
        ).get_file_storage_service()

    def test_get_images_link_with_existing_upload(self):
        # First create an upload with files
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.jpg"
        )
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=[test_file]
        )
        
        upload_result = self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )
        
        # Now get the image links
        images_link = self.service.get_images_link(upload_result.uid)
        
        self.assertEqual(images_link.count, 1)
        self.assertEqual(len(images_link.results), 1)
        self.assertTrue(images_link.results[0].startswith('https://fake-s3.example.com/'))
        self.assertTrue(f'/{upload_result.uid}/' in images_link.results[0])
        self.assertTrue(images_link.results[0].endswith('/test.jpg'))

    def test_get_images_link_with_multiple_files(self):
        # Create an upload with multiple files
        test_files = [
            lib_dataclasses.File(buffer=b"test1", name="test1.jpg"),
            lib_dataclasses.File(buffer=b"test2", name="test2.jpg"),
            lib_dataclasses.File(buffer=b"test3", name="test3.jpg"),
        ]
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=test_files
        )
        
        upload_result = self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )
        
        # Get the image links
        images_link = self.service.get_images_link(upload_result.uid)
        
        self.assertEqual(images_link.count, 3)
        self.assertEqual(len(images_link.results), 3)
        
        # Verify each link
        for i, link in enumerate(images_link.results, 1):
            self.assertTrue(link.startswith('https://fake-s3.example.com/'))
            self.assertTrue(f'/{upload_result.uid}/' in link)
            self.assertTrue(link.endswith(f'/test{i}.jpg'))

    def test_get_images_link_no_upload_exists(self):
        """Test getting image links for a non-existent upload UID"""
        # Generate a random UID that definitely won't exist
        non_existent_uid = str(uuid.uuid4())
        
        # Get image links for non-existent upload
        images_link = self.service.get_images_link(non_existent_uid)
        
        # Verify empty result is returned
        self.assertEqual(images_link.count, 0)
        self.assertEqual(images_link.results, [])
        self.assertTrue(isinstance(images_link, interfaces.ImagesLink))

    def test_get_images_link_with_unavailable_s3(self):
        # First create an upload with files
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.jpg"
        )
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=[test_file]
        )
        
        upload_result = self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )
        
        # Create a new service with unavailable S3
        service = Bootstrapper(
            date_time_utils=self.date_time,
            s3_client_factory=FakeS3ClientFactory(available=False),
        ).get_file_storage_service()
        
        # Try to get image links with unavailable S3
        with self.assertRaises(interfaces.InternalFileStorageNotAvailable):
            service.get_images_link(upload_result.uid)