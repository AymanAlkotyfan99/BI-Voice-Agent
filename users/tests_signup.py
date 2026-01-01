"""
Comprehensive tests for User Sign Up (R1)

Tests cover:
- Successful signup for all roles
- Workspace auto-creation for managers
- Email uniqueness validation
- Password validation
- Role validation
- Email sending
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from users.models import User
from workspace.models import Workspace
from unittest.mock import patch


class SignUpSuccessTests(APITestCase):
    """Tests for successful sign up scenarios."""
    
    def setUp(self):
        self.signup_url = '/auth/signup/'
    
    def test_manager_signup_creates_user_and_workspace(self):
        """R1.1: Manager signup creates both user and workspace."""
        data = {
            'name': 'John Manager',
            'email': 'john@example.com',
            'password': 'StrongPass123!',
            'role': 'manager'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['workspace_created'])
        
        # Verify user created
        user = User.objects.get(email='john@example.com')
        self.assertEqual(user.name, 'John Manager')
        self.assertEqual(user.role, 'manager')
        self.assertFalse(user.is_verified)
        
        # Verify workspace created
        workspace = Workspace.objects.get(owner=user)
        self.assertEqual(workspace.name, "John Manager's Workspace")
    
    def test_analyst_signup_creates_user_only(self):
        """R1.2: Analyst signup creates user without workspace."""
        data = {
            'name': 'Jane Analyst',
            'email': 'jane@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['workspace_created'])
        
        # Verify user created
        user = User.objects.get(email='jane@example.com')
        self.assertEqual(user.role, 'analyst')
        
        # Verify no workspace created
        self.assertFalse(Workspace.objects.filter(owner=user).exists())
    
    def test_executive_signup_creates_user_only(self):
        """R1.3: Executive signup creates user without workspace."""
        data = {
            'name': 'Bob Executive',
            'email': 'bob@example.com',
            'password': 'StrongPass123!',
            'role': 'executive'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertFalse(response.data['workspace_created'])
        
        user = User.objects.get(email='bob@example.com')
        self.assertEqual(user.role, 'executive')
        self.assertFalse(Workspace.objects.filter(owner=user).exists())
    
    def test_password_is_hashed(self):
        """R1.4: Password is properly hashed."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'PlainPassword123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email='test@example.com')
        # Password should be hashed, not plain text
        self.assertNotEqual(user.password, 'PlainPassword123!')
        self.assertTrue(user.check_password('PlainPassword123!'))
    
    def test_email_is_normalized_to_lowercase(self):
        """R1.5: Email is normalized to lowercase."""
        data = {
            'name': 'Test User',
            'email': 'Test@EXAMPLE.COM',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_user_is_not_verified_initially(self):
        """R1.6: New users are not verified initially."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_active)  # Active by default, but not verified


class SignUpValidationTests(APITestCase):
    """Tests for sign up validation errors."""
    
    def setUp(self):
        self.signup_url = '/auth/signup/'
        # Create existing user
        User.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            name='Existing User',
            role='analyst'
        )
    
    def test_duplicate_email_rejected(self):
        """R1.7: Cannot sign up with existing email."""
        data = {
            'name': 'Another User',
            'email': 'existing@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('email', str(response.data).lower())
    
    def test_duplicate_email_case_insensitive(self):
        """R1.8: Email uniqueness is case-insensitive."""
        data = {
            'name': 'Another User',
            'email': 'EXISTING@EXAMPLE.COM',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_weak_password_rejected(self):
        """R1.9: Weak passwords are rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'weak',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_password_too_short_rejected(self):
        """R1.10: Passwords shorter than 8 characters rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'Short1!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_role_rejected(self):
        """R1.11: Invalid role values are rejected."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'admin'  # Invalid role
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_missing_name_rejected(self):
        """R1.12: Name is required."""
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_email_rejected(self):
        """R1.13: Email is required."""
        data = {
            'name': 'Test User',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_password_rejected(self):
        """R1.14: Password is required."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_role_rejected(self):
        """R1.15: Role is required."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email_format_rejected(self):
        """R1.16: Invalid email format is rejected."""
        data = {
            'name': 'Test User',
            'email': 'notanemail',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_empty_name_rejected(self):
        """R1.17: Empty name is rejected."""
        data = {
            'name': '',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SignUpEmailTests(APITestCase):
    """Tests for email sending during sign up."""
    
    def setUp(self):
        self.signup_url = '/auth/signup/'
    
    @patch('users.views.send_verification_email')
    def test_verification_email_sent_on_signup(self, mock_send_email):
        """R1.18: Verification email is sent after successful signup."""
        mock_send_email.return_value = True
        
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mock_send_email.called)
        
        # Verify email was sent with correct parameters
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]['user_email'], 'test@example.com')
        self.assertEqual(call_args[1]['user_name'], 'Test User')
        self.assertIsNotNone(call_args[1]['token'])
    
    @patch('users.views.send_verification_email')
    def test_signup_succeeds_even_if_email_fails(self, mock_send_email):
        """R1.19: User is created even if email sending fails."""
        mock_send_email.return_value = False  # Email fails
        
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        # Signup should still succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # User should be created
        user = User.objects.get(email='test@example.com')
        self.assertIsNotNone(user)


class SignUpWorkspaceTests(APITestCase):
    """Tests for workspace creation during manager signup."""
    
    def setUp(self):
        self.signup_url = '/auth/signup/'
    
    def test_manager_workspace_name_format(self):
        """R1.20: Manager's workspace name follows correct format."""
        data = {
            'name': 'Alice Cooper',
            'email': 'alice@example.com',
            'password': 'StrongPass123!',
            'role': 'manager'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        user = User.objects.get(email='alice@example.com')
        workspace = Workspace.objects.get(owner=user)
        
        self.assertEqual(workspace.name, "Alice Cooper's Workspace")
    
    def test_manager_owns_one_workspace_only(self):
        """R1.21: Manager has exactly one workspace after signup."""
        data = {
            'name': 'Test Manager',
            'email': 'manager@example.com',
            'password': 'StrongPass123!',
            'role': 'manager'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        user = User.objects.get(email='manager@example.com')
        workspaces = Workspace.objects.filter(owner=user)
        
        self.assertEqual(workspaces.count(), 1)
    
    def test_analyst_has_no_workspace_after_signup(self):
        """R1.22: Analyst has no owned workspace after signup."""
        data = {
            'name': 'Test Analyst',
            'email': 'analyst@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        user = User.objects.get(email='analyst@example.com')
        workspaces = Workspace.objects.filter(owner=user)
        
        self.assertEqual(workspaces.count(), 0)
    
    def test_executive_has_no_workspace_after_signup(self):
        """R1.23: Executive has no owned workspace after signup."""
        data = {
            'name': 'Test Executive',
            'email': 'exec@example.com',
            'password': 'StrongPass123!',
            'role': 'executive'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        user = User.objects.get(email='exec@example.com')
        workspaces = Workspace.objects.filter(owner=user)
        
        self.assertEqual(workspaces.count(), 0)


class SignUpResponseTests(APITestCase):
    """Tests for sign up response format."""
    
    def setUp(self):
        self.signup_url = '/auth/signup/'
    
    def test_response_contains_user_id(self):
        """R1.24: Response includes user ID."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertIn('data', response.data)
        self.assertIn('user_id', response.data['data'])
    
    def test_response_contains_success_message(self):
        """R1.25: Response includes success message."""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertIn('message', response.data)
        self.assertIn('verify', response.data['message'].lower())
    
    def test_response_workspace_created_flag_for_manager(self):
        """R1.26: Response indicates workspace was created for manager."""
        data = {
            'name': 'Test Manager',
            'email': 'manager@example.com',
            'password': 'StrongPass123!',
            'role': 'manager'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertTrue(response.data['workspace_created'])
        self.assertIn('workspace', response.data['data'])
    
    def test_response_workspace_created_flag_for_analyst(self):
        """R1.27: Response indicates no workspace created for analyst."""
        data = {
            'name': 'Test Analyst',
            'email': 'analyst@example.com',
            'password': 'StrongPass123!',
            'role': 'analyst'
        }
        
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertFalse(response.data['workspace_created'])

