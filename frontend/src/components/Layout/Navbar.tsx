import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { useReader } from "../../contexts/ReaderContext";
import LoginModal from "../Auth/LoginModal";
import ProfileModal from "../Auth/ProfileModal";
import {
  Home,
  Radio,
  Flag,
  FileText,
  BarChart3,
  Shield,
  Briefcase,
  User,
  LogOut,
  Menu,
  Newspaper,
  Microscope,
  Book,
} from "lucide-react";

const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, userRole, isAuthenticated, logout } = useAuth();
  const { currentArticle } = useReader();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);

  // Role-based navigation links
  const baseLinks = [
    { path: "/dashboard", label: "NEWSROOM", icon: Home },
    { path: "/news", label: "LIVE NEWS", icon: Radio },
    { path: "/flagged-news", label: "FLAGGED NEWS", icon: Flag },
  ];

  const roleSpecificLinks =
    userRole === "admin"
      ? [{ path: "/admin/reports", label: "VIEW REPORTS", icon: FileText }]
      : [{ path: "/report", label: "SUBMIT STORY", icon: FileText }];

  const commonLinks = [
    { path: "/analytics", label: "ANALYTICS", icon: BarChart3 },
    {
      path: "/verify",
      label: userRole === "admin" ? "FACTS REPORTED" : "FACT CHECK",
      icon: Shield,
    },
    {
      path: "/advanced-verification",
      label: "ADVANCED VERIFY",
      icon: Microscope,
    },
    { path: "/policy", label: "POLICY DESK", icon: Briefcase },
  ];

  // Show all links when on dashboard, show basic links on landing page
  const navLinks =
    location.pathname === "/"
      ? []
      : [...baseLinks, ...roleSpecificLinks, ...commonLinks];

  const isActive = (path: string) => {
    if (path === "/dashboard") return location.pathname === "/dashboard";
    return location.pathname.startsWith(path);
  };

  // Don't show navbar on landing page
  if (location.pathname === "/") {
    return null;
  }

  return (
    <nav
      className="border-t-4 border-b-4 border-black newspaper-bg relative z-10 mt-6 sm:mt-8 overflow-x-hidden"
      style={{ background: "#e8dcc8" }}
    >
      <div className="max-w-full mx-auto px-2 sm:px-4">
        {/* Main Header */}
        <div className="border-b-2 border-black py-2">
          <div className="text-center">
            <div className="newspaper-title text-xl sm:text-2xl md:text-3xl font-black text-black tracking-wider flex items-center justify-center gap-2 flex-wrap">
              <Newspaper
                size={40}
                strokeWidth={2.5}
                className="flex-shrink-0"
              />
              <span className="whitespace-nowrap">THE INFOSPHERE HERALD</span>
            </div>
            <div className="text-xs font-bold text-black uppercase tracking-widest">
              "ALL THE NEWS THAT'S FIT TO VERIFY"
            </div>
          </div>
        </div>

        <div className="flex flex-wrap justify-between items-center min-h-12 gap-2 py-2">
          {/* Date and Edition */}
          <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
            <div className="text-xs font-bold text-black uppercase hidden lg:block">
              {new Date().toLocaleDateString("en-US", {
                weekday: "long",
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </div>
            <div className="text-xs font-bold text-black uppercase lg:hidden">
              {new Date().toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </div>
            <div className="text-xs font-bold text-black uppercase border-l border-black pl-2 sm:pl-4">
              DIGITAL EDITION
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex flex-wrap gap-1 justify-center flex-1 max-w-2xl">
            {navLinks.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-1 lg:space-x-2 px-2 lg:px-3 py-1 text-xs font-black uppercase tracking-wide transition-all duration-200 border-2 border-transparent whitespace-nowrap ${
                    isActive(link.path)
                      ? "bg-black text-white border-black"
                      : "text-black hover:bg-gray-100 hover:border-black"
                  }`}
                >
                  <IconComponent size={20} strokeWidth={2.5} />
                  <span className="hidden lg:inline">{link.label}</span>
                  <span className="lg:hidden">{link.label.split(" ")[0]}</span>
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
          <div className="hidden md:flex items-center space-x-1 lg:space-x-2 flex-shrink-0">
            {/* Reader Access Button */}
            <button
              onClick={() => {
                if (!currentArticle) {
                  alert(
                    'Select an article first by clicking "📖 READER MODE" on any article'
                  );
                }
              }}
              className={`flex items-center gap-1 text-xs font-bold uppercase px-2 py-1.5 border-2 transition-colors whitespace-nowrap ${
                currentArticle
                  ? "text-white bg-blue-600 border-blue-700 hover:bg-blue-700 cursor-default"
                  : "text-black bg-blue-100 border-blue-600 hover:bg-blue-50 cursor-pointer"
              }`}
              title={
                currentArticle
                  ? `Reading: ${currentArticle.title.substring(0, 50)}...`
                  : "Select an article to use Reader Mode"
              }
            >
              <Book size={16} strokeWidth={2.5} />
              <span className="hidden xl:inline">
                {currentArticle ? "READING..." : "READER ACCESS"}
              </span>
            </button>

            {isAuthenticated && user ? (
              <>
                {userRole && (
                  <span className="text-xs font-black text-white bg-black px-2 py-1 border-2 border-black uppercase flex items-center gap-1 whitespace-nowrap">
                    {userRole === "admin" ? (
                      <>
                        <Briefcase size={16} strokeWidth={2.5} />{" "}
                        <span className="hidden xl:inline">ADMIN</span>
                      </>
                    ) : (
                      <>
                        <Newspaper size={16} strokeWidth={2.5} />{" "}
                        <span className="hidden xl:inline">READER</span>
                      </>
                    )}
                  </span>
                )}
                <button
                  onClick={() => setShowProfileModal(true)}
                  className="flex items-center space-x-1 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors"
                  title={`Welcome, ${user.username}`}
                >
                  <span className="hidden xl:inline">
                    Welcome, {user.username}
                  </span>
                  <User size={18} strokeWidth={2.5} />
                </button>
                <div className="w-8 h-8 bg-black border-2 border-black flex items-center justify-center text-white font-black text-xs flex-shrink-0">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <button
                  onClick={logout}
                  className="flex items-center gap-1 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors whitespace-nowrap"
                >
                  <LogOut size={14} strokeWidth={2.5} />
                  <span className="hidden lg:inline">LOGOUT</span>
                </button>
              </>
            ) : (
              <>
                <div className="text-xs font-bold text-black uppercase hidden lg:block">
                  VISITOR
                </div>
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="w-8 h-8 bg-black border-2 border-black flex items-center justify-center text-white font-black text-xs hover:bg-gray-800 transition-colors flex-shrink-0"
                >
                  <User size={16} strokeWidth={2.5} />
                </button>
                <button
                  onClick={() => setShowLoginModal(true)}
                  className="flex items-center gap-1 text-xs font-bold text-black uppercase hover:bg-gray-100 px-2 py-1 border-2 border-black transition-colors whitespace-nowrap"
                >
                  <LogOut size={14} strokeWidth={2.5} className="rotate-180" />
                  <span className="hidden lg:inline">LOGIN</span>
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mobile Navigation (Hidden by default) */}
        <div className="md:hidden border-t-2 border-black py-4">
          <div className="space-y-2">
            {/* Reader Access Button - Mobile */}
            <button
              onClick={() => {
                if (!currentArticle) {
                  alert(
                    'Select an article first by clicking "📖 READER MODE" on any article'
                  );
                }
              }}
              className={`w-full flex items-center gap-2 px-4 py-3 text-sm font-black uppercase border-2 transition-colors ${
                currentArticle
                  ? "text-white bg-blue-600 border-blue-700 hover:bg-blue-700"
                  : "text-blue-700 bg-blue-50 border-blue-600 hover:bg-blue-100"
              }`}
            >
              <Book size={18} strokeWidth={2.5} />
              {currentArticle ? "READING..." : "READER ACCESS MODE"}
            </button>

            {navLinks.map((link) => {
              const IconComponent = link.icon;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`flex items-center space-x-3 px-4 py-3 text-sm font-black uppercase tracking-wide transition-all duration-200 border-2 ${
                    isActive(link.path)
                      ? "bg-black text-white border-black"
                      : "text-black border-transparent hover:bg-gray-100 hover:border-black"
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
      <LoginModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
      />

      {/* Profile Modal */}
      <ProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
      />
    </nav>
  );
};

export default Navbar;
