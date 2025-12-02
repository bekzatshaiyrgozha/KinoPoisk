from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(APITestCase):
    """Test suite for authentication endpoints"""
    
    def setUp(self):
        """Set up test client and test data"""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        self.profile_url = '/api/auth/profile/'
        
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        
    def test_register_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create first user
        User.objects.create_user(
            username='testuser',
            email='first@example.com',
            password='TestPass123!'
        )
        
        # Try to register with same username
        response = self.client.post(self.register_url, self.valid_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_register_weak_password(self):
        """Test registration with weak password"""
        weak_data = self.valid_user_data.copy()
        weak_data['password'] = '123'
        weak_data['password_confirm'] = '123'
        
        response = self.client.post(self.register_url, weak_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        mismatch_data = self.valid_user_data.copy()
        mismatch_data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(self.register_url, mismatch_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            'username': 'testuser'
        }
        
        response = self.client.post(self.register_url, incomplete_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_success(self):
        """Test successful login"""
        # Create user first
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
    def test_login_wrong_password(self):
        """Test login with incorrect password"""
        # Create user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        login_data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # API returns 400 for invalid credentials
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, login_data)
        
        # API returns 400 for invalid credentials
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_logout_success(self):
        """Test successful logout"""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        
        refresh_token = login_response.data['refresh']
        
        # Logout
        logout_response = self.client.post(
            self.logout_url,
            {'refresh': refresh_token},
            HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertIn('message', logout_response.data)
        
    def test_profile_authenticated(self):
        """Test getting profile when authenticated"""
        # Create user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        
        # Login
        login_response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'TestPass123!'
        })
        
        # Get profile
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login_response.data["access"]}')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        
    def test_profile_unauthenticated(self):
        """Test getting profile without authentication"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
