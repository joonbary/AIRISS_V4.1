/**
 * EHR System App Example with AIRISS Integration
 * EHR 시스템에 AIRISS를 통합하는 예제
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Container,
  Divider,
  ListItemButton,
} from '@mui/material';
import {
  Home,
  People,
  BusinessCenter,
  AttachMoney,
  EventNote,
  Assessment,
  Settings,
  ExitToApp,
  Analytics,
} from '@mui/icons-material';

// AIRISS 모듈 import
import AirissModule, { AirissRoutes } from '../AirissModule';

// EHR 테마 설정
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Noto Sans KR", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

// 드로어 너비
const drawerWidth = 240;

// 메뉴 아이템 설정
const menuItems = [
  { text: '홈', icon: <Home />, path: '/' },
  { text: '직원 관리', icon: <People />, path: '/employees' },
  { text: '조직도', icon: <BusinessCenter />, path: '/organization' },
  { text: '급여 관리', icon: <AttachMoney />, path: '/payroll' },
  { text: '근태 관리', icon: <EventNote />, path: '/attendance' },
  { text: 'HR 분석 (AIRISS)', icon: <Analytics />, path: '/hr/airiss', highlight: true },
  { text: '보고서', icon: <Assessment />, path: '/reports' },
  { text: '설정', icon: <Settings />, path: '/settings' },
];

// 샘플 직원 데이터
const sampleEmployees = [
  {
    id: 'EMP001',
    name: '김철수',
    department: '개발팀',
    position: '과장',
    performanceScore: 85,
    projectSuccessRate: 90,
    customerSatisfaction: 88,
    attendanceRate: 98,
    leadershipScore: 82,
    technicalSkill: 90,
    communicationScore: 78,
    problemSolving: 85,
    teamwork: 88,
    creativity: 75,
    adaptability: 80,
    reliability: 92,
    yearsOfExperience: 8,
    educationLevel: '석사',
    certifications: ['PMP', 'AWS Solutions Architect'],
  },
  {
    id: 'EMP002',
    name: '이영희',
    department: '마케팅팀',
    position: '대리',
    performanceScore: 78,
    projectSuccessRate: 82,
    customerSatisfaction: 90,
    attendanceRate: 95,
    leadershipScore: 75,
    technicalSkill: 70,
    communicationScore: 88,
    problemSolving: 72,
    teamwork: 90,
    creativity: 85,
    adaptability: 88,
    reliability: 85,
    yearsOfExperience: 5,
    educationLevel: '학사',
    certifications: ['Google Analytics', 'HubSpot'],
  },
  {
    id: 'EMP003',
    name: '박민수',
    department: '영업팀',
    position: '차장',
    performanceScore: 92,
    projectSuccessRate: 88,
    customerSatisfaction: 95,
    attendanceRate: 97,
    leadershipScore: 88,
    technicalSkill: 75,
    communicationScore: 92,
    problemSolving: 80,
    teamwork: 85,
    creativity: 70,
    adaptability: 85,
    reliability: 90,
    yearsOfExperience: 10,
    educationLevel: '학사',
    certifications: ['Salesforce Admin'],
  },
];

// 메인 EHR App 컴포넌트
function EHRApp() {
  const [currentUser] = React.useState({
    name: '관리자',
    role: 'admin', // admin, executive, manager, hr, employee
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex' }}>
          {/* 앱바 */}
          <AppBar
            position="fixed"
            sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
          >
            <Toolbar>
              <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
                EHR System - Enterprise HR Management
              </Typography>
              <Typography variant="body2" sx={{ mr: 2 }}>
                {currentUser.name}
              </Typography>
              <ExitToApp />
            </Toolbar>
          </AppBar>

          {/* 사이드바 드로어 */}
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                {menuItems.map((item) => (
                  <ListItem key={item.text} disablePadding>
                    <ListItemButton
                      component={Link}
                      to={item.path}
                      sx={{
                        backgroundColor: item.highlight ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                        '&:hover': {
                          backgroundColor: item.highlight ? 'rgba(25, 118, 210, 0.12)' : 'rgba(0, 0, 0, 0.04)',
                        },
                      }}
                    >
                      <ListItemIcon
                        sx={{
                          color: item.highlight ? 'primary.main' : 'inherit',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText 
                        primary={item.text}
                        primaryTypographyProps={{
                          fontWeight: item.highlight ? 'medium' : 'regular',
                          color: item.highlight ? 'primary.main' : 'inherit',
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            </Box>
          </Drawer>

          {/* 메인 컨텐츠 */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              bgcolor: 'background.default',
              p: 3,
              minHeight: '100vh',
            }}
          >
            <Toolbar />
            <Routes>
              {/* EHR 기본 페이지들 */}
              <Route path="/" element={<HomePage />} />
              <Route path="/employees" element={<EmployeesPage />} />
              <Route path="/organization" element={<OrganizationPage />} />
              <Route path="/payroll" element={<PayrollPage />} />
              <Route path="/attendance" element={<AttendancePage />} />
              <Route path="/reports" element={<ReportsPage />} />
              <Route path="/settings" element={<SettingsPage />} />

              {/* AIRISS 통합 라우트 */}
              <Route
                path="/hr/airiss/*"
                element={
                  <AirissRoutes
                    employees={sampleEmployees}
                    userRole={currentUser.role}
                  />
                }
              />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

// 기본 페이지 컴포넌트들
const HomePage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      EHR 시스템 홈
    </Typography>
    <Typography paragraph>
      통합 인사 관리 시스템에 오신 것을 환영합니다.
    </Typography>
  </Container>
);

const EmployeesPage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      직원 관리
    </Typography>
    <Typography paragraph>
      직원 정보를 관리하는 페이지입니다.
    </Typography>
  </Container>
);

const OrganizationPage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      조직도
    </Typography>
    <Typography paragraph>
      회사 조직 구조를 확인하는 페이지입니다.
    </Typography>
  </Container>
);

const PayrollPage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      급여 관리
    </Typography>
    <Typography paragraph>
      급여 정보를 관리하는 페이지입니다.
    </Typography>
  </Container>
);

const AttendancePage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      근태 관리
    </Typography>
    <Typography paragraph>
      출퇴근 및 휴가 정보를 관리하는 페이지입니다.
    </Typography>
  </Container>
);

const ReportsPage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      보고서
    </Typography>
    <Typography paragraph>
      각종 HR 보고서를 생성하고 확인하는 페이지입니다.
    </Typography>
  </Container>
);

const SettingsPage = () => (
  <Container>
    <Typography variant="h4" gutterBottom>
      설정
    </Typography>
    <Typography paragraph>
      시스템 설정을 관리하는 페이지입니다.
    </Typography>
  </Container>
);

export default EHRApp;