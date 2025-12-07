import React, { createContext, useContext, useState, ReactNode } from 'react';

interface Article {
  title: string;
  content: string;
  source: string;
  published_date?: string;
  url?: string;
}

interface ReaderContextType {
  currentArticle: Article | null;
  setCurrentArticle: (article: Article | null) => void;
  openReaderMode: (article: Article) => void;
}

const ReaderContext = createContext<ReaderContextType | undefined>(undefined);

export const ReaderProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentArticle, setCurrentArticle] = useState<Article | null>(null);

  const openReaderMode = (article: Article) => {
    setCurrentArticle(article);
  };

  return (
    <ReaderContext.Provider value={{ currentArticle, setCurrentArticle, openReaderMode }}>
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
