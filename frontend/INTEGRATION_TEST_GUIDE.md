# 🧪 Integration Testing Guide

Complete guide for testing the React frontend with the Django backend.

---

## 🚀 Prerequisites

### Backend Running
```bash
# Terminal 1 - Start Django backend
cd /path/to/project
python manage.py runserver
# Should be running on: http://127.0.0.1:8000
```

### Frontend Running
```bash
# Terminal 2 - Start React frontend
cd frontend
npm install  # If not already done
npm run dev
# Should be running on: http://localhost:5173
```

### Email Configuration
Ensure Django backend has SMTP configured in `config/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 📋 Test Cases

### Test Suite 1: Manager Full Flow ✅

#### 1.1 Sign Up as Manager
**Steps:**
1. Open: `http://localhost:5173/signup`
2. Fill in:
   - Name: `Test Manager`
   - Email: `manager@test.com`
   - Password: `TestPass123!`
   - Role: `Manager`
3. Click "Create Account"

**Expected:**
- ✅ Success toast: "Account created! Check your email to verify."
- ✅ Redirect to `/verify-email?sent=true`
- ✅ "Check Your Email" message displayed
- ✅ Backend creates user with `is_verified=False`
- ✅ Backend auto-creates workspace for manager
- ✅ Verification email sent

**Backend Check:**
```bash
python manage.py shell
>>> from users.models import User
>>> User.objects.filter(email='manager@test.com').first()
>>> # Should exist with is_verified=False
```

---

#### 1.2 Verify Email
**Steps:**
1. Check email inbox for verification link
2. Click verification link (opens `/verify-email?token=...`)
3. Wait for verification

**Expected:**
- ✅ Loading spinner shown
- ✅ Success icon + "Email Verified!" message
- ✅ Backend sets `is_verified=True`
- ✅ Auto-redirect to login after 3 seconds

**Backend Check:**
```bash
>>> User.objects.filter(email='manager@test.com').first().is_verified
True  # Should be True now
```

---

#### 1.3 Login as Manager
**Steps:**
1. Navigate to: `http://localhost:5173/login`
2. Fill in:
   - Email: `manager@test.com`
   - Password: `TestPass123!`
3. Click "Sign In"

**Expected:**
- ✅ Success toast: "Welcome back, Test Manager!"
- ✅ Tokens stored in localStorage
- ✅ Redirect to `/dashboard/workspace` (manager-specific)
- ✅ Sidebar shows all manager options
- ✅ User name displayed in sidebar

**Console Check:**
```javascript
localStorage.getItem('access_token')  // Should have JWT
localStorage.getItem('refresh_token')  // Should have JWT
```

---

#### 1.4 Update Workspace Settings
**Steps:**
1. Already on `/dashboard/workspace`
2. Update:
   - Workspace Name: `My Company Workspace`
   - Description: `Analytics workspace for the team`
3. Click "Save Changes"

**Expected:**
- ✅ Success toast: "Workspace updated successfully!"
- ✅ Form shows updated values
- ✅ Loading spinner during save
- ✅ Backend updates workspace

**Backend Check:**
```bash
>>> from workspace.models import Workspace
>>> Workspace.objects.first().name
'My Company Workspace'
```

---

#### 1.5 Invite Analyst Member
**Steps:**
1. Click "Invite Member" in sidebar
2. Fill in:
   - Email: `analyst@test.com`
   - Role: `Analyst`
3. Click "Send Invitation"

**Expected:**
- ✅ Success toast: "Invitation sent successfully!"
- ✅ Success screen: "Invitation Sent!"
- ✅ Email sent to `analyst@test.com`
- ✅ Backend creates Invitation record
- ✅ Form resets after 3 seconds

**Backend Check:**
```bash
>>> from workspace.models import Invitation
>>> Invitation.objects.filter(email='analyst@test.com').exists()
True
```

---

#### 1.6 Invite Executive Member
**Steps:**
1. Click "Invite Another Member" or go to `/dashboard/invite`
2. Fill in:
   - Email: `executive@test.com`
   - Role: `Executive`
3. Click "Send Invitation"

**Expected:**
- ✅ Same as 1.5 but for executive role
- ✅ Email sent to `executive@test.com`

---

#### 1.7 View Members List
**Steps:**
1. Click "Members" in sidebar
2. View members table

