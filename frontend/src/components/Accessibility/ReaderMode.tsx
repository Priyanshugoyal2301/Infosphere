import React, { useState, useEffect } from 'react';
import { X, Book, Type, Palette, Minus, Plus, Eye, Moon, Sun, Zap, Volume2, VolumeX } from 'lucide-react';

interface ReaderModeProps {
  isOpen: boolean;
  onClose: () => void;
  article?: {
    title: string;
    content: string;
    source: string;
    published_date?: string;
    url?: string;
    author?: string;
    image_url?: string;
  };
}

const ReaderMode: React.FC<ReaderModeProps> = ({ isOpen, onClose, article }) => {
  const [fontSize, setFontSize] = useState(18);
  const [lineHeight, setLineHeight] = useState(1.8);
  const [fontFamily, setFontFamily] = useState('sans-serif');
  const [colorScheme, setColorScheme] = useState('sepia');
  const [dyslexicFont, setDyslexicFont] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [readingGuide, setReadingGuide] = useState(false);
  const [guidePosition, setGuidePosition] = useState(0);
  const [speechEnabled, setSpeechEnabled] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Color schemes optimized for accessibility
  const colorSchemes = {
    sepia: {
      bg: '#f4ecd8',
      text: '#5c4a33',
      accent: '#8b7355',
      name: 'Sepia (ADHD Friendly)'
    },
    light: {
      bg: '#ffffff',
      text: '#1a1a1a',
      accent: '#3b82f6',
      name: 'Light'
    },
    dark: {
      bg: '#1a1a1a',
      text: '#e5e5e5',
      accent: '#60a5fa',
      name: 'Dark'
    },
    cream: {
      bg: '#fdf6e3',
      text: '#657b83',
      accent: '#b58900',
      name: 'Cream (Low Contrast)'
    },
    highContrast: {
      bg: '#000000',
      text: '#ffff00',
      accent: '#00ff00',
      name: 'High Contrast'
    }
  };

  const currentScheme = colorSchemes[colorScheme as keyof typeof colorSchemes];

  // Text-to-speech functionality
  const toggleSpeech = () => {
    if ('speechSynthesis' in window) {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      } else {
        const utterance = new SpeechSynthesisUtterance(article?.content || '');
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.onend = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utterance);
        setIsSpeaking(true);
      }
    }
  };

  // Cleanup speech on unmount
  useEffect(() => {
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  // ESC key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Mouse tracking for reading guide
  useEffect(() => {
    if (!readingGuide || !isOpen) return;

    const handleMouseMove = (e: MouseEvent) => {
      setGuidePosition(e.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [readingGuide, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[99999] overflow-hidden bg-white">
      {/* Reader Mode Container - Full Screen, No Distractions */}
      <div className="relative h-full w-full flex" style={{ backgroundColor: currentScheme.bg }}>
        {/* Settings Sidebar */}
        <div className="w-80 bg-white shadow-2xl overflow-y-auto border-r-4 border-black z-10">
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between border-b-2 border-black pb-4">
              <div className="flex items-center space-x-2">
                <Book className="w-6 h-6" />
                <h2 className="text-xl font-bold">Reader Access</h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-red-100 rounded border-2 border-red-600 bg-red-50 transition-colors"
                title="Close Reader Mode (ESC)"
              >
                <X className="w-5 h-5 text-red-600" />
              </button>
            </div>

            {/* Font Size */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Type className="w-5 h-5" />
                <label className="font-semibold">Font Size</label>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setFontSize(Math.max(12, fontSize - 2))}
                  className="p-2 border-2 border-black hover:bg-gray-100 rounded transition-colors"
                >
                  <Minus className="w-4 h-4" />
                </button>
                <span className="flex-1 text-center font-mono font-bold">{fontSize}px</span>
                <button
                  onClick={() => setFontSize(Math.min(32, fontSize + 2))}
                  className="p-2 border-2 border-black hover:bg-gray-100 rounded transition-colors"
                >
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Line Spacing */}
            <div className="space-y-3">
              <label className="font-semibold flex items-center space-x-2">
                <Eye className="w-5 h-5" />
                <span>Line Spacing</span>
              </label>
              <input
                type="range"
                min="1.2"
                max="3"
                step="0.1"
                value={lineHeight}
                onChange={(e) => setLineHeight(parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="text-sm text-gray-600 text-center font-mono">{lineHeight.toFixed(1)}</div>
            </div>

            {/* Font Family */}
            <div className="space-y-3">
              <label className="font-semibold">Font Style</label>
              <div className="space-y-2">
                <button
                  onClick={() => { setFontFamily('sans-serif'); setDyslexicFont(false); }}
                  className={`w-full p-3 border-2 border-black text-left transition-colors ${
                    fontFamily === 'sans-serif' && !dyslexicFont ? 'bg-black text-white' : 'hover:bg-gray-100'
                  }`}
                  style={{ fontFamily: 'sans-serif' }}
                >
                  Sans-serif (Clean)
                </button>
                <button
                  onClick={() => { setFontFamily('serif'); setDyslexicFont(false); }}
                  className={`w-full p-3 border-2 border-black text-left transition-colors ${
                    fontFamily === 'serif' && !dyslexicFont ? 'bg-black text-white' : 'hover:bg-gray-100'
                  }`}
                  style={{ fontFamily: 'serif' }}
                >
                  Serif (Traditional)
                </button>
                <button
                  onClick={() => { setFontFamily('monospace'); setDyslexicFont(false); }}
                  className={`w-full p-3 border-2 border-black text-left transition-colors ${
                    fontFamily === 'monospace' && !dyslexicFont ? 'bg-black text-white' : 'hover:bg-gray-100'
                  }`}
                  style={{ fontFamily: 'monospace' }}
                >
                  Monospace (Fixed Width)
                </button>
                <button
                  onClick={() => { setDyslexicFont(true); setFontFamily('Arial'); }}
                  className={`w-full p-3 border-2 border-black text-left transition-colors ${
                    dyslexicFont ? 'bg-black text-white' : 'hover:bg-gray-100'
                  }`}
                >
                  ✨ OpenDyslexic (ADHD/Dyslexia)
                </button>
              </div>
            </div>

            {/* Color Schemes */}
            <div className="space-y-3">
              <div className="flex items-center space-x-2">
                <Palette className="w-5 h-5" />
                <label className="font-semibold">Color Scheme</label>
              </div>
              <div className="space-y-2">
                {Object.entries(colorSchemes).map(([key, scheme]) => (
                  <button
                    key={key}
                    onClick={() => setColorScheme(key)}
                    className={`w-full p-3 border-2 border-black text-left transition-colors ${
                      colorScheme === key ? 'border-4' : ''
                    }`}
                    style={{ 
                      backgroundColor: scheme.bg,
                      color: scheme.text
                    }}
                  >
                    <span className="font-semibold">{scheme.name}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* ADHD-Specific Features */}
            <div className="space-y-3 border-t-2 border-black pt-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-blue-600" />
                <label className="font-semibold">ADHD Support</label>
              </div>
              
              <button
                onClick={() => setFocusMode(!focusMode)}
                className={`w-full p-3 border-2 border-black text-left transition-colors ${
                  focusMode ? 'bg-blue-600 text-white' : 'hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>Focus Mode (Dim Surroundings)</span>
                  <Moon className="w-4 h-4" />
                </div>
              </button>

              <button
                onClick={() => setReadingGuide(!readingGuide)}
                className={`w-full p-3 border-2 border-black text-left transition-colors ${
                  readingGuide ? 'bg-blue-600 text-white' : 'hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>Reading Guide Line</span>
                  <Eye className="w-4 h-4" />
                </div>
              </button>

              {'speechSynthesis' in window && (
                <button
                  onClick={toggleSpeech}
                  className={`w-full p-3 border-2 border-black text-left transition-colors ${
                    isSpeaking ? 'bg-green-600 text-white' : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{isSpeaking ? 'Stop Reading' : 'Read Aloud'}</span>
                    {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </div>
                </button>
              )}
            </div>

            {/* Info */}
            <div className="text-xs text-gray-600 space-y-1 border-t-2 border-gray-200 pt-4">
              <p>💡 <strong>Tip:</strong> Adjust settings to reduce eye strain and improve focus.</p>
              <p>🎯 <strong>ADHD Features:</strong> Focus mode dims everything except text, reading guide helps track lines.</p>
            </div>
          </div>
        </div>

        {/* Reader Content */}
        <div 
          className="flex-1 overflow-y-auto relative"
          style={{
            backgroundColor: currentScheme.bg,
            color: currentScheme.text
          }}
        >
          {/* Floating Close Button */}
          <button
            onClick={onClose}
            className="fixed top-4 right-4 z-20 p-3 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition-all border-2 border-white"
            title="Close Reader Mode (ESC)"
          >
            <X className="w-6 h-6" />
          </button>

          {/* Focus Mode Overlay */}
          {focusMode && (
            <div className="absolute inset-0 pointer-events-none">
              <div 
                className="absolute inset-0"
                style={{
                  background: `linear-gradient(to bottom, 
                    ${currentScheme.bg}00 30%, 
                    ${currentScheme.bg} 40%, 
                    ${currentScheme.bg} 60%, 
                    ${currentScheme.bg}00 70%)`
                }}
              />
            </div>
          )}

          {/* Reading Guide */}
          {readingGuide && (
            <div 
              className="fixed left-0 right-0 h-1 pointer-events-none z-10"
              style={{
                top: `${guidePosition}px`,
                backgroundColor: currentScheme.accent,
                boxShadow: `0 0 20px ${currentScheme.accent}, 0 0 40px ${currentScheme.accent}80`,
                transition: 'top 0.05s ease-out'
              }}
            />
          )}

          <div className="max-w-4xl mx-auto px-8 py-12 pb-24">
            {article ? (
              <article className="space-y-8">
                {/* Article Header */}
                <div className="space-y-4 pb-6 border-b-2" style={{ borderColor: currentScheme.accent }}>
                  <h1 
                    className="font-bold leading-tight break-words"
                    style={{
                      fontSize: `${fontSize + 8}px`,
                      lineHeight: lineHeight,
                      fontFamily: dyslexicFont ? 'OpenDyslexic, Arial, sans-serif' : fontFamily
                    }}
                  >
                    {article.title}
                  </h1>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm opacity-75">
                    <span className="font-semibold">{article.source}</span>
                    {article.author && (
                      <>
                        <span className="hidden sm:inline">•</span>
                        <span>By {article.author}</span>
                      </>
                    )}
                    {article.published_date && (
                      <>
                        <span className="hidden sm:inline">•</span>
                        <span>{new Date(article.published_date).toLocaleDateString('en-US', { 
                          year: 'numeric', 
                          month: 'long', 
                          day: 'numeric' 
                        })}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Featured Image */}
                {article.image_url && (
                  <div className="my-6">
                    <img 
                      src={article.image_url} 
                      alt={article.title}
                      className="w-full h-auto rounded-lg shadow-lg"
                      onError={(e) => {
                        // Hide image if it fails to load
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                )}

                {/* Article Content */}
                <div 
                  className="prose prose-lg max-w-none space-y-4"
                  style={{
                    fontSize: `${fontSize}px`,
                    lineHeight: lineHeight,
                    fontFamily: dyslexicFont ? 'OpenDyslexic, Arial, sans-serif' : fontFamily,
                    color: currentScheme.text
                  }}
                >
                  {article.content.split(/\n+/).map((paragraph, idx) => {
                    const trimmed = paragraph.trim();
                    if (!trimmed) return null;
                    
                    return (
                      <p key={idx} style={{ 
                        marginBottom: `${lineHeight * 1.2}em`,
                        textAlign: 'left',
                        wordWrap: 'break-word',
                        overflowWrap: 'break-word'
                      }}>
                        {trimmed}
                      </p>
                    );
                  })}
                </div>

                {/* Article Footer */}
                {article.url && (
                  <div className="pt-6 border-t-2" style={{ borderColor: currentScheme.accent }}>
                    <a 
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm hover:underline"
                      style={{ color: currentScheme.accent }}
                    >
                      Read original article →
                    </a>
                  </div>
                )}
              </article>
            ) : (
              <div className="text-center py-20">
                <Book className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <h2 className="text-2xl font-bold mb-2">No Article Selected</h2>
                <p className="opacity-75">Select an article to view it in reader mode</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReaderMode;
