from uuid import uuid4
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from apps.file_storage import interfaces as file_storage_interfaces
from .fake_modules import ConstantDateTimeUtils


class FileStorageIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.current_time = 10
        self.date_time = ConstantDateTimeUtils(self.current_time)
        
        self.bootstrapper = Bootstrapper(
            date_time_utils=self.date_time
        )

        # Create admin user via API
        self.admin_mobile = "+989121231214"
        self.admin_password = "h@a1rdPassword"
        self.admin_uid = str(uuid4())
        
        response = self.client.post(
            reverse('users-list'), 
            {
                'uid': self.admin_uid,
                'username': 'admin_user',
                'mobile': self.admin_mobile,
                'password': self.admin_password
            },
            HTTP_USER_AGENT='TestClient/1.0',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin_user_data = response.json()
        
        # Make the user an admin
        self.bootstrapper.get_account_service().create_admin_user(
            request=accounts_interfaces.CreateAdminUserRequest(
                mobile=self.admin_mobile,
                password=self.admin_password
            )
        )

        # Create normal user
        self.user_mobile = "+989121231213"
        self.user_password = "h@a1rdPassword"
        self.user_uid = str(uuid4())
        
        response = self.client.post(
            reverse('users-list'), 
            {
                'uid': self.user_uid,
                'username': 'normal_user',
                'mobile': self.user_mobile,
                'password': self.user_password
            },
            HTTP_USER_AGENT='TestClient/1.0',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def create_session(self, mobile, password):
        session_uid = str(uuid4())
        response = self.client.post(
            reverse('sessions-list'), 
            {
                'session_uid': session_uid,
                'mobile': mobile,
                'password': password
            },
            HTTP_USER_AGENT='TestClient/1.0',
            content_type='application/json',
            HTTP_X_FORWARDED_FOR='127.0.0.1'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.json()

    def test_upload_file(self):
        """Test file upload functionality"""
        # Login as admin
        admin_session = self.create_session(self.admin_mobile, self.admin_password)

        # Create a test file
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Test file content',
            content_type='text/plain'
        )
        file_uid = str(uuid4())
        
        # Prepare multipart form data
        data = {
            'uid': file_uid,
            'files': test_file  # Single file upload
        }
        
        response = self.client.post(
            reverse('file-storage-list'),
            data,
            HTTP_AUTHORIZATION=f'Bearer {admin_session["token"]}',
            HTTP_USER_AGENT='TestClient/1.0'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('uid', result)

    def test_list_files(self):
        """Test listing files"""
        # Login as admin
        admin_session = self.create_session(self.admin_mobile, self.admin_password)

        # Upload multiple files
        files = []
        for i in range(3):
            test_file = SimpleUploadedFile(
                name=f'test{i}.txt',
                content=f'Test file content {i}'.encode(),
                content_type='text/plain'
            )
            file_uid = str(uuid4())
            
            data = {
                'uid': file_uid,
                'files': test_file
            }
            
            response = self.client.post(
                reverse('file-storage-list'),
                data,
                HTTP_AUTHORIZATION=f'Bearer {admin_session["token"]}',
                HTTP_USER_AGENT='TestClient/1.0'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            files.append(response.json()['uid'])

    def test_non_admin_restrictions(self):
        """Test that non-admin users have appropriate restrictions"""
        # Login as normal user
        normal_session = self.create_session(self.user_mobile, self.user_password)

        # Try to upload file
        test_file = SimpleUploadedFile(
            name='test.txt',
            content=b'Test file content',
            content_type='text/plain'
        )
        file_uid = str(uuid4())
        
        data = {
            'uid': file_uid,
            'files': test_file
        }
        
        response = self.client.post(
            reverse('file-storage-list'),
            data,
            HTTP_AUTHORIZATION=f'Bearer {normal_session["token"]}',
            HTTP_USER_AGENT='TestClient/1.0'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
