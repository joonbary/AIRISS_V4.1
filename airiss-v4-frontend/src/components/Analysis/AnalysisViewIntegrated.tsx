import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box,
  Paper,
  TextField,
  MenuItem,
  Button,
  Typography,
  Grid,
  Alert,
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Switch,
  Card,
  CardContent,
  CircularProgress,
  SelectChangeEvent,
  AlertTitle,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Settings,
  Info,
  ExpandMore,
  CloudUpload,
  Analytics,
  Download
} from '@mui/icons-material';
import { apiService, FileInfo, AnalysisRequest } from '../../services/api_integration';
import { useWebSocket } from '../../hooks/useWebSocket';
import AnalysisProgress from './AnalysisProgress';
import DashboardLayout from '../Layout/DashboardLayout';

interface AnalysisViewIntegratedProps {
  fileId?: string | null;
  fileName?: string;
  totalRecords?: number;
  columns?: string[];
}

const AnalysisViewIntegrated: React.FC<AnalysisViewIntegratedProps> = ({
  fileId: propFileId,
  fileName: propFileName,
  totalRecords: propTotalRecords,
  columns: propColumns = []
}) => {
  // File state
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [isLoadingFiles, setIsLoadingFiles] = useState(true);

  // Analysis configuration state
  const [fileId, setFileId] = useState<string | null>(propFileId || null);
  const [fileName, setFileName] = useState<string>(propFileName || '');
  const [totalRecords, setTotalRecords] = useState<number>(propTotalRecords || 0);
  const [columns, setColumns] = useState<string[]>(propColumns);

  // Analysis parameters
  const [sampleSize, setSampleSize] = useState<number>(25);
  const [analysisMode, setAnalysisMode] = useState<'text' | 'quantitative' | 'hybrid'>('hybrid');
  const [enableAI, setEnableAI] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [openaiModel, setOpenaiModel] = useState('gpt-3.5-turbo');
  const [maxTokens, setMaxTokens] = useState(1200);

  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<any>(null);
  const [analysisCompleted, setAnalysisCompleted] = useState(false);

  // WebSocket connection
  const { isConnected, connect, disconnect } = useWebSocket();

  // Auto-detected columns
  const [autoDetectedColumns, setAutoDetectedColumns] = useState({
    uid: '',
    opinion: '',
    quantitative: [] as string[]
  });

  // Memoized valid columns
  const validColumns = useMemo(() => Array.isArray(columns) ? columns : [], [columns]);

  // Load files on component mount
  useEffect(() => {
    const fetchFiles = async () => {
      try {
        setIsLoadingFiles(true);
        const data = await apiService.getFiles();
        setFiles(data);
        
        // Auto-select most recent file if no prop file provided
        if (data.length > 0 && !propFileId) {
          const latestFile = data[0];
          handleFileSelection(latestFile);
        }
      } catch (error) {
        console.error('Failed to fetch files:', error);
        setError('파일 목록을 불러오는데 실패했습니다.');
      } finally {
        setIsLoadingFiles(false);
      }
    };

    fetchFiles();
  }, [propFileId]);

  // Auto-detect columns when file is selected
  useEffect(() => {
    if (validColumns.length > 0) {
      const detected = {
        uid: detectColumn(validColumns, ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp']),
        opinion: detectColumn(validColumns, ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', 'comment']),
        quantitative: validColumns.filter(col => 
          ['점수', 'score', '평점', 'rating', '등급', 'grade'].some(keyword => 
            col.toLowerCase().includes(keyword.toLowerCase())
          )
        )
      };
      
      setAutoDetectedColumns(detected);
      console.log('🎯 Auto-detected columns:', detected);
    }
  }, [validColumns]);

  // Connect to WebSocket on mount
  useEffect(() => {
    console.log('🔌 Initializing WebSocket connection...');
    connect(['analysis', 'alerts']).catch(error => {
      console.warn('WebSocket connection failed, falling back to polling:', error);
    });

    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  // Helper function to detect columns
  const detectColumn = (columns: string[], keywords: string[]): string => {
    return columns.find(col => 
      keywords.some(keyword => col.toLowerCase().includes(keyword.toLowerCase()))
    ) || '';
  };

  // Handle file selection
  const handleFileSelection = (file: FileInfo) => {
    setSelectedFile(file);
    setFileId(file.id);
    setFileName(file.filename);
    setTotalRecords(file.total_records);
    // Note: FileInfo doesn't include columns, we'd need to fetch from backend
    setColumns([]);
  };

  // Handle file select change
  const handleFileSelect = (event: SelectChangeEvent<string>) => {
    const file = files.find(f => f.id === event.target.value);
    if (file) {
      handleFileSelection(file);
    }
  };

  // Start analysis
  const handleStartAnalysis = async () => {
    if (!fileId) {
      setError('파일을 먼저 선택해주세요.');
      return;
    }

    // Validate AI settings if enabled
    if (enableAI && !apiKey.trim()) {
      setError('AI 피드백을 사용하려면 OpenAI API 키를 입력해주세요.');
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setAnalysisCompleted(false);
    setResults(null);

    try {
      const requestParams: AnalysisRequest = {
        file_id: fileId,
        sample_size: sampleSize,
        analysis_mode: analysisMode,
        enable_ai_feedback: enableAI,
        openai_api_key: enableAI ? apiKey : undefined,
        openai_model: openaiModel,
        max_tokens: maxTokens
      };

      console.log('🚀 Starting analysis:', requestParams);

      const response = await apiService.startAnalysis(requestParams);
      setJobId(response.job_id);
      
      console.log('✅ Analysis started:', response);
    } catch (err: any) {
      console.error('❌ Analysis start failed:', err);
      setError(err.message || '분석 시작에 실패했습니다.');
      setIsAnalyzing(false);
    }
  };

  // Handle analysis completion
  const handleAnalysisComplete = useCallback((result: any) => {
    console.log('🎉 Analysis completed:', result);
    setIsAnalyzing(false);
    setAnalysisCompleted(true);
    setResults(result);
  }, []);

  // Handle analysis error
  const handleAnalysisError = useCallback((errorMessage: string) => {
    console.error('❌ Analysis error:', errorMessage);
    setError(errorMessage);
    setIsAnalyzing(false);
    setAnalysisCompleted(false);
  }, []);

  // Download results
  const handleDownload = async (format: 'excel' | 'csv' | 'json' = 'excel') => {
    if (!jobId) {
      setError('다운로드할 결과가 없습니다.');
      return;
    }

    try {
      const blob = await apiService.downloadResults(jobId, format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AIRISS_분석결과_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('✅ Download completed');
    } catch (err: any) {
      console.error('❌ Download failed:', err);
      setError(`다운로드 실패: ${err.message}`);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        {/* Header */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <Analytics sx={{ mr: 2, color: 'primary.main' }} />
            AIRISS v4.0 HR 분석
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Excel/CSV 파일을 업로드하고 AI 기반 HR 분석을 수행하세요.
          </Typography>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            <AlertTitle>오류</AlertTitle>
            {error}
          </Alert>
        )}

        {/* File Selection */}
        <Accordion expanded defaultExpanded sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <CloudUpload sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">1. 파일 선택</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Card variant="outlined">
              <CardContent>
                {isLoadingFiles ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <CircularProgress size={20} />
                    <Typography>파일 목록을 불러오는 중...</Typography>
                  </Box>
                ) : files.length === 0 ? (
                  <Alert severity="warning">
                    <AlertTitle>파일 없음</AlertTitle>
                    먼저 파일을 업로드해주세요. 
                    <Button variant="text" href="/upload" sx={{ ml: 1 }}>
                      파일 업로드
                    </Button>
                  </Alert>
                ) : (
                  <>
                    <FormControl fullWidth sx={{ mb: 2 }}>
                      <InputLabel>분석할 파일 선택</InputLabel>
                      <Select
                        value={fileId || ''}
                        onChange={handleFileSelect}
                        displayEmpty
                      >
                        <MenuItem value="" disabled>
                          파일을 선택하세요
                        </MenuItem>
                        {files.map((file) => (
                          <MenuItem key={file.id} value={file.id}>
                            {file.filename} ({file.total_records.toLocaleString()}개 레코드)
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    {selectedFile && (
                      <Box>
                        <Typography variant="h6">{fileName}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          총 {totalRecords.toLocaleString()}개 레코드
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          업로드: {new Date(selectedFile.upload_time).toLocaleString()}
                        </Typography>
                      </Box>
                    )}
                  </>
                )}
              </CardContent>
            </Card>

            {/* Auto-detected columns info */}
            {validColumns.length > 0 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <AlertTitle>자동 감지된 컬럼 정보</AlertTitle>
                <Box sx={{ mt: 1 }}>
                  {autoDetectedColumns.uid && (
                    <Typography variant="body2">
                      • UID 컬럼: <strong>{autoDetectedColumns.uid}</strong>
                    </Typography>
                  )}
                  {autoDetectedColumns.opinion && (
                    <Typography variant="body2">
                      • 의견 컬럼: <strong>{autoDetectedColumns.opinion}</strong>
                    </Typography>
                  )}
                  {autoDetectedColumns.quantitative.length > 0 && (
                    <Typography variant="body2">
                      • 정량 데이터 컬럼: <strong>{autoDetectedColumns.quantitative.join(', ')}</strong>
                    </Typography>
                  )}
                  {!autoDetectedColumns.uid && !autoDetectedColumns.opinion && (
                    <Typography variant="body2" color="warning.main">
                      ⚠️ UID 또는 의견 컬럼을 자동으로 감지하지 못했습니다.
                    </Typography>
                  )}
                </Box>
              </Alert>
            )}
          </AccordionDetails>
        </Accordion>

        {/* Analysis Configuration */}
        <Accordion sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Settings sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">2. 분석 설정</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Basic Settings */}
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>샘플 크기</InputLabel>
                  <Select
                    value={sampleSize}
                    onChange={(e) => setSampleSize(e.target.value as number)}
                  >
                    <MenuItem value={10}>10개 (테스트)</MenuItem>
                    <MenuItem value={25}>25개 (표준)</MenuItem>
                    <MenuItem value={50}>50개 (상세)</MenuItem>
                    <MenuItem value={100}>100개 (정밀)</MenuItem>
                    <MenuItem value={totalRecords || 0}>
                      전체 데이터 ({totalRecords.toLocaleString()}개)
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>분석 모드</InputLabel>
                  <Select
                    value={analysisMode}
                    onChange={(e) => setAnalysisMode(e.target.value as any)}
                  >
                    <MenuItem value="text">텍스트 분석</MenuItem>
                    <MenuItem value="quantitative">정량 분석</MenuItem>
                    <MenuItem value="hybrid">하이브리드 (추천)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              {/* AI Settings */}
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <FormControlLabel
                  control={
                    <Switch
                      checked={enableAI}
                      onChange={(e) => setEnableAI(e.target.checked)}
                    />
                  }
                  label="OpenAI GPT 피드백 활성화 (선택사항)"
                />
              </Grid>

              {enableAI && (
                <>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      type="password"
                      label="OpenAI API Key"
                      value={apiKey}
                      onChange={(e) => setApiKey(e.target.value)}
                      placeholder="sk-..."
                      helperText="AI 피드백을 위한 OpenAI API 키"
                    />
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>모델 선택</InputLabel>
                      <Select
                        value={openaiModel}
                        onChange={(e) => setOpenaiModel(e.target.value)}
                      >
                        <MenuItem value="gpt-3.5-turbo">GPT-3.5 Turbo</MenuItem>
                        <MenuItem value="gpt-4">GPT-4</MenuItem>
                        <MenuItem value="gpt-4-turbo">GPT-4 Turbo</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>응답 길이</InputLabel>
                      <Select
                        value={maxTokens}
                        onChange={(e) => setMaxTokens(e.target.value as number)}
                      >
                        <MenuItem value={800}>간단 (800 토큰)</MenuItem>
                        <MenuItem value={1200}>표준 (1200 토큰)</MenuItem>
                        <MenuItem value={1500}>상세 (1500 토큰)</MenuItem>
                        <MenuItem value={2000}>완전 (2000 토큰)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Analysis Control */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            3. 분석 실행
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={isAnalyzing ? <Stop /> : <PlayArrow />}
              onClick={handleStartAnalysis}
              disabled={isAnalyzing || !fileId}
              sx={{
                bgcolor: 'primary.main',
                '&:hover': { bgcolor: 'primary.dark' }
              }}
            >
              {isAnalyzing ? '분석 중...' : '분석 시작'}
            </Button>

            {jobId && (
              <Typography variant="caption" color="text.secondary">
                작업 ID: {jobId.substring(0, 8)}...
              </Typography>
            )}
          </Box>

          <Alert severity="info" icon={<Info />}>
            <Typography variant="body2">
              • 연결 상태: {isConnected ? '실시간 연결됨' : '폴링 모드'}
              <br />
              • 분석 시간은 데이터 크기와 샘플 수에 따라 달라집니다.
              <br />
              • AI 피드백을 활성화하면 분석 시간이 더 소요될 수 있습니다.
            </Typography>
          </Alert>
        </Paper>

        {/* Progress Display */}
        {(isAnalyzing || jobId) && (
          <AnalysisProgress
            jobId={jobId || ''}
            onComplete={handleAnalysisComplete}
            onError={handleAnalysisError}
          />
        )}

        {/* Results */}
        {analysisCompleted && results && (
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              4. 분석 결과
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={4}>
                <Card>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      총 분석
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {results.total_processed || 0}개
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Card>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      평균 점수
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {results.average_score?.toFixed(1) || '0.0'}점
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Card>
                  <CardContent>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      작업 상태
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      완료
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            {/* Download Buttons */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={() => handleDownload('excel')}
                sx={{ bgcolor: 'success.main', '&:hover': { bgcolor: 'success.dark' } }}
              >
                Excel 다운로드
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleDownload('csv')}
                color="success"
              >
                CSV 다운로드
              </Button>
              
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleDownload('json')}
                color="success"
              >
                JSON 다운로드
              </Button>
            </Box>
          </Paper>
        )}
      </Box>
    </DashboardLayout>
  );
};

export default AnalysisViewIntegrated;