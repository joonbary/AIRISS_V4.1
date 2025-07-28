import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import DashboardLayout from '../Layout/DashboardLayout';

const History: React.FC = () => {
  return (
    <DashboardLayout>
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Typography variant="h4" gutterBottom>
            분석 이력
          </Typography>
          <Typography variant="body1" color="text.secondary">
            분석 이력 기능은 준비 중입니다.
          </Typography>
        </Box>
      </Container>
    </DashboardLayout>
  );
};

export default History; 