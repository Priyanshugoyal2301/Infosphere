import React, { useState } from 'react';
import api from '../../utils/api';
import NewspaperBorders from '../Layout/NewspaperBorders';
import { ENABLE_NEWSPAPER_BORDERS } from '../../utils/newspaperBorders';

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

interface ATIEResult {
  atie_trust_score: {
    score: number;
    trust_level: string;
    recommendation: string;
    components: {
      textual_integrity_base: number;
      cross_verification_adjustment?: number;
    };
  };
  textual_integrity: {
    textual_integrity_score: number;
    components: {
      fake_news_classification: any;
      sensationalism_analysis: any;
      bias_analysis: any;
      source_credibility: any;
    };
    metadata: {
      analysis_time: number;
      timestamp: string;
    };
  };
  cross_verification?: any;
  metadata: {
    analysis_time: number;
    from_cache: boolean;
  };
}

interface CompositeResult {
  composite_trust_score: {
    score: number;
    components: {
      textual_score: number;
      media_score: number;
      weights: { text: number; media: number };
    };
    trust_level: string;
    recommendation: string;
  };
  textual_analysis: ATIEResult;
  media_analysis?: MediaVerificationResult;
}

const EnhancedMediaVerification: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [documentFile, setDocumentFile] = useState<File | null>(null);
  const [textContent, setTextContent] = useState<string>('');
  const [sourceUrl, setSourceUrl] = useState<string>('');
  const [mediaType, setMediaType] = useState<'image' | 'video'>('image');
  const [analysisType, setAnalysisType] = useState<'media' | 'text' | 'composite'>('composite');
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [mediaResult, setMediaResult] = useState<MediaVerificationResult | null>(null);
  const [textResult, setTextResult] = useState<ATIEResult | null>(null);
  const [compositeResult, setCompositeResult] = useState<CompositeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [docReport, setDocReport] = useState<any>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      resetResults();

      // Auto-detect media type
      const fileType = file.type;
      if (fileType.startsWith('image/')) {
        setMediaType('image');
      } else if (fileType.startsWith('video/')) {
        setMediaType('video');
      }
    }
  };

  const handleDocumentSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDocumentFile(file);
      resetResults();
    }
  };

  const resetResults = () => {
    setMediaResult(null);
    setTextResult(null);
    setCompositeResult(null);
    setError(null);
  };

  const handleMediaAnalysis = async () => {
    if (!selectedFile) return null;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('media_type', mediaType);

    try {
      const response = await api.post('/api/v1/media/verify', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Media analysis failed');
    }
  };

  const handleTextAnalysis = async () => {
    if (!textContent.trim()) return null;

    try {
      console.log('🔍 Starting text analysis...', { textLength: textContent.length });
      
      const response = await api.post('/api/v1/atie/analyze-text', {
        text: textContent,
        source_url: sourceUrl || null,
        enable_cross_verification: true,
        cache_result: true
      });
      
      console.log('✅ Text analysis response:', response.data);
      return response.data.data;
    } catch (error: any) {
      console.error('❌ Text analysis error:', error);
      
      // More detailed error handling
      if (error.code === 'NETWORK_ERROR' || error.message.includes('Network Error')) {
        throw new Error('Unable to connect to AI service. Please check if the backend is running.');
      } else if (error.response?.status === 404) {
        throw new Error('ATIE service not found. Please ensure the backend is properly configured.');
      } else if (error.response?.status === 500) {
        throw new Error('AI service error. The model may be loading, please try again in a moment.');
      } else {
        const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Text analysis failed';
        throw new Error(`Analysis failed: ${errorMsg}`);
      }
    }
  };

  const handleCompositeAnalysis = async () => {
    if (!textContent.trim()) {
      throw new Error('Text content is required for composite analysis');
    }

    // Get media analysis first if file is selected
    let mediaData = null;
    if (selectedFile) {
      mediaData = await handleMediaAnalysis();
    }

    try {
      const response = await api.post('/api/v1/atie/analyze-composite', {
        text: textContent,
        media_data: mediaData,
        source_url: sourceUrl || null
      });
      return response.data.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Composite analysis failed');
    }
  };

  const handleDocumentAnalysis = async () => {
    if (!documentFile) return null;
    const formData = new FormData();
    formData.append('file', documentFile);
    try {
      const response = await api.post('/api/v1/atie/analyze-document', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDocReport(response.data.document_report || null);
      return response.data.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Document analysis failed');
    }
  };

  const handleFactCheckDocument = async () => {
    try {
      setIsAnalyzing(true);
      setError(null);
      const result = await handleDocumentAnalysis();
      setTextResult(result);
      setAnalysisType('text');
    } catch (err: any) {
      setError(err.message || 'Document analysis failed');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setError(null);
    resetResults();

    try {
      switch (analysisType) {
        case 'media':
          if (!selectedFile) {
            throw new Error('Please select a media file');
          }
          const mediaResult = await handleMediaAnalysis();
          setMediaResult(mediaResult);
          break;

        case 'text':
          if (!textContent.trim()) {
            throw new Error('Please enter text content');
          }
          const textResult = await handleTextAnalysis();
          setTextResult(textResult);
          break;

        case 'composite':
          const compositeResult = await handleCompositeAnalysis();
          setCompositeResult(compositeResult);
          break;
      }
    } catch (error: any) {
      setError(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getTrustScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getTrustScoreDescription = (score: number) => {
    if (score >= 85) return 'Very High Trust - Content appears highly authentic';
    if (score >= 70) return 'High Trust - Content appears authentic';
    if (score >= 50) return 'Moderate Trust - Some integrity concerns';
    if (score >= 30) return 'Low Trust - Significant integrity issues';
    return 'Very Low Trust - High likelihood of manipulation/misinformation';
  };

  const renderTrustScore = (score: number, title: string) => (
    <div className="newspaper-card">
      <div className="newspaper-card-header">
        <h3 className="text-lg font-black text-white uppercase tracking-wide">{title}</h3>
      </div>
      <div className="text-center p-6">
        <div className={`inline-flex items-center justify-center w-24 h-24 border-4 border-black text-3xl font-black ${getTrustScoreColor(score)}`}>
          {Math.round(score)}
        </div>
        <p className="mt-4 text-sm text-black font-semibold">
          {getTrustScoreDescription(score)}
        </p>
      </div>
    </div>
  );

  const renderMediaAnalysis = (result: MediaVerificationResult) => (
    <div className="space-y-4">
      {renderTrustScore(result.trust_score, 'Media Integrity Score')}
      
      <div className="bg-white rounded-lg border border-secondary-200 p-4">
        <h4 className="font-semibold text-secondary-900 mb-3">Analysis Details</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-secondary-600">Confidence:</span>
            <span className="ml-2 font-medium">{(result.confidence * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-secondary-600">Processing Time:</span>
            <span className="ml-2 font-medium">{result.processing_time.toFixed(2)}s</span>
          </div>
        </div>
        
        <div className="mt-4">
          <h5 className="font-medium text-secondary-800 mb-2">Recommendations:</h5>
          <ul className="space-y-1">
            {result.recommendations.map((rec, index) => (
              <li key={index} className="text-sm text-secondary-600 flex items-start">
                <span className="text-primary-600 mr-2">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );

  const renderTextAnalysis = (result: ATIEResult) => (
    <div className="space-y-4">
      {renderTrustScore(result.atie_trust_score.score, 'Textual Integrity Score')}
      
      <div className="bg-white rounded-lg border border-secondary-200 p-4">
        <h4 className="font-semibold text-secondary-900 mb-3">ATIE Analysis Breakdown</h4>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-secondary-600">Authenticity:</span>
              <span className="text-sm font-medium">
                {result.textual_integrity.components.fake_news_classification.authenticity_score.toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-secondary-600">Sensationalism:</span>
              <span className="text-sm font-medium">
                {result.textual_integrity.components.sensationalism_analysis.sensationalism_score}%
              </span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-secondary-600">Source Credibility:</span>
              <span className="text-sm font-medium">
                {result.textual_integrity.components.source_credibility.credibility_score}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-secondary-600">Bias Score:</span>
              <span className="text-sm font-medium">
                {result.textual_integrity.components.bias_analysis.bias_score}%
              </span>
            </div>
          </div>
        </div>

        <div className="border-t pt-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-secondary-600">Analysis Time:</span>
            <span className="font-medium">{result.metadata.analysis_time.toFixed(2)}s</span>
            {result.metadata.from_cache && (
              <span className="text-green-600 text-xs bg-green-100 px-2 py-1 rounded">
                ⚡ Cached
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 p-3 bg-blue-50 rounded">
          <p className="text-sm text-blue-800">
            <strong>Recommendation:</strong> {result.atie_trust_score.recommendation}
          </p>
        </div>
      </div>
    </div>
  );

  const renderCompositeAnalysis = (result: CompositeResult) => (
    <div className="space-y-4">
      {renderTrustScore(result.composite_trust_score.score, 'Composite Trust Score')}
      
      <div className="bg-white rounded-lg border border-secondary-200 p-4">
        <h4 className="font-semibold text-secondary-900 mb-3">Composite Analysis</h4>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center p-3 bg-blue-50 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(result.composite_trust_score.components.textual_score)}
            </div>
            <div className="text-sm text-blue-600">Text Score</div>
            <div className="text-xs text-secondary-500">
              Weight: {(result.composite_trust_score.components.weights.text * 100)}%
            </div>
          </div>
          
          {result.media_analysis && (
            <div className="text-center p-3 bg-purple-50 rounded">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(result.composite_trust_score.components.media_score)}
              </div>
              <div className="text-sm text-purple-600">Media Score</div>
              <div className="text-xs text-secondary-500">
                Weight: {(result.composite_trust_score.components.weights.media * 100)}%
              </div>
            </div>
          )}
        </div>

        <div className="p-3 bg-gray-50 rounded">
          <p className="text-sm text-gray-800">
            <strong>Overall Recommendation:</strong> {result.composite_trust_score.recommendation}
          </p>
        </div>
      </div>

      {/* Detailed breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <h5 className="font-medium text-secondary-800 mb-2">📝 Textual Analysis</h5>
          {renderTextAnalysis(result.textual_analysis)}
        </div>
        
        {result.media_analysis && (
          <div>
            <h5 className="font-medium text-secondary-800 mb-2">🎥 Media Analysis</h5>
            {renderMediaAnalysis(result.media_analysis)}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <>
      {ENABLE_NEWSPAPER_BORDERS && <NewspaperBorders />}
      <div className={`min-h-screen newspaper-bg ${ENABLE_NEWSPAPER_BORDERS ? 'pt-10 pb-10 pl-8 pr-8' : ''}`}>
        <div className="max-w-[1400px] mx-auto px-6">
        <div className="text-center mb-8">
        <div className="newspaper-header text-center py-8 mb-8">
          <div className="border-t-4 border-b-4 border-black py-4 mx-4">
            <h1 className="newspaper-title text-5xl font-black text-black mb-2 tracking-tight">
              THE ATIE VERIFICATION CENTER
            </h1>
            <div className="flex justify-center items-center space-x-8 text-sm font-semibold text-black">
              <span>TRUTH DETECTION BUREAU</span>
              <span className="border-l border-r border-black px-4">AI-POWERED INTEGRITY</span>
              <span>EST. 2025</span>
            </div>
          </div>
          <div className="mt-4">
            <p className="newspaper-subtitle text-lg font-semibold text-black max-w-3xl mx-auto italic">
              "Comprehensive News and Media Integrity Verification - Your Digital Truth Detector"
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Analysis Type Selection */}
        <div className="lg:col-span-3">
          <div className="newspaper-section">
            <h2 className="newspaper-section-title text-2xl font-black text-black border-b-2 border-black pb-2 mb-4 uppercase tracking-wide">Analysis Configuration</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <label className="flex items-center p-3 border-2 border-black bg-white cursor-pointer hover:bg-gray-50 newspaper-card">
                <input
                  type="radio"
                  value="media"
                  checked={analysisType === 'media'}
                  onChange={(e) => setAnalysisType(e.target.value as any)}
                  className="mr-3"
                />
                <div>
                  <div className="font-black text-black uppercase tracking-wide">🎥 Media Only</div>
                  <div className="text-sm text-black font-medium">Metadata analysis & visual verification</div>
                </div>
              </label>

              <label className="flex items-center p-3 border-2 border-black bg-white cursor-pointer hover:bg-gray-50 newspaper-card">
                <input
                  type="radio"
                  value="text"
                  checked={analysisType === 'text'}
                  onChange={(e) => setAnalysisType(e.target.value as any)}
                  className="mr-3"
                />
                <div>
                  <div className="font-black text-black uppercase tracking-wide">📝 Text Only</div>
                  <div className="text-sm text-black font-medium">Fake news detection & bias analysis</div>
                </div>
              </label>

              <label className="flex items-center p-3 border-2 border-black bg-white cursor-pointer hover:bg-gray-50 newspaper-card">
                <input
                  type="radio"
                  value="composite"
                  checked={analysisType === 'composite'}
                  onChange={(e) => setAnalysisType(e.target.value as any)}
                  className="mr-3"
                />
                <div>
                  <div className="font-black text-black uppercase tracking-wide">🔍 Composite</div>
                  <div className="text-sm text-black font-medium">Combined media + text analysis</div>
                </div>
              </label>
            </div>
          </div>
        </div>

        {/* Media Upload Section */}
        {(analysisType === 'media' || analysisType === 'composite') && (
          <div className="newspaper-section">
            <h2 className="newspaper-section-title text-xl font-black text-black border-b-2 border-black pb-2 mb-4 uppercase tracking-wide">📁 Media Upload</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Media Type
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
                  className="input-field"
                />
              </div>

              {selectedFile && (
                <div className="bg-secondary-50 rounded-lg p-3">
                  <p className="font-medium text-secondary-900">{selectedFile.name}</p>
                  <p className="text-sm text-secondary-600">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB • {selectedFile.type}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Text Input Section */}
        {(analysisType === 'text' || analysisType === 'composite') && (
          <div className="newspaper-section lg:col-span-2">
            <h2 className="newspaper-section-title text-xl font-black text-black border-b-2 border-black pb-2 mb-4 uppercase tracking-wide">📝 Text Content</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Source URL (Optional)
                </label>
                <input
                  type="url"
                  value={sourceUrl}
                  onChange={(e) => setSourceUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Article Content *
                </label>
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Paste the article content, headlines, or text you want to analyze for misinformation, bias, and integrity..."
                  rows={8}
                  className="input-field"
                />
                <div className="text-sm text-secondary-500 mt-1">
                  {textContent.length} characters
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Fact Check Document */}
      <div className="newspaper-section mb-6">
        <h2 className="newspaper-section-title text-xl font-black text-black border-b-2 border-black pb-2 mb-4 uppercase tracking-wide">📄 Fact Check a Document</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-secondary-700 mb-2">Upload PDF or TXT</label>
            <input type="file" accept="application/pdf,text/plain,.txt" onChange={handleDocumentSelect} className="input-field" />
            {documentFile && (
              <div className="text-xs text-secondary-600 mt-1">{documentFile.name}</div>
            )}
          </div>
          <button
            onClick={handleFactCheckDocument}
            disabled={isAnalyzing || !documentFile}
            className="bg-black text-white font-black uppercase tracking-widest px-6 py-3 border-4 border-black hover:bg-gray-800 transition-colors text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🔎 Fact Check Document
          </button>
        </div>
      </div>

      {/* Analysis Button */}
      <div className="text-center mb-8">
        <button
          onClick={handleAnalyze}
          disabled={isAnalyzing || (!selectedFile && analysisType === 'media') || (!textContent.trim() && (analysisType === 'text' || analysisType === 'composite'))}
          className="bg-black text-white font-black uppercase tracking-widest px-12 py-4 border-4 border-black hover:bg-gray-800 transition-colors text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAnalyzing ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analyzing...
            </span>
          ) : (
            `🔍 Analyze ${analysisType === 'media' ? 'Media' : analysisType === 'text' ? 'Text' : 'Content'}`
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results Display */}
      {mediaResult && analysisType === 'media' && renderMediaAnalysis(mediaResult)}
      {docReport && (
        <div className="bg-white rounded-lg border border-secondary-200 p-4 mb-4">
          <h4 className="font-semibold text-secondary-900 mb-2">Document Report</h4>
          <div className="text-sm text-secondary-700 mb-2">File: {docReport.filename} • Pages: {docReport.page_count ?? 'N/A'} • Characters: {docReport.character_count}</div>
          <div className="p-3 bg-secondary-50 rounded max-h-64 overflow-auto whitespace-pre-wrap text-xs">
            {docReport.preview}
          </div>
        </div>
      )}
      {textResult && analysisType === 'text' && renderTextAnalysis(textResult)}
      {compositeResult && analysisType === 'composite' && renderCompositeAnalysis(compositeResult)}
      </div>
      </div>
    </>
  );
};

export default EnhancedMediaVerification;