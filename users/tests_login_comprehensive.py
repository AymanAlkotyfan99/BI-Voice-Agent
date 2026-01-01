"""
Comprehensive tests for User Login (R3)

Tests cover:
- Successful login for all roles
- Token generation
- Workspace info by role
- Authentication errors
- Verification requirements
- Account status checks
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from workspace.models import Workspace, WorkspaceMember


class LoginSuccessTests(APITestCase):
    """Tests for successful login scenarios."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        
        # Create verified manager with workspace
        self.manager = User.objects.create_user(
            email='manager@example.com',
            password='Password123!',
            name='Manager User',
            role='manager',
            is_verified=True
        )
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            owner=self.manager
        )
        
        # Create verified analyst
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
    
    def test_manager_login_success(self):
        """R3.1: Manager can login with valid credentials."""
        data = {
            'email': 'manager@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_analyst_login_success(self):
        """R3.2: Analyst can login with valid credentials."""
        data = {
            'email': 'analyst@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_executive_login_success(self):
        """R3.3: Executive can login with valid credentials."""
        executive = User.objects.create_user(
            email='exec@example.com',
            password='Password123!',
            name='Executive User',
            role='executive',
            is_verified=True
        )
        
        data = {
            'email': 'exec@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_email_is_case_insensitive(self):
        """R3.4: Login email is case-insensitive."""
        data = {
            'email': 'MANAGER@EXAMPLE.COM',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'manager@example.com')


class LoginTokenTests(APITestCase):
    """Tests for JWT token generation."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
    
    def test_access_token_returned(self):
        """R3.5: Access token is returned on successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('access', response.data)
        self.assertIsNotNone(response.data['access'])
        self.assertTrue(len(response.data['access']) > 50)  # JWT tokens are long
    
    def test_refresh_token_returned(self):
        """R3.6: Refresh token is returned on successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('refresh', response.data)
        self.assertIsNotNone(response.data['refresh'])
        self.assertTrue(len(response.data['refresh']) > 50)
    
    def test_tokens_are_different(self):
        """R3.7: Access and refresh tokens are different."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertNotEqual(response.data['access'], response.data['refresh'])
    
    def test_tokens_unique_per_login(self):
        """R3.8: Each login generates unique tokens."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response1 = self.client.post(self.login_url, data, format='json')
        response2 = self.client.post(self.login_url, data, format='json')
        
        self.assertNotEqual(response1.data['access'], response2.data['access'])
        self.assertNotEqual(response1.data['refresh'], response2.data['refresh'])


class LoginUserInfoTests(APITestCase):
    """Tests for user information in login response."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
    
    def test_user_info_returned(self):
        """R3.9: User information is returned on login."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('user', response.data)
        self.assertIn('id', response.data['user'])
        self.assertIn('name', response.data['user'])
        self.assertIn('email', response.data['user'])
        self.assertIn('role', response.data['user'])
    
    def test_user_info_correct(self):
        """R3.10: Returned user info matches actual user."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['name'], 'Test User')
        self.assertEqual(response.data['user']['role'], 'analyst')
    
    def test_password_not_in_response(self):
        """R3.11: Password is not included in response."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        # Check password not in user dict
        self.assertNotIn('password', response.data['user'])
        
        # Check password not anywhere in response
        response_str = str(response.data)
        self.assertNotIn('Password123!', response_str)


class LoginWorkspaceInfoTests(APITestCase):
    """Tests for workspace information in login response."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        
        # Manager with workspace
        self.manager = User.objects.create_user(
            email='manager@example.com',
            password='Password123!',
            name='Manager User',
            role='manager',
            is_verified=True
        )
        self.workspace = Workspace.objects.create(
            name='Manager Workspace',
            owner=self.manager
        )
        
        # Analyst without workspace membership
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
        
        # Analyst with workspace membership
        self.analyst_with_workspace = User.objects.create_user(
            email='analyst2@example.com',
            password='Password123!',
            name='Analyst 2',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.analyst_with_workspace
        )
    
    def test_manager_gets_owned_workspace(self):
        """R3.12: Manager receives owned workspace info on login."""
        data = {
            'email': 'manager@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('workspace', response.data)
        self.assertIsNotNone(response.data['workspace'])
        self.assertEqual(response.data['workspace']['id'], self.workspace.id)
        self.assertEqual(response.data['workspace']['name'], 'Manager Workspace')
    
    def test_analyst_gets_joined_workspaces_list(self):
        """R3.13: Analyst receives list of joined workspaces."""
        data = {
            'email': 'analyst2@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('workspace', response.data)
        self.assertIsInstance(response.data['workspace'], list)
        self.assertEqual(len(response.data['workspace']), 1)
        self.assertEqual(response.data['workspace'][0]['id'], self.workspace.id)
    
    def test_analyst_without_workspace_gets_empty_list(self):
        """R3.14: Analyst not in any workspace gets empty list."""
        data = {
            'email': 'analyst@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('workspace', response.data)
        self.assertIsInstance(response.data['workspace'], list)
        self.assertEqual(len(response.data['workspace']), 0)


class LoginAuthenticationErrorTests(APITestCase):
    """Tests for authentication errors."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='CorrectPassword123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
    
    def test_wrong_password_rejected(self):
        """R3.15: Wrong password is rejected."""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_nonexistent_email_rejected(self):
        """R3.16: Non-existent email is rejected."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_email_rejected(self):
        """R3.17: Missing email is rejected."""
        data = {
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_password_rejected(self):
        """R3.18: Missing password is rejected."""
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_email_rejected(self):
        """R3.19: Empty email is rejected."""
        data = {
            'email': '',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_password_rejected(self):
        """R3.20: Empty password is rejected."""
        data = {
            'email': 'test@example.com',
            'password': ''
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginVerificationTests(APITestCase):
    """Tests for email verification requirements."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        
        # Unverified user
        self.unverified_user = User.objects.create_user(
            email='unverified@example.com',
            password='Password123!',
            name='Unverified User',
            role='analyst',
            is_verified=False  # Not verified
        )
    
    def test_unverified_user_cannot_login(self):
        """R3.21: Unverified user cannot login."""
        data = {
            'email': 'unverified@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('verify', response.data['message'].lower())
    
    def test_unverified_error_message(self):
        """R3.22: Clear error message for unverified accounts."""
        data = {
            'email': 'unverified@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('message', response.data)
        message = response.data['message'].lower()
        self.assertTrue('verify' in message or 'verification' in message)


class LoginAccountStatusTests(APITestCase):
    """Tests for account status (active/suspended)."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        
        # Suspended user
        self.suspended_user = User.objects.create_user(
            email='suspended@example.com',
            password='Password123!',
            name='Suspended User',
            role='analyst',
            is_verified=True,
            is_active=False  # Suspended
        )
        
        # Active user
        self.active_user = User.objects.create_user(
            email='active@example.com',
            password='Password123!',
            name='Active User',
            role='analyst',
            is_verified=True,
            is_active=True
        )
    
    def test_suspended_user_cannot_login(self):
        """R3.23: Suspended user cannot login."""
        data = {
            'email': 'suspended@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('suspend', response.data['message'].lower())
    
    def test_active_user_can_login(self):
        """R3.24: Active user can login successfully."""
        data = {
            'email': 'active@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_suspended_error_message(self):
        """R3.25: Clear error message for suspended accounts."""
        data = {
            'email': 'suspended@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('message', response.data)
        message = response.data['message'].lower()
        self.assertIn('suspend', message)


class LoginResponseFormatTests(APITestCase):
    """Tests for login response format."""
    
    def setUp(self):
        self.login_url = '/auth/login/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
    
    def test_success_flag_present(self):
        """R3.26: Success flag is present in response."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
    
    def test_message_present(self):
        """R3.27: Message is present in response."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertIn('message', response.data)
    
    def test_all_required_fields_present(self):
        """R3.28: All required fields present in response."""
        data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        required_fields = ['success', 'message', 'access', 'refresh', 'user', 'workspace']
        for field in required_fields:
            self.assertIn(field, response.data)

