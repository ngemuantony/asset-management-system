from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.conf import settings
from apps.authentication.models import CustomUser

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        """Set up test data and URLs"""
        self.client = APIClient()
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')
        self.logout_url = reverse('authentication:logout')
        self.password_reset_url = reverse('authentication:password_reset')
        self.password_change_url = reverse('authentication:password_change')
        self.profile_url = reverse('authentication:profile')
        
        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password2': 'TestPass123!',
            'firstName': 'Test',
            'lastName': 'User'
        }

        # Create a test user
        self.test_user = CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPass123!',
            firstName='Existing',
            lastName='User'
        )

    def get_tokens_for_user(self, user):
        """Helper method to get tokens for a user"""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    # ======================== Registration Tests ========================
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)  # Including the test user
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)

    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Second registration with same email
        duplicate_data = self.user_data.copy()
        duplicate_data['username'] = 'different_username'
        response = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', str(response.data))

    def test_user_registration_invalid_password(self):
        """Test registration with invalid password"""
        invalid_data = self.user_data.copy()
        invalid_data['password'] = '123'
        invalid_data['password2'] = '123'
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ======================== Login Tests ========================
    def test_user_login_with_username_success(self):
        """Test successful login with username"""
        login_data = {
            'usernameOrEmail': 'existinguser',
            'password': 'ExistingPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_user_login_with_email_success(self):
        """Test successful login with email"""
        login_data = {
            'usernameOrEmail': 'existing@example.com',
            'password': 'ExistingPass123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'usernameOrEmail': 'existinguser',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ======================== Logout Tests ========================
    def test_user_logout_success(self):
        """Test successful logout"""
        # First login to get tokens
        tokens = self.get_tokens_for_user(self.test_user)
        
        # Then logout
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.post(self.logout_url, {'refresh': tokens['refresh']})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_logout_without_token(self):
        """Test logout without token"""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ======================== Password Reset Tests ========================
    def test_password_reset_request_success(self):
        """Test successful password reset request"""
        response = self.client.post(self.password_reset_url, {
            'email': 'existing@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)  # Verify email was sent

    def test_password_reset_invalid_email(self):
        """Test password reset with invalid email"""
        response = self.client.post(self.password_reset_url, {
            'email': 'nonexistent@example.com'
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(mail.outbox), 0)  # No email should be sent

    # ======================== Password Change Tests ========================
    def test_password_change_success(self):
        """Test successful password change"""
        tokens = self.get_tokens_for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.post(self.password_change_url, {
            'oldPassword': 'ExistingPass123!',
            'newPassword': 'NewPass123!',
            'newPasswordConfirm': 'NewPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        tokens = self.get_tokens_for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        
        response = self.client.post(self.password_change_url, {
            'oldPassword': 'WrongOldPass123!',
            'newPassword': 'NewPass123!',
            'newPasswordConfirm': 'NewPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ======================== Profile Tests ========================
    def test_profile_access_success(self):
        """Test successful profile access"""
        tokens = self.get_tokens_for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

    def test_profile_access_unauthorized(self):
        """Test profile access without authentication"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_concurrent_login_attempts(self):
        """Test handling of concurrent login attempts"""
        pass

    def test_token_refresh_after_password_change(self):
        """Test token invalidation after password change"""
        pass

    def tearDown(self):
        """Clean up after tests"""
        CustomUser.objects.all().delete()
