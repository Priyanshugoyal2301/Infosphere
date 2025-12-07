import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoginModal from '../Auth/LoginModal';
import ProfileModal from '../Auth/ProfileModal';
import { Home, Radio, Flag, FileText, BarChart3, Shield, Briefcase, User, LogOut, Menu, Newspaper } from 'lucide-react';

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, userRole, isAuthenticated, logout } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  // Role-based navigation links
  const baseLinks = [
    { path: '/dashboard', label: 'NEWSROOM', icon: Home },
    { path: '/news', label: 'LIVE NEWS', icon: Radio },
    { path: '/flagged-news', label: 'FLAGGED NEWS', icon: Flag },
  ];

  const roleSpecificLinks = userRole === 'admin' 
    ? [{ path: '/admin/reports', label: 'VIEW REPORTS', icon: FileText }]
    : [{ path: '/report', label: 'SUBMIT STORY', icon: FileText }];

  const commonLinks = [
    { path: '/analytics', label: 'ANALYTICS', icon: BarChart3 },
    { path: '/verify', label: userRole === 'admin' ? 'FACTS REPORTED' : 'FACT CHECK', icon: Shield },
    { path: '/policy', label: 'POLICY DESK', icon: Briefcase },
  ];

  // Show all links when on dashboard, show basic links on landing page
  const navLinks = location.pathname === '/' 
    ? []
    : [...baseLinks, ...roleSpecificLinks, ...commonLinks];

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === '/dashboard';
    return location.pathname.startsWith(path);
  };

  // Don't show navbar on landing page
  if (location.pathname === '/') {
    return null;
  }

  return (
    <nav className="border-t-4 border-b-4 border-black newspaper-bg relative z-40 mt-8" style={{background: '#e8dcc8'}}>
      <div className="container mx-auto px-4">
        {/* Main Header */}
        <div className="border-b-2 border-black py-2">
          <div className="text-center">
            <div className="newspaper-title text-3xl font-black text-black tracking-wider flex items-center justify-center gap-2">
              <Newspaper size={32} strokeWidth={2.5} />
              THE INFOSPHERE HERALD
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
            {navLinks.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1 px-3 py-1 text-xs font-black uppercase tracking-wide transition-all duration-200 border-2 border-transparent ${
                    isActive(link.path)
                      ? 'bg-black text-white border-black'
                      : 'text-black hover:bg-gray-100 hover:border-black'
                  }`}
                >
                  <IconComponent size={16} strokeWidth={2.5} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button className="text-black hover:bg-gray-100 p-2 border-2 border-black font-black">
              <Menu size={24} strokeWidth={3} />
            </button>
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-3">
            {isAuthenticated && user ? (
              <>
                {userRole && (
                  <span className="text-xs font-black text-white bg-black px-3 py-1 border-2 border-black uppercase flex items-center gap-1">
                    {userRole === 'admin' ? (
                      <><Briefcase size={14} strokeWidth={2.5} /> ADMIN</>
                    ) : (
                      <><Newspaper size={14} strokeWidth={2.5} /> READER</>
                    )}
                  </span>
                )}
                <button
                  onClick={() => setShowProfileModal(true)}
                  className="flex items-center space-x-2 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  <span>Welcome, {user.username}</span>
                  <User size={14} strokeWidth={2.5} />
                </button>
                <div className="w-8 h-8 bg-black border-2 border-black flex items-center justify-center text-white font-black text-xs">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <button
                  onClick={logout}
                  className="flex items-center gap-1 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  <LogOut size={14} strokeWidth={2.5} />
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
                  <User size={16} strokeWidth={2.5} />
                </button>
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="flex items-center gap-1 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                >
                  <LogOut size={14} strokeWidth={2.5} className="rotate-180" />
                  LOGIN
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Navigation (Hidden by default) */}
        <div className="md:hidden border-t-2 border-black py-4">
          <div className="space-y-2">
            {navLinks.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-3 px-4 py-3 text-sm font-black uppercase tracking-wide transition-all duration-200 border-2 ${
                    isActive(link.path)
                      ? 'bg-black text-white border-black'
                      : 'text-black border-transparent hover:bg-gray-100 hover:border-black'
                  }`}
                >
                  <IconComponent size={20} strokeWidth={2.5} />
                  <span>{link.label}</span>
                </Link>
              );
            })}
            
            {/* Mobile User Section */}
            <div className="border-t-2 border-black pt-4 mt-4">
              {isAuthenticated && user ? (
                <div className="px-4 space-y-2">
                  <button
                    onClick={() => setShowProfileModal(true)}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                  >
                    <User size={18} strokeWidth={2.5} />
                    Welcome, {user.username} - VIEW PROFILE
                  </button>
                  <button
                    onClick={logout}
                    className="w-full flex items-center gap-2 px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                  >
                    <LogOut size={18} strokeWidth={2.5} />
                    LOGOUT
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="w-full flex items-center gap-2 px-4 py-3 text-sm font-black uppercase text-black border-2 border-black hover:bg-gray-100 transition-colors"
                >
                  <LogOut size={18} strokeWidth={2.5} className="rotate-180" />
                  LOGIN / REGISTER
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