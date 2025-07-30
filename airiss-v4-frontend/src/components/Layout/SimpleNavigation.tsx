/**
 * AIRISS v4.2 간소화된 네비게이션
 * Simplified Navigation for Clean UX
 */
import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Chip,
} from '@mui/material';
import {
  Assessment as AnalysisIcon,
  Dashboard as DashboardIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const SimpleNavigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  

  const menuItems = [
    { 
      path: '/', 
      label: 'AI 분석', 
      icon: <AnalysisIcon />, 
      description: '개인별 평가 업로드 및 분석'
    },
    { 
      path: '/hr-dashboard', 
      label: '경영진 대시보드', 
      icon: <DashboardIcon />, 
      description: '전체 인력 분석 결과 및 인사이트',
      badge: 'NEW'
    },
  ];

  const handleNavigate = (path: string) => {
    console.log('Navigation clicked:', path);
    console.log('Current location:', location.pathname);
    
    // 경로가 같으면 이동하지 않음
    if (location.pathname === path) {
      console.log('Already on this path, skipping navigation');
      return;
    }
    
    try {
      navigate(path);
      console.log('Navigation successful to:', path);
    } catch (error) {
      console.error('Navigation error:', error);
    }
    
    if (isMobile) {
      setMobileMenuOpen(false);
    }
  };

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname === path;
  };

  const renderDesktopMenu = () => (
    <Box sx={{ display: 'flex', gap: 1 }}>
      {menuItems.map((item) => (
        <Box key={item.path} sx={{ position: 'relative' }}>
          <Button
            color="inherit"
            onClick={() => handleNavigate(item.path)}
            startIcon={item.icon}
            sx={{
              backgroundColor: isActive(item.path) ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
              color: 'white',
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
              px: 2,
              py: 1,
            }}
          >
            {item.label}
          </Button>
          {item.badge && (
            <Chip
              label={item.badge}
              size="small"
              color="secondary"
              sx={{
                position: 'absolute',
                top: -8,
                right: -8,
                fontSize: '0.7rem',
                height: 18,
              }}
            />
          )}
        </Box>
      ))}
    </Box>
  );

  const renderMobileMenu = () => (
    <Drawer
      anchor="left"
      open={mobileMenuOpen}
      onClose={() => setMobileMenuOpen(false)}
    >
      <Box sx={{ width: 280 }} role="presentation">
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight="bold">
            AIRISS v4.2
          </Typography>
          <Typography variant="body2" color="text.secondary">
            AI 인사분석 시스템
          </Typography>
        </Box>
        <List>
          {menuItems.map((item) => (
            <ListItem
              key={item.path}
              button
              onClick={() => handleNavigate(item.path)}
              selected={isActive(item.path)}
              sx={{
                py: 1.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText 
                primary={
                  <Box display="flex" alignItems="center" gap={1}>
                    {item.label}
                    {item.badge && (
                      <Chip
                        label={item.badge}
                        size="small"
                        color="secondary"
                        sx={{ fontSize: '0.7rem', height: 20 }}
                      />
                    )}
                  </Box>
                }
                secondary={item.description}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </Drawer>
  );

  return (
    <>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          {isMobile && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={() => setMobileMenuOpen(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Box 
            sx={{ 
              flexGrow: 1, 
              display: 'flex', 
              alignItems: 'center',
              cursor: 'pointer'
            }}
            onClick={() => handleNavigate('/')}
          >
            <Typography variant="h6" component="div" fontWeight="bold">
              AIRISS
            </Typography>
            <Chip
              label="v4.2"
              size="small"
              sx={{ 
                ml: 1, 
                backgroundColor: 'rgba(255, 255, 255, 0.2)',
                color: 'white',
                fontSize: '0.7rem',
                height: 20,
              }}
            />
          </Box>
          
          {!isMobile && renderDesktopMenu()}
        </Toolbar>
      </AppBar>
      
      {isMobile && renderMobileMenu()}
    </>
  );
};

export default SimpleNavigation;