**Expected:**
- ✅ Shows manager (you) with "You" label
- ✅ Shows no action buttons for yourself
- ✅ Status: "active"
- ✅ Role: "manager"
- ✅ Email displayed

---

### Test Suite 2: Analyst Flow ✅

#### 2.1 Sign Up as Analyst
**Steps:**
1. Open: `http://localhost:5173/signup`
2. Fill in:
   - Name: `Test Analyst`
   - Email: `analyst@test.com`
   - Password: `TestPass123!`
   - Role: `Analyst`
3. Click "Create Account"

**Expected:**
- ✅ Success toast + redirect
- ✅ Verification email sent

---

#### 2.2 Verify Email
**Steps:**
1. Click verification link from email

**Expected:**
- ✅ Email verified
- ✅ Redirect to login

---

#### 2.3 Accept Invitation
**Steps:**
1. Open invitation email sent by manager (step 1.5)
2. Click invitation link
3. Should open `/accept-invite?token=...`

**Expected:**
- ✅ Loading → Success screen
- ✅ "Invitation Accepted!" message
- ✅ Workspace name shown
- ✅ Backend adds user to WorkspaceMember
- ✅ Backend updates user role to 'analyst'
- ✅ "Login to Continue" button shown

**Backend Check:**
```bash
>>> from workspace.models import WorkspaceMember
>>> WorkspaceMember.objects.filter(user__email='analyst@test.com').exists()
True
>>> User.objects.get(email='analyst@test.com').role
'analyst'
```

---

#### 2.4 Login as Analyst
**Steps:**
1. Click "Login to Continue" or go to `/login`
2. Login with analyst credentials

**Expected:**
- ✅ Success login
- ✅ Redirect to `/dashboard` (not `/dashboard/workspace`)
- ✅ Sidebar DOES NOT show "Workspace Settings"
- ✅ Sidebar DOES NOT show "Invite Member"
- ✅ Sidebar DOES show "Members"
- ✅ Sidebar DOES show "Profile"

---

#### 2.5 View Members as Analyst
**Steps:**
1. Click "Members" in sidebar

**Expected:**
- ✅ Shows all workspace members (manager + analyst)
- ✅ NO action buttons (not a manager)
- ✅ Can see all member names, roles, statuses
- ✅ NO "Invite Member" button in header

---

#### 2.6 Update Own Profile
**Steps:**
1. Click "Profile" in sidebar
2. Update name to `Test Analyst Updated`
3. Click "Save Changes"

**Expected:**
- ✅ Success toast
- ✅ Name updated in sidebar
- ✅ Name updated in profile view

---

### Test Suite 3: Executive Flow ✅

#### 3.1 Sign Up as Executive
**Steps:**
1. Sign up with:
   - Name: `Test Executive`
   - Email: `executive@test.com`
   - Password: `TestPass123!`
   - Role: `Executive`

**Expected:**
- ✅ Account created
- ✅ Verification email sent

---

#### 3.2 Accept Invitation (Executive)
**Steps:**
1. Verify email first
2. Click invitation link sent by manager (step 1.6)

**Expected:**
- ✅ Invitation accepted
- ✅ Role updated to 'executive'
- ✅ Added to workspace

---

#### 3.3 Login as Executive
**Steps:**
1. Login with executive credentials

**Expected:**
- ✅ Redirect to `/dashboard`
- ✅ Same sidebar as Analyst (no manager options)
- ✅ Can view members
- ✅ Cannot invite or manage members

---

### Test Suite 4: Manager - Member Management ✅

#### 4.1 Change Analyst Role to Executive
**Steps:**
1. Login as manager
2. Go to "Members"
3. Click "Change Role" (edit icon) next to analyst
4. Select "Executive"
5. Click "Update Role"

**Expected:**
- ✅ Modal opens
- ✅ Role dropdown shows analyst/executive only
- ✅ Success toast: "Role updated successfully!"
- ✅ Members list refreshes
- ✅ Analyst now shows as "executive" role
- ✅ Backend updates user role

**Backend Check:**
```bash
>>> User.objects.get(email='analyst@test.com').role
'executive'
```

---

#### 4.2 Suspend Executive
**Steps:**
1. Click "Suspend" (UserX icon) next to executive
2. Confirm in modal
3. Click "Suspend"

**Expected:**
- ✅ Warning modal opens
- ✅ Success toast: "Member suspended successfully!"
- ✅ Status changes to "suspended" (red badge)
- ✅ Icon changes to UserCheck (for unsuspend)
- ✅ Backend sets `is_active=False`

