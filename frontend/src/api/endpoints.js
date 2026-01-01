import apiClient from './axios'

// ============================================================================
// Authentication Endpoints
// ============================================================================

export const authAPI = {
  // R1: Sign Up
  signup: (data) => apiClient.post('/auth/signup/', data),
  
  // R2: Email Verification
  verifyEmail: (token) => apiClient.get(`/auth/verify-email/?token=${token}`),
  
  // R3: Login
  login: (credentials) => apiClient.post('/auth/login/', credentials),
  
  // R4: Logout
  logout: (refreshToken) => apiClient.post('/auth/logout/', { refresh: refreshToken }),
  
  // Token refresh
  refreshToken: (refresh) => apiClient.post('/auth/token/refresh/', { refresh }),
}

// ============================================================================
// User Profile Endpoints
// ============================================================================

export const userAPI = {
  // R5: View Profile
  getProfile: () => apiClient.get('/user/profile/'),
  
  // R6: Update Profile
  updateProfile: (data) => apiClient.put('/user/profile/', data),
  
  // R6: Deactivate Account
  deactivateAccount: (refreshToken) => apiClient.delete('/user/deactivate/', { data: { refresh: refreshToken } }),
}

// ============================================================================
// Workspace Endpoints
// ============================================================================

export const workspaceAPI = {
  // R7: Update Workspace Info
  updateWorkspace: (data) => apiClient.put('/workspace/', data),
  
  // R8: View Workspace Members
  getMembers: () => apiClient.get('/workspace/members/'),
  
  // R9: Invite Members
  inviteMember: (data) => apiClient.post('/workspace/invite/', data),
  
  // Remove Pending Invitation
  removeInvitation: (email) => apiClient.delete(`/workspace/invitation/${encodeURIComponent(email)}/`),
  
  // R10: Assign Role
  assignRole: (memberId, role) => apiClient.put(`/workspace/member/${memberId}/role/`, { role }),
  
  // R11: View Member
  getMember: (memberId) => apiClient.get(`/workspace/member/${memberId}/`),
  
  // R11: Update Member
  updateMember: (memberId, data) => apiClient.put(`/workspace/member/${memberId}/`, data),
  
  // R11: Remove Member
  removeMember: (memberId) => apiClient.delete(`/workspace/member/${memberId}/`),
  
  // R12: Suspend Member
  suspendMember: (memberId) => apiClient.put(`/workspace/member/${memberId}/suspend/`),
  
  // Unsuspend Member
  unsuspendMember: (memberId) => apiClient.put(`/workspace/member/${memberId}/unsuspend/`),
  
  // R13: Accept Invitation
  acceptInvitation: (token) => apiClient.get(`/workspace/accept-invite/?token=${token}`),
}

// ============================================================================
// Database Endpoints (Manager Only)
// ============================================================================

export const databaseAPI = {
  // Upload database file
  uploadDatabase: (file, onUploadProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    
    return apiClient.post('/database/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
  },
  
  // Get manager's database information
  getDatabaseInfo: () => apiClient.get('/database/'),
  
  // Get database preview (first 5 rows)
  getDatabasePreview: () => apiClient.get('/database/preview/'),
  
  // Delete manager's database
  deleteDatabase: () => apiClient.delete('/database/'),
}

export default {
  auth: authAPI,
  user: userAPI,
  workspace: workspaceAPI,
  database: databaseAPI,
}

