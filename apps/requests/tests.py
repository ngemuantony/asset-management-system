from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import RequestType, AssetRequest, RequestApproval
from apps.users.models import UserProfile

User = get_user_model()

class RequestTests(APITestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='ADMIN'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.regular_user,
            role='USER'
        )
        
        # Create request type
        self.request_type = RequestType.objects.create(
            name='Test Request',
            requires_approval=True,
            approval_levels=1
        )
        
        # Create test request
        self.asset_request = AssetRequest.objects.create(
            request_type=self.request_type,
            requester=self.regular_user,
            title='Test Request',
            description='Test Description'
        )

    def test_create_request(self):
        """Test creating a new request"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'request_type': self.request_type.id,
            'title': 'New Request',
            'description': 'New Description',
            'priority': 'MEDIUM'
        }
        response = self.client.post(reverse('requests:request-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AssetRequest.objects.count(), 2)

    def test_approve_request(self):
        """Test request approval process"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(
            reverse('requests:request-approve', args=[self.asset_request.id]),
            {'comments': 'Approved'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.asset_request.refresh_from_db()
        self.assertEqual(self.asset_request.status, 'APPROVED')
