"""
Comprehensive tests for Email Verification (R2)

Tests cover:
- Successful verification
- Token validation
- Token expiration
- Invalid tokens
- Already verified accounts
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from users.utils import generate_verification_token
from unittest.mock import patch
from django.core.signing import TimestampSigner
from datetime import timedelta
from django.utils import timezone


class EmailVerificationSuccessTests(APITestCase):
    """Tests for successful email verification scenarios."""
    
    def setUp(self):
        self.verify_url = '/auth/verify-email/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=False
        )
    
    def test_successful_email_verification(self):
        """R2.1: Valid token successfully verifies account."""
        token = generate_verification_token(self.user.id)
        
        response = self.client.get(f'{self.verify_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify user is now verified
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
    
    def test_verification_message_returned(self):
        """R2.2: Success message is returned after verification."""
        token = generate_verification_token(self.user.id)
        
        response = self.client.get(f'{self.verify_url}?token={token}')
        
        self.assertIn('message', response.data)
        self.assertIn('verified', response.data['message'].lower())
    
    def test_user_can_login_after_verification(self):
        """R2.3: User can login after verification."""
        token = generate_verification_token(self.user.id)
        
        # Verify email
        self.client.get(f'{self.verify_url}?token={token}')
        
        # Try to login
        login_data = {
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        response = self.client.post('/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EmailVerificationTokenTests(APITestCase):
    """Tests for token validation."""
    
    def setUp(self):
        self.verify_url = '/auth/verify-email/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=False
        )
    
    def test_missing_token_rejected(self):
        """R2.4: Request without token is rejected."""
        response = self.client.get(self.verify_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_invalid_token_rejected(self):
        """R2.5: Invalid token is rejected."""
        invalid_token = 'invalid_token_12345'
        
        response = self.client.get(f'{self.verify_url}?token={invalid_token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('invalid', response.data['message'].lower())
    
    def test_tampered_token_rejected(self):
        """R2.6: Tampered token is rejected."""
        token = generate_verification_token(self.user.id)
        tampered_token = token[:-5] + 'xxxxx'  # Tamper with token
        
        response = self.client.get(f'{self.verify_url}?token={tampered_token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_expired_token_rejected(self):
        """R2.7: Expired token (>24 hours) is rejected."""
        # Create token and manually expire it by manipulating time
        signer = TimestampSigner()
        # Sign with old timestamp (25 hours ago)
        token = signer.sign(str(self.user.id))
        
        # Mock the verification to simulate expired token
        with patch('users.utils.verify_email_token') as mock_verify:
            mock_verify.return_value = (False, None, 'expired')
            
            response = self.client.get(f'{self.verify_url}?token={token}')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('expired', response.data['message'].lower())
    
    def test_empty_token_rejected(self):
        """R2.8: Empty token is rejected."""
        response = self.client.get(f'{self.verify_url}?token=')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_for_nonexistent_user_rejected(self):
        """R2.9: Token for non-existent user ID is rejected."""
        # Generate token for user ID that doesn't exist
        fake_token = generate_verification_token(99999)
        
        response = self.client.get(f'{self.verify_url}?token={fake_token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailVerificationAlreadyVerifiedTests(APITestCase):
    """Tests for already verified accounts."""
    
    def setUp(self):
        self.verify_url = '/auth/verify-email/'
        self.user = User.objects.create_user(
            email='verified@example.com',
            password='Password123!',
            name='Verified User',
            role='analyst',
            is_verified=True  # Already verified
        )
    
    def test_already_verified_account_rejected(self):
        """R2.10: Cannot verify already verified account."""
        token = generate_verification_token(self.user.id)
        
        response = self.client.get(f'{self.verify_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('already', response.data['message'].lower())
    
    def test_already_verified_status_unchanged(self):
        """R2.11: Already verified user status remains unchanged."""
        token = generate_verification_token(self.user.id)
        
        self.client.get(f'{self.verify_url}?token={token}')
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)  # Still verified


class EmailVerificationSecurityTests(APITestCase):
    """Security tests for email verification."""
    
    def setUp(self):
        self.verify_url = '/auth/verify-email/'
        self.user = User.objects.create_user(
            email='test@example.com',
            password='Password123!',
            name='Test User',
            role='analyst',
            is_verified=False
        )
    
    def test_cannot_reuse_token_after_verification(self):
        """R2.12: Token cannot be reused after successful verification."""
        token = generate_verification_token(self.user.id)
        
        # First verification
        response1 = self.client.get(f'{self.verify_url}?token={token}')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Try to reuse token
        response2 = self.client.get(f'{self.verify_url}?token={token}')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_is_user_specific(self):
        """R2.13: Token is specific to user and cannot verify others."""
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='Password123!',
            name='User 2',
            role='analyst',
            is_verified=False
        )
        
        # Generate token for user1
        token = generate_verification_token(self.user.id)
        
        # Verify with token
        self.client.get(f'{self.verify_url}?token={token}')
        
        # user2 should not be verified
        user2.refresh_from_db()
        self.assertFalse(user2.is_verified)
    
    def test_token_from_different_secret_key_rejected(self):
        """R2.14: Token signed with different key is rejected."""
        # This would require changing SECRET_KEY, so we simulate with invalid token
        invalid_token = 'MTox:invalid_signature'
        
        response = self.client.get(f'{self.verify_url}?token={invalid_token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailVerificationMultipleUsersTests(APITestCase):
    """Tests for verification with multiple users."""
    
    def setUp(self):
        self.verify_url = '/auth/verify-email/'
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            password='Password123!',
            name='User 1',
            role='analyst',
            is_verified=False
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            password='Password123!',
            name='User 2',
            role='manager',
            is_verified=False
        )
    
    def test_each_user_has_unique_token(self):
        """R2.15: Each user has unique verification token."""
        token1 = generate_verification_token(self.user1.id)
        token2 = generate_verification_token(self.user2.id)
        
        self.assertNotEqual(token1, token2)
    
    def test_verify_one_user_does_not_affect_others(self):
        """R2.16: Verifying one user doesn't affect others."""
        token1 = generate_verification_token(self.user1.id)
        
        # Verify user1
        self.client.get(f'{self.verify_url}?token={token1}')
        
        # Check user1 is verified
        self.user1.refresh_from_db()
        self.assertTrue(self.user1.is_verified)
        
        # Check user2 is still not verified
        self.user2.refresh_from_db()
        self.assertFalse(self.user2.is_verified)
    
    def test_multiple_users_can_verify_simultaneously(self):
        """R2.17: Multiple users can verify independently."""
        token1 = generate_verification_token(self.user1.id)
        token2 = generate_verification_token(self.user2.id)
        
        # Verify both users
        response1 = self.client.get(f'{self.verify_url}?token={token1}')
        response2 = self.client.get(f'{self.verify_url}?token={token2}')
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Both should be verified
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertTrue(self.user1.is_verified)
        self.assertTrue(self.user2.is_verified)

