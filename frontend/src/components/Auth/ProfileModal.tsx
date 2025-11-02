import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name: string;
  created_at: string;
  last_login: string;
  is_active: boolean;
}

const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    full_name: '',
    email: '',
  });

  useEffect(() => {
    if (isOpen && user) {
      fetchProfile();
    }
  }, [isOpen, user]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('session_token');
      const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const profileData = await response.json();
        setProfile(profileData);
        setEditForm({
          full_name: profileData.full_name,
          email: profileData.email,
        });
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('session_token');
      const response = await fetch('http://localhost:8000/api/v1/auth/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(editForm),
      });

      if (response.ok) {
        const updatedProfile = await response.json();
        setProfile(updatedProfile);
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white border-4 border-black newspaper-bg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="border-b-4 border-black bg-white p-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="newspaper-title text-2xl font-black text-black tracking-wider">
                📰 USER PROFILE
              </h2>
              <div className="text-xs font-bold text-black uppercase tracking-widest mt-1">
                PERSONAL DETAILS & ACCOUNT INFORMATION
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-2xl font-black text-black hover:bg-gray-100 w-8 h-8 flex items-center justify-center border-2 border-black"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading ? (
            <div className="text-center py-8">
              <div className="text-lg font-bold text-black uppercase">LOADING PROFILE...</div>
              <div className="text-sm text-gray-600 mt-2">Please wait while we fetch your details</div>
            </div>
          ) : profile ? (
            <div className="space-y-6">
              {/* Profile Header */}
              <div className="text-center border-b-2 border-black pb-6">
                <div className="w-24 h-24 bg-black border-4 border-black mx-auto mb-4 flex items-center justify-center text-white text-4xl font-black">
                  {profile.username.charAt(0).toUpperCase()}
                </div>
                <h3 className="text-xl font-black text-black uppercase tracking-wide">
                  {profile.full_name}
                </h3>
                <div className="text-sm font-bold text-gray-600 uppercase tracking-wide">
                  @{profile.username}
                </div>
                <div className="mt-2">
                  <span className={`px-3 py-1 text-xs font-bold uppercase border-2 ${
                    profile.is_active 
                      ? 'bg-green-100 text-green-800 border-green-800'
                      : 'bg-red-100 text-red-800 border-red-800'
                  }`}>
                    {profile.is_active ? '✓ ACTIVE ACCOUNT' : '✗ INACTIVE ACCOUNT'}
                  </span>
                </div>
              </div>

              {/* Profile Details */}
              <div className="grid md:grid-cols-2 gap-6">
                {/* Personal Information */}
                <div className="border-2 border-black p-4">
                  <h4 className="text-lg font-black text-black uppercase mb-4 border-b-2 border-black pb-2">
                    📝 PERSONAL INFORMATION
                  </h4>
                  
                  {isEditing ? (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-bold text-black uppercase mb-2">
                          Full Name
                        </label>
                        <input
                          type="text"
                          value={editForm.full_name}
                          onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                          className="w-full p-3 border-2 border-black text-black font-bold focus:outline-none focus:bg-gray-50"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-bold text-black uppercase mb-2">
                          Email Address
                        </label>
                        <input
                          type="email"
                          value={editForm.email}
                          onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                          className="w-full p-3 border-2 border-black text-black font-bold focus:outline-none focus:bg-gray-50"
                        />
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div>
                        <div className="text-xs font-bold text-gray-600 uppercase">Full Name</div>
                        <div className="text-sm font-bold text-black">{profile.full_name}</div>
                      </div>
                      <div>
                        <div className="text-xs font-bold text-gray-600 uppercase">Email Address</div>
                        <div className="text-sm font-bold text-black">{profile.email}</div>
                      </div>
                      <div>
                        <div className="text-xs font-bold text-gray-600 uppercase">Username</div>
                        <div className="text-sm font-bold text-black">@{profile.username}</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Account Information */}
                <div className="border-2 border-black p-4">
                  <h4 className="text-lg font-black text-black uppercase mb-4 border-b-2 border-black pb-2">
                    ⏰ ACCOUNT INFORMATION
                  </h4>
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs font-bold text-gray-600 uppercase">Account ID</div>
                      <div className="text-sm font-bold text-black font-mono">{profile.id}</div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-gray-600 uppercase">Member Since</div>
                      <div className="text-sm font-bold text-black">{formatDate(profile.created_at)}</div>
                    </div>
                    <div>
                      <div className="text-xs font-bold text-gray-600 uppercase">Last Login</div>
                      <div className="text-sm font-bold text-black">{formatDate(profile.last_login)}</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="border-t-2 border-black pt-6">
                <div className="flex justify-center space-x-4">
                  {isEditing ? (
                    <>
                      <button
                        onClick={handleSaveProfile}
                        disabled={loading}
                        className="px-6 py-2 bg-green-600 text-white font-black uppercase border-2 border-black hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        💾 SAVE CHANGES
                      </button>
                      <button
                        onClick={() => {
                          setIsEditing(false);
                          setEditForm({
                            full_name: profile.full_name,
                            email: profile.email,
                          });
                        }}
                        className="px-6 py-2 bg-gray-600 text-white font-black uppercase border-2 border-black hover:bg-gray-700"
                      >
                        ❌ CANCEL
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setIsEditing(true)}
                      className="px-6 py-2 bg-blue-600 text-white font-black uppercase border-2 border-black hover:bg-blue-700"
                    >
                      ✏️ EDIT PROFILE
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="text-lg font-bold text-black uppercase">FAILED TO LOAD PROFILE</div>
              <div className="text-sm text-gray-600 mt-2">Please try again later</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfileModal;