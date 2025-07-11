import React, { useState } from 'react';
// Auth functions temporarily disabled for Railway deployment
// import { register, login, getMe, getPendingUsers, approveUser } from '../services/api';

const Auth: React.FC = () => {
  const [message] = useState('Authentication temporarily disabled for deployment');

  // Simplified Auth component for Railway deployment
  return (
    <div style={{ maxWidth: 400, margin: '40px auto', textAlign: 'center' }}>
      <h2>AIRISS v4.0</h2>
      <p>시스템이 준비 중입니다...</p>
      <p style={{ color: 'blue', fontSize: '14px' }}>{message}</p>
      <button 
        onClick={() => window.location.href = '/dashboard'} 
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#1976d2', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        대시보드로 이동
      </button>
    </div>
  );
};

export default Auth;