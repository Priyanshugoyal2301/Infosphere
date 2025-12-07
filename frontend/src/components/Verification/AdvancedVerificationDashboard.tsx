import React, { useState, useEffect } from 'react';
import { Shield, Clock, Network, Image, Quote, Activity, AlertTriangle } from 'lucide-react';
import EnhancedVerification from '../Verification/EnhancedVerification';

interface NewsArticle {
  id: number;
  title: string;
  content: string;
  source: string;
  url: string;
  published_date: string;
  category: string;
  image_url?: string;
}

const AdvancedVerificationDashboard: React.FC = () => {
  const [recentNews, setRecentNews] = useState<NewsArticle[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentNews();
  }, []);

  const fetchRecentNews = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/news/articles?limit=10');
      const data = await response.json();
      
      if (data.success) {
        setRecentNews(data.articles || []);
      }
    } catch (error) {
      console.error('Failed to fetch news:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: Clock,
      title: 'Temporal Fact-Checking',
      description: 'Tracks claims over time to detect contradictions and narrative shifts',
      color: 'text-purple-600',
      bg: 'bg-purple-50'
    },
    {
      icon: Quote,
      title: 'Source Citation Analysis',
      description: 'Verifies quotes against official sources (PIB, PM India, RBI, WHO)',
      color: 'text-indigo-600',
      bg: 'bg-indigo-50'
    },
    {
      icon: Image,
      title: 'Image Verification',
      description: 'Analyzes EXIF metadata and detects stock photos or manipulated images',
      color: 'text-green-600',
      bg: 'bg-green-50'
    },
    {
      icon: Network,
      title: 'Network Analysis',
      description: 'Detects circular reporting and calculates source trust scores',
      color: 'text-blue-600',
      bg: 'bg-blue-50'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-[1600px] mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-10 h-10 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Advanced Verification System</h1>
          </div>
          <p className="text-lg text-gray-600">
            Industry-leading fact-checking powered by AI and official source verification
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {features.map((feature, idx) => (
            <div key={idx} className={`${feature.bg} rounded-lg p-6 border border-gray-200`}>
              <feature.icon className={`w-8 h-8 ${feature.color} mb-3`} />
              <h3 className="font-semibold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Stats Banner */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 mb-8 text-white">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-3xl font-bold mb-1">{recentNews.length}</div>
              <div className="text-blue-100">Articles Available</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">7</div>
              <div className="text-blue-100">Verification Methods</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">4</div>
              <div className="text-blue-100">Official Sources</div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <Activity className="w-5 h-5 text-green-300 animate-pulse" />
                <span className="text-green-300 font-semibold">System Active</span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Article List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Articles</h2>
              
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                <div className="space-y-3 max-h-[800px] overflow-y-auto">
                  {recentNews.map((article) => (
                    <div
                      key={article.id}
                      onClick={() => setSelectedArticle(article)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedArticle?.id === article.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 bg-white'
                      }`}
                    >
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                        {article.title}
                      </h3>
                      <div className="space-y-1">
                        <p className="text-xs text-gray-600">
                          <span className="font-medium">Source:</span> {article.source}
                        </p>
                        <p className="text-xs text-gray-600">
                          <span className="font-medium">Category:</span>{' '}
                          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                            {article.category}
                          </span>
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(article.published_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  
                  {recentNews.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      <AlertTriangle className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                      <p>No articles available</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Verification Panel */}
          <div className="lg:col-span-2">
            {selectedArticle ? (
              <EnhancedVerification
                articleUrl={selectedArticle.url}
                title={selectedArticle.title}
                content={selectedArticle.content}
                source={selectedArticle.source}
                imageUrl={selectedArticle.image_url}
                claims={[]}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <Shield className="w-20 h-20 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Select an Article to Verify
                </h3>
                <p className="text-gray-500">
                  Choose an article from the list to run advanced verification analysis
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Information Section */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                <Clock className="w-5 h-5 text-purple-600" />
                <span>Temporal Tracking</span>
              </h3>
              <p className="text-sm text-gray-600">
                We maintain a timeline of all claims made by each source. When a new article is analyzed,
                we check if the source has made contradictory statements in the past 30 days.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                <Quote className="w-5 h-5 text-indigo-600" />
                <span>Official Source Verification</span>
              </h3>
              <p className="text-sm text-gray-600">
                Quotes attributed to government officials are cross-referenced with official websites
                including PIB, PM India, RBI, WHO, and Parliament records.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                <Image className="w-5 h-5 text-green-600" />
                <span>Image Analysis</span>
              </h3>
              <p className="text-sm text-gray-600">
                Images are analyzed for EXIF metadata, stock photo detection, and potential manipulation.
                Future-dated images or missing metadata trigger warnings.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center space-x-2">
                <Network className="w-5 h-5 text-blue-600" />
                <span>Citation Network</span>
              </h3>
              <p className="text-sm text-gray-600">
                We build a citation graph tracking which sources cite each other. Circular reporting
                (Source A cites B, B cites C, C cites A) is detected and penalized.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedVerificationDashboard;
