"""
Comprehensive tests for Workspace Invitations (R9, R13)

Tests cover:
- Send invitations (R9)
- Accept invitations (R13)
- Token validation
- Email sending
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from workspace.models import Workspace, WorkspaceMember, Invitation
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch
from users.utils import generate_invitation_token


class InvitationSendTests(APITestCase):
    """Tests for sending workspace invitations (R9)."""
    
    def setUp(self):
        self.invite_url = '/workspace/invite/'
        
        # Create manager with workspace
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
        
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        # Create analyst (not workspace owner)
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
    
    @patch('workspace.views.send_invitation_email')
    def test_manager_can_send_invitation(self, mock_send_email):
        """R9.1: Manager can send workspace invitation."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'newuser@example.com',
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # Verify invitation created
        invitation = Invitation.objects.get(invited_email='newuser@example.com')
        self.assertEqual(invitation.workspace, self.workspace)
        self.assertEqual(invitation.role, 'analyst')
        self.assertEqual(invitation.status, 'pending')
    
    @patch('workspace.views.send_invitation_email')
    def test_invitation_email_sent(self, mock_send_email):
        """R9.2: Invitation email is sent."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'newuser@example.com',
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertTrue(mock_send_email.called)
        call_args = mock_send_email.call_args
        self.assertEqual(call_args[1]['invited_email'], 'newuser@example.com')
    
    @patch('workspace.views.send_invitation_email')
    def test_can_invite_executive(self, mock_send_email):
        """R9.3: Manager can invite executive role."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'executive@example.com',
            'role': 'executive'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        invitation = Invitation.objects.get(invited_email='executive@example.com')
        self.assertEqual(invitation.role, 'executive')
    
    @patch('workspace.views.send_invitation_email')
    def test_cannot_invite_manager_role(self, mock_send_email):
        """R9.4: Cannot invite someone as manager."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'newuser@example.com',
            'role': 'manager'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_analyst_cannot_send_invitation(self, mock_send_email):
        """R9.5: Analyst cannot send invitations."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        data = {
            'email': 'newuser@example.com',
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_cannot_invite_existing_member(self, mock_send_email):
        """R9.6: Cannot invite someone who is already a member."""
        # Add analyst to workspace
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst)
        
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'analyst@example.com',
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_cannot_send_duplicate_pending_invitation(self, mock_send_email):
        """R9.7: Cannot send duplicate pending invitation."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'newuser@example.com',
            'role': 'analyst'
        }
        
        # Send first invitation
        response1 = self.client.post(self.invite_url, data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try to send second invitation
        response2 = self.client.post(self.invite_url, data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_missing_email_rejected(self, mock_send_email):
        """R9.8: Missing email is rejected."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_missing_role_rejected(self, mock_send_email):
        """R9.9: Missing role is rejected."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'newuser@example.com'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('workspace.views.send_invitation_email')
    def test_invalid_email_format_rejected(self, mock_send_email):
        """R9.10: Invalid email format is rejected."""
        mock_send_email.return_value = True
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'email': 'not_an_email',
            'role': 'analyst'
        }
        
        response = self.client.post(self.invite_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InvitationAcceptExistingUserTests(APITestCase):
    """Tests for accepting invitations by existing users (R13)."""
    
    def setUp(self):
        self.accept_url = '/workspace/accept-invite/'
        
        # Create manager with workspace
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
        
        # Create existing user who will be invited
        self.existing_user = User.objects.create_user(
            email='existing@example.com',
            password='Password123!',
            name='Existing User',
            role='analyst',
            is_verified=True
        )
    
    def test_existing_user_can_accept_invitation(self):
        """R13.1: Existing user can accept invitation."""
        # Create invitation
        token = generate_invitation_token(
            'existing@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='existing@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify membership created
        membership = WorkspaceMember.objects.filter(
            workspace=self.workspace,
            user=self.existing_user
        ).exists()
        self.assertTrue(membership)
    
    def test_invitation_marked_accepted(self):
        """R13.2: Invitation is marked as accepted."""
        token = generate_invitation_token(
            'existing@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='existing@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        self.client.get(f'{self.accept_url}?token={token}')
        
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, 'accepted')
    
    def test_user_role_updated_to_invited_role(self):
        """R13.3: User role is updated to invited role."""
        token = generate_invitation_token(
            'existing@example.com',
            self.workspace.id,
            'executive'
        )
        invitation = Invitation.objects.create(
            invited_email='existing@example.com',
            workspace=self.workspace,
            role='executive',
            token=token,
            status='pending'
        )
        
        self.client.get(f'{self.accept_url}?token={token}')
        
        self.existing_user.refresh_from_db()
        self.assertEqual(self.existing_user.role, 'executive')
    
    def test_cannot_accept_already_accepted_invitation(self):
        """R13.4: Cannot accept already accepted invitation."""
        token = generate_invitation_token(
            'existing@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='existing@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        # First acceptance
        response1 = self.client.get(f'{self.accept_url}?token={token}')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Try to accept again
        response2 = self.client.get(f'{self.accept_url}?token={token}')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_accept_if_already_member(self):
        """R13.5: Cannot accept invitation if already a member."""
        # Add user to workspace first
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.existing_user
        )
        
        token = generate_invitation_token(
            'existing@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='existing@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class InvitationAcceptNewUserTests(APITestCase):
    """Tests for accepting invitations by new users (R13)."""
    
    def setUp(self):
        self.accept_url = '/workspace/accept-invite/'
        
        # Create manager with workspace
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
    
    def test_new_user_instructed_to_sign_up(self):
        """R13.6: New user is instructed to sign up first."""
        token = generate_invitation_token(
            'newuser@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='newuser@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['success'])
        self.assertIn('sign up', response.data['message'].lower())
    
    def test_new_user_response_includes_email(self):
        """R13.7: Response includes invited email for new user."""
        token = generate_invitation_token(
            'newuser@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='newuser@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertIn('invited_email', response.data)
        self.assertEqual(response.data['invited_email'], 'newuser@example.com')
    
    def test_new_user_response_includes_workspace_info(self):
        """R13.8: Response includes workspace info for new user."""
        token = generate_invitation_token(
            'newuser@example.com',
            self.workspace.id,
            'analyst'
        )
        invitation = Invitation.objects.create(
            invited_email='newuser@example.com',
            workspace=self.workspace,
            role='analyst',
            token=token,
            status='pending'
        )
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertIn('workspace', response.data)
        self.assertEqual(response.data['workspace']['id'], self.workspace.id)


class InvitationTokenValidationTests(APITestCase):
    """Tests for invitation token validation (R13)."""
    
    def setUp(self):
        self.accept_url = '/workspace/accept-invite/'
        
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
    
    def test_missing_token_rejected(self):
        """R13.9: Missing token is rejected."""
        response = self.client.get(self.accept_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_token_rejected(self):
        """R13.10: Invalid token is rejected."""
        response = self.client.get(f'{self.accept_url}?token=invalid_token')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_expired_token_rejected(self):
        """R13.11: Expired token is rejected."""
        # Mock expired token
        with patch('workspace.serializers.verify_invitation_token') as mock_verify:
            mock_verify.return_value = (False, None, 'expired')
            
            response = self.client.get(f'{self.accept_url}?token=expired_token')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('expired', response.data['message'].lower())
    
    def test_invitation_without_token_in_db_rejected(self):
        """R13.12: Token not found in database is rejected."""
        token = generate_invitation_token(
            'test@example.com',
            self.workspace.id,
            'analyst'
        )
        # Note: Not creating invitation record
        
        response = self.client.get(f'{self.accept_url}?token={token}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

