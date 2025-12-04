# Admin/User Role-Based Access System

## Overview
The Infosphere platform now features a comprehensive role-based access control system with two distinct user roles:
- **Admin**: Authenticated users with Google OAuth who can view and manage submitted reports
- **User**: Guest users who can submit stories and access all other platform features

## Features Implemented

### 1. Landing Page (`/`)
- **Location**: `frontend/src/components/Landing/LandingPage.tsx`
- **Purpose**: Role selection interface
- **Design**: Vintage newspaper aesthetic with two card options
- **Options**:
  - Admin Access: Google login required
  - User Access: Guest access (no registration)

### 2. Authentication System
- **Location**: `frontend/src/contexts/AuthContext.tsx`
- **Features**:
  - `userRole` state management ('admin' | 'user' | null)
  - `loginAsUser()`: Guest access for regular users
  - `loginAsAdmin()`: Google OAuth integration for admins
  - Role persistence in localStorage across sessions
  - Google token storage for admin authentication

### 3. Google OAuth Integration
- **Package**: `@react-oauth/google`
- **Configuration**: 
  - Wrapped app with `GoogleOAuthProvider` in `index.tsx`
  - Client ID from environment variable `REACT_APP_GOOGLE_CLIENT_ID`
- **Authentication Flow**:
  1. Admin clicks "Login with Google"
  2. Google OAuth popup/redirect
  3. Fetch user info from Google API
  4. Store user data and admin role
  5. Redirect to dashboard

### 4. Role-Based Navigation
- **Location**: `frontend/src/components/Layout/Navbar.tsx`
- **Features**:
  - Dynamic navigation links based on userRole
  - Admin sees: "VIEW REPORTS" instead of "SUBMIT STORY"
  - User sees: "SUBMIT STORY" for issue reporting
  - Role badge display (👨‍💼 ADMIN or 📰 READER)
  - Hidden navbar on landing page
  - Logout functionality that clears role and tokens

### 5. Admin Dashboard - ViewReports
- **Location**: `frontend/src/components/Admin/ViewReports.tsx`
- **Route**: `/admin/reports` (admin only)
- **Features**:
  - View all submitted reports in table format
  - Filter by status (all, pending, approved, rejected)
  - Search by title, description, or category
  - Actions for pending reports:
    - ✓ APPROVE - Mark report as approved
    - ✗ REJECT - Mark report as rejected
    - 🗑 DELETE - Permanently remove report
  - Summary statistics cards (Total, Pending, Approved, Rejected)
  - Vintage newspaper table styling
  - Route protection: Redirects non-admins to dashboard

### 6. Backend API Endpoints
- **Location**: `backend/api/v1/endpoints/reports.py`
- **Endpoints**:
  - `GET /api/v1/admin/reports` - Fetch all reports (sorted by date)
  - `PUT /api/v1/admin/reports/{id}/approve` - Approve a report
  - `PUT /api/v1/admin/reports/{id}/reject` - Reject a report
  - `DELETE /api/v1/admin/reports/{id}` - Delete a report
  - `GET /api/v1/admin/reports/stats` - Get report statistics

### 7. Data Storage
- **Location**: `backend/data/reports.json`
- **Format**: JSON array of report objects
- **Schema**:
  ```json
  {
    "id": "rpt_001",
    "title": "Report title",
    "description": "Detailed description",
    "category": "Infrastructure|Public Safety|Environment|Public Property",
    "location": "Location details",
    "status": "pending|approved|rejected",
    "submitted_by": "username",
    "submitted_at": "ISO 8601 timestamp",
    "reviewed_at": "ISO 8601 timestamp (optional)"
  }
  ```
- **Sample Data**: 5 sample reports provided for testing

## Setup Instructions

### 1. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized JavaScript origins:
   - `http://localhost:3000` (development)
   - Your production domain (e.g., `https://infosphere-five.vercel.app`)
6. Add authorized redirect URIs:
   - `http://localhost:3000` (development)
   - Your production domain
7. Copy the Client ID

### 2. Frontend Environment Configuration
1. Open `frontend/.env`
2. Replace `YOUR_GOOGLE_CLIENT_ID_HERE` with your actual Google Client ID:
   ```
   REACT_APP_GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
   ```

### 3. Install Dependencies
```bash
cd frontend
npm install
```

### 4. Start Development Servers
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm start
```

### 5. Access the Application
1. Navigate to `http://localhost:3000`
2. You'll see the Landing Page with Admin/User selection
3. Choose your role:
   - **Admin**: Click "LOGIN WITH GOOGLE" → Authenticate → Access admin dashboard
   - **User**: Click "ENTER AS GUEST" → Access user dashboard

## User Flows

### Admin Flow
1. Landing Page → Click "LOGIN WITH GOOGLE"
2. Google OAuth popup → Authenticate with Google account
3. Redirect to `/dashboard` with admin role
4. Navbar shows: NEWSROOM | LIVE NEWS | VIEW REPORTS | ANALYTICS | FACT CHECK | POLICY DESK
5. Click "VIEW REPORTS" → Admin dashboard with all submitted reports
6. Filter, search, approve/reject/delete reports
7. Click "LOGOUT" → Return to landing page

