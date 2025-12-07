import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, LineChart, Line, ResponsiveContainer } from 'recharts';
import NewspaperBorders from '../Layout/NewspaperBorders';
import { ENABLE_NEWSPAPER_BORDERS } from '../../utils/newspaperBorders';
import './Analytics.css';

interface NewsSection {
  name: string;
  count: number;
  percentage: number;
  color: string;
  [key: string]: any;
}

interface PredictedNews {
  section: string;
  title: string;
  confidence: number;
  keywords: string[];
  trend: 'rising' | 'stable' | 'declining';
}

interface ModelInfo {
  name: string;
  version: string;
  algorithm: string;
  accuracy: number;
  model_path: string;
}

interface AnalyticsData {
  newsSections: NewsSection[];
  predictedNews: PredictedNews[];
  totalArticles: number;
  trendsData: Array<{
    period: string;
    politics: number;
    sports: number;
    technology: number;
    entertainment: number;
    business: number;
  }>;
}

interface AnalyticsResponse {
  success: boolean;
  data: AnalyticsData;
  model_info: ModelInfo;
  timestamp: string;
  message: string;
}

const Analytics: React.FC = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedSection, setSelectedSection] = useState<string>('all');

  // Mock data with vintage newspaper colors - more visually distinct but faded
  const mockAnalyticsData: AnalyticsData = {
    newsSections: [
      { name: 'Politics', count: 156, percentage: 31.2, color: '#B8860B' }, // Dark goldenrod
      { name: 'Sports', count: 98, percentage: 19.6, color: '#8B4513' },   // Saddle brown
      { name: 'Technology', count: 87, percentage: 17.4, color: '#556B2F' }, // Dark olive green
      { name: 'Entertainment', count: 73, percentage: 14.6, color: '#800080' }, // Purple (faded)
      { name: 'Business', count: 65, percentage: 13.0, color: '#B22222' }, // Fire brick red
      { name: 'Health', count: 21, percentage: 4.2, color: '#2F4F4F' }    // Dark slate gray
    ],
    predictedNews: [
      {
        section: 'Politics',
        title: 'Election Commission announces enhanced security measures',
        confidence: 89.5,
        keywords: ['election', 'security', 'measures', 'commission'],
        trend: 'rising'
      },
      {
        section: 'Sports',
        title: 'Cricket World Cup preparations intensify',
        confidence: 84.2,
        keywords: ['cricket', 'world cup', 'team', 'preparations'],
        trend: 'stable'
      },
      {
        section: 'Technology',
        title: 'AI breakthrough in healthcare diagnostics',
        confidence: 91.7,
        keywords: ['AI', 'healthcare', 'diagnostics', 'breakthrough'],
        trend: 'rising'
      },
      {
        section: 'Entertainment',
        title: 'Bollywood gears up for festive season releases',
        confidence: 76.8,
        keywords: ['bollywood', 'festive', 'releases', 'movies'],
        trend: 'stable'
      },
      {
        section: 'Business',
        title: 'Stock markets show positive trend amid economic recovery',
        confidence: 82.1,
        keywords: ['stock market', 'economic recovery', 'positive trend'],
        trend: 'rising'
      }
    ],
    totalArticles: 500,
    trendsData: [
      { period: 'Week 1', politics: 45, sports: 32, technology: 28, entertainment: 22, business: 18 },
      { period: 'Week 2', politics: 52, sports: 35, technology: 31, entertainment: 25, business: 21 },
      { period: 'Week 3', politics: 48, sports: 38, technology: 29, entertainment: 27, business: 19 },
      { period: 'Week 4', politics: 55, sports: 41, technology: 33, entertainment: 24, business: 23 },
      { period: 'Week 5', politics: 49, sports: 36, technology: 35, entertainment: 26, business: 22 },
      { period: 'Week 6', politics: 58, sports: 39, technology: 32, entertainment: 28, business: 25 },
      { period: 'Week 7', politics: 62, sports: 42, technology: 37, entertainment: 30, business: 27 }
    ]
  };

  const mockModelInfo: ModelInfo = {
    name: 'NewsClassifier',
    version: '2.1.3',
    algorithm: 'Transformer-Based BERT',
    accuracy: 95.2,
    model_path: '/models/news_classifier_v2.1.3.pkl'
  };

  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setAnalyticsData(mockAnalyticsData);
        setModelInfo(mockModelInfo);
      } catch (error) {
        console.error('Error fetching analytics data:', error);
        setAnalyticsData(mockAnalyticsData);
        setModelInfo(mockModelInfo);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  const filteredPredictions = selectedSection === 'all' 
    ? analyticsData?.predictedNews || []
    : analyticsData?.predictedNews.filter(p => p.section.toLowerCase() === selectedSection.toLowerCase()) || [];

  if (loading) {
    return (
      <div className="analytics-container">
        <div className="analytics-loading">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-black"></div>
          <span className="analytics-loading-text">Loading Analytics...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      {ENABLE_NEWSPAPER_BORDERS && <NewspaperBorders />}
      <div className={`enhanced-typography newspaper-bg ${ENABLE_NEWSPAPER_BORDERS ? 'pt-4 pb-4 pl-4 pr-4' : 'py-4'}`}>
        <div className="max-w-[1600px] mx-auto px-4">
          {/* Newspaper Header */}
          <div className="newspaper-header text-center py-4 mb-4">
            <div className="border-t-4 border-b-4 border-black py-4 mx-4">
              <h1 className="bold-title text-6xl font-black text-black mb-2 tracking-tight">
                THE ANALYTICS HERALD
              </h1>
              <div className="italic-content flex justify-center items-center space-x-8 text-sm font-semibold text-black">
                <span>DATA INTELLIGENCE BUREAU</span>
                <span className="border-l border-r border-black px-4">AI-POWERED INSIGHTS</span>
                <span>REAL-TIME ANALYTICS</span>
              </div>
            </div>
            <div className="mt-4">
              <p className="italic-content text-lg font-semibold text-black max-w-3xl mx-auto italic">
                "Comprehensive News Intelligence - Data-Driven Insights & AI-Powered Predictions"
              </p>
            </div>
          </div>

          {/* Statistics Banner */}
          <div className="newspaper-section mb-4">
            <div className="bg-black text-white p-6 border-4 border-black shadow-lg">
              <div className="text-center">
                <div className="bold-title text-2xl font-black uppercase tracking-wide mb-2">📊 ANALYTICS OVERVIEW</div>
                <div className="text-xl font-bold">
                  Total Articles Analyzed: {analyticsData?.totalArticles.toLocaleString()}
                </div>
                <div className="italic-content text-sm opacity-90 italic">Real-time data processing and trend analysis</div>
              </div>
            </div>
          </div>

          <div className="space-y-4 px-4">
            {/* News Distribution and Category Statistics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              <div className="newspaper-section">
                <div className="newspaper-card-header bg-black text-white p-4">
                  <h2 className="bold-title text-xl font-black text-white uppercase tracking-wider">
                    News Distribution by Category
                  </h2>
                </div>
                <div className="p-4">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={analyticsData?.newsSections}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(1)}%`}
                          outerRadius={80}
                          fill="#B8860B"
                          dataKey="count"
                          stroke="#8B4513"
                          strokeWidth={2}
                        >
                          {analyticsData?.newsSections.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} stroke="#8B4513" strokeWidth={1} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: '#f2ebda',
                            border: '2px solid #B8860B',
                            borderRadius: '4px',
                            color: '#8B4513',
                            fontWeight: 'bold'
                          }}
                        />
                        <Legend 
                          wrapperStyle={{
                            color: '#8B4513',
                            fontWeight: 'bold'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Category Statistics */}
              <div className="newspaper-section">
                <div className="newspaper-card-header bg-black text-white p-4">
                  <h3 className="bold-title text-xl font-black text-white uppercase tracking-wider">
                    Category Statistics
                  </h3>
                </div>
                <div className="p-6">
                  <div className="space-y-3">
                    {analyticsData?.newsSections.map((section) => (
                      <div key={section.name} className="flex items-center justify-between p-3 border-2" style={{
                        backgroundColor: 'rgba(212,193,160,0.2)',
                        borderColor: '#B8860B'
                      }}>
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-4 h-4 rounded-full" 
                            style={{ backgroundColor: section.color }}
                          ></div>
                          <span className="bold-title font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>{section.name}</span>
                        </div>
                        <div className="text-right">
                          <div className="font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>{section.count} articles</div>
                          <div className="italic-content text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>{section.percentage}%</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
              {/* Bar Chart - Article Count by Category */}
              <div className="newspaper-section">
                <div className="newspaper-card-header bg-black text-white p-4">
                  <h2 className="bold-title text-xl font-black text-white uppercase tracking-wider">
                    Article Volume by Category
                  </h2>
                </div>
                <div className="p-4">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData?.newsSections}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#8d6e63" opacity={0.3} />
                        <XAxis 
                          dataKey="name" 
                          angle={-45}
                          textAnchor="end"
                          height={60}
                          fontSize={12}
                          tick={{ fill: '#8B4513', fontSize: 12, fontWeight: 'bold' }}
                          axisLine={{ stroke: '#B8860B' }}
                        />
                        <YAxis 
                          tick={{ fill: '#8B4513', fontSize: 12, fontWeight: 'bold' }}
                          axisLine={{ stroke: '#B8860B' }}
                        />
                        <Tooltip 
                          formatter={(value, name) => [`${value} articles`, 'Count']}
                          labelFormatter={(label) => `Category: ${label}`}
                          contentStyle={{
                            backgroundColor: '#f2ebda',
                            border: '2px solid #B8860B',
                            borderRadius: '4px',
                            color: '#8B4513',
                            fontWeight: 'bold'
                          }}
                        />
                        <Bar dataKey="count" fill="#B8860B">
                          {analyticsData?.newsSections.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Trends Chart */}
              <div className="newspaper-section">
                <div className="newspaper-card-header bg-black text-white p-4">
                  <h2 className="bold-title text-xl font-black text-white uppercase tracking-wider">
                    Weekly Trends Analysis
                  </h2>
                </div>
                <div className="p-4">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analyticsData?.trendsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#B8860B" opacity={0.3} />
                        <XAxis 
                          dataKey="period" 
                          tick={{ fill: '#8B4513', fontSize: 12, fontWeight: 'bold' }}
                          axisLine={{ stroke: '#B8860B' }}
                        />
                        <YAxis 
                          tick={{ fill: '#8B4513', fontSize: 12, fontWeight: 'bold' }}
                          axisLine={{ stroke: '#B8860B' }}
                        />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: '#f2ebda',
                            border: '2px solid #B8860B',
                            borderRadius: '4px',
                            color: '#8B4513',
                            fontWeight: 'bold'
                          }}
                        />
                        <Legend 
                          wrapperStyle={{
                            color: '#8B4513',
                            fontWeight: 'bold'
                          }}
                        />
                        <Line type="monotone" dataKey="politics" stroke="#B8860B" strokeWidth={3} name="Politics" />
                        <Line type="monotone" dataKey="sports" stroke="#8B4513" strokeWidth={3} name="Sports" />
                        <Line type="monotone" dataKey="technology" stroke="#556B2F" strokeWidth={3} name="Technology" />
                        <Line type="monotone" dataKey="entertainment" stroke="#800080" strokeWidth={3} name="Entertainment" />
                        <Line type="monotone" dataKey="business" stroke="#B22222" strokeWidth={3} name="Business" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Predicted News Section */}
            <div className="newspaper-section">
              <div className="text-black p-6 border-b-4 border-black" style={{
                background: '#e8dcc8'
              }}>
                <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl">🔮</div>
                    <div>
                      <h2 className="bold-title text-3xl font-black text-black uppercase tracking-wider mb-2">
                        AI-Powered News Predictions
                      </h2>
                      <p className="italic-content text-gray-700 text-sm">
                        Machine Learning algorithms predict emerging news trends
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-gray-700 text-sm font-bold">Filter by Category:</div>
                    <select
                      value={selectedSection}
                      onChange={(e) => setSelectedSection(e.target.value)}
                      className="italic-content px-4 py-3 bg-white text-black font-bold focus:outline-none rounded-lg shadow-lg text-lg min-w-[150px]"
                      style={{
                        border: '3px solid #8d6e63',
                        backgroundColor: '#f2ebda',
                        color: '#5d4037'
                      }}
                    >
                      <option value="all">🌐 All Categories</option>
                      {analyticsData?.newsSections.map(section => (
                        <option key={section.name} value={section.name}>
                          {section.name === 'Politics' && '🏛️'} 
                          {section.name === 'Sports' && '⚽'}
                          {section.name === 'Technology' && '💻'}
                          {section.name === 'Entertainment' && '🎬'}
                          {section.name === 'Business' && '💼'}
                          {section.name === 'Health' && '🏥'}
                          {' '}{section.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <div className="space-y-6">
                  {filteredPredictions.map((prediction, index) => {
                    // Get category color from newsSections data
                    const categoryInfo = analyticsData?.newsSections.find(section => 
                      section.name.toLowerCase() === prediction.section.toLowerCase()
                    );
                    const categoryColor = categoryInfo?.color || '#6B7280';
                    
                    // Confidence color based on percentage - beige/brown tones
                    const getConfidenceColor = (confidence: number) => {
                      if (confidence >= 90) return '#8B7355'; // Dark tan
                      if (confidence >= 80) return '#A0826D'; // Medium tan
                      if (confidence >= 70) return '#B8956A'; // Light tan
                      return '#C4A57B'; // Pale tan
                    };
                    
                    // Trend color and icon - beige/brown tones
                    const getTrendInfo = (trend: string) => {
                      switch (trend) {
                        case 'rising': return { color: '#8B7355', icon: '📈', text: 'Rising' };
                        case 'declining': return { color: '#C4A57B', icon: '📉', text: 'Declining' };
                        default: return { color: '#A0826D', icon: '📊', text: 'Stable' };
                      }
                    };
                    
                    const trendInfo = getTrendInfo(prediction.trend);
                    const confidenceColor = getConfidenceColor(prediction.confidence);
                    
                    return (
                      <div key={index} className="border-3 border-gray-400 bg-white shadow-lg rounded-lg overflow-hidden transform hover:scale-105 transition-all duration-300">
                        {/* Enhanced Header with Category Color */}
                        <div className="px-6 py-4 text-white font-black uppercase tracking-wider text-lg" 
                             style={{ backgroundColor: categoryColor, fontFamily: 'Playfair Display, serif' }}>
                          <div className="flex justify-between items-center">
                            <span className="text-2xl font-black">{prediction.section}</span>
                            <div className="flex items-center space-x-4">
                              {/* Confidence Badge */}
                              <div className="bg-white bg-opacity-20 px-4 py-2 rounded-full flex items-center space-x-2">
                                <span className="text-lg font-bold">🎯</span>
                                <span className="text-lg font-black" style={{ color: confidenceColor }}>
                                  {prediction.confidence}%
                                </span>
                              </div>
                              {/* Trend Badge */}
                              <div className="bg-white bg-opacity-20 px-4 py-2 rounded-full flex items-center space-x-2">
                                <span className="text-lg">{trendInfo.icon}</span>
                                <span className="text-lg font-black" style={{ color: trendInfo.color }}>
                                  {trendInfo.text}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        {/* Enhanced Content */}
                        <div className="p-8">
                          <h4 className="bold-title font-black text-2xl mb-4 text-black leading-tight" 
                              style={{ fontFamily: 'Playfair Display, serif', color: categoryColor }}>
                            {prediction.title}
                          </h4>
                          
                          {/* Enhanced Keywords */}
                          <div className="mt-6">
                            <div className="bold-title text-lg font-bold text-gray-800 mb-3" 
                                 style={{ fontFamily: 'Playfair Display, serif' }}>
                              🔍 Key Topics:
                            </div>
                            <div className="flex flex-wrap gap-3">
                              {prediction.keywords.map((keyword, idx) => (
                                <span key={idx} 
                                      className="italic-content px-4 py-2 text-sm font-bold rounded-full border-2 transform hover:scale-110 transition-transform duration-200" 
                                      style={{ 
                                        backgroundColor: `${categoryColor}15`,
                                        borderColor: categoryColor,
                                        color: categoryColor,
                                        fontFamily: 'Georgia, serif'
                                      }}>
                                  #{keyword}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          {/* Confidence Bar */}
                          <div className="mt-6">
                            <div className="bold-title text-lg font-bold text-gray-800 mb-2" 
                                 style={{ fontFamily: 'Playfair Display, serif' }}>
                              📊 AI Confidence Level:
                            </div>
                            <div className="w-full rounded-full h-4 border-2" style={{
                              backgroundColor: '#e8dcc6',
                              borderColor: '#8d6e63'
                            }}>
                              <div 
                                className="h-full rounded-full transition-all duration-500 ease-out"
                                style={{ 
                                  width: `${prediction.confidence}%`,
                                  backgroundColor: confidenceColor
                                }}
                              ></div>
                            </div>
                            <div className="flex justify-between text-sm font-bold mt-2" style={{ fontFamily: 'Georgia, serif' }}>
                              <span className="italic-content text-gray-600">Prediction Accuracy</span>
                              <span className="font-black" style={{ color: confidenceColor }}>
                                {prediction.confidence}% Confident
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {filteredPredictions.length === 0 && (
                  <div className="italic-content text-center py-4 text-amber-600 font-serif">
                    No predictions available for the selected category.
                  </div>
                )}
              </div>
            </div>

            {/* AI Model Information */}
            <div className="newspaper-section mt-4">
              <div className="newspaper-card-header bg-black text-white p-4">
                <h3 className="bold-title text-xl font-black text-white uppercase tracking-wider text-center">
                  AI Model Information
                </h3>
              </div>
              <div className="p-6">
                {modelInfo ? (
                  <>
                    <div className="bg-white border-2 border-gray-300 p-4 mb-4">
                      <h4 className="bold-title text-lg font-black text-black text-center mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
                        {modelInfo.name} v{modelInfo.version}
                      </h4>
                      <div className="italic-content text-center text-xs text-gray-500" style={{ fontFamily: 'Georgia, serif' }}>
                        Model Path: {modelInfo.model_path}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                      <div className="bg-white border-2 border-gray-300 p-4">
                        <div className="text-lg font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>{modelInfo.algorithm}</div>
                        <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Learning Algorithm</div>
                      </div>
                      <div className="bg-white border-2 border-gray-300 p-4">
                        <div className="text-2xl font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>{modelInfo.accuracy}%</div>
                        <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Model Accuracy</div>
                      </div>
                      <div className="bg-white border-2 border-gray-300 p-4">
                        <div className="text-2xl font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>24/7</div>
                        <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Real-time Analysis</div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                    <div className="bg-white border-2 border-gray-300 p-4">
                      <div className="text-2xl font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>Unsupervised ML</div>
                      <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Learning Algorithm</div>
                    </div>
                    <div className="bg-white border-2 border-gray-300 p-4">
                      <div className="text-2xl font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>95.2%</div>
                      <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Model Accuracy</div>
                    </div>
                    <div className="bg-white border-2 border-gray-300 p-4">
                      <div className="text-2xl font-black text-black" style={{ fontFamily: 'Playfair Display, serif' }}>24/7</div>
                      <div className="italic-content text-sm text-gray-600 italic" style={{ fontFamily: 'Georgia, serif' }}>Real-time Analysis</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Analytics;