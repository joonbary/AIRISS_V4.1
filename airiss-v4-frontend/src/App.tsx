import React, { createContext, useContext, useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard/Dashboard';

// PendingApproval 컴포넌트 임시 구현
function PendingApproval() {
  return <div style={{textAlign:'center',marginTop:80}}><h2>승인 대기 중입니다</h2><p>관리자의 승인을 기다려주세요.</p></div>;
}

// User 타입 예시
interface User {
  email: string;
  name: string;
  isApproved: boolean;
}

interface AuthState {
  isAuthenticated: boolean;
  isApproved: boolean;
  user: User | null;
  loading: boolean;
}

const AuthContext = createContext<{
  state: AuthState;
  setState: React.Dispatch<React.SetStateAction<AuthState>>;
}>({
  state: { isAuthenticated: false, isApproved: false, user: null, loading: true },
  setState: () => {},
});

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    isAuthenticated: false,
    isApproved: false,
    user: null,
    loading: true,
  });

  useEffect(() => {
    // 토큰/유저정보 로드(예시: localStorage)
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        setState({
          isAuthenticated: true,
          isApproved: !!user.isApproved,
          user,
          loading: false,
        });
      } catch {
        setState(s => ({ ...s, loading: false }));
      }
    } else {
      setState(s => ({ ...s, loading: false }));
    }
  }, []);

  return <AuthContext.Provider value={{ state, setState }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { state } = useAuth();
  if (state.loading) return <div>로딩 중...</div>;
  if (!state.isAuthenticated) return <Navigate to="/login" replace />;
  if (!state.isApproved) return <Navigate to="/pending-approval" replace />;
  return <>{children}</>;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true }}>
        <Routes>
          <Route path="/login" element={<Auth />} />
          <Route path="/pending-approval" element={<PendingApproval />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;