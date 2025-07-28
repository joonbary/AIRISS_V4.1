import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const OK_ORANGE = "#ff8200";

function AuthDisabled() {
  const navigate = useNavigate();

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'center', 
      background: `linear-gradient(135deg, ${OK_ORANGE} 0%, #fff7e6 100%)` 
    }}>
      <Box sx={{ textAlign: 'center', p: 4, bgcolor: 'white', borderRadius: 2, boxShadow: 3 }}>
        <Typography variant="h4" gutterBottom>
          인증이 비활성화되었습니다
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          이 버전은 로그인이 필요하지 않습니다.
          <br />
          바로 대시보드로 이동하세요.
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/dashboard')}
          sx={{ 
            background: OK_ORANGE, 
            '&:hover': { background: '#e67300' } 
          }}
        >
          대시보드로 이동
        </Button>
      </Box>
    </Box>
  );
}

export default AuthDisabled;