import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginModal from '../Auth/LoginModal';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [loginMode, setLoginMode] = useState<'admin' | 'user'>('user');

  const handleAdminAccess = () => {
    setLoginMode('admin');
    setShowLoginModal(true);
  };

  const handleUserAccess = () => {
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-[#f4e4c1] flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        {/* Newspaper Header */}
        <div className="text-center mb-12">
          <div className="border-t-4 border-b-4 border-black py-6">
            <h1 className="text-6xl md:text-8xl font-black text-black mb-3 tracking-tight font-serif">
              THE INFOSPHERE HERALD
            </h1>
            <div className="flex justify-center items-center space-x-8 text-sm font-semibold text-black">
              <span>ESTABLISHED 2025</span>
              <span className="border-l border-r border-black px-4">CIVIC INTELLIGENCE DAILY</span>
              <span>{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
            </div>
          </div>
          <div className="mt-6">
            <p className="text-2xl font-serif italic text-black">
              "AI-Powered Truth in the Digital Age"
            </p>
          </div>
        </div>

        {/* Role Selection Cards */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Admin Card */}
          <div className="border-4 border-black bg-white p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] transition-all">
            <div className="text-center">
              <div className="text-6xl mb-4">👨‍💼</div>
              <h2 className="text-3xl font-black text-black mb-4 font-serif border-b-2 border-black pb-2">
                ADMIN ACCESS
              </h2>
              <p className="text-lg mb-6 font-serif text-gray-700">
                Manage reports, review submissions, and oversee platform operations
              </p>
              <ul className="text-left mb-8 space-y-2 text-sm font-serif">
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  View all submitted reports
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Approve or reject submissions
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Access analytics dashboard
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Manage platform content
                </li>
              </ul>
              <button
                onClick={handleAdminAccess}
                className="w-full bg-black text-white px-6 py-4 font-black text-lg border-4 border-black hover:bg-red-600 hover:border-red-600 transition-colors"
              >
                ADMIN LOGIN
              </button>
              <p className="text-xs mt-4 text-gray-600 font-serif">
                Username/Password or Google OAuth
              </p>
            </div>
          </div>

          {/* User Card */}
          <div className="border-4 border-black bg-white p-8 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] transition-all">
            <div className="text-center">
              <div className="text-6xl mb-4">📰</div>
              <h2 className="text-3xl font-black text-black mb-4 font-serif border-b-2 border-black pb-2">
                USER ACCESS
              </h2>
              <p className="text-lg mb-6 font-serif text-gray-700">
                Browse news, submit stories, and engage with civic intelligence
              </p>
              <ul className="text-left mb-8 space-y-2 text-sm font-serif">
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Read live news updates
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Submit issue reports
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Verify media authenticity
                </li>
                <li className="flex items-center">
                  <span className="mr-2">✓</span>
                  Track policy changes
                </li>
              </ul>
              <button
                onClick={handleUserAccess}
                className="w-full bg-black text-white px-6 py-4 font-black text-lg border-4 border-black hover:bg-blue-600 hover:border-blue-600 transition-colors"
              >
                ENTER AS GUEST
              </button>
              <p className="text-xs mt-4 text-gray-600 font-serif">
                No registration required
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-sm font-serif text-gray-700">
          <p className="border-t-2 border-black pt-4">
            © 2025 The Infosphere Herald • Powered by AI • Trusted by Citizens
          </p>
        </div>
      </div>

      {/* Login Modal */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)}
        initialMode={loginMode}
      />
    </div>
  );
};

export default LandingPage;
