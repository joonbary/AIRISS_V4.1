import React from 'react';
import { Box, Typography, Chip } from '@mui/material';

const UserInfo: React.FC = () => {
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;

  if (!user) return null;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
      <Typography variant="body1">
        {user.name} ({user.email})
      </Typography>
      {user.is_admin && (
        <Chip label="관리자" color="primary" size="small" />
      )}
    </Box>
  );
};

export default UserInfo; 