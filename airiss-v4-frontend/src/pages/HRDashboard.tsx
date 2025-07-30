/**
 * AIRISS v4.2 HR 대시보드 페이지
 * HR Dashboard Page with AI Analysis
 */
import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Paper,
  Typography,
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import EnhancedEmployeeDetailCard from '../components/Employee/EnhancedEmployeeDetailCard';
import EmployeeDashboardTable from '../components/Employee/EmployeeDashboardTable';
import ExecutiveDashboard from '../components/Employee/ExecutiveDashboard';
import { employeeApi } from '../services/employeeApi';
import type { EmployeeAIAnalysis } from '../services/employeeApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`hr-tabpanel-${index}`}
      aria-labelledby={`hr-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `hr-tab-${index}`,
    'aria-controls': `hr-tabpanel-${index}`,
  };
}

const HRDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeAIAnalysis | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleViewEmployeeDetail = async (employeeId: string) => {
    try {
      const employee = await employeeApi.getEmployeeAIAnalysis(employeeId);
      setSelectedEmployee(employee);
      setDetailDialogOpen(true);
    } catch (error) {
      showSnackbar('직원 정보를 불러오는데 실패했습니다.', 'error');
    }
  };

  const handleCloseDetailDialog = () => {
    setDetailDialogOpen(false);
    setSelectedEmployee(null);
  };

  const handleSaveFeedback = async (feedback: string) => {
    if (!selectedEmployee) return;

    try {
      const response = await employeeApi.saveAIFeedback({
        employee_id: selectedEmployee.employee_id,
        ai_feedback_text: feedback,
        action: 'save_to_record',
      });

      if (response.success) {
        showSnackbar('AI 피드백이 저장되었습니다.', 'success');
      } else {
        showSnackbar('피드백 저장에 실패했습니다.', 'error');
      }
    } catch (error) {
      showSnackbar('피드백 저장 중 오류가 발생했습니다.', 'error');
    }
  };

  const handleCopyFeedback = () => {
    showSnackbar('피드백이 클립보드에 복사되었습니다.', 'success');
  };

  const handleSendEmail = async () => {
    if (!selectedEmployee) return;

    try {
      await employeeApi.saveAIFeedback({
        employee_id: selectedEmployee.employee_id,
        ai_feedback_text: selectedEmployee.ai_comment,
        action: 'send_email',
      });
      showSnackbar('이메일이 전송되었습니다.', 'success');
    } catch (error) {
      showSnackbar('이메일 전송에 실패했습니다.', 'error');
    }
  };

  const handleExportData = async () => {
    try {
      const blob = await employeeApi.exportEmployeesData();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `AIRISS_직원분석_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showSnackbar('엑셀 파일이 다운로드되었습니다.', 'success');
    } catch (error) {
      showSnackbar('데이터 내보내기에 실패했습니다.', 'error');
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  return (
    <Box>
      <Box sx={{ mt: 4, mb: 2 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          경영진 대시보드 - 전체 인력 분석
        </Typography>
        <Typography variant="body1" color="text.secondary">
          전체 직원의 AI 분석 결과를 종합적으로 확인하고 인사 인사이트를 얻으세요
        </Typography>
      </Box>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="HR dashboard tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            icon={<DashboardIcon />}
            label="경영진 대시보드"
            {...a11yProps(0)}
          />
          <Tab
            icon={<PeopleIcon />}
            label="전체 직원 분석"
            {...a11yProps(1)}
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <ExecutiveDashboard />
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <EmployeeDashboardTable
            onViewDetail={handleViewEmployeeDetail}
            onExportData={handleExportData}
          />
        </TabPanel>
      </Paper>

      {/* 직원 상세 정보 다이얼로그 */}
      <Dialog
        open={detailDialogOpen}
        onClose={handleCloseDetailDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          직원 AI 분석 상세
          <IconButton
            aria-label="close"
            onClick={handleCloseDetailDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedEmployee && (
            <EnhancedEmployeeDetailCard
              employee={selectedEmployee}
              onSaveFeedback={handleSaveFeedback}
              onCopyFeedback={handleCopyFeedback}
              onSendEmail={handleSendEmail}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* 스낵바 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbarOpen(false)}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default HRDashboard;