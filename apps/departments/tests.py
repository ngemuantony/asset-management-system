from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Department
from apps.users.models import UserProfile

User = get_user_model()

class DepartmentTests(APITestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='ADMIN',
            employee_id='ADM001'
        )

        # Create manager user
        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpass123'
        )

        # Create department
        self.department = Department.objects.create(
            name='Test Department',
            code='TEST01'
        )

        self.manager_profile = UserProfile.objects.create(
            user=self.manager_user,
            role='MANAGER',
            department=self.department,
            employee_id='MGR001'
        )

        # API endpoints
        self.list_url = reverse('departments:department-list')
        self.detail_url = reverse('departments:department-detail', args=[self.department.id])

    def test_create_department(self):
        """Test creating a new department"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'name': 'New Department',
            'code': 'NEW01',
            'description': 'New department description'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 2)

    def test_list_departments(self):
        """Test listing departments"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_department(self):
        """Test updating a department"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'name': 'Updated Department'}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Department')

    def test_delete_department(self):
        """Test deleting a department"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Department.objects.count(), 0)

    def test_department_stats(self):
        """Test getting department statistics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('departments:department-stats', args=[self.department.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('total_assets', response.data)

    def test_unauthorized_access(self):
        """Test unauthorized access to departments"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_department_hierarchy_operations(self):
        """Test department parent-child relationships"""
        pass

    def test_department_user_reassignment(self):
        """Test user reassignment when department is deactivated"""
        pass
