# Quick Start Guide - BI Voice Agent Frontend

Get up and running in 5 minutes!

## 🚀 Quick Setup

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start the development server
npm run dev

# 4. Open your browser
# Visit: http://localhost:5173
```

## 🎯 Test User Journeys

### 1. Manager Journey (Full Access)

1. **Sign Up as Manager**
   - Go to `/signup`
   - Fill in details and select "Manager" role
   - Submit and check email for verification link

2. **Verify Email**
   - Click link in email
   - Redirects to login page

3. **Login**
   - Use your credentials
   - Redirected to `/dashboard/workspace`

4. **Update Workspace**
   - Already on workspace settings
   - Update workspace name and description

5. **Invite Team Members**
   - Go to "Invite Member" from sidebar
   - Enter email and select role (Analyst/Executive)
   - Invitation sent via email

6. **Manage Members**
   - Go to "Members" from sidebar
   - Change member roles
   - Suspend/unsuspend members
   - Remove members from workspace

7. **Update Profile**
   - Go to "Profile" from sidebar
   - Update name or email
   - Deactivate account option available

### 2. Analyst/Executive Journey (Join Workspace)

1. **Receive Invitation**
   - Check email for invitation link

2. **Sign Up** (if new user)
   - Click invitation link → prompted to sign up
   - Use the invited email address
   - Select role matching invitation
   - Verify email

3. **Accept Invitation**
   - Click invitation link again after signup
   - Automatically joins workspace

4. **Login & Access**
   - Login with credentials
   - Redirected to `/dashboard`
   - View workspace members
   - Update profile

## 🔑 Key Features to Test

### Authentication
- ✅ Signup with role selection
- ✅ Email verification
- ✅ Login with redirect based on role
- ✅ Logout with token blacklisting
- ✅ Auto token refresh on 401

### Profile Management
- ✅ View profile details
- ✅ Update name and email
- ✅ Email re-verification on email change
- ✅ Deactivate account

### Workspace Management (Manager Only)
- ✅ Update workspace settings
- ✅ View all members with status
- ✅ Invite new members via email
- ✅ Change member roles
- ✅ Suspend/unsuspend members
- ✅ Remove members from workspace

### Invitation Flow
- ✅ Receive invitation email
- ✅ Accept invitation (existing user)
- ✅ Sign up first prompt (new user)
- ✅ Token expiration handling (48 hours)

## 📱 Responsive Design

Test on different screen sizes:
- 📱 **Mobile**: Hamburger menu, collapsible sidebar
- 💻 **Tablet**: Optimized layouts
- 🖥️ **Desktop**: Full sidebar navigation

## 🎨 UI Components Showcase

Visit the home page to see:
- Hero section with gradient background
- Feature cards with icons
- Call-to-action sections
- Smooth transitions and hover effects

## 🔐 Role-Based Access

### Manager
- Full workspace access
- All CRUD operations on members
- Workspace settings management

### Analyst
- View members
- Update own profile
- View dashboards (Sprint 2)

### Executive
- View members (read-only)
- Update own profile
- View dashboards (read-only, Sprint 2)

## ⚙️ Environment Configuration

Default configuration works out of the box:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_FRONTEND_URL=http://localhost:5173
```

Change these if your backend runs on a different port.

## 🐛 Common Issues & Solutions

### Issue: "Network Error"
**Solution**: Ensure backend is running on port 8000

### Issue: "CORS Error"
**Solution**: Check backend CORS settings allow `http://localhost:5173`

### Issue: "Email not sending"
**Solution**: Check backend email configuration (SMTP settings)

### Issue: "Token expired"
**Solution**: Logout and login again to get fresh tokens

## 📝 Testing Checklist

- [ ] Sign up as Manager
- [ ] Verify email
- [ ] Login successfully
- [ ] Update workspace settings
- [ ] Invite an Analyst
- [ ] Invite an Executive
- [ ] Sign up as invited user
- [ ] Accept invitation
- [ ] Login as Analyst
- [ ] View members list
- [ ] Update profile
- [ ] Change member role (as Manager)
- [ ] Suspend member (as Manager)
- [ ] Remove member (as Manager)
- [ ] Logout
- [ ] Login again (test token refresh)
- [ ] Test on mobile device
- [ ] Deactivate account

## 🎉 Production Deployment

When ready for production:

1. Update environment variables
2. Build the application: `npm run build`
3. Deploy the `dist/` folder to your hosting provider
4. Update backend CORS settings for production domain

## 📚 Documentation

- **Full README**: See `FRONTEND_README.md`
- **Backend API**: See `../SPRINT_1_REQUIREMENTS_DETAILED.md`
- **Project Overview**: See `../README.md`

## 🆘 Need Help?

Check the detailed `FRONTEND_README.md` for:
- Project structure
- API integration details
- Component documentation
- Troubleshooting guide
- Architecture decisions

---

**Happy Coding! 🚀**

