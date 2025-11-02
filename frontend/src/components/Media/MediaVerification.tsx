import React, { useState } from 'react';
import api from '../../utils/api';

interface MediaVerificationResult {
  trust_score: number;
  confidence: number;
  analysis_details: {
    face_detection: any;
    temporal_consistency?: any;
    visual_artifacts: any;
    metadata_analysis: any;
  };
  recommendations: string[];
  processing_time: number;
}

const MediaVerification: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [mediaType, setMediaType] = useState<'image' | 'video'>('image');
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<MediaVerificationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setResult(null);
      setError(null);

      // Auto-detect media type
      const fileType = file.type;
      if (fileType.startsWith('image/')) {
        setMediaType('image');
      } else if (fileType.startsWith('video/')) {
        setMediaType('video');
      }
    }
  };

  const handleVerify = async () => {
    if (!selectedFile) return;

    setIsVerifying(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('media_type', mediaType);

    try {
      const response = await api.post('/api/v1/media/verify', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Verification failed');
    } finally {
      setIsVerifying(false);
    }
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getTrustScoreDescription = (score: number) => {
    if (score >= 80) return 'High Trust - Media appears authentic';
    if (score >= 60) return 'Medium Trust - Some indicators of manipulation';
    return 'Low Trust - Likely manipulated content';
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-secondary-900 mb-2">AI Media Integrity Engine</h1>
        <p className="text-lg text-secondary-600">
          Real-time deepfake detection and media authenticity verification
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="card">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Upload Media</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Select Media Type
              </label>
              <div className="flex space-x-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="image"
                    checked={mediaType === 'image'}
                    onChange={(e) => setMediaType(e.target.value as 'image' | 'video')}
                    className="mr-2"
                  />
                  📷 Image
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="video"
                    checked={mediaType === 'video'}
                    onChange={(e) => setMediaType(e.target.value as 'image' | 'video')}
                    className="mr-2"
                  />
                  🎥 Video
                </label>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-700 mb-2">
                Choose File
              </label>
              <input
                type="file"
                accept={mediaType === 'image' ? 'image/*' : 'video/*'}
                onChange={handleFileSelect}
                className="w-full text-sm text-secondary-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              />
            </div>

            {selectedFile && (
              <div className="bg-secondary-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-secondary-900">{selectedFile.name}</p>
                    <p className="text-sm text-secondary-600">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.type}
                    </p>
                  </div>
                  <button
                    onClick={handleVerify}
                    disabled={isVerifying}
                    className="btn-primary"
                  >
                    {isVerifying ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Analyzing...
                      </span>
                    ) : (
                      '🔍 Verify Media'
                    )}
                  </button>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                <strong>Error:</strong> {error}
              </div>
            )}
          </div>

          {/* AI Features Info */}
          <div className="mt-6 pt-6 border-t border-secondary-200">
            <h3 className="font-medium text-secondary-900 mb-3">🤖 AI Analysis Features</h3>
            <div className="space-y-2 text-sm text-secondary-600">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                Face detection and temporal consistency analysis
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                Visual artifact detection using MobileNetV2-LSTM
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                Metadata analysis for manipulation signatures
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-600 rounded-full mr-3"></span>
                Real-time trust scoring (0-100 scale)
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="card">
          <h2 className="text-xl font-semibold text-secondary-900 mb-4">Verification Results</h2>
          
          {!result && !isVerifying && (
            <div className="text-center py-12 text-secondary-500">
              <div className="text-6xl mb-4">🔍</div>
              <p>Upload media to see AI verification results</p>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Trust Score */}
              <div className="text-center">
                <div className={`inline-flex items-center px-6 py-3 rounded-full text-2xl font-bold ${getTrustScoreColor(result.trust_score)}`}>
                  {result.trust_score}/100
                </div>
                <p className="mt-2 text-secondary-600">{getTrustScoreDescription(result.trust_score)}</p>
                <p className="text-sm text-secondary-500">
                  Confidence: {Math.round(result.confidence * 100)}% • 
                  Processed in {result.processing_time.toFixed(2)}s
                </p>
              </div>

              {/* Analysis Details */}
              <div className="space-y-4">
                <div className="bg-secondary-50 rounded-lg p-4">
                  <h4 className="font-medium text-secondary-900 mb-2">👤 Face Detection</h4>
                  <div className="text-sm text-secondary-700">
                    {result.analysis_details.face_detection.faces_detected > 0 ? (
                      <div>
                        <p>✅ {result.analysis_details.face_detection.faces_detected} face(s) detected</p>
                        {result.analysis_details.face_detection.largest_face_size && (
                          <p className="text-secondary-600">
                            Largest face: {result.analysis_details.face_detection.largest_face_size}
                          </p>
                        )}
                      </div>
                    ) : (
                      <p>⚠️ No faces detected in media</p>
                    )}
                  </div>
                </div>

                {result.analysis_details.temporal_consistency && (
                  <div className="bg-secondary-50 rounded-lg p-4">
                    <h4 className="font-medium text-secondary-900 mb-2">⏱️ Temporal Consistency</h4>
                    <div className="text-sm text-secondary-700">
                      <p>Score: {Math.round(result.analysis_details.temporal_consistency.consistency_score * 100)}%</p>
                      <p className="text-secondary-600">
                        Frames analyzed: {result.analysis_details.temporal_consistency.frame_scores?.length || 0}
                      </p>
                    </div>
                  </div>
                )}

                <div className="bg-secondary-50 rounded-lg p-4">
                  <h4 className="font-medium text-secondary-900 mb-2">🔍 Visual Artifacts</h4>
                  <div className="text-sm text-secondary-700">
                    {result.analysis_details.visual_artifacts.artifacts_detected ? (
                      <p>⚠️ Potential artifacts detected</p>
                    ) : (
                      <p>✅ No obvious visual artifacts found</p>
                    )}
                    {result.analysis_details.visual_artifacts.artifacts_score && (
                      <p className="text-secondary-600">
                        Artifact score: {result.analysis_details.visual_artifacts.artifacts_score}/100
                      </p>
                    )}
                  </div>
                </div>

                <div className="bg-secondary-50 rounded-lg p-4">
                  <h4 className="font-medium text-secondary-900 mb-2">📊 Metadata Analysis</h4>
                  <div className="text-sm text-secondary-700">
                    {result.analysis_details.metadata_analysis.suspicious_metadata ? (
                      <p>⚠️ Suspicious metadata patterns detected</p>
                    ) : (
                      <p>✅ Metadata appears normal</p>
                    )}
                    {result.analysis_details.metadata_analysis.metadata_score && (
                      <p className="text-secondary-600">
                        Metadata score: {result.analysis_details.metadata_analysis.metadata_score}/100
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {result.recommendations && result.recommendations.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">💡 Recommendations</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    {result.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start">
                        <span className="w-2 h-2 bg-blue-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Technology Information */}
      <div className="mt-8 bg-gradient-to-r from-primary-600 to-blue-600 rounded-xl text-white p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Advanced AI Technology</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl mb-2">🧠</div>
              <h3 className="font-semibold mb-2">Hybrid Architecture</h3>
              <p className="text-sm opacity-90">
                MobileNetV2 CNN for spatial features + Bidirectional LSTM for temporal analysis
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="font-semibold mb-2">Real-time Processing</h3>
              <p className="text-sm opacity-90">
                Optimized for GPU acceleration with ONNX Runtime for fast inference
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">🎯</div>
              <h3 className="font-semibold mb-2">Multi-modal Analysis</h3>
              <p className="text-sm opacity-90">
                Combines visual, temporal, and metadata signals for comprehensive verification
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MediaVerification;