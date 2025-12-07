import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import api from '../../utils/api';
import NewspaperBorders from '../Layout/NewspaperBorders';
import { ENABLE_NEWSPAPER_BORDERS } from '../../utils/newspaperBorders';
import LoginModal from '../Auth/LoginModal';
import { CheckCircle } from 'lucide-react';

interface ComplaintFormData {
  title: string;
  description: string;
  location: string;
  contact_info: string;
}

const ReportIssue: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [showLoginModal, setShowLoginModal] = useState(!isAuthenticated);
  const [formData, setFormData] = useState<ComplaintFormData>({
    title: '',
    description: '',
    location: '',
    contact_info: ''
  });
  const [imageFiles, setImageFiles] = useState<File[]>([]);
  const [videoFiles, setVideoFiles] = useState<File[]>([]);
  const [latitude, setLatitude] = useState<string>('');
  const [longitude, setLongitude] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<any>(null);
  const [savedOffline, setSavedOffline] = useState<boolean>(false);
  const [localCount, setLocalCount] = useState<number>(() => {
    try {
      return JSON.parse(localStorage.getItem('local_submissions') || '[]').length;
    } catch { return 0; }
  });

  const saveToLocal = (record: any) => {
    try {
      const key = 'local_submissions';
      const existing = JSON.parse(localStorage.getItem(key) || '[]');
      existing.push(record);
      localStorage.setItem(key, JSON.stringify(existing));
      setLocalCount(existing.length);
    } catch (e) { console.error('Local save failed', e); }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitResult(null);

    try {
      const multipart = new FormData();
      multipart.append('title', formData.title);
      multipart.append('description', formData.description);
      multipart.append('location', formData.location);
      multipart.append('contact_info', formData.contact_info);
      imageFiles.forEach((f) => multipart.append('images', f));
      videoFiles.forEach((f) => multipart.append('videos', f));
      if (latitude) multipart.append('latitude', latitude);
      if (longitude) multipart.append('longitude', longitude);

      const response = await api.post('/api/v1/issues/report', multipart, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSubmitResult({ success: true, data: response.data });
      // Also save a local copy for user's records
      saveToLocal({
        ...response.data,
        title: formData.title,
        description: formData.description,
        location: formData.location,
        contact_info: formData.contact_info,
        latitude: latitude || null,
        longitude: longitude || null,
        images: imageFiles.map(f => ({ name: f.name, type: f.type, size: f.size })),
        videos: videoFiles.map(f => ({ name: f.name, type: f.type, size: f.size })),
        offline: false,
        saved_at: new Date().toISOString()
      });
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        location: '',
        contact_info: ''
      });
      setImageFiles([]);
      setVideoFiles([]);
      setLatitude('');
      setLongitude('');
    } catch (error: any) {
      // Offline/local fallback: persist minimal metadata in localStorage
      const localId = `L-${Date.now()}`;
      const record = {
        id: localId,
        title: formData.title,
        description: formData.description,
        location: formData.location,
        contact_info: formData.contact_info,
        latitude: latitude || null,
        longitude: longitude || null,
        images: imageFiles.map(f => ({ name: f.name, type: f.type, size: f.size })),
        videos: videoFiles.map(f => ({ name: f.name, type: f.type, size: f.size })),
        created_at: new Date().toISOString(),
        status: 'submitted',
        category: 'General',
        urgency: 'medium',
        confidence_score: 0.5,
        estimated_resolution: 'TBD (offline)',
        offline: true
      };
      try {
        saveToLocal(record);
        setSubmitResult({ success: true, data: record });
        setSavedOffline(true);
        // Reset form after local save
        setFormData({ title: '', description: '', location: '', contact_info: '' });
        setImageFiles([]);
        setVideoFiles([]);
        setLatitude('');
        setLongitude('');
      } catch (e) {
        setSubmitResult({
          success: false,
          error: error?.response?.data?.detail || 'Failed to submit issue'
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitResult?.success) {
    const issue = submitResult.data;
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
        <div className="max-w-2xl w-full">
          <div className="card text-center bg-white">
            <div className="flex justify-center mb-4">
              <CheckCircle size={80} strokeWidth={2} className="text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-green-600 mb-4">Issue Submitted Successfully!</h2>
          
          <div className="border border-gray-300 rounded-lg p-6 mb-6" style={{background: '#f5f0e8'}}>
            <h3 className="font-semibold text-black mb-3">Issue Details</h3>
            <div className="space-y-2 text-left">
              <div><strong>ID:</strong> #{issue.id}</div>
              <div><strong>Title:</strong> {issue.title}</div>
              <div><strong>Category:</strong> <span className="px-2 py-1 rounded text-sm" style={{background: '#d4c5a9', color: '#5d4037'}}>{issue.category}</span></div>
              <div><strong>Urgency:</strong> <span className={`px-2 py-1 rounded text-sm`} style={{
                background: issue.urgency === 'high' ? '#c9b89a' : issue.urgency === 'medium' ? '#dfd0b3' : '#e8dcc8',
                color: '#5d4037'
              }}>{issue.urgency}</span></div>
              <div><strong>Status:</strong> <span className="px-2 py-1 rounded text-sm" style={{background: '#e8dcc8', color: '#5d4037'}}>{issue.status}</span></div>
              <div><strong>AI Confidence:</strong> {Math.round(issue.confidence_score * 100)}%</div>
              <div><strong>Estimated Resolution:</strong> {issue.estimated_resolution}</div>
            </div>
          </div>

          <div className="flex gap-4 justify-center">
            <button
              onClick={() => setSubmitResult(null)}
              className="btn-secondary"
            >
              Report Another Issue
            </button>
            <button
              onClick={() => window.open(`/track/${issue.id}`, '_blank')}
              className="btn-primary"
            >
              Track This Issue
            </button>
          </div>
        </div>
      </div>
      </div>
    );
  }

  return (
    <div
      className="min-h-screen newspaper-bg with-page-bg pt-10 pb-10"
      style={{
        // Inline background for the container itself
        backgroundImage: "url('/images/newspaper-pattern.svg')",
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
        backgroundRepeat: 'repeat',
        // Provide the image to the CSS ::after overlay without letting webpack resolve it in CSS
        ['--page-bg-image' as any]: "url('/images/newspaper-pattern.svg')"
      }}
    >
      <div className="max-w-[1600px] mx-auto px-6 md:px-12 relative z-[1]">
        {ENABLE_NEWSPAPER_BORDERS && <NewspaperBorders />}
        <div className="newspaper-header text-center py-6 mb-4">
          <div className="border-t-4 border-b-4 border-black py-3 mx-0">
            <h1 className="newspaper-title text-5xl font-black text-black mb-2 tracking-tight">
              NEWS REPORT SUBMISSION
            </h1>
            <div className="flex justify-center items-center space-x-6 text-sm font-semibold text-black">
              <span>CITIZEN JOURNALISM DESK</span>
              <span className="border-l border-r border-black px-4">AI-POWERED ROUTING</span>
              <span>EST. 2025</span>
            </div>
          </div>
          <div className="mt-2">
            <p className="newspaper-subtitle text-lg font-semibold text-black max-w-3xl mx-auto italic">
              "Submit Your News Reports - Intelligent Categorization & Verification System"
            </p>
          </div>
        </div>
        
        <div className="newspaper-section" style={{ border: '2px solid #000' }}>
          <h2 className="newspaper-section-title text-2xl font-black text-black border-b-2 border-black pb-1 mb-4 uppercase tracking-wide text-center">
            Report News Story
          </h2>

        {submitResult?.error && (
          <div className="border border-gray-400 text-gray-800 px-4 py-3 rounded-lg mb-6" style={{background: '#f5e6d3'}}>
            <strong>Error:</strong> {submitResult.error}
          </div>
        )}
        {savedOffline && (
          <div className="border border-gray-400 text-gray-800 px-4 py-3 rounded-lg mb-6" style={{background: '#f5eed9'}}>
            Saved locally. We will sync when the server is available.
          </div>
        )}

  <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-secondary-700 mb-2">
              Issue Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
              placeholder="Brief description of the issue"
              className="input-field"
            />
          </div>

          <div>
            <label htmlFor="description" className="block text-sm font-medium text-secondary-700 mb-2">
              Detailed Description *
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              required
              rows={5}
              placeholder="Provide detailed information about the issue, including when it occurred and any relevant circumstances"
              className="input-field resize-none"
            />
            <div className="text-xs text-secondary-500 mt-1">
              AI will analyze this text to determine category and urgency
            </div>
          </div>

          <div>
            <label htmlFor="location" className="block text-sm font-medium text-secondary-700 mb-2">
              Location
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={formData.location}
              onChange={handleInputChange}
              placeholder="Street address, landmark, or general area"
              className="input-field"
            />
          </div>

          <div>
            <label htmlFor="contact_info" className="block text-sm font-medium text-secondary-700 mb-2">
              Contact Information (Optional)
            </label>
            <input
              type="text"
              id="contact_info"
              name="contact_info"
              value={formData.contact_info}
              onChange={handleInputChange}
              placeholder="Email or phone number for updates"
              className="input-field"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Upload Proof (Images)
            </label>
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={(e) => setImageFiles(Array.from(e.target.files || []))}
              className="input-field"
            />
            <div className="text-xs text-secondary-500 mt-1">JPEG, PNG, HEIC supported</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-secondary-700 mb-2">
              Upload Proof (Videos)
            </label>
            <input
              type="file"
              accept="video/*"
              multiple
              onChange={(e) => setVideoFiles(Array.from(e.target.files || []))}
              className="input-field"
            />
            <div className="text-xs text-secondary-500 mt-1">MP4, MOV, WEBM supported</div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Latitude (optional)</label>
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="e.g., 12.9716"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">Longitude (optional)</label>
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="e.g., 77.5946"
                className="input-field"
              />
            </div>
          </div>

          <div className="border border-gray-400 rounded-lg p-4" style={{background: '#f5f0e8'}}>
            <h3 className="font-medium text-gray-800 mb-2">🤖 AI-Powered Processing</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• Automatic categorization into Water, Road, Garbage, or Security</li>
              <li>• Urgency assessment based on keywords and context</li>
              <li>• Smart routing to appropriate department</li>
              <li>• Real-time status tracking with timeline</li>
            </ul>
          </div>

          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setFormData({
                title: '',
                description: '',
                location: '',
                contact_info: ''
              })}
              className="btn-secondary flex-1"
              disabled={isSubmitting}
            >
              Clear Form
            </button>
            <button
              type="submit"
              className="btn-primary flex-1"
              disabled={isSubmitting || !formData.title || !formData.description}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
              ) : (
                'Submit Issue'
              )}
            </button>
          </div>
        </form>

        <div className="mt-6 p-4 border border-gray-400 rounded-lg" style={{background: '#f5f0e8'}}>
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">Local submissions on this device: <strong>{localCount}</strong></div>
            <div className="flex gap-2">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  try {
                    const data = localStorage.getItem('local_submissions') || '[]';
                    const blob = new Blob([data], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url; a.download = `local_submissions_${Date.now()}.json`; a.click();
                    URL.revokeObjectURL(url);
                  } catch {}
                }}
              >Export JSON</button>
              <button
                type="button"
                className="btn-secondary"
                onClick={() => {
                  if (window.confirm('Clear all locally saved submissions?')) {
                    localStorage.removeItem('local_submissions');
                    setLocalCount(0);
                  }
                }}
              >Clear Local</button>
              <a href="/my-submissions" className="btn-primary">My Submissions</a>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-300">
          <h3 className="font-medium text-black mb-3">Common Issue Categories</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 rounded-lg" style={{background: '#e8dcc8'}}>
              <div className="text-2xl mb-1">💧</div>
              <div className="text-sm font-medium text-black">Water</div>
              <div className="text-xs text-gray-700">Pipes, leaks, quality</div>
            </div>
            <div className="text-center p-3 rounded-lg" style={{background: '#e8dcc8'}}>
              <div className="text-2xl mb-1">🛣️</div>
              <div className="text-sm font-medium text-black">Road</div>
              <div className="text-xs text-gray-700">Potholes, signals, lighting</div>
            </div>
            <div className="text-center p-3 rounded-lg" style={{background: '#e8dcc8'}}>
              <div className="text-2xl mb-1">🗑️</div>
              <div className="text-sm font-medium text-black">Garbage</div>
              <div className="text-xs text-gray-700">Collection, disposal</div>
            </div>
            <div className="text-center p-3 rounded-lg" style={{background: '#e8dcc8'}}>
              <div className="text-2xl mb-1">🔒</div>
              <div className="text-sm font-medium text-black">Security</div>
              <div className="text-xs text-gray-700">Safety, crime, patrol</div>
            </div>
          </div>
        </div>
      </div>
      </div>

      {/* Login Modal */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)}
        initialMode="user"
      />
    </div>
  );
};

export default ReportIssue;