import React, { useState } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import NewspaperBorders from '../Layout/NewspaperBorders';
import { ENABLE_NEWSPAPER_BORDERS } from '../../utils/newspaperBorders';
import './PolicyDashboard.css';

interface Policy {
  id: number;
  title: string;
  category: string;
  ai_summary: string;
  status: string;
  created_at: string;
}

interface SentimentData {
  positive_score: number;
  negative_score: number;
  neutral_score: number;
  total_comments: number;
}

interface PolicyAnalysis {
  title: string;
  summary: string;
  key_points: string[];
  structure: string;
  sentiment: {
    label: string;
    score: number;
  };
}

const PolicyDashboard: React.FC = () => {
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [newComment, setNewComment] = useState('');
  const [isSubmittingComment, setIsSubmittingComment] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [policyAnalysis, setPolicyAnalysis] = useState<PolicyAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<'policies' | 'upload'>('policies');

  // Mock data for demonstration
  const mockPolicies: Policy[] = [
    {
      id: 1,
      title: "Urban Green Spaces Development Initiative",
      category: "Environment",
      ai_summary: "• Proposes creation of 15 new public parks across the city over next 3 years\n• Allocates $50M budget for land acquisition and development\n• Establishes community involvement programs for park design and maintenance",
      status: "active",
      created_at: "2025-10-25T00:00:00Z"
    },
    {
      id: 2,
      title: "Digital Infrastructure Modernization Plan",
      category: "Technology",
      ai_summary: "• Upgrades city-wide fiber optic network to support 5G technology\n• Implements smart city sensors for traffic, air quality, and energy monitoring\n• Provides free public Wi-Fi in all municipal buildings and parks",
      status: "active",
      created_at: "2025-10-20T00:00:00Z"
    },
    {
      id: 3,
      title: "Affordable Housing Development Strategy",
      category: "Housing",
      ai_summary: "• Mandates 20% affordable housing units in new residential developments\n• Creates $100M housing assistance fund for first-time homebuyers\n• Establishes rent stabilization measures for existing tenants",
      status: "active",
      created_at: "2025-10-15T00:00:00Z"
    }
  ];

  const mockSentimentData: { [key: number]: SentimentData } = {
    1: { positive_score: 0.65, negative_score: 0.20, neutral_score: 0.15, total_comments: 127 },
    2: { positive_score: 0.45, negative_score: 0.35, neutral_score: 0.20, total_comments: 89 },
    3: { positive_score: 0.55, negative_score: 0.30, neutral_score: 0.15, total_comments: 203 }
  };

  const handlePolicyClick = (policy: Policy) => {
    setSelectedPolicy(policy);
  };

  const handleSubmitComment = async () => {
    if (!newComment.trim() || !selectedPolicy) return;

    setIsSubmittingComment(true);
    
    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Simulate sentiment analysis result
      alert(`Comment analyzed! Sentiment: ${Math.random() > 0.5 ? 'Positive' : 'Negative'}`);
      setNewComment('');
    } catch (error) {
      alert('Failed to submit comment');
    } finally {
      setIsSubmittingComment(false);
    }
  };

  const getSentimentChartData = (sentiment: SentimentData) => [
    { name: 'Positive', value: Math.round(sentiment.positive_score * 100), color: '#10b981' },
    { name: 'Negative', value: Math.round(sentiment.negative_score * 100), color: '#ef4444' },
    { name: 'Neutral', value: Math.round(sentiment.neutral_score * 100), color: '#6b7280' }
  ];

  const getOverallSentimentData = () => {
    return mockPolicies.map(policy => ({
      name: policy.title.slice(0, 20) + '...',
      positive: Math.round(mockSentimentData[policy.id].positive_score * 100),
      negative: Math.round(mockSentimentData[policy.id].negative_score * 100),
      neutral: Math.round(mockSentimentData[policy.id].neutral_score * 100),
      comments: mockSentimentData[policy.id].total_comments
    }));
  };

  const getDominantSentiment = (sentiment: SentimentData) => {
    const scores = {
      positive: sentiment.positive_score,
      negative: sentiment.negative_score,
      neutral: sentiment.neutral_score
    };
    
    return Object.keys(scores).reduce((a, b) => scores[a as keyof typeof scores] > scores[b as keyof typeof scores] ? a : b);
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-600 bg-green-100';
      case 'negative': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
      setPolicyAnalysis(null);
    } else {
      alert('Please select a valid PDF file');
    }
  };

  const handlePDFAnalysis = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setPolicyAnalysis(null);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/api/v1/policy/summarize', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to analyze PDF');
      }

      const result = await response.json();
      
      // Transform API response to match PolicyAnalysis interface
      setPolicyAnalysis({
        title: result.filename || 'Policy Document',
        summary: result.summary || 'No summary available',
        key_points: result.key_points || [],
        structure: `${result.metadata?.total_pages || 0} pages, ${result.metadata?.word_count || 0} words`,
        sentiment: {
          label: 'Neutral',
          score: 0.5
        }
      });
    } catch (error: any) {
      console.error('Error analyzing PDF:', error);
      alert(error.message || 'An error occurred while analyzing the PDF. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const clearUpload = () => {
    setSelectedFile(null);
    setPolicyAnalysis(null);
  };

  return (
    <>
      {ENABLE_NEWSPAPER_BORDERS && <NewspaperBorders />}
      <div className={`enhanced-typography policy-container ${ENABLE_NEWSPAPER_BORDERS ? 'pt-10 pb-10 pl-8 pr-8' : ''}`}>
        <div className="max-w-[1400px] mx-auto px-6">
        <div className="policy-header">
          <div className="border-t-4 border-b-4 border-black py-4 mx-4">
            <h1 className="bold-title policy-title">
              THE POLICY HERALD
            </h1>
            <div className="italic-content flex justify-center items-center space-x-8 text-sm font-semibold text-black">
              <span>POLICY ANALYSIS BUREAU</span>
              <span className="border-l border-r border-black px-4">AI-POWERED INSIGHTS</span>
              <span>EST. 2025</span>
            </div>
          </div>
          <div className="mt-4">
            <p className="italic-content policy-subtitle">
              "Your Digital Policy Navigator - AI-Enhanced Public Sentiment Analysis"
            </p>
          </div>
        </div>
        
        {/* Tab Navigation */}
        <div className="flex justify-center mt-6">
          <div className="flex bg-secondary-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('policies')}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                activeTab === 'policies'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              📋 Active Policies
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-6 py-2 rounded-md font-medium transition-all ${
                activeTab === 'upload'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-secondary-600 hover:text-secondary-900'
              }`}
            >
              📄 Upload PDF Policy
            </button>
          </div>
        </div>
      </div>

      {activeTab === 'policies' ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Policy List */}
          <div className="lg:col-span-1">
            <div className="card">
              <h2 className="bold-title text-xl font-semibold text-secondary-900 mb-4">Active Policies</h2>
            <div className="space-y-3">
              {mockPolicies.map((policy) => {
                const sentiment = mockSentimentData[policy.id];
                const dominantSentiment = getDominantSentiment(sentiment);
                
                return (
                  <div
                    key={policy.id}
                    onClick={() => handlePolicyClick(policy)}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      selectedPolicy?.id === policy.id
                        ? 'border-primary-300 bg-primary-50'
                        : 'border-secondary-200 hover:border-primary-200 hover:bg-primary-25'
                    }`}
                  >
                    <h3 className="bold-title font-medium text-secondary-900 mb-2 line-clamp-2">
                      {policy.title}
                    </h3>
                    <div className="flex items-center justify-between text-sm">
                      <span className="italic-content px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        {policy.category}
                      </span>
                      <span className={`italic-content px-2 py-1 rounded text-xs font-medium ${getSentimentColor(dominantSentiment)}`}>
                        {dominantSentiment.charAt(0).toUpperCase() + dominantSentiment.slice(1)}
                      </span>
                    </div>
                    <div className="italic-content mt-2 text-xs text-secondary-500">
                      {sentiment.total_comments} public comments
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Overall Sentiment Chart */}
          <div className="card mt-6">
            <h3 className="bold-title text-lg font-semibold text-secondary-900 mb-4">Policy Sentiment Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getOverallSentimentData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" fontSize={12} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="positive" fill="#10b981" name="Positive %" />
                <Bar dataKey="negative" fill="#ef4444" name="Negative %" />
                <Bar dataKey="neutral" fill="#6b7280" name="Neutral %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Policy Details */}
        <div className="lg:col-span-2">
          {selectedPolicy ? (
            <div className="space-y-6">
              {/* Policy Header */}
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h2 className="bold-title text-2xl font-bold text-secondary-900 mb-2">
                      {selectedPolicy.title}
                    </h2>
                    <div className="flex items-center gap-3">
                      <span className="italic-content px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                        {selectedPolicy.category}
                      </span>
                      <span className="italic-content px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                        {selectedPolicy.status.charAt(0).toUpperCase() + selectedPolicy.status.slice(1)}
                      </span>
                    </div>
                  </div>
                  <div className="italic-content text-sm text-secondary-500 ml-4">
                    Published {new Date(selectedPolicy.created_at).toLocaleDateString()}
                  </div>
                </div>

                {/* AI Summary */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <div className="flex items-center mb-3">
                    <div className="text-2xl mr-3">🤖</div>
                    <h3 className="bold-title font-semibold text-blue-900">AI-Generated Summary</h3>
                  </div>
                  <div className="italic-content text-blue-800 whitespace-pre-line">
                    {selectedPolicy.ai_summary}
                  </div>
                </div>
              </div>

              {/* Sentiment Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Sentiment Chart */}
                <div className="card">
                  <h3 className="bold-title text-lg font-semibold text-secondary-900 mb-4">Public Sentiment</h3>
                  <div className="h-64 flex items-center justify-center">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={getSentimentChartData(mockSentimentData[selectedPolicy.id])}
                          cx="50%"
                          cy="50%"
                          outerRadius={80}
                          dataKey="value"
                          label={(entry) => `${entry.name}: ${entry.value}%`}
                        >
                          {getSentimentChartData(mockSentimentData[selectedPolicy.id]).map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Sentiment Stats */}
                <div className="card">
                  <h3 className="bold-title text-lg font-semibold text-secondary-900 mb-4">Sentiment Statistics</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="italic-content text-secondary-700">Total Comments</span>
                      <span className="font-semibold text-secondary-900">
                        {mockSentimentData[selectedPolicy.id].total_comments}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="italic-content text-green-700">Positive</span>
                        <span className="font-semibold text-green-700">
                          {Math.round(mockSentimentData[selectedPolicy.id].positive_score * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${mockSentimentData[selectedPolicy.id].positive_score * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="italic-content text-red-700">Negative</span>
                        <span className="font-semibold text-red-700">
                          {Math.round(mockSentimentData[selectedPolicy.id].negative_score * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-red-500 h-2 rounded-full"
                          style={{ width: `${mockSentimentData[selectedPolicy.id].negative_score * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="italic-content text-gray-700">Neutral</span>
                        <span className="font-semibold text-gray-700">
                          {Math.round(mockSentimentData[selectedPolicy.id].neutral_score * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-gray-500 h-2 rounded-full"
                          style={{ width: `${mockSentimentData[selectedPolicy.id].neutral_score * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Add Comment */}
              <div className="card">
                <h3 className="bold-title text-lg font-semibold text-secondary-900 mb-4">Add Your Comment</h3>
                <div className="space-y-4">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Share your thoughts on this policy. Our AI will analyze the sentiment of your comment in real-time."
                    className="input-field resize-none"
                    rows={4}
                  />
                  <div className="flex justify-between items-center">
                    <div className="italic-content text-sm text-secondary-600">
                      💡 Your comment will be analyzed for sentiment using multilingual AI
                    </div>
                    <button
                      onClick={handleSubmitComment}
                      disabled={!newComment.trim() || isSubmittingComment}
                      className="btn-primary"
                    >
                      {isSubmittingComment ? (
                        <span className="flex items-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Analyzing...
                        </span>
                      ) : (
                        'Submit Comment'
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="card text-center py-12">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="bold-title text-xl font-semibold text-secondary-900 mb-2">Select a Policy</h3>
              <p className="italic-content text-secondary-600 mb-6">
                Choose a policy from the left panel to view AI summaries and sentiment analysis
              </p>
              
              <div className="bg-secondary-50 rounded-lg p-6 max-w-md mx-auto">
                <h4 className="bold-title font-medium text-secondary-900 mb-3">AI Features Available</h4>
                <ul className="italic-content text-sm text-secondary-600 space-y-2 text-left">
                  <li>• Automated policy summarization using BART</li>
                  <li>• Multilingual sentiment analysis with XLM-R</li>
                  <li>• Real-time public opinion monitoring</li>
                  <li>• Interactive sentiment visualization</li>
                  <li>• Comment analysis and classification</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
      ) : (
        /* PDF Upload Section */
        <div className="max-w-4xl mx-auto">
          <div className="card mb-8">
            <h2 className="bold-title text-2xl font-bold text-secondary-900 mb-6 text-center">📄 PDF Policy Analysis</h2>
            
            {!selectedFile ? (
              <div className="text-center py-12 border-2 border-dashed border-secondary-300 rounded-lg">
                <div className="text-6xl mb-4">📁</div>
                <h3 className="bold-title text-xl font-semibold text-secondary-900 mb-4">Upload Policy PDF</h3>
                <p className="italic-content text-secondary-600 mb-6 max-w-md mx-auto">
                  Upload a PDF policy document to get AI-powered analysis including summaries, 
                  key points extraction, and sentiment evaluation.
                </p>
                
                <div className="space-y-4">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="pdf-upload"
                  />
                  <label
                    htmlFor="pdf-upload"
                    className="inline-block btn-primary cursor-pointer"
                  >
                    📤 Select PDF File
                  </label>
                  
                  <div className="text-sm text-secondary-500">
                    Maximum file size: 10MB • Supported format: PDF
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* File Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="text-2xl mr-3">📄</div>
                      <div>
                        <div className="font-medium text-blue-900">{selectedFile.name}</div>
                        <div className="text-sm text-blue-700">
                          {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handlePDFAnalysis}
                        disabled={isAnalyzing}
                        className="btn-primary"
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
                          '🤖 Analyze with AI'
                        )}
                      </button>
                      <button
                        onClick={clearUpload}
                        className="px-4 py-2 text-secondary-600 hover:text-secondary-800 border border-secondary-300 rounded-md hover:bg-secondary-50"
                      >
                        Clear
                      </button>
                    </div>
                  </div>
                </div>

                {/* Analysis Results */}
                {policyAnalysis && (
                  <div className="space-y-6">
                    {/* Title and Summary */}
                    <div className="card">
                      <h3 className="text-xl font-bold text-secondary-900 mb-4">
                        {policyAnalysis.title || 'Policy Document Analysis'}
                      </h3>
                      
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6 mb-6">
                        <div className="flex items-start">
                          <div className="text-2xl mr-3">🤖</div>
                          <div>
                            <h4 className="font-semibold text-blue-900 mb-3">AI-Generated Summary</h4>
                            <p className="text-blue-800 leading-relaxed">{policyAnalysis.summary}</p>
                          </div>
                        </div>
                      </div>

                      {/* Sentiment Analysis */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div className="bg-secondary-50 rounded-lg p-4">
                          <h4 className="font-semibold text-secondary-900 mb-3">📊 Sentiment Analysis</h4>
                          <div className="flex items-center justify-between">
                            <span className="text-secondary-700">Overall Sentiment:</span>
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                              policyAnalysis.sentiment.label.toLowerCase() === 'positive' 
                                ? 'bg-green-100 text-green-800'
                                : policyAnalysis.sentiment.label.toLowerCase() === 'negative'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-gray-100 text-gray-800'
                            }`}>
                              {policyAnalysis.sentiment.label} ({(policyAnalysis.sentiment.score * 100).toFixed(1)}%)
                            </span>
                          </div>
                        </div>

                        <div className="bg-secondary-50 rounded-lg p-4">
                          <h4 className="font-semibold text-secondary-900 mb-3">📋 Document Structure</h4>
                          <p className="text-secondary-700 text-sm">{policyAnalysis.structure}</p>
                        </div>
                      </div>

                      {/* Key Points */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <h4 className="font-semibold text-green-900 mb-4">🎯 Key Points Extracted</h4>
                        <ul className="space-y-2">
                          {policyAnalysis.key_points.map((point, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-green-600 mr-2 mt-1">•</span>
                              <span className="text-green-800">{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* PDF Analysis Features */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl text-white p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">🤖 AI-Powered PDF Analysis</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="text-3xl mb-2">📄</div>
                  <h3 className="font-semibold mb-2">Text Extraction</h3>
                  <p className="text-sm opacity-90">
                    Advanced PDF parsing with PyPDF2 and pdfplumber for comprehensive text extraction
                  </p>
                </div>
                <div>
                  <div className="text-3xl mb-2">📝</div>
                  <h3 className="font-semibold mb-2">BART Summarization</h3>
                  <p className="text-sm opacity-90">
                    Generates concise summaries and extracts key policy points automatically
                  </p>
                </div>
                <div>
                  <div className="text-3xl mb-2">😊</div>
                  <h3 className="font-semibold mb-2">Sentiment Analysis</h3>
                  <p className="text-sm opacity-90">
                    RoBERTa-based sentiment evaluation to understand policy tone and implications
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Technology Information */}
      <div className="mt-8 bg-gradient-to-r from-primary-600 to-blue-600 rounded-xl text-white p-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Advanced NLP Technology</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-3xl mb-2">📝</div>
              <h3 className="font-semibold mb-2">BART Summarization</h3>
              <p className="text-sm opacity-90">
                Automatically generates concise 3-point summaries from complex policy documents
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">🌍</div>
              <h3 className="font-semibold mb-2">Multilingual Sentiment</h3>
              <p className="text-sm opacity-90">
                XLM-RoBERTa model analyzes sentiment across multiple languages and dialects
              </p>
            </div>
            <div>
              <div className="text-3xl mb-2">📊</div>
              <h3 className="font-semibold mb-2">Real-time Analysis</h3>
              <p className="text-sm opacity-90">
                Continuous monitoring and updating of public sentiment as new comments arrive
              </p>
            </div>
          </div>
        </div>
        </div>
      </div>
    </>
  );
};

export default PolicyDashboard;