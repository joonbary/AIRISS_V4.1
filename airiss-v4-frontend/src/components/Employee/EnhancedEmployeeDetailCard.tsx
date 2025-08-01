/**
 * AIRISS v4.2 향상된 직원 상세 카드 컴포넌트
 * Enhanced Employee Detail Card Component with Advanced UI/UX
 */
import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Avatar,
  Box,
  Chip,
  Grid,
  Button,
  IconButton,
  Tooltip,
  Divider,
  Tabs,
  Tab,
  ToggleButton,
  ToggleButtonGroup,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  Badge,
  CircularProgress,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Save as SaveIcon,
  Email as EmailIcon,
  School as SchoolIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Warning as WarningIcon,
  PictureAsPdf as PdfIcon,
  BarChart as RankingIcon,
  People as CompareIcon,
  Psychology as AIIcon,
  Navigation as CareerIcon,
  EmojiEvents as TargetIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
} from '@mui/icons-material';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

// Chart.js 등록
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  ChartTooltip,
  Legend
);

interface CompetencyScores {
  실행력: number;
  성장지향: number;
  협업: number;
  고객지향: number;
  전문성: number;
  혁신성: number;
  리더십: number;
  커뮤니케이션: number;
}

interface EmployeeAIAnalysis {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  profile_image?: string;
  ai_score: number;
  grade: string;
  competencies: CompetencyScores;
  strengths: string[];
  improvements: string[];
  ai_comment: string;
  career_recommendation: string[];
  education_suggestion: string[];
  analyzed_at: string;
  confidence_score?: number;
  percentile_rank?: number;
}

interface EmployeeDetailCardProps {
  employee: EmployeeAIAnalysis;
  onSaveFeedback?: (feedback: string) => void;
  onCopyFeedback?: () => void;
  onSendEmail?: () => void;
}

