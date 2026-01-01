"""
Comprehensive tests for Role Assignment and Suspension (R10, R12)

Tests cover:
- Assign/update member roles (R10)
- Suspend members (R12)
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from workspace.models import Workspace, WorkspaceMember
from rest_framework_simplejwt.tokens import RefreshToken


class RoleAssignmentTests(APITestCase):
    """Tests for assigning/updating member roles (R10)."""
    
    def setUp(self):
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
        
        # Create analyst member
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst)
        
        # Create another analyst
        self.analyst2 = User.objects.create_user(
            email='analyst2@example.com',
            password='Password123!',
            name='Analyst 2',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst2)
        
        # Generate tokens
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
        
        self.role_url = f'/workspace/member/{self.analyst.id}/role/'
    
    def test_manager_can_assign_role(self):
        """R10.1: Manager can assign role to member."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'role': 'executive'
        }
        
        response = self.client.put(self.role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['member']['role'], 'executive')
        
        # Verify in database
        self.analyst.refresh_from_db()
        self.assertEqual(self.analyst.role, 'executive')
    
    def test_can_change_analyst_to_executive(self):
        """R10.2: Can change analyst to executive."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'role': 'executive'
        }
        
        response = self.client.put(self.role_url, data, format='json')
        
        self.analyst.refresh_from_db()
        self.assertEqual(self.analyst.role, 'executive')
    
    def test_can_change_executive_to_analyst(self):
        """R10.3: Can change executive to analyst."""
        # First change to executive
        self.analyst.role = 'executive'
        self.analyst.save()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'role': 'analyst'
        }
        
        response = self.client.put(self.role_url, data, format='json')
        
        self.analyst.refresh_from_db()
        self.assertEqual(self.analyst.role, 'analyst')
    
    def test_cannot_change_own_role(self):
        """R10.4: Manager cannot change their own role."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        own_role_url = f'/workspace/member/{self.manager.id}/role/'
        data = {
            'role': 'analyst'
        }
        
        response = self.client.put(own_role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Role should remain unchanged
        self.manager.refresh_from_db()
        self.assertEqual(self.manager.role, 'manager')
    
    def test_cannot_demote_another_manager(self):
        """R10.5: Cannot demote another manager."""
        # Create another manager
        manager2 = User.objects.create_user(
            email='manager2@example.com',
            password='Password123!',
            name='Manager 2',
            role='manager',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=manager2)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        role_url = f'/workspace/member/{manager2.id}/role/'
        data = {
            'role': 'analyst'
        }
        
        response = self.client.put(role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Role should remain manager
        manager2.refresh_from_db()
        self.assertEqual(manager2.role, 'manager')
    
    def test_analyst_cannot_assign_roles(self):
        """R10.6: Analyst cannot assign roles."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        role_url = f'/workspace/member/{self.analyst2.id}/role/'
        data = {
            'role': 'executive'
        }
        
        response = self.client.put(role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Role should remain unchanged
        self.analyst2.refresh_from_db()
        self.assertEqual(self.analyst2.role, 'analyst')
    
    def test_cannot_assign_to_non_member(self):
        """R10.7: Cannot assign role to non-workspace member."""
        # Create user not in workspace
        outsider = User.objects.create_user(
            email='outsider@example.com',
            password='Password123!',
            name='Outsider',
            role='analyst',
            is_verified=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        role_url = f'/workspace/member/{outsider.id}/role/'
        data = {
            'role': 'executive'
        }
        
        response = self.client.put(role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_missing_role_rejected(self):
        """R10.8: Missing role is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {}  # No role
        
        response = self.client.put(self.role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_role_rejected(self):
        """R10.9: Invalid role is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'role': 'admin'  # Invalid role
        }
        
        response = self.client.put(self.role_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MemberSuspensionTests(APITestCase):
    """Tests for suspending workspace members (R12)."""
    
    def setUp(self):
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
        
        # Create analyst member
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst)
        
        # Create executive member
        self.executive = User.objects.create_user(
            email='executive@example.com',
            password='Password123!',
            name='Executive User',
            role='executive',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.executive)
        
        # Generate tokens
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
        
        self.suspend_url = f'/workspace/member/{self.analyst.id}/suspend/'
    
    def test_manager_can_suspend_analyst(self):
        """R12.1: Manager can suspend analyst."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.put(self.suspend_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify user is suspended
        self.analyst.refresh_from_db()
        self.assertFalse(self.analyst.is_active)
    
    def test_manager_can_suspend_executive(self):
        """R12.2: Manager can suspend executive."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        suspend_exec_url = f'/workspace/member/{self.executive.id}/suspend/'
        response = self.client.put(suspend_exec_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.executive.refresh_from_db()
        self.assertFalse(self.executive.is_active)
    
    def test_suspended_user_cannot_login(self):
        """R12.3: Suspended user cannot login."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        # Suspend user
        self.client.put(self.suspend_url)
        
        # Try to login as suspended user
        login_data = {
            'email': 'analyst@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post('/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('suspend', response.data['message'].lower())
    
    def test_cannot_suspend_self(self):
        """R12.4: Manager cannot suspend themselves."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        suspend_self_url = f'/workspace/member/{self.manager.id}/suspend/'
        response = self.client.put(suspend_self_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Should still be active
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.is_active)
    
    def test_cannot_suspend_another_manager(self):
        """R12.5: Cannot suspend another manager."""
        # Create another manager
        manager2 = User.objects.create_user(
            email='manager2@example.com',
            password='Password123!',
            name='Manager 2',
            role='manager',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=manager2)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        suspend_manager_url = f'/workspace/member/{manager2.id}/suspend/'
        response = self.client.put(suspend_manager_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Should still be active
        manager2.refresh_from_db()
        self.assertTrue(manager2.is_active)
    
    def test_analyst_cannot_suspend_members(self):
        """R12.6: Analyst cannot suspend members."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        suspend_exec_url = f'/workspace/member/{self.executive.id}/suspend/'
        response = self.client.put(suspend_exec_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Executive should still be active
        self.executive.refresh_from_db()
        self.assertTrue(self.executive.is_active)
    
    def test_cannot_suspend_non_member(self):
        """R12.7: Cannot suspend non-workspace member."""
        # Create user not in workspace
        outsider = User.objects.create_user(
            email='outsider@example.com',
            password='Password123!',
            name='Outsider',
            role='analyst',
            is_verified=True
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        suspend_outsider_url = f'/workspace/member/{outsider.id}/suspend/'
        response = self.client.put(suspend_outsider_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_suspension_sets_is_active_false(self):
        """R12.8: Suspension sets is_active to False."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        self.client.put(self.suspend_url)
        
        self.analyst.refresh_from_db()
        self.assertFalse(self.analyst.is_active)
    
    def test_suspension_preserves_other_data(self):
        """R12.9: Suspension preserves other user data."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        self.client.put(self.suspend_url)
        
        self.analyst.refresh_from_db()
        self.assertEqual(self.analyst.email, 'analyst@example.com')
        self.assertEqual(self.analyst.name, 'Analyst User')
        self.assertEqual(self.analyst.role, 'analyst')
        self.assertTrue(self.analyst.is_verified)
    
    def test_suspended_user_remains_in_workspace(self):
        """R12.10: Suspended user remains in workspace."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        self.client.put(self.suspend_url)
        
        # Membership should still exist
        membership_exists = WorkspaceMember.objects.filter(
            workspace=self.workspace,
            user=self.analyst
        ).exists()
        self.assertTrue(membership_exists)
    
    def test_suspended_user_shown_in_members_list(self):
        """R12.11: Suspended user appears in members list with status."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        # Suspend user
        self.client.put(self.suspend_url)
        
        # Get members list
        response = self.client.get('/workspace/members/')
        
        # Find suspended analyst in members list
        suspended_member = next(
            (m for m in response.data['members'] if m['email'] == 'analyst@example.com'),
            None
        )
        
        self.assertIsNotNone(suspended_member)
        self.assertEqual(suspended_member['status'], 'suspended')
    
    def test_unauthenticated_cannot_suspend(self):
        """R12.12: Unauthenticated user cannot suspend."""
        response = self.client.put(self.suspend_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_suspend_nonexistent_user_returns_error(self):
        """R12.13: Suspending non-existent user returns error."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.put('/workspace/member/99999/suspend/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnsuspendTests(APITestCase):
    """Tests for unsuspending members (reactivation)."""
    
    def setUp(self):
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
        
        # Create suspended analyst
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True,
            is_active=False  # Already suspended
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst)
        
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        self.update_url = f'/workspace/member/{self.analyst.id}/'
    
    def test_can_reactivate_suspended_user(self):
        """R12.14: Manager can reactivate suspended user."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'status': 'active'
        }
        
        response = self.client.put(self.update_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is active again
        self.analyst.refresh_from_db()
        self.assertTrue(self.analyst.is_active)
    
    def test_reactivated_user_can_login(self):
        """R12.15: Reactivated user can login."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        # Reactivate
        data = {'status': 'active'}
        self.client.put(self.update_url, data, format='json')
        
        # Try to login
        login_data = {
            'email': 'analyst@example.com',
            'password': 'Password123!'
        }
        
        response = self.client.post('/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

