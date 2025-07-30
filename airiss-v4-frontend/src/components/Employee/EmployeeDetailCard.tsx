/**
 * AIRISS v4.2 직원 상세 카드 컴포넌트
 * Employee Detail Card Component with AI Analysis
 */
import React from 'react';
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
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  ContentCopy as CopyIcon,
  Save as SaveIcon,
  Email as EmailIcon,
  School as SchoolIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
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
}

interface EmployeeDetailCardProps {
  employee: EmployeeAIAnalysis;
  onSaveFeedback?: (feedback: string) => void;
  onCopyFeedback?: () => void;
  onSendEmail?: () => void;
}

const EmployeeDetailCard: React.FC<EmployeeDetailCardProps> = ({
  employee,
  onSaveFeedback,
  onCopyFeedback,
  onSendEmail,
}) => {
  // 등급별 색상
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

  // 레이더 차트 데이터
  const radarData = {
    labels: Object.keys(employee.competencies),
    datasets: [
      {
        label: employee.name,
        data: Object.values(employee.competencies),
        backgroundColor: 'rgba(33, 150, 243, 0.2)',
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(33, 150, 243, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(33, 150, 243, 1)',
      },
    ],
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
        display: false,
      },
    },
    maintainAspectRatio: false,
  };

  const handleCopyToClipboard = () => {
    const feedbackText = `
${employee.name} (${employee.department} ${employee.position})
AI 종합점수: ${employee.ai_score} (${employee.grade}등급)

[강점]
${employee.strengths.join(', ')}

[개발 필요 역량]
${employee.improvements.join(', ')}

[AI 종합 피드백]
${employee.ai_comment}

[경력 개발 추천]
${employee.career_recommendation.join(', ')}

[교육 추천]
${employee.education_suggestion.join(', ')}
    `.trim();

    navigator.clipboard.writeText(feedbackText);
    onCopyFeedback?.();
  };

  const handleSaveFeedback = () => {
    onSaveFeedback?.(employee.ai_comment);
  };

  return (
    <Card sx={{ maxWidth: 800, margin: 'auto' }}>
      <CardContent>
        {/* 직원 기본 정보 */}
        <Box display="flex" alignItems="center" mb={3}>
          <Avatar
            src={employee.profile_image}
            alt={employee.name}
            sx={{ width: 80, height: 80, mr: 2 }}
          >
            {employee.name[0]}
          </Avatar>
          <Box flex={1}>
            <Typography variant="h5" component="h2" gutterBottom>
              {employee.name}
            </Typography>
            <Typography color="text.secondary" gutterBottom>
              {employee.department} | {employee.position}
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <Typography variant="h6">
                AI 종합점수: {employee.ai_score}
              </Typography>
              <Chip
                label={`${employee.grade}등급`}
                sx={{
                  backgroundColor: getGradeColor(employee.grade),
                  color: 'white',
                  fontWeight: 'bold',
                }}
              />
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Grid container spacing={3}>
          {/* 8대 역량 레이더 차트 */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              8대 핵심 역량
            </Typography>
            <Box height={300}>
              <Radar data={radarData} options={radarOptions} />
            </Box>
          </Grid>

          {/* 강점 및 개선점 */}
          <Grid item xs={12} md={6}>
            <Box mb={3}>
              <Typography variant="h6" gutterBottom>
                <TrendingUpIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                강점 TOP 3
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {employee.strengths.map((strength, index) => (
                  <Chip
                    key={index}
                    label={strength}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            <Box mb={3}>
              <Typography variant="h6" gutterBottom>
                <WarningIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                개발 필요 역량
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {employee.improvements.map((improvement, index) => (
                  <Chip
                    key={index}
                    label={improvement}
                    color="warning"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          </Grid>

          {/* AI 종합 피드백 */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              AI 종합 피드백
            </Typography>
            <Box
              p={2}
              bgcolor="grey.50"
              borderRadius={1}
              sx={{ position: 'relative' }}
            >
              <Typography variant="body1" paragraph>
                {employee.ai_comment}
              </Typography>
              <IconButton
                size="small"
                onClick={handleCopyToClipboard}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                <CopyIcon />
              </IconButton>
            </Box>
          </Grid>

          {/* 추천 사항 */}
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <TrendingUpIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              AI 추천 경력 방향
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {employee.career_recommendation.map((career, index) => (
                <Chip
                  key={index}
                  label={career}
                  color="success"
                  size="small"
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              <SchoolIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
              교육 추천
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1}>
              {employee.education_suggestion.map((education, index) => (
                <Chip
                  key={index}
                  label={education}
                  color="info"
                  size="small"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </CardContent>

      <CardActions sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
        <Tooltip title="피드백 복사">
          <Button
            startIcon={<CopyIcon />}
            onClick={handleCopyToClipboard}
            size="small"
          >
            복사
          </Button>
        </Tooltip>
        <Tooltip title="피드백 저장">
          <Button
            startIcon={<SaveIcon />}
            onClick={handleSaveFeedback}
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
      </CardActions>
    </Card>
  );
};

export default EmployeeDetailCard;