**Backend Check:**
```bash
>>> User.objects.get(email='executive@test.com').is_active
False
```

**Login Test:**
- ✅ Suspended user CANNOT login
- ✅ Error message: "Your account is suspended"

---

#### 4.3 Unsuspend Executive
**Steps:**
1. Click "Unsuspend" (UserCheck icon) next to suspended executive
2. Confirm
3. Click "Unsuspend"

**Expected:**
- ✅ Success toast: "Member unsuspended successfully!"
- ✅ Status changes to "active"
- ✅ Backend sets `is_active=True`
- ✅ User can login again

---

#### 4.4 Remove Member
**Steps:**
1. Click "Remove" (Trash icon) next to executive
2. Read warning modal
3. Click "Remove Member"

**Expected:**
- ✅ Red warning modal
- ✅ Success toast: "Member removed successfully!"
- ✅ Member disappears from list
- ✅ Backend deletes WorkspaceMember record
- ✅ User account still exists but not in workspace

**Backend Check:**
```bash
>>> WorkspaceMember.objects.filter(user__email='executive@test.com').exists()
False  # Not in workspace anymore
>>> User.objects.filter(email='executive@test.com').exists()
True  # User account still exists
```

---

### Test Suite 5: Profile & Account Management ✅

#### 5.1 Update Profile Name
**Steps:**
1. Login as any user
2. Go to Profile
3. Update name
4. Save

**Expected:**
- ✅ Success toast
- ✅ Name updated everywhere
- ✅ Sidebar shows new name

---

#### 5.2 Update Email (Triggers Re-verification)
**Steps:**
1. Go to Profile
2. Change email to `newemail@test.com`
3. Save

**Expected:**
- ✅ Yellow warning banner appears
- ✅ Success toast: "Profile updated! Please verify your new email address."
- ✅ New verification email sent to new address
- ✅ Backend sets `is_verified=False`
- ✅ Email status badge shows "Pending"

**Backend Check:**
```bash
>>> user = User.objects.get(id=1)
>>> user.email
'newemail@test.com'
>>> user.is_verified
False  # Needs re-verification
```

---

#### 5.3 Deactivate Account
**Steps:**
1. Go to Profile
2. Scroll to "Danger Zone"
3. Click "Deactivate Account"
4. Read warning modal
5. Confirm deactivation

**Expected:**
- ✅ Red warning modal with bullet points
- ✅ Success toast: "Account deactivated successfully"
- ✅ Auto logout
- ✅ Redirect to login
- ✅ Backend sets `is_active=False`
- ✅ Refresh token blacklisted

**Login Test:**
- ✅ Deactivated user CANNOT login
- ✅ Error message shown

---

### Test Suite 6: Authentication Edge Cases ✅

#### 6.1 Login with Unverified Email
**Steps:**
1. Create account but don't verify
2. Try to login

**Expected:**
- ✅ Error: "Please verify your email before logging in"
- ✅ Login fails

---

#### 6.2 Login with Wrong Password
**Steps:**
1. Enter correct email, wrong password
2. Try to login

**Expected:**
- ✅ Error toast: "Invalid login credentials"
- ✅ Login fails
- ✅ No details leaked about which is wrong

---

#### 6.3 Email Already Registered
**Steps:**
1. Try to sign up with existing email

**Expected:**
- ✅ Error toast: "Email already registered"
- ✅ Signup fails

---

#### 6.4 Expired Verification Token
**Steps:**
1. Use old verification link (> 24 hours)

**Expected:**
- ✅ Error: "Verification link expired"
- ✅ Red X icon shown
- ✅ Option to create new account

---

#### 6.5 Expired Invitation Token
**Steps:**
1. Use old invitation link (> 48 hours)

**Expected:**
- ✅ Error: "Invitation link has expired"
- ✅ Red X icon shown

---

#### 6.6 Token Refresh Flow
**Steps:**
1. Login
2. Wait for access token to expire (1 hour) OR
3. Manually delete access token from localStorage
4. Make any API request

**Expected:**
- ✅ Request fails with 401
- ✅ Auto token refresh triggered
- ✅ New access token received
- ✅ Original request retried automatically
- ✅ No user interruption

**Console Check:**
```javascript
// Watch Network tab for:
// 1. Original request → 401
// 2. POST /auth/token/refresh/ → 200
// 3. Original request retried → 200
```