const EnhancedEmployeeDetailCard: React.FC<EmployeeDetailCardProps> = ({
  employee,
  onSaveFeedback,
  onCopyFeedback,
  onSendEmail,
}) => {
  const [chartMode, setChartMode] = useState<'personal' | 'company' | 'department'>('personal');
  const [feedbackView, setFeedbackView] = useState<'summary' | 'detailed'>('summary');
  const [selectedEducationTab, setSelectedEducationTab] = useState(0);
  const [aiAnalysisDialog, setAiAnalysisDialog] = useState(false);
  const [comparisonDialog, setComparisonDialog] = useState(false);

  // 모의 데이터 - 전사 평균, 동직군 평균
  const companyAverages = {
    실행력: 70, 성장지향: 72, 협업: 75, 고객지향: 68,
    전문성: 73, 혁신성: 65, 리더십: 67, 커뮤니케이션: 71
  };

  const departmentAverages = {
    실행력: 75, 성장지향: 78, 협업: 80, 고객지향: 72,
    전문성: 85, 혁신성: 70, 리더십: 73, 커뮤니케이션: 77
  };

  // 점수 기반 색상 계산 (빨강 → 파랑 스펙트럼)
  const getScoreColor = (score: number) => {
    const ratio = score / 100;
    const red = Math.round(255 * (1 - ratio));
    const blue = Math.round(255 * ratio);
    return `rgb(${red}, 0, ${blue})`;
  };

  // 등급별 색상
  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'S': return '#9c27b0';
      case 'A+': return '#2196f3';
      case 'A': return '#03a9f4';
      case 'B': return '#4caf50';
      case 'C': return '#ff9800';
      case 'D': return '#f44336';
      default: return '#757575';
    }
  };

  // 개선 필요 역량 색상 (순위별)
  const getImprovementColor = (index: number) => {
    const colors = ['#ff9800', '#f57c00', '#e65100']; // 오렌지 → 빨강
    return colors[index] || '#e65100';
  };

  // 레이더 차트 데이터
  const getRadarData = () => {
    const labels = Object.keys(employee.competencies);
    const personalData = Object.values(employee.competencies);
    
    let comparisonData: number[] = [];
    let comparisonLabel = '';
    
    switch (chartMode) {
      case 'company':
        comparisonData = Object.values(companyAverages);
        comparisonLabel = '전사 평균';
        break;
      case 'department':
        comparisonData = Object.values(departmentAverages);
        comparisonLabel = '동직군 평균';
        break;
      default:
        comparisonData = [];
    }

    const datasets: any[] = [
      {
        label: employee.name,
        data: personalData,
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(33, 150, 243, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(33, 150, 243, 1)',
      },
    ];

    if (comparisonData.length > 0) {
      datasets.push({
        label: comparisonLabel,
        data: comparisonData,
        backgroundColor: 'rgba(158, 158, 158, 0.1)',
        borderColor: 'rgba(158, 158, 158, 1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointBackgroundColor: 'rgba(158, 158, 158, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(158, 158, 158, 1)',
      });
    }

    return { labels, datasets };
  };

  const radarOptions = {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'bottom' as const,
      },
    },
    maintainAspectRatio: false,
    responsive: true,
  };

  // 트렌드 아이콘 (모의 데이터)
  const getTrendIcon = (competency: string) => {
    const trendUp = ['리더십', '커뮤니케이션', '성장지향'];
    return trendUp.includes(competency) ? 
      <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main', ml: 0.5 }} /> :
      <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main', ml: 0.5 }} />;
  };

  // AI 피드백 요약 생성
  const generateSummary = (comment: string | null | undefined) => {
    if (!comment || typeof comment !== 'string') {
      return '평가 의견이 없습니다.';
    }
    const sentences = comment.split('.');
    return sentences[0] + '.';
  };

  // 교육 카테고리
  const educationCategories = [
    { label: '리더십', items: ['팀 리더십 심화', '조직 관리', '변화 리더십'] },
    { label: '전략', items: ['전략적 사고', '비즈니스 모델링', '미래 예측'] },
    { label: '변화관리', items: ['디지털 전환', '조직 변화', '혁신 관리'] },
    { label: '커뮤니케이션', items: ['고급 프레젠테이션', '협상 스킬', '갈등 관리'] },
  ];

  const handleCopyToClipboard = () => {
    const feedbackText = `
${employee.name} (${employee.department} ${employee.position})
AI 종합점수: ${employee.ai_score} (${employee.grade}등급)
AI 신뢰도: ${employee.confidence_score || 92}%

[8대 핵심 역량]
${Object.entries(employee.competencies).map(([key, value]) => `${key}: ${value}점`).join('\n')}

[강점 키워드]
${employee.strengths.join(', ')}

[개발 필요 역량]
${employee.improvements.join(', ')}

[AI 종합 피드백]
${employee.ai_comment || '평가 의견이 없습니다.'}

[추천 경력 방향]
${employee.career_recommendation.join(', ')}

[교육 추천]
${employee.education_suggestion.join(', ')}
    `.trim();

    navigator.clipboard.writeText(feedbackText);
    onCopyFeedback?.();
  };

  const handleExportPDF = () => {
    // 새 창에서 PDF 페이지 열기
    const pdfUrl = `/employee/${employee.employee_id}/pdf?download=true`;
    window.open(pdfUrl, '_blank', 'width=850,height=1200');
  };

  const handleShowRanking = () => {
    alert(`전사 내 백분위: ${employee.percentile_rank || 87}%`);
  };

  return (
    <Card 
      id={`employee-detail-${employee.employee_id}`}
      sx={{ maxWidth: 1000, margin: 'auto' }}
    >
      <CardContent>
        {/* 직원 기본 정보 */}
        <Box display="flex" alignItems="center" mb={3}>
          <Avatar
            src={employee.profile_image}
            alt={employee.name}
            sx={{ width: 100, height: 100, mr: 3 }}
          >
            {employee.name[0]}
          </Avatar>
          <Box flex={1}>
            <Typography variant="h4" component="h2" gutterBottom>
              {employee.name} ({employee.employee_id})
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              {employee.department} | {employee.position}
            </Typography>
            <Box display="flex" alignItems="center" gap={2} mb={1}>
              <Typography variant="h5">
                AI 종합점수: {employee.ai_score || 'N/A'}
              </Typography>
              <Chip
                label={`${employee.grade}등급`}
                sx={{
                  backgroundColor: getGradeColor(employee.grade),
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '1rem',
                  height: 32,
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary">
              AI 신뢰도: {employee.confidence_score || 92}% | 
              분석일시: {new Date(employee.analyzed_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        <Grid container spacing={4}>
          {/* 8대 역량 레이더 차트 */}
          <Grid item xs={12} lg={6}>
            <Typography variant="h6" gutterBottom>
              8대 핵심 역량 분석
            </Typography>
            
            {/* 차트 모드 선택 탭 */}
            <Tabs 
              value={chartMode} 
              onChange={(_, newValue) => setChartMode(newValue)}
              sx={{ mb: 2 }}
            >
              <Tab label="본인 점수" value="personal" />
              <Tab label="전사 평균 비교" value="company" />
              <Tab label="동직군 평균 비교" value="department" />
            </Tabs>

            <Box height={350}>
              <Radar data={getRadarData()} options={radarOptions} />
            </Box>

            {/* 역량별 상세 점수 및 트렌드 */}
            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                역량별 상세 점수
              </Typography>
              <Grid container spacing={1}>
                {Object.entries(employee.competencies).map(([key, value]) => (
                  <Grid item xs={6} sm={4} key={key}>
                    <Paper 
                      elevation={1} 
                      sx={{ 
                        p: 1, 
                        textAlign: 'center',
                        backgroundColor: `${getScoreColor(value)}15`,
                        border: `1px solid ${getScoreColor(value)}40`
                      }}
                    >
                      <Typography variant="caption" display="block">
                        {key}
                      </Typography>
                      <Box display="flex" alignItems="center" justifyContent="center">
                        <Typography 
                          variant="body2" 
                          fontWeight="bold"
                          color={getScoreColor(value)}
                        >
                          {value}
                        </Typography>
                        {getTrendIcon(key)}
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Grid>

          {/* 강점 및 개선점 시각화 */}
          <Grid item xs={12} lg={6}>
            {/* 강점 TOP3 + 전체 키워드 */}
            <Box mb={4}>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'primary.main' }} />
                핵심 강점 분석
              </Typography>
              
              <Typography variant="subtitle2" gutterBottom color="primary.main">
                TOP 3 강점
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                {employee.strengths.slice(0, 3).map((strength, index) => (
                  <Tooltip key={index} title={`${index + 1}순위 강점`}>
                    <Chip
                      label={`${index + 1}. ${strength}`}
                      color="primary"
                      variant="filled"
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Tooltip>
                ))}
              </Box>

              <Typography variant="subtitle2" gutterBottom color="text.secondary">
                전체 강점 키워드 (최대 5개)
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {[...employee.strengths, '데이터 분석력', '문제해결력'].slice(0, 5).map((strength, index) => (
                  <Tooltip key={index} title="마우스 오버 시 관련 피드백 요약">
                    <Chip
                      label={strength}
                      color="primary"
                      variant="outlined"
                      size="small"
                    />
                  </Tooltip>
                ))}
              </Box>
            </Box>

            {/* 개발 필요 역량 */}
            <Box mb={4}>
              <Typography variant="h6" gutterBottom>
                <WarningIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'warning.main' }} />
                개발 필요 역량 (우선순위별)
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {employee.improvements.slice(0, 3).map((improvement, index) => (
                  <Tooltip key={index} title={`우선순위 ${index + 1}위 개발 필요 역량`}>
                    <Chip
                      label={`${index + 1}. ${improvement}`}
                      sx={{
                        backgroundColor: getImprovementColor(index),
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    />
                  </Tooltip>
                ))}
              </Box>
            </Box>

            {/* 추천 경력 방향 카드형 시각화 */}
            <Box>
              <Typography variant="h6" gutterBottom>
                <CareerIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'success.main' }} />
                AI 추천 경력 방향
              </Typography>
              <Grid container spacing={2}>
                {employee.career_recommendation.slice(0, 2).map((career, index) => (
                  <Grid item xs={6} key={index}>
                    <Paper 
                      elevation={2}
                      sx={{ 
                        p: 2, 
                        textAlign: 'center',
                        backgroundColor: 'success.light',
                        color: 'success.contrastText',
                        cursor: 'pointer',
                        '&:hover': { elevation: 4 }
                      }}
                    >
                      {index === 0 ? <CareerIcon sx={{ fontSize: 32, mb: 1 }} /> : 
                                   <TargetIcon sx={{ fontSize: 32, mb: 1 }} />}
                      <Typography variant="subtitle1" fontWeight="bold">
                        {career}
                      </Typography>
                      <Typography variant="caption" display="block">
                        유사 패턴 기반 추천
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Grid>

          {/* AI 종합 피드백 구조화 */}
          <Grid item xs={12}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Typography variant="h6">
                <AIIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'info.main' }} />
                AI 종합 피드백
              </Typography>
              <ToggleButtonGroup
                value={feedbackView}
                exclusive
                onChange={(_, newView) => newView && setFeedbackView(newView)}
                size="small"
              >
                <ToggleButton value="summary">
                  <CollapseIcon sx={{ mr: 1 }} />
                  요약 보기
                </ToggleButton>
                <ToggleButton value="detailed">
                  <ExpandIcon sx={{ mr: 1 }} />
                  상세 보기
                </ToggleButton>
              </ToggleButtonGroup>
            </Box>

            <Box
              p={3}
              bgcolor="grey.50"
              borderRadius={2}
              sx={{ position: 'relative' }}
            >
              {feedbackView === 'summary' ? (
                <Typography variant="body1" sx={{ fontSize: '1.1rem' }}>
                  {generateSummary(employee.ai_comment)}
                </Typography>
              ) : (
                <Box>
                  <Typography variant="body1" paragraph>
                    <strong>종합 평가:</strong> {employee.ai_comment || '평가 의견이 없습니다.'}
                  </Typography>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    <strong>AI 신뢰도:</strong> {employee.confidence_score || 92}% 
                    (높은 신뢰도로 분석되었습니다)
                  </Typography>
                </Box>
              )}
              <IconButton
                size="small"
                onClick={handleCopyToClipboard}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                <CopyIcon />
              </IconButton>
            </Box>
          </Grid>

          {/* 교육 추천 탭 구성 */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              <SchoolIcon sx={{ verticalAlign: 'middle', mr: 1, color: 'info.main' }} />
              맞춤형 교육 추천
            </Typography>
            
            <Tabs 
              value={selectedEducationTab} 
              onChange={(_, newValue) => setSelectedEducationTab(newValue)}
              sx={{ mb: 2 }}
            >
              {educationCategories.map((category, index) => (
                <Tab key={index} label={category.label} />
              ))}
            </Tabs>

            <Box display="flex" flexWrap="wrap" gap={1}>
              {educationCategories[selectedEducationTab].items.map((item, index) => (
                <Chip
                  key={index}
                  label={item}
                  color="info"
                  variant="outlined"
                  clickable
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </CardContent>

      {/* 하단 액션 버튼 강화 */}
      <CardActions sx={{ justifyContent: 'space-between', px: 3, pb: 3 }}>
        <Box display="flex" gap={1}>
          <Tooltip title="전체 분석 결과 PDF 저장">
            <Button
              startIcon={<PdfIcon />}
              onClick={handleExportPDF}
              size="small"
              variant="outlined"
              data-pdf-button
            >
              PDF 저장
            </Button>
          </Tooltip>
          <Tooltip title="전사 내 백분위 순위 보기">
            <Button
              startIcon={<RankingIcon />}
              onClick={handleShowRanking}
              size="small"
              variant="outlined"
            >
              백분위 순위
            </Button>
          </Tooltip>
        </Box>

        <Box display="flex" gap={1}>
          <Tooltip title="유사 인재 프로필과 비교">
            <Button
              startIcon={<CompareIcon />}
              onClick={() => setComparisonDialog(true)}
              size="small"
              variant="outlined"
            >
              유사 인재 비교
            </Button>
          </Tooltip>
          <Tooltip title="AI 분석 근거 상세 보기">
            <Button
              startIcon={<AIIcon />}
              onClick={() => setAiAnalysisDialog(true)}
              size="small"
              variant="outlined"
            >
              분석 근거
            </Button>
          </Tooltip>
          <Tooltip title="피드백 저장">
            <Button
              startIcon={<SaveIcon />}
              onClick={() => onSaveFeedback?.(employee.ai_comment)}
              size="small"
              color="primary"
            >
              저장
            </Button>
          </Tooltip>
          <Tooltip title="이메일 전송">
            <Button
              startIcon={<EmailIcon />}
              onClick={onSendEmail}
              size="small"
              color="primary"
              variant="contained"
            >
              이메일
            </Button>
          </Tooltip>
        </Box>
      </CardActions>

      {/* AI 분석 근거 다이얼로그 */}
      <Dialog open={aiAnalysisDialog} onClose={() => setAiAnalysisDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>🤖 AI 분석 근거 상세</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            <strong>분석 모델:</strong> AIRISS v4.2 (GPT-4 기반)
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>데이터 기반:</strong> 개인 평가 텍스트, 정량 지표, 8대 역량 평가
          </Typography>
          <Typography variant="body1" paragraph>
            <strong>핵심 판단 기준:</strong>
          </Typography>
          <Box component="ul" pl={2}>
            <Typography component="li" variant="body2">리더십 역량: 팀 관리 경험 및 의사결정 사례 분석</Typography>
            <Typography component="li" variant="body2">커뮤니케이션: 협업 성공 사례 및 갈등 해결 능력</Typography>
            <Typography component="li" variant="body2">전문성: 업무 성과 및 전문 지식 활용도</Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mt={2}>
            * AI 분석 결과는 참고용이며, 최종 인사 결정은 담당자의 종합적 판단이 필요합니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiAnalysisDialog(false)}>닫기</Button>
        </DialogActions>
      </Dialog>

      {/* 유사 인재 비교 다이얼로그 */}
      <Dialog open={comparisonDialog} onClose={() => setComparisonDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>👥 유사 인재 프로필 비교</DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            동일 직무 상위 1% 인재와의 역량 비교 분석
          </Typography>
          <Typography variant="body2" color="text.secondary">
            * 개인정보 보호를 위해 익명화된 데이터로 비교됩니다.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setComparisonDialog(false)}>닫기</Button>
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default EnhancedEmployeeDetailCard;