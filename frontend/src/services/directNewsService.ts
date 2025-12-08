/**
 * Direct News Fetching Service
 * Fetches news directly from APIs without backend caching
 */

const NEWS_API_KEY = "b9332a9838474c4e9f42521e4b2bb197";
const GNEWS_API_KEY = "eda407cf5b208678dcba2187d0ad083c";
const NEWSDATA_API_KEY = "pub_6212126cd950424e9655636edc039ad9";

// CORS proxy for browsers (only use in development/client-side)
const CORS_PROXY = "https://corsproxy.io/?";

interface DirectNewsArticle {
  id?: number;
  title: string;
  content: string;
  source: string;
  category: string;
  published_date: string;
  fetched_date: string;
  url: string;
  image?: string;
  location?: string;
  confidence?: number;
}

/**
 * Fetch news from NewsAPI
 */
async function fetchFromNewsAPI(
  category: string = "general",
  limit: number = 50
): Promise<DirectNewsArticle[]> {
  try {
    const country = "us";
    const apiUrl = `https://newsapi.org/v2/top-headlines?country=${country}&category=${category}&pageSize=${limit}&apiKey=${NEWS_API_KEY}`;
    const url = CORS_PROXY + encodeURIComponent(apiUrl);

    console.log("📰 Fetching from NewsAPI...");
    const response = await fetch(url);

    if (!response.ok) {
      console.error(`NewsAPI HTTP error: ${response.status}`);
      throw new Error(`NewsAPI error: ${response.status}`);
    }

    const data = await response.json();
    console.log("NewsAPI response:", data);

    if (data.status !== "ok" || !data.articles) {
      console.error("Invalid NewsAPI response:", data);
      throw new Error("Invalid NewsAPI response");
    }

    console.log(`✅ NewsAPI returned ${data.articles.length} articles`);
    return data.articles.map((article: any) => ({
      title: article.title || "No title",
      content: article.description || article.content || "No content available",
      source: article.source?.name || "NewsAPI",
      category: category,
      published_date: article.publishedAt || new Date().toISOString(),
      fetched_date: new Date().toISOString(),
      url: article.url || "#",
      image: article.urlToImage,
    }));
  } catch (error) {
    console.error("❌ NewsAPI fetch failed:", error);
    return [];
  }
}

/**
 * Fetch news from GNews
 */
async function fetchFromGNews(
  category: string = "general",
  limit: number = 50
): Promise<DirectNewsArticle[]> {
  try {
    const apiUrl = `https://gnews.io/api/v4/top-headlines?category=${category}&lang=en&max=${limit}&apikey=${GNEWS_API_KEY}`;
    const url = CORS_PROXY + encodeURIComponent(apiUrl);

    console.log("📰 Fetching from GNews...");
    const response = await fetch(url);

    if (!response.ok) {
      console.error(`GNews HTTP error: ${response.status}`);
      throw new Error(`GNews error: ${response.status}`);
    }

    const data = await response.json();
    console.log("GNews response:", data);

    if (!data.articles) {
      console.error("Invalid GNews response:", data);
      throw new Error("Invalid GNews response");
    }

    console.log(`✅ GNews returned ${data.articles.length} articles`);
    return data.articles.map((article: any) => ({
      title: article.title || "No title",
      content: article.description || article.content || "No content available",
      source: article.source?.name || "GNews",
      category: category,
      published_date: article.publishedAt || new Date().toISOString(),
      fetched_date: new Date().toISOString(),
      url: article.url || "#",
      image: article.image,
    }));
  } catch (error) {
    console.error("❌ GNews fetch failed:", error);
    return [];
  }
}

/**
 * Fetch news from NewsData.io
 */
async function fetchFromNewsData(
  category: string = "top",
  limit: number = 50
): Promise<DirectNewsArticle[]> {
  try {
    const url = `https://newsdata.io/api/1/news?apikey=${NEWSDATA_API_KEY}&category=${category}&language=en&size=${limit}`;

    console.log("📰 Fetching from NewsData.io...");
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`NewsData error: ${response.status}`);
    }

    const data = await response.json();

    if (data.status !== "success" || !data.results) {
      throw new Error("Invalid NewsData response");
    }

    return data.results.map((article: any) => ({
      title: article.title || "No title",
      content: article.description || article.content || "No content available",
      source: article.source_id || "NewsData",
      category: article.category?.[0] || category,
      published_date: article.pubDate || new Date().toISOString(),
      fetched_date: new Date().toISOString(),
      url: article.link || "#",
      image: article.image_url,
    }));
  } catch (error) {
    console.error("❌ NewsData fetch failed:", error);
    return [];
  }
}

