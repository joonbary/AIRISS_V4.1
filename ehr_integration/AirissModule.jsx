/**
 * AIRISS Module for EHR Integration
 * EHR 시스템에 통합되는 메인 AIRISS 모듈
 */

import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate, NavLink } from 'react-router-dom';
import { AirissProvider } from './context/AirissContext';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Container,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Dashboard,
  People,
  Analytics,
  Settings,
  Notifications,
  Help,
} from '@mui/icons-material';

// Lazy load components for better performance
const ExecutiveDashboard = lazy(() => import('./components/ExecutiveDashboard'));
const EmployeeAnalysisTable = lazy(() => import('./components/EmployeeAnalysisTable'));

// Loading component
const LoadingFallback = () => (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
    <CircularProgress />
  </Box>
);

// Tab Panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`airiss-tabpanel-${index}`}
      aria-labelledby={`airiss-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

// Main AIRISS Module Component
const AirissModule = ({ employees = [], userRole = 'manager' }) => {
  const [tabValue, setTabValue] = React.useState(0);
  const [notifications, setNotifications] = React.useState(3);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  // 권한 체크
  const canViewExecutiveDashboard = ['admin', 'executive', 'manager'].includes(userRole);
  const canAnalyzeEmployees = ['admin', 'hr', 'manager'].includes(userRole);

  return (
    <AirissProvider>
      <Box sx={{ flexGrow: 1 }}>
        {/* AIRISS 모듈 헤더 */}
        <AppBar position="static" color="default" elevation={1}>
          <Toolbar>
            <Analytics sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AIRISS HR Analytics
            </Typography>
            <IconButton color="inherit">
              <Badge badgeContent={notifications} color="error">
                <Notifications />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <Settings />
            </IconButton>
            <IconButton color="inherit">
              <Help />
            </IconButton>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 3 }}>
          {/* 권한 체크 */}
          {!canViewExecutiveDashboard && !canAnalyzeEmployees ? (
            <Alert severity="warning">
              HR Analytics 모듈에 접근 권한이 없습니다. 시스템 관리자에게 문의하세요.
            </Alert>
          ) : (
            <>
              {/* 탭 네비게이션 */}
              <Paper sx={{ mb: 3 }}>
                <Tabs
                  value={tabValue}
                  onChange={handleTabChange}
                  indicatorColor="primary"
                  textColor="primary"
                  variant="fullWidth"
                >
                  {canViewExecutiveDashboard && (
                    <Tab
                      icon={<Dashboard />}
                      label="경영진 대시보드"
                      iconPosition="start"
                    />
                  )}
                  {canAnalyzeEmployees && (
                    <Tab
                      icon={<People />}
                      label="직원 분석"
                      iconPosition="start"
                    />
                  )}
                </Tabs>
              </Paper>

              {/* 탭 컨텐츠 */}
              <Suspense fallback={<LoadingFallback />}>
                {canViewExecutiveDashboard && (
                  <TabPanel value={tabValue} index={0}>
                    <ExecutiveDashboard />
                  </TabPanel>
                )}
                {canAnalyzeEmployees && (
                  <TabPanel value={tabValue} index={canViewExecutiveDashboard ? 1 : 0}>
                    <EmployeeAnalysisTable employees={employees} />
                  </TabPanel>
                )}
              </Suspense>
            </>
          )}
        </Container>
      </Box>
    </AirissProvider>
  );
};

// Route-based version for React Router integration
export const AirissRoutes = ({ employees = [], userRole = 'manager' }) => {
  return (
    <AirissProvider>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/" element={<Navigate to="dashboard" replace />} />
          <Route
            path="dashboard"
            element={
              ['admin', 'executive', 'manager'].includes(userRole) ? (
                <ExecutiveDashboard />
              ) : (
                <Alert severity="warning">접근 권한이 없습니다.</Alert>
              )
            }
          />
          <Route
            path="employees"
            element={
              ['admin', 'hr', 'manager'].includes(userRole) ? (
                <EmployeeAnalysisTable employees={employees} />
              ) : (
                <Alert severity="warning">접근 권한이 없습니다.</Alert>
              )
            }
          />
          <Route path="*" element={<Navigate to="dashboard" replace />} />
        </Routes>
      </Suspense>
    </AirissProvider>
  );
};

export default AirissModule;