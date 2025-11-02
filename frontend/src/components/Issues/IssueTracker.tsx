import React, { useState } from 'react';
import { useParams } from 'react-router-dom';

interface StatusUpdate {
  status: string;
  message: string;
  timestamp: string;
}

interface Issue {
  id: number;
  title: string;
  category: string;
  urgency: string;
  current_status: string;
  created_at: string;
}

const IssueTracker: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [trackingId, setTrackingId] = useState(id || '');
  const [issue, setIssue] = useState<Issue | null>(null);
  const [statusHistory, setStatusHistory] = useState<StatusUpdate[]>([]);
  const [progressPercentage, setProgressPercentage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock data for demonstration
  const mockIssues = {
    '1': {
      id: 1,
      title: "Water pipe burst on Main Street",
      category: "Water",
      urgency: "high",
      current_status: "In Progress",
      created_at: "2025-10-30T10:00:00Z"
    },
    '2': {
      id: 2,
      title: "Streetlight not working near Central Park",
      category: "Road", 
      urgency: "medium",
      current_status: "Assigned",
      created_at: "2025-10-30T05:00:00Z"
    }
  };

  const mockStatusHistory = {
    '1': [
      { status: "submitted", message: "Complaint submitted and classified", timestamp: "2025-10-30T10:00:00Z" },
      { status: "under_review", message: "Issue reviewed by Water Department", timestamp: "2025-10-30T11:30:00Z" },
      { status: "assigned", message: "Assigned to repair crew #A5", timestamp: "2025-10-30T14:00:00Z" },
      { status: "in_progress", message: "Repair crew on site, excavation in progress", timestamp: "2025-10-30T16:00:00Z" }
    ],
    '2': [
      { status: "submitted", message: "Complaint submitted and classified", timestamp: "2025-10-30T05:00:00Z" },
      { status: "under_review", message: "Issue reviewed by Roads & Infrastructure Department", timestamp: "2025-10-30T08:00:00Z" },
      { status: "assigned", message: "Assigned to electrical maintenance team", timestamp: "2025-10-30T10:00:00Z" }
    ]
  };

  const handleTrackIssue = async () => {
    if (!trackingId.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Simulate API call with mock data
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockIssue = mockIssues[trackingId as keyof typeof mockIssues];
      const mockHistory = mockStatusHistory[trackingId as keyof typeof mockStatusHistory];

      if (mockIssue && mockHistory) {
        setIssue(mockIssue);
        setStatusHistory(mockHistory);
        setProgressPercentage(calculateProgress(mockIssue.current_status));
      } else {
        setError(`Issue #${trackingId} not found`);
        setIssue(null);
        setStatusHistory([]);
        setProgressPercentage(0);
      }
    } catch (error: any) {
      setError('Failed to fetch issue details');
    } finally {
      setLoading(false);
    }
  };

  const calculateProgress = (status: string): number => {
    const statusProgress: { [key: string]: number } = {
      "submitted": 10,
      "under_review": 25,
      "assigned": 40,
      "in_progress": 65,
      "testing": 85,
      "resolved": 100,
      "closed": 100
    };
    return statusProgress[status.toLowerCase().replace(' ', '_')] || 0;
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase().replace(' ', '_')) {
      case 'resolved':
      case 'closed':
        return 'text-green-600 bg-green-100 border-green-200';
      case 'in_progress':
      case 'testing':
        return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'assigned':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'under_review':
        return 'text-purple-600 bg-purple-100 border-purple-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency.toLowerCase()) {
      case 'critical': return 'text-red-700 bg-red-100 border-red-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
  };

  React.useEffect(() => {
    if (id) {
      handleTrackIssue();
    }
  }, [id]);

  return (
    <div className="min-h-screen newspaper-bg">
      <div className="max-w-4xl mx-auto px-4">
        <div className="newspaper-header text-center py-8 mb-8">
          <div className="border-t-4 border-b-4 border-black py-4 mx-4">
            <h1 className="newspaper-title text-5xl font-black text-black mb-2 tracking-tight">
              NEWS TRACKING BUREAU
            </h1>
            <div className="flex justify-center items-center space-x-8 text-sm font-semibold text-black">
              <span>ISSUE MONITORING DESK</span>
              <span className="border-l border-r border-black px-4">REAL-TIME STATUS</span>
              <span>EST. 2025</span>
            </div>
          </div>
          <div className="mt-4">
            <p className="newspaper-subtitle text-lg font-semibold text-black max-w-3xl mx-auto italic">
              "Track Your News Reports - Real-Time Progress Monitoring System"
            </p>
          </div>
        </div>

      {/* Search Section */}
      <div className="newspaper-section mb-8">
        <h2 className="newspaper-section-title text-xl font-black text-black border-b-2 border-black pb-2 mb-4 uppercase tracking-wide">Enter Report ID</h2>
        <div className="flex gap-4">
          <input
            type="text"
            value={trackingId}
            onChange={(e) => setTrackingId(e.target.value)}
            placeholder="Enter issue ID (e.g., 1, 2)"
            className="input-field flex-1"
          />
          <button
            onClick={handleTrackIssue}
            disabled={loading || !trackingId.trim()}
            className="btn-primary"
          >
            {loading ? 'Searching...' : '🔍 Track Issue'}
          </button>
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4">
            {error}
          </div>
        )}

        <div className="mt-4 text-sm text-secondary-600">
          <p className="mb-2"><strong>Try these sample IDs:</strong></p>
          <div className="flex gap-2">
            <button
              onClick={() => setTrackingId('1')}
              className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded hover:bg-secondary-200"
            >
              Issue #1 (Water)
            </button>
            <button
              onClick={() => setTrackingId('2')}
              className="px-3 py-1 bg-secondary-100 text-secondary-700 rounded hover:bg-secondary-200"
            >
              Issue #2 (Road)
            </button>
          </div>
        </div>
      </div>

      {issue && (
        <div className="space-y-8">
          {/* Issue Details */}
          <div className="card">
            <div className="flex items-start justify-between mb-6">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-secondary-900 mb-2">
                  Issue #{issue.id}: {issue.title}
                </h2>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {issue.category}
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getUrgencyColor(issue.urgency)}`}>
                    {issue.urgency.charAt(0).toUpperCase() + issue.urgency.slice(1)} Priority
                  </span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(issue.current_status)}`}>
                    {issue.current_status}
                  </span>
                </div>
              </div>
              <div className="text-sm text-secondary-500 ml-4">
                Reported {getTimeAgo(issue.created_at)}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-secondary-700">Progress</span>
                <span className="text-sm text-secondary-500">{progressPercentage}% Complete</span>
              </div>
              <div className="w-full bg-secondary-200 rounded-full h-3">
                <div 
                  className="bg-primary-600 h-3 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progressPercentage}%` }}
                ></div>
              </div>
            </div>

            {/* Estimated Resolution */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="text-2xl mr-3">⏱️</div>
                <div>
                  <h3 className="font-medium text-blue-900">Estimated Resolution</h3>
                  <p className="text-blue-700">
                    {issue.urgency === 'high' ? '1-2 business days' : 
                     issue.urgency === 'medium' ? '3-5 business days' : 
                     '5-7 business days'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Status Timeline */}
          <div className="card">
            <h3 className="text-xl font-semibold text-secondary-900 mb-6">Status Timeline</h3>
            <div className="space-y-6">
              {statusHistory.map((update, index) => (
                <div key={index} className="flex items-start">
                  <div className="flex-shrink-0">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                      index === statusHistory.length - 1 ? 'bg-primary-600' : 'bg-secondary-400'
                    }`}>
                      {index + 1}
                    </div>
                  </div>
                  <div className="ml-4 flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-secondary-900 capitalize">
                        {update.status.replace('_', ' ')}
                      </h4>
                      <span className="text-sm text-secondary-500">
                        {formatTimestamp(update.timestamp)}
                      </span>
                    </div>
                    <p className="text-secondary-700 mt-1">{update.message}</p>
                    {index === statusHistory.length - 1 && (
                      <div className="inline-flex items-center mt-2 text-sm text-primary-600">
                        <div className="w-2 h-2 bg-primary-600 rounded-full mr-2 animate-pulse"></div>
                        Current Status
                      </div>
                    )}
                  </div>
                  {index !== statusHistory.length - 1 && (
                    <div className="absolute left-4 mt-8 w-0.5 h-6 bg-secondary-300"></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div className="card bg-gradient-to-r from-primary-50 to-blue-50 border-primary-200">
            <h3 className="font-semibold text-primary-900 mb-3">🎯 What's Next?</h3>
            <div className="space-y-2 text-sm text-primary-800">
              {issue.current_status.toLowerCase() === 'in progress' && (
                <>
                  <p>• Repair work is currently underway at the reported location</p>
                  <p>• You'll receive updates as progress is made</p>
                  <p>• Expected completion within the estimated timeframe</p>
                </>
              )}
              {issue.current_status.toLowerCase() === 'assigned' && (
                <>
                  <p>• The issue has been assigned to the appropriate team</p>
                  <p>• Work will begin shortly based on priority and scheduling</p>
                  <p>• You'll be notified when work starts</p>
                </>
              )}
              {issue.current_status.toLowerCase() === 'under review' && (
                <>
                  <p>• Your issue is being reviewed by the relevant department</p>
                  <p>• Assessment and resource allocation is in progress</p>
                  <p>• Assignment to a team will follow shortly</p>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {!issue && !loading && !error && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-secondary-900 mb-2">Ready to Track</h3>
          <p className="text-secondary-600 mb-6">Enter an issue ID above to see real-time tracking information</p>
          
          <div className="bg-secondary-50 rounded-lg p-6 max-w-md mx-auto">
            <h4 className="font-medium text-secondary-900 mb-3">E-commerce Style Tracking</h4>
            <ul className="text-sm text-secondary-600 space-y-2 text-left">
              <li>• Real-time status updates</li>
              <li>• Detailed timeline with timestamps</li>
              <li>• Progress percentage calculation</li>
              <li>• Estimated resolution timeframes</li>
              <li>• Automated notifications (coming soon)</li>
            </ul>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default IssueTracker;