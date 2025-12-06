import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Check if Google OAuth is available
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  created_at: string;
  last_login?: string;
}

type UserRole = 'admin' | 'user' | null;

interface AuthContextType {
  user: User | null;
  userRole: UserRole;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (userData: RegisterData) => Promise<boolean>;
  logout: () => void;
  loginAsAdmin: () => void;
  loginWithGoogle: (tokenResponse: any) => Promise<void>;
  error: string | null;
  clearError: () => void;
  refreshProfile: () => Promise<void>;
  updateProfile: (profileData: { full_name: string; email: string }) => Promise<boolean>;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [userRole, setUserRole] = useState<UserRole>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = user !== null;

  // Check for existing session on app load
  useEffect(() => {
    const checkSession = async () => {
      const token = localStorage.getItem('session_token');
      const storedRole = localStorage.getItem('user_role') as UserRole;
      
      if (storedRole) {
        setUserRole(storedRole);
      }
      
      if (token) {
        try {
          const response = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Invalid token, remove it
            localStorage.removeItem('session_token');
          }
        } catch (error) {
          console.error('Session check failed:', error);
          localStorage.removeItem('session_token');
        }
      }
      setIsLoading(false);
    };

    checkSession();
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
        localStorage.setItem('session_token', data.session_token);
        
        // Set role from localStorage if available
        const storedRole = localStorage.getItem('user_role') as UserRole;
        if (storedRole) {
          setUserRole(storedRole);
        }
        
        setIsLoading(false);
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed');
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
      setIsLoading(false);
      return false;
    }
  };

  const register = async (userData: RegisterData): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        // After successful registration, automatically log in
        const loginSuccess = await login(userData.username, userData.password);
        setIsLoading(false);
        return loginSuccess;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Registration failed');
        setIsLoading(false);
        return false;
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('Network error. Please try again.');
      setIsLoading(false);
      return false;
    }
  };

  const logout = async () => {
    const token = localStorage.getItem('session_token');
    
    if (token) {
      try {
        await fetch('http://localhost:8000/api/v1/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      }
    }

    setUser(null);
    setUserRole(null);
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('google_token');
    setError(null);
  };

  // Login with Google OAuth token
  const loginWithGoogle = async (tokenResponse: any) => {
    try {
      setIsLoading(true);
      // Fetch user info from Google
      const userInfoResponse = await fetch(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        }
      );

      if (userInfoResponse.ok) {
        const googleUser = await userInfoResponse.json();
        
        const adminUser: User = {
          id: googleUser.sub,
          username: googleUser.email.split('@')[0],
          email: googleUser.email,
          full_name: googleUser.name,
          created_at: new Date().toISOString()
        };

        setUser(adminUser);
        setUserRole('admin');
        localStorage.setItem('user_role', 'admin');
        localStorage.setItem('google_token', tokenResponse.access_token);
        setError(null);
      } else {
        setError('Failed to fetch Google user info');
      }
    } catch (error) {
      console.error('Google user info fetch error:', error);
      setError('Failed to authenticate with Google');
    } finally {
      setIsLoading(false);
    }
  };

  // Admin access with fallback
  const loginAsAdmin = () => {
    if (!GOOGLE_CLIENT_ID) {
      // Fallback: If Google OAuth not configured, use mock admin login
      console.log('Google OAuth not configured, using fallback admin login');
      const adminUser: User = {
        id: 'admin-local',
        username: 'admin',
        email: 'admin@infosphere.local',
        full_name: 'Local Admin',
        created_at: new Date().toISOString()
      };
      setUser(adminUser);
      setUserRole('admin');
      localStorage.setItem('user_role', 'admin');
      setError(null);
    } else {
      // Google OAuth is configured - component should handle Google login button
      console.log('Google OAuth configured - use Google login button');
    }
  };

  const clearError = () => {
    setError(null);
  };

  const refreshProfile = async (): Promise<void> => {
    const token = localStorage.getItem('session_token');
    if (!token) return;

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const profileData = await response.json();
        setUser(profileData);
      }
    } catch (error) {
      console.error('Failed to refresh profile:', error);
    }
  };

  const updateProfile = async (profileData: { full_name: string; email: string }): Promise<boolean> => {
    const token = localStorage.getItem('session_token');
    if (!token) return false;

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (response.ok) {
        const updatedUser = await response.json();
        setUser(updatedUser);
        return true;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update profile');
        return false;
      }
    } catch (error) {
      console.error('Profile update error:', error);
      setError('Network error. Please try again.');
      return false;
    }
  };

  const value: AuthContextType = {
    user,
    userRole,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    loginAsAdmin,
    loginWithGoogle,
    error,
    clearError,
    refreshProfile,
    updateProfile,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};