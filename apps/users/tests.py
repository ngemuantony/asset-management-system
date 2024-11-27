from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import UserProfile
from apps.departments.models import Department
from core.constants import ROLE_ADMIN, ROLE_MANAGER, ROLE_USER

User = get_user_model()

class UserProfileTests(APITestCase):
    def setUp(self):
        # Create test department
        self.department = Department.objects.create(
            name='Test Department',
            code='TEST01'
        )

        # Create test users with different roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            firstName='Admin',
            lastName='User'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role=ROLE_ADMIN,
            employee_id='ADM001'
        )

        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpass123',
            firstName='Manager',
            lastName='User'
        )
        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user,
            role=ROLE_MANAGER,
            department=self.department,
            employee_id='MGR001'
        )

        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123',
            firstName='Regular',
            lastName='User'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            role=ROLE_USER,
            department=self.department,
            employee_id='USR001'
        )

        # Set up API client
        self.client = APIClient()
        
        # API endpoints
        self.user_list_url = reverse('users:user-list')
        self.profile_list_url = reverse('users:profile-list')

    def test_create_user_profile(self):
        """Test creating a new user profile"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'firstName': 'New',
            'lastName': 'User',
            'role': ROLE_USER,
            'department': self.department.id
        }
        response = self.client.post(self.user_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(UserProfile.objects.count(), 4)

    def test_list_users(self):
        """Test listing users with different permissions"""
        # Test admin access
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

        # Test manager access
        self.client.force_authenticate(user=self.manager_user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Managers should only see users in their department
        self.assertEqual(len(response.data), 2)

    def test_update_profile(self):
        """Test updating user profile"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('users:profile-detail', args=[self.user_profile.id])
        data = {
            'department': self.department.id,
            'phone_number': '1234567890'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone_number'], '1234567890')

    def test_profile_permissions(self):
        """Test profile access permissions"""
        # Regular user trying to access other profiles
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('users:profile-detail', args=[self.admin_profile.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_operations(self):
        """Test bulk user operations performance"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test bulk create
        bulk_data = [
            {
                'username': f'bulkuser{i}',
                'email': f'bulk{i}@example.com',
                'password': 'bulkpass123',
                'firstName': f'Bulk{i}',
                'lastName': 'User',
                'role': ROLE_USER,
                'department': self.department.id
            } for i in range(100)
        ]
        
        response = self.client.post(f"{self.user_list_url}bulk/", bulk_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_search_and_filter(self):
        """Test search and filter functionality"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test search by name
        response = self.client.get(f"{self.user_list_url}?search=Admin")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Test filter by department
        response = self.client.get(
            f"{self.user_list_url}?department={self.department.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_profile_deactivation(self):
        """Test profile deactivation"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('users:profile-deactivate', args=[self.user_profile.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserProfile.objects.get(id=self.user_profile.id).is_active)

    def tearDown(self):
        """Clean up after tests"""
        User.objects.all().delete()
        Department.objects.all().delete()
