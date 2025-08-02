import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Alert,
  AlertTitle,
  IconButton,
  Collapse
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  ExpandMore,
  ExpandLess,
  Timeline,
  Speed,
  Person
} from '@mui/icons-material';
import { useWebSocket } from '../../hooks/useWebSocket';

interface AnalysisProgressProps {
  jobId: string;
  autoStart?: boolean;
  onComplete?: (result: any) => void;
  onError?: (error: string) => void;
}

const AnalysisProgress: React.FC<AnalysisProgressProps> = ({
  jobId,
  autoStart = true,
  onComplete,
  onError
}) => {
  const {
    isConnected,
    connectionStatus,
    progress,
    lastMessage,
    error,
    connect,
    subscribeToJob,
    getJobProgress,
    clearError
  } = useWebSocket({
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8003',
    autoConnect: autoStart
  });
  
  const [expanded, setExpanded] = useState(true);
  const [estimatedTimeLeft, setEstimatedTimeLeft] = useState<string>('');
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<'idle' | 'starting' | 'running' | 'completed' | 'failed'>('idle');
  
  const jobProgress = getJobProgress(jobId);

  // WebSocket connection and job subscription
  useEffect(() => {
    if (autoStart && jobId) {
      connect().then(() => {
        subscribeToJob(jobId);
        setStartTime(new Date());
        setAnalysisStatus('running');
      }).catch(error => {
        console.error('WebSocket connection failed:', error);
      });
    }
  }, [jobId, autoStart, connect, subscribeToJob]);

  // Handle WebSocket messages
  useEffect(() => {
    if (lastMessage?.job_id === jobId) {
      console.log('📨 AnalysisProgress received message:', lastMessage);
      
      switch (lastMessage.type) {
        case 'analysis_started':
          setAnalysisStatus('running');
          setStartTime(new Date());
          break;
        case 'analysis_progress':
          setAnalysisStatus('running');
          // 진행률 메시지에서 상태 업데이트
          if (lastMessage.status) {
            console.log(`📊 Progress update: ${lastMessage.progress}% - ${lastMessage.status}`);
          }
          break;
        case 'analysis_completed':
          setAnalysisStatus('completed');
          if (onComplete) {
            // Pass the entire message or specific fields
            onComplete({
              job_id: lastMessage.job_id,
              average_score: lastMessage.average_score,
              total_processed: lastMessage.total_processed,
              message: lastMessage.message
            });
          }
          break;
        case 'analysis_failed':
          setAnalysisStatus('failed');
          if (onError) {
            onError(lastMessage.error || 'Analysis failed');
          }
          break;
      }
    }
  }, [lastMessage, jobId, onComplete, onError]);
  
  // Calculate estimated time left
  useEffect(() => {
    if (startTime && jobProgress && jobProgress.progress > 0 && jobProgress.progress < 100) {
      const elapsed = Date.now() - startTime.getTime();
      const rate = jobProgress.progress / elapsed;
      const remaining = (100 - jobProgress.progress) / rate;
      
      if (remaining > 0 && remaining < Infinity) {
        const minutes = Math.floor(remaining / (1000 * 60));
        const seconds = Math.floor((remaining % (1000 * 60)) / 1000);
        setEstimatedTimeLeft(`${minutes}분 ${seconds}초`);
      }
    }
  }, [jobProgress, startTime]);

  if (!jobId || analysisStatus === 'idle') {
    return null;
  }

  const getStatusIcon = () => {
    switch (analysisStatus) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      case 'running':
        return <PlayArrow color="primary" />;
      default:
        return <Pause color="disabled" />;
    }
  };

  const getStatusColor = () => {
    switch (analysisStatus) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'primary';
      default:
        return 'info';
    }
  };

  const getStatusText = () => {
    switch (analysisStatus) {
      case 'completed':
        return '분석 완료';
      case 'failed':
        return '분석 실패';
      case 'running':
        return '분석 진행 중';
      case 'starting':
        return '분석 시작 중';
      default:
        return '분석 준비 중';
    }
  };

  // 진행률 계산 개선 - lastMessage에서도 가져오기
  const progressValue = jobProgress?.progress || lastMessage?.progress || 0;
  const processed = jobProgress?.processed || lastMessage?.processed || 0;
  const total = jobProgress?.total || lastMessage?.total || 0;

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {getStatusIcon()}
        <Typography variant="h6" sx={{ ml: 1, flexGrow: 1 }}>
          {getStatusText()}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            label={isConnected ? '실시간 연결됨' : '폴링 모드'}
            color={isConnected ? 'success' : 'warning'}
            size="small"
            icon={isConnected ? <CheckCircle /> : <Warning />}
          />
          
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
            sx={{ ml: 1 }}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </Box>

      {/* Progress Bar */}
      <Box sx={{ mb: 2 }}>
        <LinearProgress
          variant="determinate"
          value={progressValue}
          sx={{
            height: 12,
            borderRadius: 6,
            bgcolor: 'grey.200',
            '& .MuiLinearProgress-bar': {
              bgcolor: getStatusColor() === 'error' ? 'error.main' : 
                     getStatusColor() === 'success' ? 'success.main' : 'primary.main'
            }
          }}
        />
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {progressValue.toFixed(1)}% 완료
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {processed.toLocaleString()} / {total.toLocaleString()}
          </Typography>
        </Box>
      </Box>

      {/* Expandable Details */}
      <Collapse in={expanded}>
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {/* Current Status */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Timeline color="primary" sx={{ fontSize: 20, mr: 1 }} />
                  <Typography variant="subtitle2">현재 상태</Typography>
                </Box>
                <Typography variant="body2">
                  {lastMessage?.status || jobProgress?.status || '분석을 준비 중입니다...'}
                </Typography>
                {(jobProgress?.current_uid || lastMessage?.current_uid) && (
                  <Typography variant="caption" color="text.secondary">
                    처리 중: {jobProgress?.current_uid || lastMessage?.current_uid}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Processing Speed */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Speed color="primary" sx={{ fontSize: 20, mr: 1 }} />
                  <Typography variant="subtitle2">처리 속도</Typography>
                </Box>
                <Typography variant="body2">
                  {processed > 0 && startTime ? (
                    `${(processed / ((Date.now() - startTime.getTime()) / 1000 / 60)).toFixed(1)} 건/분`
                  ) : (
                    '계산 중...'
                  )}
                </Typography>
                {estimatedTimeLeft && (
                  <Typography variant="caption" color="text.secondary">
                    남은 시간: {estimatedTimeLeft}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Job Info */}
          <Grid item xs={12} md={4}>
            <Card variant="outlined">
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Person color="primary" sx={{ fontSize: 20, mr: 1 }} />
                  <Typography variant="subtitle2">작업 정보</Typography>
                </Box>
                <Typography variant="body2">
                  작업 ID: {jobId.substring(0, 8)}...
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  시작: {startTime?.toLocaleTimeString() || '확인 중...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Average Score (if available) */}
        {jobProgress?.average_score !== undefined && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <AlertTitle>중간 결과</AlertTitle>
            현재까지 평균 점수: <strong>{jobProgress.average_score.toFixed(2)}점</strong>
          </Alert>
        )}

        {/* Error Alert */}
        {error && (
          <Alert severity="error" onClose={clearError}>
            <AlertTitle>오류 발생</AlertTitle>
            {error.message}
          </Alert>
        )}
      </Collapse>
    </Paper>
  );
};

export default AnalysisProgress;