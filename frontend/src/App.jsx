import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import AnalysisStudioPage from './pages/AnalysisStudioPage';
import ReportDetailPage from './pages/ReportDetailPage';
import HistoryPage from './pages/HistoryPage';
import ModelPerformancePage from './pages/ModelPerformancePage';
import AboutPage from './pages/AboutPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#080D1B] text-[#F8FAFC] flex flex-col font-sans selection:bg-purple-600/30 selection:text-purple-200">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 pt-8">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/studio" element={<AnalysisStudioPage />} />
            <Route path="/report/:id" element={<ReportDetailPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/models" element={<ModelPerformancePage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
