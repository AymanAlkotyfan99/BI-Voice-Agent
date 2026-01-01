# BI Voice Agent - Frontend

A modern React + Vite + TailwindCSS frontend for the BI Voice Agent project.

## 🚀 Tech Stack

- **React 18+** - Modern React with hooks
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client with interceptors
- **Zustand** - Lightweight state management
- **React Hot Toast** - Beautiful toast notifications
- **Lucide React** - Modern icon library

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/              # API configuration & endpoints
│   │   ├── axios.js      # Axios instance with JWT handling
│   │   └── endpoints.js  # API endpoint definitions
│   ├── components/       # Reusable UI components
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Select.jsx
│   │   ├── Card.jsx
│   │   ├── Badge.jsx
│   │   ├── Modal.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── EmptyState.jsx
│   │   └── index.js      # Component exports
│   ├── layouts/          # Page layouts
│   │   ├── AuthLayout.jsx
│   │   └── DashboardLayout.jsx
│   ├── pages/            # Application pages
│   │   ├── Home.jsx
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   └── VerifyEmail.jsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.jsx
│   │   ├── profile/
│   │   │   └── Profile.jsx
│   │   └── workspace/
│   │       ├── AcceptInvite.jsx
│   │       ├── InviteMember.jsx
│   │       ├── MembersList.jsx
│   │       └── WorkspaceSettings.jsx
│   ├── store/            # Zustand state management
│   │   └── auth.js       # Authentication store
│   ├── styles/           # Global styles
│   │   └── index.css     # Tailwind + custom styles
│   ├── App.jsx           # Main app component with routing
│   └── main.jsx          # Application entry point
├── .env.example          # Environment variables template
├── index.html            # HTML entry point
├── package.json          # Dependencies & scripts
├── tailwind.config.js    # Tailwind configuration
├── vite.config.js        # Vite configuration
└── postcss.config.js     # PostCSS configuration
```

## 🛠️ Setup & Installation

### Prerequisites

- Node.js 16+ and npm/yarn
- Backend server running on `http://127.0.0.1:8000`

### Installation Steps

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` if needed:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   VITE_FRONTEND_URL=http://localhost:5173
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to `http://localhost:5173`

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🔐 Authentication Flow

### JWT Token Management

The application uses JWT tokens for authentication:
- **Access Token**: Short-lived (1 hour), stored in localStorage
- **Refresh Token**: Long-lived (7 days), stored in localStorage

### Automatic Token Refresh

The Axios interceptor automatically:
1. Attaches access token to requests
2. Detects 401 errors
3. Attempts token refresh
4. Retries failed request
5. Redirects to login if refresh fails

### Protected Routes

Routes are protected using the `PrivateRoute` component:
```jsx
<PrivateRoute roles={['manager']}>
  <Component />
</PrivateRoute>
```

## 🎯 Features Implemented

### Sprint 1 Requirements (R1-R13)

#### Authentication (R1-R4)
- ✅ **R1: Sign Up** - User registration with role selection
- ✅ **R2: Email Verification** - Account activation via email
- ✅ **R3: Login** - JWT-based authentication with role-based redirect
- ✅ **R4: Logout** - Token blacklisting

#### Profile Management (R5-R6)
- ✅ **R5: View/Update Profile** - Name and email management
- ✅ **R6: Deactivate Account** - Account soft-delete

#### Workspace Management (R7-R13)
- ✅ **R7: Edit Workspace Info** - Workspace settings (Manager only)
- ✅ **R8: View Members** - List all workspace members
- ✅ **R9: Invite Members** - Send email invitations (Manager only)
- ✅ **R10: Assign Roles** - Change member roles (Manager only)
- ✅ **R11: Manage Members** - View, update, remove members
- ✅ **R12: Suspend Member** - Suspend/unsuspend members (Manager only)
- ✅ **R13: Accept Invitation** - Join workspace via invitation link

## 🎨 UI Components

### Reusable Components

All components are built with TailwindCSS and follow consistent design patterns:

- **Button** - Primary, secondary, danger variants with loading states
- **Input** - Form input with icon support and validation
- **Select** - Dropdown with custom styling
- **Card** - Content container with optional title/actions
- **Badge** - Status indicators (success, warning, danger, info)
- **Modal** - Overlay dialog with backdrop
- **LoadingSpinner** - Loading indicator with sizes
- **EmptyState** - Empty data placeholder with actions

