import React, { useState } from 'react';
import { Shield, AlertTriangle, CheckCircle, XCircle, Network, Clock, Image, Quote } from 'lucide-react';

interface EnhancedVerificationProps {
  articleUrl: string;
  title: string;
  content: string;
  source: string;
  imageUrl?: string;
  claims?: string[];
}

interface VerificationResult {
  overall_score: number;
  verdict: string;
  verifications: {
    temporal: any;
    citations: any[];
    image: any;
    network: any;
  };
  warnings: string[];
  flags: string[];
}

const EnhancedVerification: React.FC<EnhancedVerificationProps> = ({
  articleUrl,
  title,
  content,
  source,
  imageUrl,
  claims = []
}) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runVerification = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/enhanced-verification/enhanced-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: articleUrl,
          title,
          content,
          source,
          image_url: imageUrl,
          claims
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setResult(data.data);
      } else {
        setError('Verification failed');
      }
    } catch (err) {
      setError('Failed to connect to verification service');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case 'VERIFIED':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'NEEDS_REVIEW':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'QUESTIONABLE':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Shield className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Enhanced Verification</h2>
        </div>
        <button
          onClick={runVerification}
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Shield className="w-4 h-4" />
              <span>Run Verification</span>
            </>
          )}
        </button>
      </div>

      {/* Article Info */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-2">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600">Source: {source}</p>
        <a href={articleUrl} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline">
          {articleUrl}
        </a>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
          <XCircle className="w-5 h-5 text-red-600 mt-0.5" />
          <div>
            <h4 className="font-semibold text-red-900">Error</h4>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Overall Verdict */}
          <div className={`border rounded-lg p-6 ${getVerdictColor(result.verdict)}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold">Overall Assessment</h3>
              <div className="flex items-center space-x-2">
                {result.verdict === 'VERIFIED' && <CheckCircle className="w-6 h-6" />}
                {result.verdict === 'QUESTIONABLE' && <XCircle className="w-6 h-6" />}
                {result.verdict === 'NEEDS_REVIEW' && <AlertTriangle className="w-6 h-6" />}
              </div>
            </div>
            <div className="flex items-baseline space-x-3">
              <span className="text-3xl font-bold">{result.verdict}</span>
              <span className={`text-2xl font-semibold ${getScoreColor(result.overall_score)}`}>
                {(result.overall_score * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Warnings & Flags */}
          {result.warnings.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-semibold text-yellow-900 mb-2">Warnings</h4>
                  <ul className="space-y-1">
                    {result.warnings.map((warning, idx) => (
                      <li key={idx} className="text-sm text-yellow-700">• {warning}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Temporal Verification */}
          {result.verifications.temporal && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Clock className="w-5 h-5 text-purple-600" />
                <h4 className="font-semibold text-gray-900">Temporal Analysis</h4>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Claims Tracked:</span>{' '}
                  {result.verifications.temporal.total_claims || 0}
                </p>
                <p>
                  <span className="font-medium">Contradictions:</span>{' '}
                  {result.verifications.temporal.contradictory_claims || 0}
                </p>
                {result.verifications.temporal.shift_detected && (
                  <div className="bg-red-50 border border-red-200 rounded p-2 mt-2">
                    <p className="text-red-700 font-medium">⚠️ Narrative shift detected in recent articles</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Network Analysis */}
          {result.verifications.network && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Network className="w-5 h-5 text-blue-600" />
                <h4 className="font-semibold text-gray-900">Network Analysis</h4>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Trust Score:</span>{' '}
                  <span className={getScoreColor(result.verifications.network.trust_score)}>
                    {(result.verifications.network.trust_score * 100).toFixed(1)}%
                  </span>
                </p>
                {result.verifications.network.circular_reporting?.circular && (
                  <div className="bg-red-50 border border-red-200 rounded p-2 mt-2">
                    <p className="text-red-700 font-medium">⚠️ Circular reporting detected</p>
                    <p className="text-xs text-red-600 mt-1">
                      Chain length: {result.verifications.network.circular_reporting.chain?.length || 0}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Image Verification */}
          {result.verifications.image && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Image className="w-5 h-5 text-green-600" />
                <h4 className="font-semibold text-gray-900">Image Analysis</h4>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium">Confidence:</span>{' '}
                  <span className={getScoreColor(result.verifications.image.confidence)}>
                    {(result.verifications.image.confidence * 100).toFixed(1)}%
                  </span>
                </p>
                {result.verifications.image.is_stock_photo && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded p-2">
                    <p className="text-yellow-700">📸 Stock photo detected</p>
                  </div>
                )}
                {result.verifications.image.metadata && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-blue-600 hover:underline">View Metadata</summary>
                    <pre className="mt-2 bg-gray-50 rounded p-2 text-xs overflow-auto">
                      {JSON.stringify(result.verifications.image.metadata, null, 2)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          )}

          {/* Citation Verification */}
          {result.verifications.citations.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Quote className="w-5 h-5 text-indigo-600" />
                <h4 className="font-semibold text-gray-900">Quote Verification</h4>
              </div>
              <div className="space-y-3">
                {result.verifications.citations.map((citation, idx) => (
                  <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                    <p className="font-medium text-gray-900 mb-2">"{citation.quote.substring(0, 80)}..."</p>
                    {citation.verification.verified ? (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span>Verified from official source</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-red-600">
                        <XCircle className="w-4 h-4" />
                        <span>Could not verify from official sources</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Flags */}
          {result.flags.length > 0 && (
            <div className="border border-orange-200 bg-orange-50 rounded-lg p-4">
              <h4 className="font-semibold text-orange-900 mb-2">Detection Flags</h4>
              <div className="flex flex-wrap gap-2">
                {result.flags.map((flag, idx) => (
                  <span key={idx} className="px-3 py-1 bg-orange-200 text-orange-800 rounded-full text-xs font-medium">
                    {flag.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedVerification;
