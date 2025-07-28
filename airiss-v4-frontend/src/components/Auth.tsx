import React from 'react';
import { Box, Typography, Button, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import '../App.css';

const OK_ORANGE = "#ff8200";

// 인증 비활성화 버전
function Auth() {
  const navigate = useNavigate();
  
  // 자동으로 대시보드로 리다이렉트
  React.useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 2000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      background: `linear-gradient(135deg, ${OK_ORANGE} 0%, #fff7e6 100%)` 
    }}>
      <Card sx={{ maxWidth: 600, boxShadow: 6, borderRadius: 3, p: 2 }}>
        <CardContent sx={{ textAlign: 'center' }}>
          <Box sx={{ mb: 4 }}>
            <img src="/okfn_kr_brown.svg" alt="OK금융그룹 로고" style={{ height: 150, width: 'auto' }} />
          </Box>
          <Typography variant="h4" gutterBottom>
            인증이 비활성화되었습니다
          </Typography>
          <Typography variant="body1" sx={{ mb: 3 }}>
            이 버전은 로그인이 필요하지 않습니다.
            <br />
            잠시 후 대시보드로 이동합니다...
          </Typography>
          <Button 
            variant="contained" 
            onClick={() => navigate('/dashboard')}
            sx={{ 
              background: OK_ORANGE, 
              '&:hover': { background: '#e67300' },
              fontWeight: 700
            }}
          >
            바로 대시보드로 이동
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
}

export default Auth;