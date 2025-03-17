import uuid
from django.test import TestCase
from libs import dataclasses as lib_dataclasses
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from .. import interfaces
from .fake_modules import FakeS3ClientFactory, ConstantDateTimeUtils


class UploadFilesTestCase(TestCase):
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
        self.user_session = accounts_interfaces.Session(
            session_uid=str(uuid.uuid4()),
            user_uid=str(uuid.uuid4()),
            user=accounts_interfaces.User(
                uid=str(uuid.uuid4()),
                is_identified=True,
                full_name="user session",
                user_type=accounts_interfaces.UserType.ORDINARY,
            ),
        )

        self.current_time = 10 
        self.date_time = ConstantDateTimeUtils(self.current_time)
        self.s3_client_factory = FakeS3ClientFactory()
        
        self.service = Bootstrapper(
            date_time_utils=self.date_time,
            s3_client_factory=self.s3_client_factory,
        ).get_file_storage_service()

    def test_happy_upload_files(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.txt"
        )
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=[test_file]
        )
        
        result = self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )
        
        self.assertEqual(result.uid, upload_request.uid)
        self.assertEqual(result.uploaded_at, self.current_time)
        self.assertEqual(result.uploaded_by, self.app_session.user_uid)
        self.assertEqual(len(result.files), 1)
        
        file_metadata = result.files[0]
        self.assertEqual(file_metadata.file_name, "test.txt")
        self.assertEqual(file_metadata.file_size_in_bytes, len(b"test content"))

    def test_upload_with_non_admin_user(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.txt"
        )
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=[test_file]
        )
        
        with self.assertRaises(interfaces.OnlyAdminException):
            self.service.upload_files(
                caller=self.user_session,
                upload_request=upload_request
            )

    def test_upload_with_used_uid(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content 1",
            name="test.txt"
        )
        
        uid = str(uuid.uuid4())
        upload_request = interfaces.UploadRequest(
            uid=uid,
            files=[test_file]
        )
        
        # First upload should succeed
        self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )

        test_file = lib_dataclasses.File(
            buffer=b"test content 2",
            name="test.txt"
        )

        self.service.upload_files(
            caller=self.app_session,
            upload_request=upload_request
        )

    def test_unavailable_s3(self):
        test_file = lib_dataclasses.File(
            buffer=b"test content",
            name="test.txt"
        )
        
        upload_request = interfaces.UploadRequest(
            uid=str(uuid.uuid4()),
            files=[test_file]
        )
        
        # Create a new service with unavailable S3
        service = Bootstrapper(
            date_time=self.date_time,
            s3_client_factory=FakeS3ClientFactory(available=False),
        ).get_file_storage_service()
        
        with self.assertRaises(interfaces.InternalFileStorageNotAvailable):
            service.upload_files(
                caller=self.app_session,
                upload_request=upload_request
            )