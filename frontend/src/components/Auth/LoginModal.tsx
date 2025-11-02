import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const LoginModal: React.FC<LoginModalProps> = ({ isOpen, onClose }) => {
  const { login, register, error, isLoading, clearError } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);
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
    } else {
      success = await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name
      });
    }

    if (success) {
      onClose();
      setFormData({
        username: '',
        password: '',
        email: '',
        full_name: '',
        confirmPassword: ''
      });
    }
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 newspaper-bg border-4 border-black">
        {/* Header */}
        <div className="border-b-2 border-black p-4">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-black text-black uppercase tracking-wide font-serif">
              📰 {isLoginMode ? 'Reader Login' : 'New Subscription'}
            </h2>
            <button
              onClick={onClose}
              className="text-black hover:bg-gray-100 p-2 border-2 border-black font-black text-xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Error Messages */}
          {(error || validationErrors.length > 0) && (
            <div className="mb-4 p-3 bg-red-100 border-2 border-red-400 rounded">
              {error && (
                <p className="text-red-700 font-semibold font-serif mb-2">❌ {error}</p>
              )}
              {validationErrors.map((err, index) => (
                <p key={index} className="text-red-600 text-sm font-serif">• {err}</p>
              ))}
            </div>
          )}

          {/* Username */}
          <div className="mb-4">
            <label className="block text-black font-bold mb-2 font-serif uppercase text-sm">
              📝 Username
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
                <label className="block text-black font-bold mb-2 font-serif uppercase text-sm">
                  📧 Email Address
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
                <label className="block text-black font-bold mb-2 font-serif uppercase text-sm">
                  👤 Full Name
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
            <label className="block text-black font-bold mb-2 font-serif uppercase text-sm">
              🔒 Password
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
              <label className="block text-black font-bold mb-2 font-serif uppercase text-sm">
                🔒 Confirm Password
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
            className="w-full bg-black text-white py-3 px-6 font-black uppercase tracking-wide border-2 border-black hover:bg-gray-800 transition-colors disabled:bg-gray-500 font-serif"
          >
            {isLoading ? '⏳ PROCESSING...' : (isLoginMode ? '🔓 LOGIN' : '📝 REGISTER')}
          </button>

          {/* Mode Switch */}
          <div className="mt-4 text-center">
            <p className="text-black font-serif">
              {isLoginMode ? "Don't have an account?" : "Already have an account?"}
            </p>
            <button
              type="button"
              onClick={switchMode}
              className="text-black font-bold underline hover:no-underline font-serif uppercase text-sm mt-1"
            >
              {isLoginMode ? '📝 CREATE NEW SUBSCRIPTION' : '🔓 LOGIN TO EXISTING ACCOUNT'}
            </button>
          </div>
        </form>

        {/* Footer */}
        <div className="border-t-2 border-black p-3 bg-gray-100 text-center">
          <p className="text-xs font-bold text-black uppercase font-serif">
            🔒 SECURE • PRIVATE • TRUSTED
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;