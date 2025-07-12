import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../App';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { state } = useAuth();
  if (state.loading) return <div>로딩 중...</div>;
  if (!state.isAuthenticated) return <Navigate to="/login" replace />;
  if (!state.isApproved) return <Navigate to="/pending-approval" replace />;
  return <>{children}</>;
};

export default ProtectedRoute; 