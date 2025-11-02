import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';
import Dashboard from './components/Dashboard/Dashboard';
import ReportIssue from './components/Issues/ReportIssue';
import Analytics from './components/Analytics/Analytics';
import MySubmissions from './components/Issues/MySubmissions';
import EnhancedMediaVerification from './components/Media/EnhancedMediaVerification';
import PolicyDashboard from './components/Policy/PolicyDashboard';
import RealTimeNews from './components/News/RealTimeNews';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-secondary-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/report" element={<ReportIssue />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/verify" element={<EnhancedMediaVerification />} />
              <Route path="/my-submissions" element={<MySubmissions />} />
              <Route path="/policy" element={<PolicyDashboard />} />
              <Route path="/news" element={<RealTimeNews />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
