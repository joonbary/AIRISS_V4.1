import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Typography, 
  Paper,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  People,
  TrendingUp,
  Assessment,
  School,
  Refresh,
  Download
} from '@mui/icons-material';
import { DataCard, ProgressCard, MetricCard, GradeBadge } from '../components/common';

const Dashboard = () => {
  const [loading, setLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState({
    totalEmployees: 156,
    averageGrade: 'B',
    performanceScore: 78,
    trainingCompletion: 65,
    metrics: [
      { label: '생산성', value: '92%', change: 5, color: 'success' },
      { label: '만족도', value: '4.5', change: 0.3, color: 'primary' },
      { label: '이직률', value: '3.2%', change: -0.5, color: 'success' },
      { label: '교육 참여율', value: '87%', change: 12, color: 'success' },
    ],
    departmentData: [
      { name: '인사부', employees: 12, grade: 'A', performance: 85 },
      { name: '개발부', employees: 45, grade: 'A+', performance: 92 },
      { name: '영업부', employees: 34, grade: 'B', performance: 78 },
      { name: '마케팅부', employees: 23, grade: 'B', performance: 75 },
      { name: '재무부', employees: 18, grade: 'A', performance: 88 },
      { name: '운영부', employees: 24, grade: 'B', performance: 72 },
    ]
  });

  const handleRefresh = () => {
    setLoading(true);
    // 데이터 새로고침 시뮬레이션
    setTimeout(() => {
      setLoading(false);
    }, 1500);
  };

  return (
    <Box>
      {/* 헤더 섹션 */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom fontWeight="bold">
            AIRISS 대시보드
          </Typography>
          <Typography variant="body1" color="text.secondary">
            실시간 인사 분석 및 성과 모니터링
          </Typography>
        </Box>
        <Box>
          <Tooltip title="새로고침">
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="보고서 다운로드">
            <IconButton color="primary">
              <Download />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* 주요 지표 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <DataCard
            title="전체 직원"
            subtitle="Active Employees"
            value={dashboardData.totalEmployees}
            unit="명"
            icon={<People />}
            color="primary"
            trend={{ type: 'up', label: '+8명', icon: <TrendingUp /> }}
            loading={loading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <DataCard
            title="평균 등급"
            subtitle="Average Grade"
            value={dashboardData.averageGrade}
            icon={<Assessment />}
            color="secondary"
            loading={loading}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <ProgressCard
            title="성과 점수"
            percentage={dashboardData.performanceScore}
            color="success"
            showLabel={true}
            thickness={10}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <ProgressCard
            title="교육 이수율"
            percentage={dashboardData.trainingCompletion}
            color="info"
            showLabel={true}
            thickness={10}
          />
        </Grid>
      </Grid>

      {/* 주요 메트릭 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <MetricCard
            title="주요 성과 지표"
            metrics={dashboardData.metrics}
            loading={loading}
          />
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                부서별 현황
              </Typography>
              <Box sx={{ mt: 2 }}>
                {dashboardData.departmentData.map((dept, index) => (
                  <Paper
                    key={index}
                    sx={{ 
                      p: 2, 
                      mb: 1, 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      '&:hover': {
                        bgcolor: 'action.hover',
                        cursor: 'pointer'
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography variant="body1" fontWeight="medium">
                        {dept.name}
                      </Typography>
                      <Chip 
                        label={`${dept.employees}명`} 
                        size="small" 
                        variant="outlined" 
                      />
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <GradeBadge grade={dept.grade} size="small" />
                      <Typography 
                        variant="body2" 
                        color={dept.performance >= 80 ? 'success.main' : 'text.secondary'}
                      >
                        {dept.performance}%
                      </Typography>
                    </Box>
                  </Paper>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI 분석 인사이트 */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 AI 분석 인사이트
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                      이번 분기 추천
                    </Typography>
                    <Typography variant="h6" sx={{ color: 'white', mt: 1 }}>
                      개발부 인력 15% 증원 필요
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                      성과 예측
                    </Typography>
                    <Typography variant="h6" sx={{ color: 'white', mt: 1 }}>
                      다음 분기 생산성 8% 상승 예상
                    </Typography>
                  </Paper>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Paper sx={{ p: 2, bgcolor: 'rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
                    <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                      위험 알림
                    </Typography>
                    <Typography variant="h6" sx={{ color: 'white', mt: 1 }}>
                      영업부 이직 위험도 상승 감지
                    </Typography>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;