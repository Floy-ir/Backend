from uuid import uuid4
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from runner.bootstrap import Bootstrapper
from apps.accounts import interfaces as accounts_interfaces
from apps.statistics.models import Statistic
from .fake_modules import ConstantDateTimeUtils


class StatisticsIntegrationTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.current_time = 10
        self.date_time = ConstantDateTimeUtils(self.current_time)
        
        self.bootstrapper = Bootstrapper(
            date_time_utils=self.date_time
        )

        # Create admin user
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

    def test_increase_redirect(self):
        """Test increasing redirect count for a provider"""
        # Create a session for making authenticated requests
        session = self.create_session(self.admin_mobile, self.admin_password)

        # Test increasing redirect count
        provider = "test_provider"
        data = {
            'provider': provider
        }
        
        response = self.client.post(
            reverse('statistics-list'),
            data,
            HTTP_AUTHORIZATION=f'Bearer {session["token"]}',
            HTTP_USER_AGENT='TestClient/1.0',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistic was created
        statistic = Statistic.objects.get(provider=provider)
        self.assertEqual(statistic.redirect_number, 1)

        # Increase again
        response = self.client.post(
            reverse('statistics-list'),
            data,
            HTTP_AUTHORIZATION=f'Bearer {session["token"]}',
            HTTP_USER_AGENT='TestClient/1.0',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify count increased
        statistic.refresh_from_db()
        self.assertEqual(statistic.redirect_number, 2)

    def test_get_providers(self):
        """Test getting provider statistics"""
        # Create a session for making authenticated requests
        session = self.create_session(self.admin_mobile, self.admin_password)

        # Create some statistics
        providers = ["provider1", "provider2", "provider3"]
        for provider in providers:
            Statistic.objects.create(
                uid=str(uuid4()),
                provider=provider,
                redirect_number=0
            )

        # Test listing providers
        response = self.client.get(
            reverse('statistics-list'),
            HTTP_AUTHORIZATION=f'Bearer {session["token"]}',
            HTTP_USER_AGENT='TestClient/1.0'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result = response.json()
        self.assertEqual(result['count'], len(providers))
        self.assertEqual(len(result['results']), len(providers))
        
        # Verify each provider is in results
        provider_names = [stat['provider'] for stat in result['results']]
        for provider in providers:
            self.assertIn(provider, provider_names)