/**
 * Normalize category names for different APIs
 */
function normalizeCategory(category: string): {
  newsapi: string;
  gnews: string;
  newsdata: string;
} {
  const categoryMap: {
    [key: string]: { newsapi: string; gnews: string; newsdata: string };
  } = {
    all: { newsapi: "general", gnews: "general", newsdata: "top" },
    general: { newsapi: "general", gnews: "general", newsdata: "top" },
    business: { newsapi: "business", gnews: "business", newsdata: "business" },
    technology: {
      newsapi: "technology",
      gnews: "technology",
      newsdata: "technology",
    },
    entertainment: {
      newsapi: "entertainment",
      gnews: "entertainment",
      newsdata: "entertainment",
    },
    sports: { newsapi: "sports", gnews: "sports", newsdata: "sports" },
    science: { newsapi: "science", gnews: "science", newsdata: "science" },
    health: { newsapi: "health", gnews: "health", newsdata: "health" },
  };

  return categoryMap[category.toLowerCase()] || categoryMap["all"];
}

/**
 * Fetch news from all sources and combine results
 */
export async function fetchDirectNews(
  category: string = "all",
  limit: number = 150
): Promise<DirectNewsArticle[]> {
  const categories = normalizeCategory(category);

  console.log("🚀 Starting direct news fetch from all APIs...");

  // Fetch from all APIs in parallel
  const [newsApiArticles, gnewsArticles, newsdataArticles] = await Promise.all([
    fetchFromNewsAPI(categories.newsapi, Math.floor(limit / 3)),
    fetchFromGNews(categories.gnews, Math.floor(limit / 3)),
    fetchFromNewsData(categories.newsdata, Math.floor(limit / 3)),
  ]);

  console.log(
    `Fetched: NewsAPI=${newsApiArticles.length}, GNews=${gnewsArticles.length}, NewsData=${newsdataArticles.length}`
  );

  // Combine all articles
  const allArticles = [
    ...newsApiArticles,
    ...gnewsArticles,
    ...newsdataArticles,
  ];

  if (allArticles.length === 0) {
    console.error("❌ All API sources failed to return articles");
    throw new Error("No articles available from any source");
  }

  // Remove duplicates based on title similarity
  const uniqueArticles = removeDuplicates(allArticles);

  // Sort by published date (newest first)
  uniqueArticles.sort((a, b) => {
    const dateA = new Date(a.published_date).getTime();
    const dateB = new Date(b.published_date).getTime();
    return dateB - dateA;
  });

  console.log(
    `✅ Fetched ${uniqueArticles.length} unique articles from all sources`
  );

  return uniqueArticles.slice(0, limit);
}

/**
 * Remove duplicate articles based on title similarity
 */
function removeDuplicates(articles: DirectNewsArticle[]): DirectNewsArticle[] {
  const seen = new Set<string>();
  const unique: DirectNewsArticle[] = [];

  for (const article of articles) {
    // Create a normalized title for comparison
    const normalizedTitle = article.title
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "")
      .substring(0, 50);

    if (!seen.has(normalizedTitle)) {
      seen.add(normalizedTitle);
      unique.push(article);
    }
  }

  return unique;
}

/**
 * Search news across all APIs
 */
export async function searchDirectNews(
  query: string,
  limit: number = 100
): Promise<DirectNewsArticle[]> {
  try {
    console.log(`🔍 Searching for: "${query}"`);

    // For search, we use NewsAPI's everything endpoint which supports search
    const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(
      query
    )}&pageSize=${limit}&sortBy=publishedAt&apiKey=${NEWS_API_KEY}`;

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Search failed: ${response.status}`);
    }

    const data = await response.json();

    if (data.status !== "ok" || !data.articles) {
      return [];
    }

    return data.articles.map((article: any) => ({
      title: article.title || "No title",
      content: article.description || article.content || "No content available",
      source: article.source?.name || "NewsAPI",
      category: "search",
      published_date: article.publishedAt || new Date().toISOString(),
      fetched_date: new Date().toISOString(),
      url: article.url || "#",
      image: article.urlToImage,
    }));
  } catch (error) {
    console.error("❌ Search failed:", error);
    return [];
  }
}