### User Flow
1. Landing Page → Click "ENTER AS GUEST"
2. Redirect to `/dashboard` with user role
3. Navbar shows: NEWSROOM | LIVE NEWS | SUBMIT STORY | ANALYTICS | FACT CHECK | POLICY DESK
4. Click "SUBMIT STORY" → Report issue form
5. Access all other features (news, analytics, media verify, policy)
6. Click "LOGOUT" → Return to landing page

## Role Persistence
- User roles are stored in `localStorage` under key `user_role`
- Google tokens stored under key `google_token`
- Session persists across browser refreshes
- Cleared on logout

## Security Considerations
1. **Client-Side Only**: Current implementation is client-side for demo purposes
2. **Production Recommendations**:
   - Add backend JWT authentication
   - Verify Google tokens on backend
   - Implement proper RBAC middleware
   - Add admin user whitelist/database
   - Secure admin endpoints with authentication
   - Add rate limiting for API endpoints

## File Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Landing/
│   │   │   └── LandingPage.tsx       # Role selection page
│   │   ├── Admin/
│   │   │   └── ViewReports.tsx       # Admin dashboard
│   │   └── Layout/
│   │       └── Navbar.tsx            # Updated with role-based menu
│   ├── contexts/
│   │   └── AuthContext.tsx           # Auth + Role management
│   ├── App.tsx                        # Updated routes
│   └── index.tsx                      # Google OAuth provider wrapper
│
backend/
├── api/
│   └── v1/
│       └── endpoints/
│           └── reports.py             # Admin API endpoints
├── data/
│   └── reports.json                   # Reports data storage
└── main.py                            # Router registration
```

## Testing Checklist
- [ ] Landing page displays with two role cards
- [ ] Admin button triggers Google OAuth popup
- [ ] User button grants guest access immediately
- [ ] Admin role shows "VIEW REPORTS" in navbar
- [ ] User role shows "SUBMIT STORY" in navbar
- [ ] Admin can view all reports
- [ ] Admin can approve/reject/delete reports
- [ ] Reports filter by status correctly
- [ ] Search functionality works
- [ ] Role persists after page refresh
- [ ] Logout clears role and returns to landing page
- [ ] Non-admin redirected from `/admin/reports`

## Future Enhancements
1. Backend admin authentication validation
2. Admin user management (create/delete admin accounts)
3. Report comments/notes system
4. Email notifications for report status changes
5. Advanced analytics for admin (trends, categories, etc.)
6. Bulk actions (approve/reject multiple reports)
7. Export reports to CSV/PDF
8. Report priority/urgency levels
9. Automated report categorization using ML
10. Real-time notifications for new reports

## API Documentation

### Admin Reports Endpoints

#### GET /api/v1/admin/reports
Fetch all submitted reports
```bash
curl http://localhost:8000/api/v1/admin/reports
```
Response: Array of report objects

#### PUT /api/v1/admin/reports/{id}/approve
Approve a pending report
```bash
curl -X PUT http://localhost:8000/api/v1/admin/reports/rpt_001/approve
```
Response: `{"message": "Report approved successfully"}`

#### PUT /api/v1/admin/reports/{id}/reject
Reject a pending report
```bash
curl -X PUT http://localhost:8000/api/v1/admin/reports/rpt_001/reject
```
Response: `{"message": "Report rejected successfully"}`

#### DELETE /api/v1/admin/reports/{id}
Delete a report permanently
```bash
curl -X DELETE http://localhost:8000/api/v1/admin/reports/rpt_001
```
Response: `{"message": "Report deleted successfully"}`

#### GET /api/v1/admin/reports/stats
Get report statistics
```bash
curl http://localhost:8000/api/v1/admin/reports/stats
```
Response: 
```json
{
  "total": 5,
  "pending": 3,
  "approved": 1,
  "rejected": 1
}
```

## Troubleshooting

### Google OAuth Not Working
- Check Client ID is correctly set in `frontend/.env`
- Verify authorized origins/redirect URIs in Google Console
- Ensure app is wrapped with `GoogleOAuthProvider`
- Check browser console for errors

### Reports Not Loading
- Verify backend is running on port 8000
- Check `REACT_APP_API_URL` in frontend/.env
- Ensure `reports.json` exists in `backend/data/`
- Check backend console for endpoint registration

### Role Not Persisting
- Check browser localStorage has `user_role` key
- Verify `AuthContext` is reading from localStorage on mount
- Clear localStorage and try again

### Navbar Not Updating
- Confirm `userRole` is being set correctly in AuthContext
- Check Navbar is consuming `userRole` from `useAuth()` hook
- Verify conditional rendering logic

## Credits
- Design: Vintage newspaper aesthetic maintained throughout
- Authentication: Google OAuth via `@react-oauth/google`
- Framework: React 19.2.0 + TypeScript + React Router
- Backend: FastAPI with JSON file storage