---

#### 6.7 Refresh Token Expired
**Steps:**
1. Login
2. Manually expire refresh token (delete or wait 7 days)
3. Make API request

**Expected:**
- ✅ Token refresh fails
- ✅ User logged out automatically
- ✅ Redirect to login
- ✅ Toast: "Session expired, please login again"

---

### Test Suite 7: Workspace Edge Cases ✅

#### 7.1 Manager Cannot Remove Self
**Steps:**
1. Login as manager
2. Try to click remove on own row

**Expected:**
- ✅ No action buttons shown for manager's own row
- ✅ Just a dash (-) shown

---

#### 7.2 Manager Cannot Change Own Role
**Steps:**
1. Check if edit button appears for manager's own row

**Expected:**
- ✅ No edit button for own role
- ✅ Protection in place

---

#### 7.3 Manager Cannot Suspend Self
**Steps:**
1. Check if suspend button appears for manager's own row

**Expected:**
- ✅ No suspend button for self
- ✅ Protection in place

---

#### 7.4 Cannot Invite Existing Member
**Steps:**
1. Try to invite email that's already a member

**Expected:**
- ✅ Backend error: "Already a member"
- ✅ Toast error shown
- ✅ Invitation not sent

---

#### 7.5 Cannot Invite with Pending Invitation
**Steps:**
1. Send invitation to `test@example.com`
2. Try to send another invitation to same email

**Expected:**
- ✅ Backend error: "Invitation already sent"
- ✅ Toast error shown

---

### Test Suite 8: Navigation & Routing ✅

#### 8.1 Unauthenticated Access to Dashboard
**Steps:**
1. Logout
2. Try to visit `/dashboard`

**Expected:**
- ✅ Auto redirect to `/login`
- ✅ No flash of dashboard

---

#### 8.2 Analyst Access to Manager-Only Pages
**Steps:**
1. Login as analyst
2. Try to visit `/dashboard/workspace`

**Expected:**
- ✅ Access denied screen OR
- ✅ Auto redirect to `/dashboard`

---

#### 8.3 Already Logged In User on Auth Pages
**Steps:**
1. Login successfully
2. Try to visit `/login` or `/signup`

**Expected:**
- ✅ Auto redirect to `/dashboard`
- ✅ Cannot access auth pages while logged in

---

#### 8.4 Role-Based Sidebar
**Steps:**
1. Check sidebar options for each role

**Expected:**

**Manager:**
- ✅ Dashboard
- ✅ Profile
- ✅ Workspace Settings
- ✅ Members
- ✅ Invite Member

**Analyst:**
- ✅ Dashboard
- ✅ Profile
- ✅ Members
- ❌ Workspace Settings
- ❌ Invite Member

**Executive:**
- ✅ Dashboard
- ✅ Profile
- ✅ Members
- ❌ Workspace Settings
- ❌ Invite Member

---

## 🎯 Success Criteria

All test suites should PASS with:
- ✅ No console errors
- ✅ Correct API calls in Network tab
- ✅ Correct backend data changes
- ✅ Correct UI feedback (toasts, loading states)
- ✅ Smooth navigation without glitches
- ✅ Responsive on mobile/tablet/desktop

---

## 🐛 Reporting Issues

If any test fails, report with:
1. **Test ID** (e.g., 1.3 Login as Manager)
2. **Expected Result**
3. **Actual Result**
4. **Console Errors** (if any)
5. **Network Tab** (failed requests)
6. **Backend Logs** (if relevant)

---

## 📝 Test Log Template

```markdown
## Test Date: [DATE]

### Environment
- Backend: http://127.0.0.1:8000 ✅
- Frontend: http://localhost:5173 ✅
- Email: Configured ✅

### Results
- Test Suite 1: ✅ PASS / ❌ FAIL
- Test Suite 2: ✅ PASS / ❌ FAIL
- Test Suite 3: ✅ PASS / ❌ FAIL
- Test Suite 4: ✅ PASS / ❌ FAIL
- Test Suite 5: ✅ PASS / ❌ FAIL
- Test Suite 6: ✅ PASS / ❌ FAIL
- Test Suite 7: ✅ PASS / ❌ FAIL
- Test Suite 8: ✅ PASS / ❌ FAIL

### Issues Found
[List any issues]

### Notes
[Any additional observations]
```

---

**Ready to test!** 🚀

