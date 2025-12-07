import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Article {
  title: string;
  content: string;
  source: string;
  published_date?: string;
  url?: string;
  author?: string;
  image_url?: string;
}

interface ReaderContextType {
  currentArticle: Article | null;
  isReaderOpen: boolean;
  setCurrentArticle: (article: Article | null) => void;
  openReaderMode: (article: Article) => void;
  closeReaderMode: () => void;
}

const ReaderContext = createContext<ReaderContextType | undefined>(undefined);

export const ReaderProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentArticle, setCurrentArticle] = useState<Article | null>(null);
  const [isReaderOpen, setIsReaderOpen] = useState(false);

  const openReaderMode = (article: Article) => {
    setCurrentArticle(article);
    setIsReaderOpen(true);
  };

  const closeReaderMode = () => {
    setIsReaderOpen(false);
    // Keep article in memory briefly in case user wants to reopen
    setTimeout(() => setCurrentArticle(null), 300);
  };

  return (
    <ReaderContext.Provider value={{ 
      currentArticle, 
      isReaderOpen,
      setCurrentArticle, 
      openReaderMode,
      closeReaderMode 
    }}>
      {children}
    </ReaderContext.Provider>
  );
};

export const useReader = () => {
  const context = useContext(ReaderContext);
  if (!context) {
    throw new Error('useReader must be used within a ReaderProvider');
  }
  return context;
};
