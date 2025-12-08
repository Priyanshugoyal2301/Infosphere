import React, { useState, useEffect } from "react";
import {
  Shield,
  Clock,
  Network,
  Image,
  Quote,
  Activity,
  AlertTriangle,
} from "lucide-react";
import EnhancedVerification from "../Verification/EnhancedVerification";
import NewspaperBorders from "../Layout/NewspaperBorders";
import { ENABLE_NEWSPAPER_BORDERS } from "../../utils/newspaperBorders";

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
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecentNews();
  }, []);

  const fetchRecentNews = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/news/live-news?limit=50"
      );
      const data = await response.json();

      if (data.status === "success") {
        setRecentNews(data.articles || []);
      }
    } catch (error) {
      console.error("Failed to fetch news:", error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: Clock,
      title: "Temporal Fact-Checking",
      description:
        "Tracks claims over time to detect contradictions and narrative shifts",
      color: "text-purple-600",
      bg: "bg-purple-50",
    },
    {
      icon: Quote,
      title: "Source Citation Analysis",
      description:
        "Verifies quotes against official sources (PIB, PM India, RBI, WHO)",
      color: "text-indigo-600",
      bg: "bg-indigo-50",
    },
    {
      icon: Image,
      title: "Image Verification",
      description:
        "Analyzes EXIF metadata and detects stock photos or manipulated images",
      color: "text-green-600",
      bg: "bg-green-50",
    },
    {
      icon: Network,
      title: "Network Analysis",
      description:
        "Detects circular reporting and calculates source trust scores",
      color: "text-blue-600",
      bg: "bg-blue-50",
    },
  ];

  return (
    <div
      className="min-h-screen newspaper-bg py-8"
      style={{ background: "#e8dcc8" }}
    >
      <div className="max-w-[1600px] mx-auto px-4 lg:px-12">
        {/* Header */}
        <div className="mb-8 bg-white border-4 border-black p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Shield className="w-10 h-10 text-black" strokeWidth={2.5} />
            <h1
              className="text-3xl md:text-4xl font-black text-black uppercase tracking-tight"
              style={{ fontFamily: "Playfair Display, Georgia, serif" }}
            >
              Advanced Verification System
            </h1>
          </div>
          <p
            className="text-base md:text-lg text-black font-medium"
            style={{ fontFamily: "Georgia, serif" }}
          >
            Industry-leading fact-checking powered by AI and official source
            verification
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="bg-white p-6 border-4 border-black hover:shadow-lg transition-shadow"
            >
              <feature.icon
                className="w-8 h-8 text-black mb-3"
                strokeWidth={2.5}
              />
              <h3
                className="font-black text-black mb-2 uppercase text-sm"
                style={{ fontFamily: "Georgia, serif" }}
              >
                {feature.title}
              </h3>
              <p
                className="text-sm text-black"
                style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
              >
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Stats Banner */}
        <div className="bg-black border-4 border-black p-6 mb-8 text-white">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div
                className="text-3xl font-black mb-1"
                style={{ fontFamily: "Playfair Display, Georgia, serif" }}
              >
                {recentNews.length}
              </div>
              <div
                className="text-gray-300 uppercase text-xs font-bold"
                style={{ fontFamily: "Georgia, serif" }}
              >
                Articles Available
              </div>
            </div>
            <div>
              <div
                className="text-3xl font-black mb-1"
                style={{ fontFamily: "Playfair Display, Georgia, serif" }}
              >
                7
              </div>
              <div
                className="text-gray-300 uppercase text-xs font-bold"
                style={{ fontFamily: "Georgia, serif" }}
              >
                Verification Methods
              </div>
            </div>
            <div>
              <div
                className="text-3xl font-black mb-1"
                style={{ fontFamily: "Playfair Display, Georgia, serif" }}
              >
                4
              </div>
              <div
                className="text-gray-300 uppercase text-xs font-bold"
                style={{ fontFamily: "Georgia, serif" }}
              >
                Official Sources
              </div>
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <Activity
                  className="w-5 h-5 text-green-400 animate-pulse"
                  strokeWidth={2.5}
                />
                <span
                  className="text-green-400 font-black uppercase text-sm"
                  style={{ fontFamily: "Georgia, serif" }}
                >
                  System Active
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Article List */}
          <div className="lg:col-span-1">
            <div className="bg-white border-4 border-black p-6">
              <h2
                className="text-xl font-black text-black mb-4 uppercase border-b-2 border-black pb-2"
                style={{ fontFamily: "Playfair Display, Georgia, serif" }}
              >
                Recent Articles
              </h2>

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
                      className={`p-4 border-2 border-black cursor-pointer transition-all ${
                        selectedArticle?.id === article.id
                          ? "bg-black text-white"
                          : "bg-white hover:bg-gray-100"
                      }`}
                    >
                      <h3
                        className={`font-bold mb-2 line-clamp-2 ${
                          selectedArticle?.id === article.id
                            ? "text-white"
                            : "text-black"
                        }`}
                        style={{ fontFamily: "Georgia, serif" }}
                      >
                        {article.title}
                      </h3>
                      <div className="space-y-1">
                        <p
                          className={`text-xs ${
                            selectedArticle?.id === article.id
                              ? "text-gray-300"
                              : "text-black"
                          }`}
                        >
                          <span className="font-bold">Source:</span>{" "}
                          {article.source}
                        </p>
                        <p
                          className={`text-xs ${
                            selectedArticle?.id === article.id
                              ? "text-gray-300"
                              : "text-black"
                          }`}
                        >
                          <span className="font-bold">Category:</span>{" "}
                          <span
                            className={`px-2 py-0.5 border border-black font-bold uppercase text-xs ${
                              selectedArticle?.id === article.id
                                ? "bg-white text-black"
                                : "bg-black text-white"
                            }`}
                          >
                            {article.category}
                          </span>
                        </p>
                        <p
                          className={`text-xs ${
                            selectedArticle?.id === article.id
                              ? "text-gray-400"
                              : "text-gray-600"
                          }`}
                        >
                          {new Date(
                            article.published_date
                          ).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}

                  {recentNews.length === 0 && (
                    <div className="text-center py-8 text-black">
                      <AlertTriangle
                        className="w-12 h-12 mx-auto mb-2 text-black"
                        strokeWidth={2.5}
                      />
                      <p
                        className="font-bold"
                        style={{ fontFamily: "Georgia, serif" }}
                      >
                        No articles available
                      </p>
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
              <div className="bg-white border-4 border-black p-12 text-center">
                <Shield
                  className="w-20 h-20 mx-auto mb-4 text-black"
                  strokeWidth={2.5}
                />
                <h3
                  className="text-xl font-black text-black mb-2 uppercase"
                  style={{ fontFamily: "Playfair Display, Georgia, serif" }}
                >
                  Select an Article to Verify
                </h3>
                <p
                  className="text-black font-medium"
                  style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
                >
                  Choose an article from the list to run advanced verification
                  analysis
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Information Section */}
        <div className="mt-8 bg-white border-4 border-black p-6">
          <h2
            className="text-2xl font-black text-black mb-4 uppercase border-b-2 border-black pb-2"
            style={{ fontFamily: "Playfair Display, Georgia, serif" }}
          >
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3
                className="font-black text-black mb-2 flex items-center space-x-2 uppercase text-sm"
                style={{ fontFamily: "Georgia, serif" }}
              >
                <Clock className="w-5 h-5 text-black" strokeWidth={2.5} />
                <span>Temporal Tracking</span>
              </h3>
              <p
                className="text-sm text-black"
                style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
              >
                We maintain a timeline of all claims made by each source. When a
                new article is analyzed, we check if the source has made
                contradictory statements in the past 30 days.
              </p>
            </div>

            <div>
              <h3
                className="font-black text-black mb-2 flex items-center space-x-2 uppercase text-sm"
                style={{ fontFamily: "Georgia, serif" }}
              >
                <Quote className="w-5 h-5 text-black" strokeWidth={2.5} />
                <span>Official Source Verification</span>
              </h3>
              <p
                className="text-sm text-black"
                style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
              >
                Quotes attributed to government officials are cross-referenced
                with official websites including PIB, PM India, RBI, WHO, and
                Parliament records.
              </p>
            </div>

            <div>
              <h3
                className="font-black text-black mb-2 flex items-center space-x-2 uppercase text-sm"
                style={{ fontFamily: "Georgia, serif" }}
              >
                <Image className="w-5 h-5 text-black" strokeWidth={2.5} />
                <span>Image Analysis</span>
              </h3>
              <p
                className="text-sm text-black"
                style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
              >
                Images are analyzed for EXIF metadata, stock photo detection,
                and potential manipulation. Future-dated images or missing
                metadata trigger warnings.
              </p>
            </div>

            <div>
              <h3
                className="font-black text-black mb-2 flex items-center space-x-2 uppercase text-sm"
                style={{ fontFamily: "Georgia, serif" }}
              >
                <Network className="w-5 h-5 text-black" strokeWidth={2.5} />
                <span>Citation Network</span>
              </h3>
              <p
                className="text-sm text-black"
                style={{ fontFamily: "Georgia, serif", fontStyle: "italic" }}
              >
                We build a citation graph tracking which sources cite each
                other. Circular reporting (Source A cites B, B cites C, C cites
                A) is detected and penalized.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Newspaper Borders */}
      {ENABLE_NEWSPAPER_BORDERS && <NewspaperBorders />}
    </div>
  );
};

export default AdvancedVerificationDashboard;
