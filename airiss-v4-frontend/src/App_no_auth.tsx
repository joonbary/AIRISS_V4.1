import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import AdminDashboard from './components/AdminDashboard';
import Profile from './components/Profile';
import FileUpload from './components/Upload/FileUpload';
import AnalysisView from './components/Analysis/AnalysisView';
import AdvancedSearch from './components/Search/AdvancedSearch';
import History from './components/History/History';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true }}>
      <Routes>
        {/* 모든 라우트 Public Access */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/upload" element={<FileUpload />} />
        <Route path="/analysis" element={<AnalysisView />} />
        <Route path="/search" element={<AdvancedSearch />} />
        <Route path="/history" element={<History />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/profile" element={<Profile />} />
        {/* 루트 경로는 대시보드로 */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        {/* 모든 경로를 대시보드로 리다이렉트 */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;