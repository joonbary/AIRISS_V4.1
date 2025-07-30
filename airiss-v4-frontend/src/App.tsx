import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Container, Box } from '@mui/material';
import SimpleNavigation from './components/Layout/SimpleNavigation';
import UnifiedDashboard from './pages/UnifiedDashboard';
import HRDashboard from './pages/HRDashboard';
import EmployeePdfPage from './pages/EmployeePdfPage';

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true }}>
      <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
        <SimpleNavigation />
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Routes>
            {/* AIRISS v4.2 - 간소화된 구조 */}
            <Route path="/" element={<UnifiedDashboard />} />
            <Route path="/hr-dashboard" element={<HRDashboard />} />
            
            {/* PDF 출력 전용 페이지 */}
            <Route path="/employee/:uid/pdf" element={<EmployeePdfPage />} />
            
            {/* 호환성: 기존 경로들을 새 구조로 리다이렉션 */}
            <Route path="/dashboard" element={<Navigate to="/" replace />} />
            <Route path="/analysis" element={<Navigate to="/" replace />} />
            <Route path="/admin" element={<Navigate to="/hr-dashboard" replace />} />
            <Route path="/profile" element={<Navigate to="/hr-dashboard" replace />} />
            
            {/* 잘못된 경로는 AI 분석으로 리다이렉트 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Container>
      </Box>
    </BrowserRouter>
  );
}

// 더미 useAuth (컴파일 에러 방지용)
export function useAuth() {
  return {
    state: {
      isAuthenticated: true,
      isApproved: true,
      user: {
        email: 'public@airiss.com',
        name: 'Public User',
        is_approved: true,
        is_admin: true
      },
      loading: false
    },
    setState: () => {}
  };
}

export default App;