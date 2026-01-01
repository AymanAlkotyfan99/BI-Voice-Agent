"""
Comprehensive tests for User Profile (R5 & R6)

Tests cover:
- View profile
- Update profile (name and email)
- Email change triggers re-verification
- Validation and permissions
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch


class ProfileViewTests(APITestCase):
    """Tests for viewing user profile."""
    
    def setUp(self):
        self.profile_url = '/user/profile/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_view_own_profile(self):
        """R5.1: User can view their own profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_profile_contains_all_fields(self):
        """R5.2: Profile contains all required fields."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.profile_url)
        
        required_fields = ['id', 'name', 'email', 'role', 'is_verified', 'is_active', 'created_at']
        for field in required_fields:
            self.assertIn(field, response.data['user'])
    
    def test_profile_data_correct(self):
        """R5.3: Profile data matches user data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        self.assertEqual(response.data['user']['name'], 'Test User')
        self.assertEqual(response.data['user']['role'], 'analyst')
        self.assertTrue(response.data['user']['is_verified'])
    
    def test_unauthenticated_cannot_view_profile(self):
        """R5.4: Unauthenticated user cannot view profile."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_password_not_in_profile(self):
        """R5.5: Password is not included in profile data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertNotIn('password', response.data['user'])


class ProfileUpdateNameTests(APITestCase):
    """Tests for updating profile name."""
    
    def setUp(self):
        self.profile_url = '/user/profile/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Old Name',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_update_name_success(self):
        """R5.6: User can update their name."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'name': 'New Name'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['name'], 'New Name')
        
        # Verify in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'New Name')
    
    def test_update_name_only_no_email_change(self):
        """R5.7: Updating name only doesn't affect verification."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'name': 'New Name'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # User should still be verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertEqual(self.user.email, 'test@example.com')  # Email unchanged
    
    def test_empty_name_rejected(self):
        """R5.8: Empty name is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'name': ''
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # Should be rejected or name should remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Old Name')


class ProfileUpdateEmailTests(APITestCase):
    """Tests for updating profile email."""
    
    def setUp(self):
        self.profile_url = '/user/profile/'
        self.user = User.objects.create_user(
            email='old@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    @patch('users.views.send_verification_email')
    def test_update_email_success(self, mock_send_email):
        """R5.9: User can update their email."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'new@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['email'], 'new@example.com')
        
        # Verify in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
    
    @patch('users.views.send_verification_email')
    def test_email_change_resets_verification(self, mock_send_email):
        """R5.10: Changing email resets is_verified to False."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'new@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # User should now be unverified
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)
    
    @patch('users.views.send_verification_email')
    def test_email_change_sends_verification_email(self, mock_send_email):
        """R5.11: Changing email sends new verification email."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'new@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertTrue(mock_send_email.called)
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]['user_email'], 'new@example.com')
    
    @patch('users.views.send_verification_email')
    def test_email_change_message_includes_verification_notice(self, mock_send_email):
        """R5.12: Response message mentions verification requirement."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'new@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertIn('verify', response.data['message'].lower())
    
    def test_duplicate_email_rejected(self):
        """R5.13: Cannot update to an existing email."""
        # Create another user
        User.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            name='Existing User',
            role='analyst',
            is_verified=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'existing@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_duplicate_email_case_insensitive(self):
        """R5.14: Email uniqueness check is case-insensitive."""
        User.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            name='Existing User',
            role='analyst',
            is_verified=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'EXISTING@EXAMPLE.COM'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email_format_rejected(self):
        """R5.15: Invalid email format is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'not_an_email'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('users.views.send_verification_email')
    def test_same_email_no_reverification_needed(self, mock_send_email):
        """R5.16: Updating to same email doesn't reset verification."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'email': 'old@example.com'  # Same as current
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # User should still be verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        
        # Verification email should not be sent
        self.assertFalse(mock_send_email.called)


class ProfileUpdateBothFieldsTests(APITestCase):
    """Tests for updating both name and email."""
    
    def setUp(self):
        self.profile_url = '/user/profile/'
        self.user = User.objects.create_user(
            email='old@example.com',
            password='Password123!',
            name='Old Name',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    @patch('users.views.send_verification_email')
    def test_update_both_name_and_email(self, mock_send_email):
        """R5.17: Can update both name and email simultaneously."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'name': 'New Name',
            'email': 'new@example.com'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify both updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'New Name')
        self.assertEqual(self.user.email, 'new@example.com')
        self.assertFalse(self.user.is_verified)


class ProfileUpdateProtectedFieldsTests(APITestCase):
    """Tests for attempting to update protected fields."""
    
    def setUp(self):
        self.profile_url = '/user/profile/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
    
    def test_cannot_update_role(self):
        """R5.18: Cannot update role via profile endpoint."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'role': 'manager'  # Try to change role
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # Role should remain unchanged
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'analyst')
    
    def test_cannot_update_is_verified_directly(self):
        """R5.19: Cannot directly update is_verified."""
        self.user.is_verified = False
        self.user.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'is_verified': True
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # is_verified should remain False
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)
    
    def test_cannot_update_is_active_directly(self):
        """R5.20: Cannot directly update is_active."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'is_active': False
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        # is_active should remain True
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class ProfileDeactivateTests(APITestCase):
    """Tests for account deactivation (R6)."""
    
    def setUp(self):
        self.deactivate_url = '/user/deactivate/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=True
        )
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)
    
    def test_deactivate_account_success(self):
        """R6.1: User can deactivate their account."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.delete(self.deactivate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify account is deactivated
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_deactivate_sets_is_active_false(self):
        """R6.2: Deactivation sets is_active to False."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': self.refresh_token
        }
        
        self.client.delete(self.deactivate_url, data, format='json')
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
    
    def test_deactivate_preserves_user_data(self):
        """R6.3: Deactivation preserves user data (soft delete)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': self.refresh_token
        }
        
        self.client.delete(self.deactivate_url, data, format='json')
        
        # User should still exist in database
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.name, 'Test User')
    
    def test_deactivated_user_cannot_login(self):
        """R6.4: Deactivated user cannot login."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': self.refresh_token
        }
        
        self.client.delete(self.deactivate_url, data, format='json')
        
        # Try to login
        login_data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post('/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_deactivate_requires_authentication(self):
        """R6.5: Deactivation requires authentication."""
        data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.delete(self.deactivate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_deactivate_requires_refresh_token(self):
        """R6.6: Deactivation requires refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {}  # No refresh token
        
        response = self.client.delete(self.deactivate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

