import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Mail, UserCircle, X, AlertCircle, Loader, LogIn, UserPlus, Shield, Briefcase, Newspaper } from 'lucide-react';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: 'admin' | 'user';
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose, initialMode = 'user' }) => {
  const { login, register, loginAsAdmin, error, isLoading, clearError } = useAuth();
  const navigate = useNavigate();
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [isAdminMode] = useState(initialMode === 'admin');
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    full_name: '',
    confirmPassword: ''
  });
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const validateForm = () => {
    const errors: string[] = [];

    if (formData.username.length < 3) {
      errors.push('Username must be at least 3 characters long');
    }

    if (formData.password.length < 6) {
      errors.push('Password must be at least 6 characters long');
    }

    if (!isLoginMode) {
      if (!formData.email || !formData.email.includes('@')) {
        errors.push('Please enter a valid email address');
      }

      if (formData.full_name.length < 2) {
        errors.push('Please enter your full name');
      }

      if (formData.password !== formData.confirmPassword) {
        errors.push('Passwords do not match');
      }
    }

    setValidationErrors(errors);
    return errors.length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationErrors([]);

    if (!validateForm()) {
      return;
    }

    let success = false;
    
    if (isLoginMode) {
      success = await login(formData.username, formData.password);
      // Set role based on mode after successful login
      if (success && isAdminMode) {
        localStorage.setItem('user_role', 'admin');
      } else if (success) {
        localStorage.setItem('user_role', 'user');
      }
    } else {
      success = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      });
      // Set role based on mode after successful registration
      if (success && isAdminMode) {
        localStorage.setItem('user_role', 'admin');
      } else if (success) {
        localStorage.setItem('user_role', 'user');
      }
    }

    if (success) {
      onClose();
      navigate('/dashboard');
      setFormData({
        username: '',
        password: '',
        email: '',
        full_name: '',
        confirmPassword: ''
      });
    }
  };

  const handleGoogleLogin = () => {
    loginAsAdmin();
    onClose();
    navigate('/dashboard');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const switchMode = () => {
    setIsLoginMode(!isLoginMode);
    clearError();
    setValidationErrors([]);
    setFormData({
      username: '',
      password: '',
      email: '',
      full_name: '',
      confirmPassword: ''
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl max-w-md w-full border-4 border-black my-8 relative z-[10000]">
        {/* Header */}
        <div className="border-b-2 border-black p-4 bg-white">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-black text-black uppercase tracking-wide font-serif flex items-center gap-2">
              {isAdminMode ? (
                <><Briefcase size={24} strokeWidth={2.5} /> Admin Access</>
              ) : (
                <><Newspaper size={24} strokeWidth={2.5} /> Reader Access</>
              )}
            </h2>
            <button
              onClick={onClose}
              className="text-black hover:bg-gray-100 p-2 border-2 border-black font-black"
            >
              <X size={20} strokeWidth={3} />
            </button>
          </div>
          <p className="text-xs mt-2 font-serif text-gray-700">
            {isLoginMode ? 'Sign in to your account' : 'Create a new account'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 bg-white">
          {/* Error Messages */}
          {(error || validationErrors.length > 0) && (
            <div className="mb-4 p-3 bg-red-100 border-2 border-red-400 rounded">
              {error && (
                <p className="text-red-700 font-semibold font-serif mb-2 flex items-center gap-2">
                  <AlertCircle size={16} strokeWidth={2.5} /> {error}
                </p>
              )}
              {validationErrors.map((err, index) => (
                <p key={index} className="text-red-600 text-sm font-serif">• {err}</p>
              ))}
            </div>
          )}

          {/* Username */}
          <div className="mb-4">
            <label className="block text-black font-bold mb-2 font-serif uppercase text-sm flex items-center gap-1">
              <User size={16} strokeWidth={2.5} /> Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border-2 border-black focus:outline-none focus:border-gray-600 font-serif"
              placeholder="Enter your username"
              required
            />
          </div>

          {/* Email (Register only) */}
          {!isLoginMode && (
            <>
              <div className="mb-4">
                <label className="block text-black font-bold mb-2 font-serif uppercase text-sm flex items-center gap-1">
                  <Mail size={16} strokeWidth={2.5} /> Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border-2 border-black focus:outline-none focus:border-gray-600 font-serif"
                  placeholder="Enter your email"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-black font-bold mb-2 font-serif uppercase text-sm flex items-center gap-1">
                  <UserCircle size={16} strokeWidth={2.5} /> Full Name
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border-2 border-black focus:outline-none focus:border-gray-600 font-serif"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            </>
          )}

          {/* Password */}
          <div className="mb-4">
            <label className="block text-black font-bold mb-2 font-serif uppercase text-sm flex items-center gap-1">
              <Lock size={16} strokeWidth={2.5} /> Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border-2 border-black focus:outline-none focus:border-gray-600 font-serif"
              placeholder="Enter your password"
              required
            />
          </div>

          {/* Confirm Password (Register only) */}
          {!isLoginMode && (
            <div className="mb-6">
              <label className="block text-black font-bold mb-2 font-serif uppercase text-sm flex items-center gap-1">
                <Lock size={16} strokeWidth={2.5} /> Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border-2 border-black focus:outline-none focus:border-gray-600 font-serif"
                placeholder="Confirm your password"
                required
              />
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-black text-white py-3 px-6 font-black uppercase tracking-wide border-2 border-black hover:bg-gray-800 transition-colors disabled:bg-gray-500 font-serif flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <><Loader size={18} strokeWidth={2.5} className="animate-spin" /> PROCESSING...</>
            ) : isLoginMode ? (
              <><LogIn size={18} strokeWidth={2.5} /> LOGIN</>
            ) : (
              <><UserPlus size={18} strokeWidth={2.5} /> REGISTER</>
            )}
          </button>

          {/* Google Login Option */}
          <div className="mt-4">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t-2 border-black"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-black font-bold font-serif uppercase">OR</span>
              </div>
            </div>

            <button
              type="button"
              onClick={handleGoogleLogin}
              className="w-full mt-4 bg-white text-black py-3 px-6 font-black uppercase tracking-wide border-2 border-black hover:bg-gray-100 transition-colors font-serif flex items-center justify-center space-x-2"
            >
              <Shield size={18} strokeWidth={2.5} />
              <span>LOGIN WITH GOOGLE</span>
            </button>
          </div>

          {/* Mode Switch */}
          <div className="mt-4 text-center">
            <p className="text-black font-serif">
              {isLoginMode ? "Don't have an account?" : "Already have an account?"}
            </p>
            <button
              type="button"
              onClick={switchMode}
              className="text-black font-bold underline hover:no-underline font-serif uppercase text-sm mt-1 flex items-center gap-1 mx-auto"
            >
              {isLoginMode ? (
                <><UserPlus size={14} strokeWidth={2.5} /> CREATE NEW SUBSCRIPTION</>
              ) : (
                <><LogIn size={14} strokeWidth={2.5} /> LOGIN TO EXISTING ACCOUNT</>
              )}
            </button>
          </div>
        </form>

        {/* Footer */}
        <div className="border-t-2 border-black p-3 bg-white text-center">
          <p className="text-xs font-bold text-black uppercase font-serif flex items-center justify-center gap-2">
            <Lock size={14} strokeWidth={2.5} /> SECURE • PRIVATE • TRUSTED
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;