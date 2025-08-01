import React from 'react';
import { Card, CardContent, Typography, Box, Chip, LinearProgress, Grid } from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Psychology as PsychologyIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

// 스타일 컴포넌트
const StyledCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  borderRadius: theme.spacing(2),
  boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
  '&:hover': {
    boxShadow: '0 6px 16px rgba(0,0,0,0.12)',
  },
}));

const ScoreBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.spacing(1),
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  textAlign: 'center',
}));

const DimensionBar = styled(Box)<{ score: number }>(({ theme, score }) => ({
  position: 'relative',
  height: 8,
  backgroundColor: theme.palette.grey[200],
  borderRadius: 4,
  overflow: 'hidden',
  '&::after': {
    content: '""',
    position: 'absolute',
    left: 0,
    top: 0,
    height: '100%',
    width: `${score}%`,
    backgroundColor: score >= 80 ? '#4caf50' : score >= 60 ? '#ff9800' : '#f44336',
    transition: 'width 0.3s ease',
  },
}));

interface OpinionAnalysisData {
  uid: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  text_score: number;
  sentiment_score: number;
  specificity_score: number;
  consistency_score: number;
  dimension_scores: {
    leadership: number;
    collaboration: number;
    problem_solving: number;
    innovation: number;
    communication: number;
    expertise: number;
    execution: number;
    growth: number;
  };
  hybrid_score: number;
  confidence: number;
  years_analyzed: string[];
}

interface OpinionAnalysisCardProps {
  data: OpinionAnalysisData;
  employeeName?: string;
}

const OpinionAnalysisCard: React.FC<OpinionAnalysisCardProps> = ({ data, employeeName }) => {
  // 8대 역량 한국어 라벨
  const dimensionLabels: { [key: string]: string } = {
    leadership: '리더십',
    collaboration: '협업',
    problem_solving: '문제해결',
    innovation: '혁신',
    communication: '소통',
    expertise: '전문성',
    execution: '실행력',
    growth: '성장',
  };

  // 감성 점수를 텍스트로 변환
  const getSentimentText = (score: number) => {
    if (score >= 0.5) return '매우 긍정적';
    if (score >= 0.2) return '긍정적';
    if (score >= -0.2) return '중립적';
    if (score >= -0.5) return '부정적';
    return '매우 부정적';
  };

  // 감성 점수에 따른 색상
  const getSentimentColor = (score: number) => {
    if (score >= 0.5) return '#4caf50';
    if (score >= 0.2) return '#8bc34a';
    if (score >= -0.2) return '#ff9800';
    if (score >= -0.5) return '#ff5722';
    return '#f44336';
  };

  return (
    <StyledCard>
      <CardContent>
        {/* 헤더 */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h6" fontWeight="bold">
              평가의견 분석
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {employeeName || data.uid} | 분석 연도: {data.years_analyzed.join(', ')}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Chip
              icon={<PsychologyIcon />}
              label={`신뢰도 ${Math.round(data.confidence * 100)}%`}
              size="small"
              color="primary"
            />
          </Box>
        </Box>

        {/* 요약 */}
        <Box mb={3} p={2} bgcolor="grey.50" borderRadius={1}>
          <Typography variant="body1" paragraph>
            {data.summary}
          </Typography>
        </Box>

        {/* 점수 카드 */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={6} md={3}>
            <ScoreBox>
              <Typography variant="h4" fontWeight="bold">
                {Math.round(data.text_score)}
              </Typography>
              <Typography variant="caption">텍스트 점수</Typography>
            </ScoreBox>
          </Grid>
          <Grid item xs={6} md={3}>
            <ScoreBox sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
              <Typography variant="h4" fontWeight="bold">
                {Math.round(data.hybrid_score)}
              </Typography>
              <Typography variant="caption">통합 점수</Typography>
            </ScoreBox>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center" p={2}>
              <Typography
                variant="h6"
                fontWeight="bold"
                color={getSentimentColor(data.sentiment_score)}
              >
                {getSentimentText(data.sentiment_score)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                감성 분석
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} md={3}>
            <Box textAlign="center" p={2}>
              <Typography variant="h6" fontWeight="bold">
                {Math.round(data.specificity_score * 100)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                구체성
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* 강점과 약점 */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} md={6}>
            <Box>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  강점
                </Typography>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {data.strengths.map((strength, index) => (
                  <Chip
                    key={index}
                    label={strength}
                    size="small"
                    color="success"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingDownIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  개선필요
                </Typography>
              </Box>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {data.weaknesses.map((weakness, index) => (
                  <Chip
                    key={index}
                    label={weakness}
                    size="small"
                    color="error"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          </Grid>
        </Grid>

        {/* 8대 역량 점수 */}
        <Box>
          <Box display="flex" alignItems="center" mb={2}>
            <AssessmentIcon sx={{ mr: 1 }} />
            <Typography variant="subtitle1" fontWeight="bold">
              8대 역량 평가
            </Typography>
          </Box>
          <Grid container spacing={2}>
            {Object.entries(data.dimension_scores).map(([dimension, score]) => (
              <Grid item xs={12} md={6} key={dimension}>
                <Box mb={1}>
                  <Box display="flex" justifyContent="space-between" mb={0.5}>
                    <Typography variant="body2">{dimensionLabels[dimension]}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {Math.round(score)}점
                    </Typography>
                  </Box>
                  <DimensionBar score={score} />
                </Box>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* 일관성 점수 */}
        <Box mt={3} display="flex" justifyContent="flex-end">
          <Typography variant="caption" color="text.secondary">
            연도별 일관성: {Math.round(data.consistency_score * 100)}%
          </Typography>
        </Box>
      </CardContent>
    </StyledCard>
  );
};

export default OpinionAnalysisCard;