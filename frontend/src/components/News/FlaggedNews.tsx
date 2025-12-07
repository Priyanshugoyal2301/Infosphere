import React, { useState, useEffect } from 'react';
import api from '../../utils/api';
import { Flag, RefreshCw } from 'lucide-react';

interface FlaggedArticle {
  id: number;
  title: string;
  url: string;
  flagged_at: string;
  verification_score: number;
  flag_reasons: string[];
  checks_summary: {
    [key: string]: {
      score: number;
      status: string;
    };
  };
}

interface FlaggedStats {
  total_flagged: number;
  common_reasons: Array<{
    reason: string;
    count: number;
  }>;
  average_score: number;
}

const FlaggedNews: React.FC = () => {
  const [flaggedArticles, setFlaggedArticles] = useState<FlaggedArticle[]>([]);
  const [stats, setStats] = useState<FlaggedStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFlaggedNews();
  }, []);

  const fetchFlaggedNews = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/v1/verification/flagged-news?limit=50');
      
      if (response.data.success) {
        setFlaggedArticles(response.data.flagged_articles);
        setStats(response.data.statistics);
      }
    } catch (err: any) {
      console.error('Failed to fetch flagged news:', err);
      setError(err.response?.data?.detail || 'Failed to load flagged news');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.80) return '#10b981'; // green
    if (score >= 0.65) return '#f59e0b'; // yellow
    if (score >= 0.50) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const getStatusBadgeClass = (status: string): string => {
    const statusColors: { [key: string]: string } = {
      'verified': 'bg-green-100 text-green-800',
      'debunked': 'bg-red-100 text-red-800',
      'unreliable': 'bg-red-100 text-red-800',
      'stock_photo': 'bg-yellow-100 text-yellow-800',
      'future_dated': 'bg-red-100 text-red-800',
      'not_found': 'bg-gray-100 text-gray-800',
      'moderate': 'bg-yellow-100 text-yellow-800',
      'unknown': 'bg-gray-100 text-gray-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-[1600px] mx-auto px-6 py-8">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading flagged news...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-[1600px] mx-auto px-6 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-800">{error}</p>
          <button
            onClick={fetchFlaggedNews}
            className="mt-4 btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
          <Flag size={36} strokeWidth={2.5} className="text-red-600" /> Flagged News Articles
        </h1>
        <p className="text-gray-600">
          Articles that failed advanced verification checks and require scrutiny
        </p>
      </div>

      {/* Statistics Dashboard */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
            <div className="text-sm font-medium text-gray-600">Total Flagged</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {stats.total_flagged}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <div className="text-sm font-medium text-gray-600">Average Score</div>
            <div className="text-3xl font-bold text-gray-900 mt-2">
              {(stats.average_score * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-500">
            <div className="text-sm font-medium text-gray-600">Top Flag Reason</div>
            <div className="text-lg font-semibold text-gray-900 mt-2">
              {stats.common_reasons[0]?.reason.substring(0, 40) || 'N/A'}...
            </div>
          </div>
        </div>
      )}

      {/* Common Flag Reasons */}
      {stats && stats.common_reasons.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Most Common Flag Reasons
          </h2>
          <div className="space-y-3">
            {stats.common_reasons.map((reason, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center flex-1">
                  <span className="text-sm font-medium text-gray-700">
                    {index + 1}. {reason.reason}
                  </span>
                </div>
                <div className="ml-4">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                    {reason.count} articles
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Flagged Articles List */}
      <div className="space-y-6">
        {flaggedArticles.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Flagged Articles
            </h3>
            <p className="text-gray-600">
              All recent news articles have passed verification checks!
            </p>
          </div>
        ) : (
          flaggedArticles.map((article) => (
            <div
              key={article.id}
              className="bg-white rounded-lg shadow-md border-l-4 border-red-500 p-6 hover:shadow-lg transition-shadow"
            >
              {/* Article Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {article.title}
                  </h3>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:underline"
                  >
                    {article.url}
                  </a>
                </div>
                <div className="ml-4">
                  <div
                    className="inline-flex items-center px-4 py-2 rounded-lg font-bold text-white"
                    style={{ backgroundColor: getScoreColor(article.verification_score) }}
                  >
                    {(article.verification_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Timestamp */}
              <div className="text-sm text-gray-500 mb-4">
                Flagged: {formatDate(article.flagged_at)}
              </div>

              {/* Flag Reasons */}
              <div className="mb-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">
                  ⚠️ Flag Reasons:
                </h4>
                <ul className="space-y-1">
                  {article.flag_reasons.map((reason, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-red-500 mr-2">•</span>
                      <span className="text-sm text-gray-700">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Verification Checks Summary */}
              <div className="border-t pt-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-3">
                  Verification Checks:
                </h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {Object.entries(article.checks_summary).map(([checkName, checkData]) => (
                    <div key={checkName} className="text-center">
                      <div className="text-xs text-gray-600 mb-1 capitalize">
                        {checkName.replace(/_/g, ' ')}
                      </div>
                      <div
                        className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getStatusBadgeClass(
                          checkData.status
                        )}`}
                      >
                        {(checkData.score * 100).toFixed(0)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Refresh Button */}
      <div className="mt-8 text-center">
        <button
          onClick={fetchFlaggedNews}
          className="btn-secondary"
        >
          🔄 Refresh Flagged News
        </button>
      </div>
    </div>
  );
};

export default FlaggedNews;
