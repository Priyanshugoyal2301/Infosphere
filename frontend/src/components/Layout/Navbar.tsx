import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoginModal from '../Auth/LoginModal';
import ProfileModal from '../Auth/ProfileModal';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  const navLinks = [
    { path: '/', label: 'NEWSROOM', icon: '🏠' },
    { path: '/news', label: 'LIVE NEWS', icon: '📡' },
    { path: '/report', label: 'SUBMIT STORY', icon: '📝' },
    { path: '/analytics', label: 'ANALYTICS', icon: '📊' },
    { path: '/verify', label: 'FACT CHECK', icon: '🔍' },
    { path: '/policy', label: 'POLICY DESK', icon: '📋' },
  ];

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="border-t-4 border-b-4 border-black newspaper-bg relative z-30 mt-8" style={{background: '#e8dcc8'}}>
      <div className="container mx-auto px-4">
        {/* Main Header */}
        <div className="border-b-2 border-black py-2">
          <div className="text-center">
            <div className="newspaper-title text-3xl font-black text-black tracking-wider">
              📰 THE INFOSPHERE HERALD
            </div>
            <div className="text-xs font-bold text-black uppercase tracking-widest">
              "ALL THE NEWS THAT'S FIT TO VERIFY"
            </div>
          </div>
        </div>
        
        <div className="flex justify-between items-center h-12">
          {/* Date and Edition */}
          <div className="flex items-center space-x-4">
            <div className="text-xs font-bold text-black uppercase">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </div>
            <div className="text-xs font-bold text-black uppercase border-l border-black pl-4">
              DIGITAL EDITION
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center space-x-1 px-3 py-1 text-xs font-black uppercase tracking-wide transition-all duration-200 border-2 border-transparent ${
                  isActive(link.path)
                    ? 'bg-black text-white border-black'
                    : 'text-black hover:bg-gray-100 hover:border-black'
                }`}
              >
                <span className="text-sm">{link.icon}</span>
                <span>{link.label}</span>
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="text-black hover:bg-gray-100 p-2 border-2 border-black font-black">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-3">
            {isAuthenticated && user ? (
              <>
                <button
                  onClick={() => setShowProfileModal(true)}
                  className="flex items-center space-x-2 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  <span>Welcome, {user.username}</span>
                  <span className="text-sm">👤</span>
                </button>
                <div className="w-8 h-8 bg-black border-2 border-black flex items-center justify-center text-white font-black text-xs">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <button
                  onClick={logout}
                  className="text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  LOGOUT
                </button>
              </>
            ) : (
              <>
                <div className="text-xs font-bold text-black uppercase">READER ACCESS</div>
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="w-8 h-8 bg-black border-2 border-black flex items-center justify-center text-white font-black text-xs hover:bg-gray-800 transition-colors"
                >
                  🔓
                </button>
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  LOGIN
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Navigation (Hidden by default) */}
        <div className="md:hidden border-t-2 border-black py-4">
          <div className="space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={`flex items-center space-x-3 px-4 py-3 text-sm font-black uppercase tracking-wide transition-all duration-200 border-2 ${
                  isActive(link.path)
                    ? 'bg-black text-white border-black'
                    : 'text-black border-transparent hover:bg-gray-100 hover:border-black'
                }`}
              >
                <span className="text-lg">{link.icon}</span>
                <span>{link.label}</span>
              </Link>
            ))}
            
            {/* Mobile User Section */}
            <div className="border-t-2 border-black pt-4 mt-4">
              {isAuthenticated && user ? (
                <div className="px-4 space-y-2">
                  <button
                    onClick={() => setShowProfileModal(true)}
                    className="w-full text-left px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                  >
                    👤 Welcome, {user.username} - VIEW PROFILE
                  </button>
                  <button
                    onClick={logout}
                    className="w-full text-left px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                  >
                    🔓 LOGOUT
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="w-full text-left px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                >
                  🔓 LOGIN / REGISTER
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Login Modal */}
      <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />
      
      {/* Profile Modal */}
      <ProfileModal isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
    </nav>
  );
};

export default Navbar;