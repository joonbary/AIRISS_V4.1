import React from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
}

// 인증 비활성화 - 모든 라우트가 public
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // 인증 체크 없이 바로 렌더링
  return <>{children}</>;
};

export default ProtectedRoute;