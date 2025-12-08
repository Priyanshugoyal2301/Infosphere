import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ReaderProvider, useReader } from "./contexts/ReaderContext";
import ReaderMode from "./components/Accessibility/ReaderMode";
import Navbar from "./components/Layout/Navbar";
import Footer from "./components/Layout/Footer";
import LandingPage from "./components/Landing/LandingPage";
import Dashboard from "./components/Dashboard/Dashboard";
import ViewReports from "./components/Admin/ViewReports";
import ReportIssue from "./components/Issues/ReportIssue";
import Analytics from "./components/Analytics/Analytics";
import MySubmissions from "./components/Issues/MySubmissions";
import EnhancedMediaVerification from "./components/Media/EnhancedMediaVerification";
import PolicyDashboard from "./components/Policy/PolicyDashboard";
import RealTimeNews from "./components/News/RealTimeNews";
import FlaggedNews from "./components/News/FlaggedNews";
import AdvancedVerificationDashboard from "./components/Verification/AdvancedVerificationDashboard";
import "./App.css";

function AppContent() {
  const { isReaderOpen, closeReaderMode, currentArticle } = useReader();

  return (
    <>
      <div className="min-h-screen bg-secondary-50 overflow-x-hidden">
        <Navbar />
        <main className="max-w-[1600px] mx-auto px-2 sm:px-4 lg:px-6 py-4 sm:py-6 lg:py-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/admin/reports" element={<ViewReports />} />
            <Route path="/report" element={<ReportIssue />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/verify" element={<EnhancedMediaVerification />} />
            <Route path="/my-submissions" element={<MySubmissions />} />
            <Route path="/policy" element={<PolicyDashboard />} />
            <Route path="/news" element={<RealTimeNews />} />
            <Route path="/flagged-news" element={<FlaggedNews />} />
            <Route
              path="/advanced-verification"
              element={<AdvancedVerificationDashboard />}
            />
          </Routes>
        </main>
        <Footer />
      </div>

      {/* Reader Mode - Renders on top of everything */}
      <ReaderMode
        isOpen={isReaderOpen}
        onClose={closeReaderMode}
        article={currentArticle || undefined}
      />
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <ReaderProvider>
        <Router>
          <AppContent />
        </Router>
      </ReaderProvider>
    </AuthProvider>
  );
}

export default App;
