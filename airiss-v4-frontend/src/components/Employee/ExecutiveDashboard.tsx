/**
 * AIRISS v4.2 경영진 대시보드
 * Executive Dashboard with AI Insights and Charts
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Button,
  IconButton,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  Star as StarIcon,
  School as SchoolIcon,
  Download as DownloadIcon,
  PictureAsPdf as PdfIcon,
  Slideshow as PptIcon,
} from '@mui/icons-material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js';
import { Bar, Doughnut, Radar } from 'react-chartjs-2';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
);

interface DashboardStatistics {
  total_employees: number;
  grade_distribution: Record<string, number>;
  average_score: number;
  talent_count: number;
  promotion_candidates: number;
  risk_employees: number;
  competency_averages: Record<string, number>;
}

interface AIRecommendation {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  recommendation_score: number;
  recommendation_reason: string;
  ai_score: number;
  grade: string;
}

const ExecutiveDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<DashboardStatistics | null>(null);
  const [topTalents, setTopTalents] = useState<AIRecommendation[]>([]);
  const [promotionCandidates, setPromotionCandidates] = useState<AIRecommendation[]>([]);
  const [riskEmployees, setRiskEmployees] = useState<AIRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8006';
      
      // 통계 데이터 가져오기
      console.log('📊 대시보드 통계 API 호출:', `${API_BASE_URL}/api/v1/employees/dashboard/statistics`);
      const statsResponse = await fetch(`${API_BASE_URL}/api/v1/employees/dashboard/statistics`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      console.log('📊 통계 API 응답:', statsResponse.status, statsResponse.ok);
      
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        console.log('📊 받은 통계 데이터:', statsData);
        setStatistics(statsData);
      } else {
        console.error('❌ 통계 API 오류:', statsResponse.status, statsResponse.statusText);
      }

      // AI 추천 데이터 가져오기
      const [talentRes, promotionRes, riskRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/employees/ai-recommendation?type=talent&limit=5`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }),
        fetch(`${API_BASE_URL}/api/v1/employees/ai-recommendation?type=promotion&limit=5`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }),
        fetch(`${API_BASE_URL}/api/v1/employees/ai-recommendation?type=risk&limit=5`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }),
      ]);

      console.log('🎯 AI 추천 API 응답 상태:', {
        talent: talentRes.status,
        promotion: promotionRes.status,
        risk: riskRes.status
      });

      const [talentData, promotionData, riskData] = await Promise.all([
        talentRes.ok ? talentRes.json() : [],
        promotionRes.ok ? promotionRes.json() : [],
        riskRes.ok ? riskRes.json() : [],
      ]);

      console.log('🎯 받은 AI 추천 데이터:', {
        talents: talentData.length || 0,
        promotions: promotionData.length || 0,
        risks: riskData.length || 0
      });

      setTopTalents(talentData || []);
      setPromotionCandidates(promotionData || []);
      setRiskEmployees(riskData || []);
    } catch (error) {
      console.error('❌ 대시보드 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'S':
        return '#9c27b0';
      case 'A+':
        return '#2196f3';
      case 'A':
        return '#03a9f4';
      case 'B':
        return '#4caf50';
      case 'C':
        return '#ff9800';
      case 'D':
        return '#f44336';
      default:
        return '#757575';
    }
  };

  // 등급 분포 차트 데이터
  const gradeChartData = {
    labels: Object.keys(statistics?.grade_distribution || {}),
    datasets: [
      {
        data: Object.values(statistics?.grade_distribution || {}),
        backgroundColor: ['#9c27b0', '#2196f3', '#03a9f4', '#4caf50', '#ff9800', '#f44336'],
        borderWidth: 0,
      },
    ],
  };

  // 역량 평균 레이더 차트 데이터
  const competencyRadarData = {
    labels: Object.keys(statistics?.competency_averages || {}),
    datasets: [
      {
        label: '전사 평균',
        data: Object.values(statistics?.competency_averages || {}),
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
      },
    ],
  };

  const doughnutOptions = {
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
    maintainAspectRatio: false,
  };

  const radarOptions = {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
    maintainAspectRatio: false,
  };

  if (loading) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <Box>
      {/* 헤더 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          HR AI 경영진 대시보드
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<PdfIcon />}
            sx={{ mr: 1 }}
          >
            PDF 리포트
          </Button>
          <Button
            variant="contained"
            startIcon={<PptIcon />}
          >
            PPT 다운로드
          </Button>
        </Box>
      </Box>

      {/* 주요 지표 카드 */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                전체 직원 수
              </Typography>
              <Typography variant="h4">
                {statistics?.total_employees || 0}명
              </Typography>
              <Typography variant="body2" color="text.secondary">
                평균 AI 점수: {statistics?.average_score?.toFixed(1) || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <StarIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="text.secondary">
                  Top Talent
                </Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {statistics?.talent_count || 0}명
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI 점수 900점 이상
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                <Typography color="text.secondary">
                  승진 후보자
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {statistics?.promotion_candidates || 0}명
              </Typography>
              <Typography variant="body2" color="text.secondary">
                리더십 잠재력 우수
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <WarningIcon color="warning" sx={{ mr: 1 }} />
                <Typography color="text.secondary">
                  관리 필요 인력
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {statistics?.risk_employees || 0}명
              </Typography>
              <Typography variant="body2" color="text.secondary">
                이직 위험 또는 저성과
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 차트 영역 */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              등급 분포
            </Typography>
            <Box height={350}>
              <Doughnut data={gradeChartData} options={doughnutOptions} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: 400 }}>
            <Typography variant="h6" gutterBottom>
              전사 8대 역량 평균
            </Typography>
            <Box height={350}>
              <Radar data={competencyRadarData} options={radarOptions} />
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* AI 추천 리스트 */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              <StarIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              Top Talent
            </Typography>
            <List>
              {topTalents.map((talent) => (
                <ListItem key={talent.employee_id} divider>
                  <ListItemAvatar>
                    <Avatar>{talent.name[0]}</Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={talent.name}
                    secondary={`${talent.department} | ${talent.position}`}
                  />
                  <Chip
                    label={talent.grade}
                    size="small"
                    sx={{
                      backgroundColor: getGradeColor(talent.grade),
                      color: 'white',
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              <TrendingUpIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              승진 후보자
            </Typography>
            <List>
              {promotionCandidates.map((candidate) => (
                <ListItem key={candidate.employee_id} divider>
                  <ListItemAvatar>
                    <Avatar>{candidate.name[0]}</Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={candidate.name}
                    secondary={`${candidate.department} | ${candidate.position}`}
                  />
                  <Typography variant="body2" color="success.main">
                    {candidate.recommendation_score.toFixed(0)}%
                  </Typography>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              <WarningIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              관리 필요 인력
            </Typography>
            <List>
              {riskEmployees.map((employee) => (
                <ListItem key={employee.employee_id} divider>
                  <ListItemAvatar>
                    <Avatar>{employee.name[0]}</Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={employee.name}
                    secondary={`${employee.department} | ${employee.position}`}
                  />
                  <Typography variant="body2" color="warning.main">
                    위험도 {employee.recommendation_score.toFixed(0)}%
                  </Typography>
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExecutiveDashboard;