/**
 * AIRISS v4.2 통합 대시보드
 * Unified Dashboard with Step-by-Step Workflow
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Typography,
  Button,
  Tabs,
  Tab,
  Alert,
  Chip,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Analytics as AnalyticsIcon,
  Assessment as ResultsIcon,
  Download as DownloadIcon,
  TrendingUp,
  People,
  Speed,
  PictureAsPdf as PdfIcon,
  Person as PersonIcon,
} from '@mui/icons-material';

// 기존 컴포넌트들 임포트
import FileUpload from '../components/Upload/FileUpload';
import AnalysisView from '../components/Analysis/AnalysisView';
import ExecutiveDashboard from '../components/Employee/ExecutiveDashboard';
import EmployeeDashboardTable from '../components/Employee/EmployeeDashboardTable';
import EnhancedEmployeeDetailCard from '../components/Employee/EnhancedEmployeeDetailCard';
import { API_BASE_URL, downloadResults } from '../services/api';

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
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 2 }}>{children}</Box>}
    </div>
  );
}

const UnifiedDashboard: React.FC = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [resultsTabValue, setResultsTabValue] = useState(0);
  const [analysisStats, setAnalysisStats] = useState({
    totalAnalyzed: 0,
    employeeCount: 0,
    averageScore: 0,
    confidence: 92.3
  });
  const [analysisResults, setAnalysisResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string | null>(null);

  // pandas Series 문자열에서 실제 값 추출
  const extractFromPandasSeries = (value: any) => {
    if (typeof value !== 'string') return String(value);
    
    // pandas Series 형태 감지
    if (value.includes('dtype: object')) {
      // EMP001과 같은 패턴 추출
      const empIdMatch = value.match(/EMP\d+/);
      if (empIdMatch) {
        return empIdMatch[0];
      }
      
      // 한글 이름 패턴 추출 (예: 관리자1, 관리자2)
      const nameMatch = value.match(/관리자\d+/);
      if (nameMatch) {
        return nameMatch[0];
      }
      
      // 기타 텍스트 추출 시도
      const lines = value.split('\n');
      for (const line of lines) {
        const cleanLine = line.trim();
        if (cleanLine && !cleanLine.includes('uid') && !cleanLine.includes('Name:') && !cleanLine.includes('dtype:')) {
          return cleanLine;
        }
      }
    }
    
    return String(value);
  };

  // 분석 결과 데이터 정리 함수 (pandas Series 객체 처리)
  const cleanAnalysisResults = (results: any[]) => {
    if (!Array.isArray(results)) return [];
    console.log('🔧 데이터 정리 전:', results.slice(0, 1)); // 첫 번째 항목만 로그
    
    const cleaned = results.map((result: any, index: number) => {
      const originalEmpId = result.employee_id;
      const originalUid = result.uid;
      const originalName = result.name;
      
      console.log(`🔧 정리 중 [${index}]:`, {
        originalEmpId: originalEmpId,
        originalUid: originalUid,
        originalName: originalName,
        empIdType: typeof originalEmpId,
        uidType: typeof originalUid,
        nameType: typeof originalName
      });
      
      // pandas Series에서 실제 값 추출
      const cleanedEmpId = extractFromPandasSeries(originalEmpId) || extractFromPandasSeries(originalUid) || `employee_${index}`;
      const cleanedUid = extractFromPandasSeries(originalUid) || extractFromPandasSeries(originalEmpId) || `employee_${index}`;
      const cleanedName = extractFromPandasSeries(originalName) || cleanedEmpId || `직원${index + 1}`;
      
      console.log(`🔧 추출된 값 [${index}]:`, {
        cleanedEmpId,
        cleanedUid, 
        cleanedName
      });
      
      return {
        ...result,
        employee_id: cleanedEmpId,
        uid: cleanedUid,
        name: cleanedName,
      };
    });
    
    console.log('🔧 데이터 정리 후:', cleaned.slice(0, 1)); // 첫 번째 항목만 로그
    return cleaned;
  };

  // 첫 번째 직원 자동 선택
  useEffect(() => {
    if (analysisResults.length > 0 && !selectedEmployeeId) {
      const firstResult = analysisResults[0];
      const firstEmployeeId = String(firstResult.employee_id || firstResult.uid || `employee_0`);
      setSelectedEmployeeId(firstEmployeeId);
    }
  }, [analysisResults]);

  // 분석 결과를 가져오는 함수
  const fetchAnalysisStats = async () => {
    console.log('📊 분석 통계 가져오기 시작...');
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/analysis/jobs`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      console.log('📊 API 응답:', response.status, response.ok);
      
      if (response.ok) {
        const jobs = await response.json();
        console.log('📊 받은 작업 목록:', jobs);
        const completedJobs = jobs.filter((job: any) => job.status === 'completed');
        console.log('📊 완료된 작업:', completedJobs);
        
        // 분석 통계 계산
        let totalAnalyzed = 0;
        let employeeSet = new Set();
        let totalScore = 0;
        let scoreCount = 0;
        
        completedJobs.forEach((job: any) => {
          if (job.result && job.result.analysis_results) {
            totalAnalyzed++;
            job.result.analysis_results.forEach((result: any) => {
              employeeSet.add(result.employee_id);
              if (result.final_score) {
                totalScore += result.final_score;
                scoreCount++;
              }
            });
          }
        });
        
        const newStats = {
          totalAnalyzed: totalAnalyzed,
          employeeCount: employeeSet.size,
          averageScore: scoreCount > 0 ? totalScore / scoreCount : 0,
          confidence: 92.3 // 일단 고정값
        };
        
        console.log('📊 계산된 통계:', newStats);
        setAnalysisStats(newStats);
        
        // 최신 분석 결과 저장
        if (completedJobs.length > 0) {
          const latestJob = completedJobs[completedJobs.length - 1];
          if (latestJob.result) {
            // Handle both nested and flat structure
            const results = latestJob.result.analysis_results || latestJob.result.data || [];
            console.log('📊 Latest job results:', results.length, 'items');
            setAnalysisResults(cleanAnalysisResults(results));
            // currentJobId가 없을 때만 설정 (새로운 분석을 덮어쓰지 않기 위해)
            if (!currentJobId) {
              setCurrentJobId(latestJob.id);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error fetching analysis stats:', error);
    }
  };

  useEffect(() => {
    fetchAnalysisStats();
    // 30초마다 업데이트
    const interval = setInterval(fetchAnalysisStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const steps = [
    {
      label: '파일 업로드',
      icon: <UploadIcon />,
      description: '분석할 엑셀 파일을 업로드하세요',
    },
    {
      label: '분석 진행',
      icon: <AnalyticsIcon />,
      description: 'AI가 직원 데이터를 분석하고 있습니다',
    },
    {
      label: '결과 확인 및 다운로드',
      icon: <ResultsIcon />,
      description: 'AI 분석 결과를 확인하고 다운로드하세요',
    },
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleStepClick = async (step: number) => {
    setActiveStep(step);
    
    // 결과 확인 단계로 직접 이동할 때
    if (step === 2) {
      // 최신 작업 목록 가져오기
      await fetchAnalysisStats();
      
      // currentJobId가 없으면 가장 최근 완료된 작업 사용
      if (!currentJobId && analysisResults.length === 0) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/v1/analysis/jobs`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
          });
          
          if (response.ok) {
            const jobs = await response.json();
            const completedJobs = jobs.filter((job: any) => job.status === 'completed');
            
            if (completedJobs.length > 0) {
              const latestJob = completedJobs[0];
              setCurrentJobId(latestJob.id);
              
              // 결과 가져오기
              if (latestJob.result) {
                const results = latestJob.result.analysis_results || latestJob.result.data || [];
                console.log('📊 Setting results from latest job:', results.length, 'items');
                setAnalysisResults(cleanAnalysisResults(results));
              }
            }
          }
        } catch (error) {
          console.error('Error fetching latest job:', error);
        }
      }
    }
  };

  const handleResultsTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setResultsTabValue(newValue);
  };

  // 다운로드 핸들러
  const handleDownload = async (format: string) => {
    if (!currentJobId) return;
    
    try {
      const blob = await downloadResults(currentJobId, format);
      
      // 파일 확장자 및 MIME 타입 설정
      let extension = 'xlsx';
      let mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      
      if (format === 'csv') {
        extension = 'csv';
        mimeType = 'text/csv;charset=utf-8;';
      } else if (format === 'json') {
        extension = 'json';
        mimeType = 'application/json;charset=utf-8;';
      }
      
      // 다운로드 실행
      const url = window.URL.createObjectURL(new Blob([blob], { type: mimeType }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `AIRISS_v4_분석결과_${new Date().toISOString().split('T')[0]}.${extension}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('다운로드 실패:', error);
    }
  };

  // 개인별 PDF 다운로드 - 경영진 대시보드와 동일한 방식 사용
  const handlePdfDownload = (employeeId: string) => {
    if (!employeeId) return;
    
    // pandas Series 문자열 처리
    const cleanEmployeeId = extractFromPandasSeries(employeeId);
    
    // 새 창에서 PDF 페이지 열기
    const pdfUrl = `/employee/${cleanEmployeeId}/pdf?download=true`;
    window.open(pdfUrl, '_blank', 'width=850,height=1200');
    
    console.log('PDF 창 열림:', { employeeId: cleanEmployeeId, url: pdfUrl });
  };

  return (
    <Box>
      {/* 헤더 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          AI 분석 - 개인별 평가 시스템
        </Typography>
        <Typography variant="body1" color="text.secondary">
          직원 평가 파일을 업로드하고 AI 분석을 통해 개인별 결과를 확인하세요
        </Typography>
      </Box>

      {/* 현황 요약 카드 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    총 분석 건수
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {analysisStats.totalAnalyzed}
                  </Typography>
                </Box>
                <AnalyticsIcon sx={{ fontSize: 40, opacity: 0.3, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    분석 직원 수
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {analysisStats.employeeCount}
                  </Typography>
                </Box>
                <People sx={{ fontSize: 40, opacity: 0.3, color: 'secondary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    평균 점수
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {analysisStats.averageScore.toFixed(1)}
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, opacity: 0.3, color: 'success.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" variant="body2">
                    분석 신뢰도
                  </Typography>
                  <Typography variant="h5" fontWeight="bold">
                    {analysisStats.confidence}%
                  </Typography>
                </Box>
                <Speed sx={{ fontSize: 40, opacity: 0.3, color: 'warning.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 워크플로우 스테퍼 */}
      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          {steps.map((step, index) => (
            <Step key={step.label}>
              <StepLabel
                onClick={() => handleStepClick(index)}
                sx={{ cursor: 'pointer' }}
                icon={step.icon}
              >
                <Typography variant="h6">{step.label}</Typography>
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {step.description}
                </Typography>

                {/* Step 0: 파일 업로드 */}
                {index === 0 && (
                  <Box>
                    <FileUpload />
                    <Box sx={{ mt: 2 }}>
                      <Button
                        variant="contained"
                        onClick={handleNext}
                        sx={{ mr: 1 }}
                      >
                        다음 단계
                      </Button>
                    </Box>
                  </Box>
                )}

                {/* Step 1: 분석 진행 */}
                {index === 1 && (
                  <Box>
                    <Alert severity="info" sx={{ mb: 2 }}>
                      AI가 업로드된 파일을 분석하고 있습니다. 잠시만 기다려주세요.
                    </Alert>
                    <AnalysisView 
                      onAnalysisComplete={async (jobId) => {
                        console.log('분석 완료, jobId:', jobId);
                        setCurrentJobId(jobId);
                        
                        // 분석 결과 직접 가져오기
                        try {
                          console.log(`📡 분석 결과 API 호출: ${API_BASE_URL}/api/v1/analysis/results/${jobId}`);
                          const response = await fetch(`${API_BASE_URL}/api/v1/analysis/results/${jobId}`, {
                            method: 'GET',
                            headers: {
                              'Content-Type': 'application/json',
                            },
                            credentials: 'include',
                          });
                          
                          console.log('📡 API 응답 상태:', response.status, response.statusText);
                          
                          if (response.ok) {
                            const results = await response.json();
                            console.log('📊 받은 분석 결과:', results);
                            console.log('📊 결과 타입:', typeof results, '배열인가?', Array.isArray(results));
                            
                            // 결과가 배열이 아니면 배열로 변환
                            if (results && !Array.isArray(results)) {
                              if (results.analysis_results) {
                                console.log('📊 analysis_results 필드 사용');
                                setAnalysisResults(cleanAnalysisResults(results.analysis_results));
                              } else if (results.results) {
                                console.log('📊 results 필드 사용');
                                setAnalysisResults(cleanAnalysisResults(results.results));
                              } else {
                                console.log('📊 결과를 배열로 감싸기');
                                setAnalysisResults(cleanAnalysisResults([results]));
                              }
                            } else {
                              setAnalysisResults(cleanAnalysisResults(results || []));
                            }
                          } else {
                            console.error('❌ API 응답 에러:', response.status, await response.text());
                          }
                        } catch (error) {
                          console.error('❌ 분석 결과 가져오기 실패:', error);
                        }
                        
                        // 분석 통계도 업데이트
                        fetchAnalysisStats();
                      }}
                    />
                    <Box sx={{ mt: 2 }}>
                      <Button onClick={handleBack} sx={{ mr: 1 }}>
                        이전
                      </Button>
                      <Button
                        variant="contained"
                        onClick={async () => {
                          handleNext();
                          // 결과 탭을 0으로 리셋 (기본으로 AnalysisView가 보이도록)
                          setResultsTabValue(0);
                          
                          // 현재 jobId가 있으면 결과를 다시 가져오기
                          if (currentJobId) {
                            try {
                              console.log(`📡 결과 확인 시 API 호출: ${API_BASE_URL}/api/v1/analysis/results/${currentJobId}`);
                              const response = await fetch(`${API_BASE_URL}/api/v1/analysis/results/${currentJobId}`, {
                                method: 'GET',
                                headers: {
                                  'Content-Type': 'application/json',
                                },
                                credentials: 'include',
                              });
                              
                              console.log('📡 API 응답 상태:', response.status, response.statusText);
                              
                              if (response.ok) {
                                const results = await response.json();
                                console.log('📊 결과 확인 시 받은 분석 결과:', results);
                                
                                // 결과가 배열이 아니면 배열로 변환
                                if (results && !Array.isArray(results)) {
                                  if (results.analysis_results) {
                                    setAnalysisResults(cleanAnalysisResults(results.analysis_results));
                                  } else if (results.results) {
                                    setAnalysisResults(cleanAnalysisResults(results.results));
                                  } else {
                                    setAnalysisResults(cleanAnalysisResults([results]));
                                  }
                                } else {
                                  setAnalysisResults(cleanAnalysisResults(results || []));
                                }
                              } else {
                                console.error('❌ API 응답 에러:', response.status);
                              }
                            } catch (error) {
                              console.error('❌ 분석 결과 가져오기 실패:', error);
                            }
                          }
                          
                          // 최신 작업 목록도 업데이트
                          fetchAnalysisStats();
                        }}
                        sx={{ mr: 1 }}
                      >
                        결과 확인
                      </Button>
                    </Box>
                  </Box>
                )}

                {/* Step 2: 결과 확인 및 다운로드 */}
                {index === 2 && (
                  <Box>
                    <Alert severity="success" sx={{ mb: 2 }}>
                      AI 분석이 완료되었습니다. 아래에서 결과를 확인하고 다운로드하세요.
                    </Alert>
                    
                    {/* 디버깅 정보 */}
                    <Box sx={{ mb: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
                      <Typography variant="caption" display="block">
                        🔍 디버깅: currentJobId = {currentJobId || 'null'}, 
                        analysisResults.length = {analysisResults.length},
                        selectedEmployeeId = {selectedEmployeeId || 'null'}
                      </Typography>
                    </Box>
                    
                    {/* 다운로드 버튼들 */}
                    <Grid container spacing={2} sx={{ mb: 3 }}>
                      <Grid item xs={12} md={3}>
                        <Button
                          fullWidth
                          variant="contained"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownload('excel')}
                          disabled={!currentJobId}
                          color="primary"
                        >
                          엑셀 다운로드
                        </Button>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Button
                          fullWidth
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownload('csv')}
                          disabled={!currentJobId}
                        >
                          CSV 다운로드
                        </Button>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Button
                          fullWidth
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownload('json')}
                          disabled={!currentJobId}
                        >
                          JSON 다운로드
                        </Button>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <Button
                          fullWidth
                          variant="outlined"
                          startIcon={<PdfIcon />}
                          onClick={() => {
                            if (selectedEmployeeId) {
                              handlePdfDownload(selectedEmployeeId);
                            } else if (analysisResults.length > 0) {
                              const firstResult = analysisResults[0];
                              const firstEmployeeId = String(firstResult?.employee_id || firstResult?.uid || `employee_0`);
                              setSelectedEmployeeId(firstEmployeeId);
                              handlePdfDownload(firstEmployeeId);
                            }
                          }}
                          disabled={analysisResults.length === 0}
                          color="secondary"
                        >
                          개인별 PDF 리포트
                        </Button>
                      </Grid>
                    </Grid>

                    {/* 분석 결과 요약 */}
                    {analysisResults.length > 0 && (
                      <Paper sx={{ p: 3, mb: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          분석 결과 요약
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12} sm={4}>
                            <Card>
                              <CardContent>
                                <Typography color="text.secondary" gutterBottom>
                                  총 분석 인원
                                </Typography>
                                <Typography variant="h4">
                                  {analysisResults.length}명
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Card>
                              <CardContent>
                                <Typography color="text.secondary" gutterBottom>
                                  평균 점수
                                </Typography>
                                <Typography variant="h4">
                                  {analysisStats.averageScore.toFixed(1)}점
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                          <Grid item xs={12} sm={4}>
                            <Card>
                              <CardContent>
                                <Typography color="text.secondary" gutterBottom>
                                  분석 신뢰도
                                </Typography>
                                <Typography variant="h4">
                                  {analysisStats.confidence}%
                                </Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                        </Grid>
                      </Paper>
                    )}

                    {/* 개인별 리포트 */}
                    <Paper sx={{ p: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        개인별 분석 결과
                      </Typography>
                      
                      {/* 직원 선택 드롭다운 */}
                      {analysisResults.length > 0 && (
                        <Box sx={{ mb: 3 }}>
                          <FormControl fullWidth>
                            <InputLabel>직원 선택</InputLabel>
                            <Select
                              value={selectedEmployeeId || ''}
                              onChange={(e) => setSelectedEmployeeId(e.target.value)}
                              label="직원 선택"
                            >
                              {analysisResults.map((result, index) => {
                                const employeeId = String(result.employee_id || result.uid || `employee_${index}`);
                                const employeeName = String(result.name || employeeId);
                                return (
                                  <MenuItem key={index} value={employeeId}>
                                    {employeeName} ({employeeId}) - 점수: {result.final_score?.toFixed(1) || 'N/A'}
                                  </MenuItem>
                                );
                              })}
                            </Select>
                          </FormControl>
                        </Box>
                      )}

                      {/* 선택된 직원의 상세 정보 */}
                      {selectedEmployeeId && analysisResults.length > 0 && (() => {
                        const selectedResult = analysisResults.find(r => {
                          const id = String(r.employee_id || r.uid || '');
                          return id === selectedEmployeeId;
                        });
                        if (!selectedResult) return null;
                        
                        // EmployeeAIAnalysis 타입에 맞게 데이터 변환
                        const employeeData: any = {
                          employee_id: String(selectedResult.employee_id || selectedResult.uid || selectedEmployeeId),
                          name: String(selectedResult.name || selectedResult.employee_id || selectedResult.uid || '직원'),
                          department: selectedResult.department || '부서 정보 없음',
                          position: selectedResult.position || '직급 정보 없음',
                          ai_score: selectedResult.final_score || 0,
                          grade: selectedResult.grade || 'B',
                          competencies: {
                            실행력: selectedResult.competencies?.실행력 || selectedResult.qualitative_scores?.sentiment || 70,
                            성장지향: selectedResult.competencies?.성장지향 || 70,
                            협업: selectedResult.competencies?.협업 || selectedResult.qualitative_scores?.keyword || 70,
                            고객지향: selectedResult.competencies?.고객지향 || 70,
                            전문성: selectedResult.competencies?.전문성 || selectedResult.quantitative_score || 70,
                            혁신성: selectedResult.competencies?.혁신성 || 70,
                            리더십: selectedResult.competencies?.리더십 || 70,
                            커뮤니케이션: selectedResult.competencies?.커뮤니케이션 || 70,
                          },
                          strengths: selectedResult.strengths || ['업무 수행 능력이 우수함', '팀워크가 좋음'],
                          improvements: selectedResult.improvements || ['전문성 향상 필요', '리더십 개발 필요'],
                          ai_comment: selectedResult.ai_feedback || selectedResult.feedback || '직원의 전반적인 성과가 양호하며, 지속적인 성장 가능성이 있습니다.',
                          career_recommendation: selectedResult.career_recommendation || ['프로젝트 리더 역할 수행', '전문 교육 과정 이수'],
                          education_suggestion: selectedResult.education_suggestion || ['리더십 교육', '전문 기술 교육'],
                          analyzed_at: selectedResult.analyzed_at || new Date().toISOString(),
                          confidence_score: selectedResult.confidence_score || 85,
                          percentile_rank: selectedResult.percentile_rank || 75,
                        };
                        
                        return (
                          <Box>
                            <EnhancedEmployeeDetailCard
                              employee={employeeData}
                              onSaveFeedback={(feedback) => console.log('피드백 저장:', feedback)}
                              onCopyFeedback={() => {
                                navigator.clipboard.writeText(employeeData.ai_comment);
                                alert('피드백이 클립보드에 복사되었습니다.');
                              }}
                              onSendEmail={() => alert('이메일 전송 기능은 준비 중입니다.')}
                            />
                            
                            {/* PDF 다운로드 버튼 */}
                            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                              <Button
                                variant="contained"
                                color="secondary"
                                startIcon={<PdfIcon />}
                                onClick={() => handlePdfDownload(selectedEmployeeId)}
                                size="large"
                              >
                                개인 분석 리포트 PDF 다운로드
                              </Button>
                            </Box>
                          </Box>
                        );
                      })()}
                    </Paper>

                    <Box sx={{ mt: 2 }}>
                      <Button onClick={handleBack} sx={{ mr: 1 }}>
                        이전
                      </Button>
                      <Button
                        variant="contained"
                        onClick={() => setActiveStep(0)}
                        color="success"
                      >
                        새 분석 시작
                      </Button>
                    </Box>
                  </Box>
                )}

              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {/* 도움말 */}
      <Box sx={{ mt: 3 }}>
        <Alert severity="info">
          <Typography variant="body2">
            💡 <strong>사용법:</strong> 각 단계를 순서대로 진행하시거나, 스텝 라벨을 클릭하여 원하는 단계로 바로 이동할 수 있습니다.
          </Typography>
        </Alert>
      </Box>
    </Box>
  );
};

export default UnifiedDashboard;