### Design System

- **Colors**: Primary blue palette with semantic colors
- **Spacing**: Consistent padding and margins
- **Typography**: Clear hierarchy with Tailwind defaults
- **Shadows**: Subtle elevation with `shadow-md` and `shadow-xl`
- **Rounded Corners**: `rounded-lg` and `rounded-xl`
- **Hover Effects**: Smooth transitions on interactive elements
- **Dark Mode Ready**: Uses Tailwind's dark mode classes

## 🔄 State Management

### Zustand Auth Store

Located in `src/store/auth.js`:

```javascript
const { user, workspace, isAuthenticated, login, logout } = useAuthStore()
```

**State:**
- `user` - Current user object
- `workspace` - User's workspace
- `accessToken` - JWT access token
- `refreshToken` - JWT refresh token
- `isAuthenticated` - Authentication status
- `isLoading` - Loading state

**Actions:**
- `login(email, password)` - Authenticate user
- `signup(data)` - Register new user
- `logout()` - Clear session
- `loadUser()` - Fetch user profile
- `updateUser(data)` - Update user in store
- `hasRole(roles)` - Check user role

## 🌐 API Integration

### Endpoint Structure

All API calls are centralized in `src/api/endpoints.js`:

```javascript
import { authAPI, userAPI, workspaceAPI } from './api/endpoints'

// Usage
await authAPI.login({ email, password })
await userAPI.getProfile()
await workspaceAPI.inviteMember({ email, role })
```

### Error Handling

- Toast notifications for user feedback
- Automatic 401 handling with token refresh
- Graceful error messages from backend

## 📱 Responsive Design

The application is fully responsive:
- **Mobile**: Collapsible sidebar, touch-friendly buttons
- **Tablet**: Optimized layouts
- **Desktop**: Full sidebar navigation

## 🚦 Role-Based Access Control

### Role Hierarchy

1. **Manager**
   - Full workspace access
   - Invite and manage members
   - Update workspace settings
   - Change member roles
   - Suspend/remove members

2. **Analyst**
   - View workspace members
   - Access shared dashboards
   - Create reports (Sprint 2)

3. **Executive**
   - View workspace members
   - View dashboards (read-only)

### Route Protection

Routes automatically redirect based on role:
```javascript
// Manager → /dashboard/workspace
// Analyst → /dashboard
// Executive → /dashboard
```

## 🎉 Production Build

### Build for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deployment Checklist

- [ ] Update `VITE_API_BASE_URL` to production API
- [ ] Update `VITE_FRONTEND_URL` to production domain
- [ ] Test all authentication flows
- [ ] Verify role-based access control
- [ ] Test responsive design on all devices
- [ ] Check email verification links
- [ ] Test invitation flow end-to-end

## 🔧 Environment Variables

```env
# Required
VITE_API_BASE_URL=http://127.0.0.1:8000

# Optional (defaults shown)
VITE_FRONTEND_URL=http://localhost:5173
```

## 🐛 Troubleshooting

### Common Issues

**1. CORS Errors**
- Ensure backend CORS settings allow frontend origin
- Check `config/settings.py` for `CORS_ALLOWED_ORIGINS`

**2. 401 Unauthorized**
- Clear localStorage and login again
- Check if access token is expired
- Verify backend is running

**3. API Not Found (404)**
- Verify `VITE_API_BASE_URL` is correct
- Check backend server is running on port 8000

**4. Email Not Sending**
- Check backend email configuration
- Verify SMTP settings in backend

**5. Invitation Links Not Working**
- Ensure `VITE_FRONTEND_URL` matches actual frontend URL
- Check invitation token expiration (48 hours)

## 📚 Next Steps (Sprint 2)

- Voice query interface
- Dashboard creation and visualization
- Data source integration
- Real-time analytics
- Advanced role permissions
- Audit logging

## 🤝 Contributing

When adding new features:
1. Follow the existing component structure
2. Use TailwindCSS for styling
3. Add proper error handling
4. Include loading states
5. Make components responsive
6. Add toast notifications for user feedback

## 📄 License

This project is part of the BI Voice Agent system.

---

**Built with ❤️ using React, Vite, and TailwindCSS**

