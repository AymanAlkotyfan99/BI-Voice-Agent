"""
Comprehensive tests for Workspace Management (R7, R8, R11)

Tests cover:
- Update workspace info (R7)
- View workspace members (R8)
- Manage members (R11)
"""

from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User
from workspace.models import Workspace, WorkspaceMember
from rest_framework_simplejwt.tokens import RefreshToken


class WorkspaceUpdateTests(APITestCase):
    """Tests for updating workspace information (R7)."""
    
    def setUp(self):
        self.workspace_url = '/workspace/'
        
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
            description='Original description',
            owner=self.manager
        )
        
        refresh = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh.access_token)
        
        # Create analyst (no workspace)
        self.analyst = User.objects.create_user(
            email='analyst@example.com',
            password='Password123!',
            name='Analyst User',
            role='analyst',
            is_verified=True
        )
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
    
    def test_manager_can_update_workspace_name(self):
        """R7.1: Manager can update workspace name."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'name': 'Updated Workspace Name'
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['workspace']['name'], 'Updated Workspace Name')
        
        # Verify in database
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.name, 'Updated Workspace Name')
    
    def test_manager_can_update_workspace_description(self):
        """R7.2: Manager can update workspace description."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'description': 'New description for workspace'
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['workspace']['description'], 'New description for workspace')
        
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.description, 'New description for workspace')
    
    def test_manager_can_update_both_name_and_description(self):
        """R7.3: Manager can update both name and description."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'name': 'New Name',
            'description': 'New Description'
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.name, 'New Name')
        self.assertEqual(self.workspace.description, 'New Description')
    
    def test_analyst_cannot_update_workspace(self):
        """R7.4: Analyst cannot update workspace."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        data = {
            'name': 'Hacked Name'
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Workspace should remain unchanged
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.name, 'Test Workspace')
    
    def test_unauthenticated_cannot_update_workspace(self):
        """R7.5: Unauthenticated user cannot update workspace."""
        data = {
            'name': 'Hacked Name'
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_empty_name_rejected(self):
        """R7.6: Empty workspace name is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        data = {
            'name': ''
        }
        
        response = self.client.put(self.workspace_url, data, format='json')
        
        # Workspace name should remain unchanged
        self.workspace.refresh_from_db()
        self.assertEqual(self.workspace.name, 'Test Workspace')


class WorkspaceMembersViewTests(APITestCase):
    """Tests for viewing workspace members (R8)."""
    
    def setUp(self):
        self.members_url = '/workspace/members/'
        
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
        
        # Create analysts and add to workspace
        self.analyst1 = User.objects.create_user(
            email='analyst1@example.com',
            password='Password123!',
            name='Analyst 1',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst1)
        
        self.analyst2 = User.objects.create_user(
            email='analyst2@example.com',
            password='Password123!',
            name='Analyst 2',
            role='analyst',
            is_verified=True
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.analyst2)
        
        # Create suspended analyst
        self.suspended_analyst = User.objects.create_user(
            email='suspended@example.com',
            password='Password123!',
            name='Suspended Analyst',
            role='analyst',
            is_verified=True,
            is_active=False  # Suspended
        )
        WorkspaceMember.objects.create(workspace=self.workspace, user=self.suspended_analyst)
        
        # Generate tokens
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        refresh_analyst = RefreshToken.for_user(self.analyst1)
        self.analyst_token = str(refresh_analyst.access_token)
    
    def test_manager_can_view_members(self):
        """R8.1: Manager can view workspace members."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('members', response.data)
        self.assertIn('workspace_id', response.data)
    
    def test_members_list_includes_manager(self):
        """R8.2: Members list includes the manager/owner."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        # Find manager in members list
        manager_found = any(m['email'] == 'manager@example.com' for m in response.data['members'])
        self.assertTrue(manager_found)
    
    def test_members_list_includes_all_analysts(self):
        """R8.3: Members list includes all workspace members."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        # Should have manager + 3 analysts
        self.assertGreaterEqual(len(response.data['members']), 3)
    
    def test_member_has_correct_fields(self):
        """R8.4: Each member has required fields."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        member = response.data['members'][0]
        required_fields = ['id', 'name', 'email', 'role', 'status']
        for field in required_fields:
            self.assertIn(field, member)
    
    def test_suspended_member_status_correct(self):
        """R8.5: Suspended member has status='suspended'."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        # Find suspended analyst
        suspended_member = next(
            (m for m in response.data['members'] if m['email'] == 'suspended@example.com'),
            None
        )
        
        self.assertIsNotNone(suspended_member)
        self.assertEqual(suspended_member['status'], 'suspended')
    
    def test_active_member_status_correct(self):
        """R8.6: Active verified member has status='active'."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.members_url)
        
        # Find active analyst
        active_member = next(
            (m for m in response.data['members'] if m['email'] == 'analyst1@example.com'),
            None
        )
        
        self.assertIsNotNone(active_member)
        self.assertEqual(active_member['status'], 'active')
    
    def test_analyst_can_view_members(self):
        """R8.7: Analyst can view workspace members."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        response = self.client.get(self.members_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('members', response.data)
    
    def test_unauthenticated_cannot_view_members(self):
        """R8.8: Unauthenticated user cannot view members."""
        response = self.client.get(self.members_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MemberManageViewTests(APITestCase):
    """Tests for viewing individual member details (R11)."""
    
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
        
        # Generate tokens
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
        
        self.member_detail_url = f'/workspace/member/{self.analyst.id}/'
    
    def test_manager_can_view_member_details(self):
        """R11.1: Manager can view member details."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.member_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'analyst@example.com')
    
    def test_member_can_view_own_details(self):
        """R11.2: Member can view their own details."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        member_own_url = f'/workspace/member/{self.analyst.id}/'
        response = self.client.get(member_own_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_member_details_have_correct_fields(self):
        """R11.3: Member details include all required fields."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get(self.member_detail_url)
        
        required_fields = ['id', 'name', 'email', 'role', 'status']
        for field in required_fields:
            self.assertIn(field, response.data)
    
    def test_nonexistent_member_returns_404(self):
        """R11.4: Viewing non-existent member returns 404."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.get('/workspace/member/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MemberRemoveTests(APITestCase):
    """Tests for removing members from workspace (R11)."""
    
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
        self.membership = WorkspaceMember.objects.create(
            workspace=self.workspace,
            user=self.analyst
        )
        
        # Generate tokens
        refresh_manager = RefreshToken.for_user(self.manager)
        self.manager_token = str(refresh_manager.access_token)
        
        refresh_analyst = RefreshToken.for_user(self.analyst)
        self.analyst_token = str(refresh_analyst.access_token)
        
        self.remove_url = f'/workspace/member/{self.analyst.id}/'
    
    def test_manager_can_remove_member(self):
        """R11.5: Manager can remove member from workspace."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.delete(self.remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verify membership removed
        self.assertFalse(WorkspaceMember.objects.filter(
            workspace=self.workspace,
            user=self.analyst
        ).exists())
    
    def test_manager_cannot_remove_self(self):
        """R11.6: Manager cannot remove themselves."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        remove_self_url = f'/workspace/member/{self.manager.id}/'
        response = self.client.delete(remove_self_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_analyst_cannot_remove_members(self):
        """R11.7: Analyst cannot remove members."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.analyst_token}')
        
        response = self.client.delete(self.remove_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Membership should still exist
        self.assertTrue(WorkspaceMember.objects.filter(
            workspace=self.workspace,
            user=self.analyst
        ).exists())
    
    def test_remove_nonexistent_member_returns_404(self):
        """R11.8: Removing non-existent member returns 404."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.manager_token}')
        
        response = self.client.delete('/workspace/member/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

