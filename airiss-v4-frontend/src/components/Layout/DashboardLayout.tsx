import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
  Typography,
  IconButton,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import PersonIcon from '@mui/icons-material/Person';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

const drawerWidth = 240;

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const userStr = localStorage.getItem('user');
  const user = userStr ? JSON.parse(userStr) : null;
  const isAdmin = user?.is_admin;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    {
      text: '대시보드',
      icon: <DashboardIcon />,
      path: '/dashboard',
    },
    {
      text: '파일 업로드',
      icon: <UploadFileIcon />,
      path: '/upload',
    },
    {
      text: 'AI 분석',
      icon: <AnalyticsIcon />,
      path: '/analysis',
    },
    {
      text: '분석 검색',
      icon: <SearchIcon />,
      path: '/search',
    },
    {
      text: '분석 이력',
      icon: <HistoryIcon />,
      path: '/history',
    },
  ];

  const userMenuItems = [
    {
      text: '내 프로필',
      icon: <PersonIcon />,
      path: '/profile',
    },
  ];

  if (isAdmin) {
    userMenuItems.push({
      text: '관리자 대시보드',
      icon: <AdminPanelSettingsIcon />,
      path: '/admin',
    });
  }

  const drawer = (
    <>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          AIRISS v4.0
        </Typography>
        {isMobile && (
          <IconButton
            onClick={handleDrawerToggle}
            sx={{ ml: 'auto' }}
          >
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Toolbar>
      <Divider />
      
      {/* 주요 메뉴 */}
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) setMobileOpen(false);
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      <Divider />
      
      {/* 사용자 메뉴 */}
      <List>
        {userMenuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                if (isMobile) setMobileOpen(false);
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* 모바일 토글 버튼 */}
      {isMobile && (
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={handleDrawerToggle}
          sx={{
            position: 'fixed',
            left: 16,
            top: 16,
            zIndex: theme.zIndex.drawer + 1,
            display: mobileOpen ? 'none' : 'block',
          }}
        >
          <MenuIcon />
        </IconButton>
      )}

      {/* 사이드바 */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true,
            }}
            sx={{
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
              },
            }}
          >
            {drawer}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            sx={{
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: drawerWidth,
              },
            }}
            open
          >
            {drawer}
          </Drawer>
        )}
      </Box>

      {/* 메인 콘텐츠 영역 */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default DashboardLayout; 