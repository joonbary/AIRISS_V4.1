import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Tooltip,
  IconButton,
  Menu,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Download,
  Search,
  FilterList,
  Visibility,
  Assessment,
  Person,
  TrendingUp,
  TrendingDown,
  MoreVert,
  ExpandMore,
  BarChart,
  PieChart,
  TableChart as TableIcon
} from '@mui/icons-material';
import { getAnalysisStatus, getAnalysisResults, downloadResults } from '../../services/api';
import DashboardLayout from '../Layout/DashboardLayout';

interface ResultsViewerProps {
  jobId: string;
  autoLoad?: boolean;
}

interface EmployeeResult {
  uid: string;
  name?: string;
  department?: string;
  position?: string;
  overall_score: number;
  grade: string;
  dimension_scores: Record<string, number>;
  ai_feedback?: string;
  competency_scores?: Record<string, number>;
  strengths?: string[];
  improvement_areas?: string[];
}

interface AnalysisResult {
  job_id: string;
  status: string;
  filename: string;
  total_analyzed: number;
  average_score: number;
  processing_time: string;
  results: EmployeeResult[];
  analysis_summary: {
    high_performers: number;
    low_performers: number;
    grade_distribution: Record<string, number>;
  };
}

const ResultsViewer: React.FC<ResultsViewerProps> = ({ jobId, autoLoad = true }) => {
  // Results state
  const [results, setResults] = useState<AnalysisResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Table state
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchTerm, setSearchTerm] = useState('');
  const [gradeFilter, setGradeFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'score' | 'grade' | 'uid'>('score');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Dialog state
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeResult | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  
  // Menu state
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  // Visualization state
  const [visualizationMode, setVisualizationMode] = useState<'table' | 'chart'>('table');

  // Load results on component mount
  useEffect(() => {
    if (autoLoad && jobId) {
      loadResults();
    }
  }, [jobId, autoLoad]);

  // Load analysis results
  const loadResults = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // First check job status
      const jobStatus = await getAnalysisStatus(jobId);
      
      if (jobStatus.status !== 'completed') {
        setError(`분석이 아직 완료되지 않았습니다. 상태: ${jobStatus.status}`);
        return;
      }
      
      // Get real analysis results from backend
      const analysisResults = await getAnalysisResults(jobId);
      
      console.log('📥 백엔드에서 받은 원본 데이터:', analysisResults);
      console.log('📋 데이터 항목 수:', analysisResults?.data?.length);
      console.log('🔍 첫 번째 데이터:', analysisResults?.data?.[0]);
      
      if (!analysisResults || !analysisResults.data) {
        setError('분석 결과 데이터를 찾을 수 없습니다.');
        return;
      }
      
      // Transform backend results to frontend format
      const transformedResults: AnalysisResult = {
        job_id: jobId,
        status: 'completed',
        filename: analysisResults.filename || jobStatus.filename || '분석파일',
        total_analyzed: analysisResults.summary?.total_analyzed || analysisResults.data.length,
        average_score: analysisResults.summary?.average_score || 0,
        processing_time: analysisResults.metadata?.processing_time || '완료',
        results: analysisResults.data.map((item: any) => ({
          uid: item.uid || 'N/A',
          name: item.name || '',
          department: item.department || '',
          position: item.position || '',
          overall_score: item.score || item.ai_score || 0,
          grade: item.grade || 'N/A',
          dimension_scores: item.dimension_scores || {},
          ai_feedback: item.explainability?.ai_feedback,
          competency_scores: item.dimension_scores,
          strengths: item.explainability?.strengths || [],
          improvement_areas: item.explainability?.improvement_areas || []
        })),
        analysis_summary: {
          high_performers: analysisResults.summary?.successful || 0,
          low_performers: analysisResults.summary?.failed || 0,
          grade_distribution: analysisResults.summary?.grade_distribution || {}
        }
      };
      
      setResults(transformedResults);
    } catch (err: any) {
      console.error('Failed to load results:', err);
      setError(err.message || '분석 결과를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // Download results
  const handleDownload = async (format: 'excel' | 'csv' | 'json') => {
    try {
      console.log(`📥 Downloading: ${format.toUpperCase()} format for job ${jobId}`);
      
      const blob = await downloadResults(jobId, format);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename with proper extension
      const extensions = { excel: 'xlsx', csv: 'csv', json: 'json' };
      const extension = extensions[format] || 'xlsx';
      link.download = `AIRISS_분석결과_${jobId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.${extension}`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log(`✅ ${format.toUpperCase()} download completed`);
    } catch (err: any) {
      console.error(`❌ ${format.toUpperCase()} download failed:`, err);
      setError(err.message || `${format.toUpperCase()} 다운로드 실패`);
    }
  };

  // Filter and sort results
  const getFilteredAndSortedResults = (): EmployeeResult[] => {
    if (!results?.results) return [];

    let filtered = results.results.filter(result => {
      const matchesSearch = searchTerm === '' || 
        result.uid.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesGrade = gradeFilter === 'all' || result.grade === gradeFilter;
      return matchesSearch && matchesGrade;
    });

    // Sort results
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'score':
          comparison = a.overall_score - b.overall_score;
          break;
        case 'grade':
          comparison = a.grade.localeCompare(b.grade);
          break;
        case 'uid':
          comparison = a.uid.localeCompare(b.uid);
          break;
      }
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return filtered;
  };

  // Get grade color
  const getGradeColor = (grade: string) => {
    const gradeColors: Record<string, string> = {
      'A': 'success',
      'B': 'info',
      'C': 'warning',
      'D': 'error',
      'F': 'error'
    };
    return gradeColors[grade] || 'default';
  };

  // Get score color
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success.main';
    if (score >= 60) return 'info.main';
    if (score >= 40) return 'warning.main';
    return 'error.main';
  };

  // Handle employee detail view
  const handleViewDetails = (employee: EmployeeResult) => {
    console.log('🔍 선택된 직원 상세 정보:', employee);
    console.log('👤 UID:', employee.uid);
    console.log('📛 이름:', employee.name);
    console.log('📊 점수:', employee.overall_score);
    setSelectedEmployee(employee);
    setDetailDialogOpen(true);
  };

  // Handle table pagination
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const filteredResults = getFilteredAndSortedResults();
  const paginatedResults = filteredResults.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Get unique grades for filter
  const availableGrades = results?.results 
    ? Array.from(new Set(results.results.map(r => r.grade))).sort()
    : [];

  if (isLoading) {
    return (
      <DashboardLayout>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" gutterBottom>
            분석 결과를 불러오는 중...
          </Typography>
          <LinearProgress sx={{ mt: 2, maxWidth: 400, mx: 'auto' }} />
        </Box>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <Alert severity="error" sx={{ m: 3 }}>
          {error}
          <Button variant="outlined" onClick={loadResults} sx={{ ml: 2 }}>
            다시 시도
          </Button>
        </Alert>
      </DashboardLayout>
    );
  }

  if (!results) {
    return (
      <DashboardLayout>
        <Alert severity="info" sx={{ m: 3 }}>
          분석 결과가 없습니다.
          <Button variant="outlined" onClick={loadResults} sx={{ ml: 2 }}>
            결과 불러오기
          </Button>
        </Alert>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box sx={{ maxWidth: 1400, mx: 'auto' }}>
        {/* Header */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4" sx={{ display: 'flex', alignItems: 'center' }}>
              <Assessment sx={{ mr: 2, color: 'primary.main' }} />
              분석 결과
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="contained"
                startIcon={<Download />}
                onClick={(e) => setAnchorEl(e.currentTarget)}
                sx={{ bgcolor: 'success.main', '&:hover': { bgcolor: 'success.dark' } }}
              >
                다운로드
              </Button>
              
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem onClick={() => { handleDownload('excel'); setAnchorEl(null); }}>
                  📊 Excel (.xlsx)
                </MenuItem>
                <MenuItem onClick={() => { handleDownload('csv'); setAnchorEl(null); }}>
                  📄 CSV (.csv)
                </MenuItem>
                <MenuItem onClick={() => { handleDownload('json'); setAnchorEl(null); }}>
                  🔧 JSON (.json)
                </MenuItem>
              </Menu>
            </Box>
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            작업 ID: {jobId} • 처리 시간: {results.processing_time} • 파일: {results.filename}
          </Typography>
        </Paper>

        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Person color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    총 분석
                  </Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {results.total_analyzed.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  명
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <BarChart color="primary" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    평균 점수
                  </Typography>
                </Box>
                <Typography variant="h4" color="primary">
                  {results.average_score.toFixed(1)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  점
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingUp color="success" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    우수 성과자
                  </Typography>
                </Box>
                <Typography variant="h4" color="success.main">
                  {results.analysis_summary.high_performers}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  명
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <TrendingDown color="error" sx={{ mr: 1 }} />
                  <Typography variant="body2" color="text.secondary">
                    개선 필요
                  </Typography>
                </Box>
                <Typography variant="h4" color="error.main">
                  {results.analysis_summary.low_performers}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  명
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Grade Distribution */}
        <Accordion sx={{ mb: 3 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <PieChart sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">등급 분포</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {Object.entries(results.analysis_summary.grade_distribution).map(([grade, count]) => (
                <Grid item xs={6} sm={4} md={2} key={grade}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center', py: 2 }}>
                      <Typography variant="h5" color={`${getGradeColor(grade)}.main`}>
                        {grade}
                      </Typography>
                      <Typography variant="h6">
                        {count}명
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ({((count / results.total_analyzed) * 100).toFixed(1)}%)
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Filters and Controls */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            상세 결과 ({filteredResults.length.toLocaleString()}명)
          </Typography>
          
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="직원 ID로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>등급 필터</InputLabel>
                <Select
                  value={gradeFilter}
                  onChange={(e) => setGradeFilter(e.target.value)}
                  startAdornment={<FilterList sx={{ mr: 1 }} />}
                >
                  <MenuItem value="all">전체</MenuItem>
                  {availableGrades.map(grade => (
                    <MenuItem key={grade} value={grade}>
                      등급 {grade}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth size="small">
                <InputLabel>정렬 기준</InputLabel>
                <Select
                  value={`${sortBy}_${sortOrder}`}
                  onChange={(e) => {
                    const [newSortBy, newSortOrder] = e.target.value.split('_');
                    setSortBy(newSortBy as any);
                    setSortOrder(newSortOrder as any);
                  }}
                >
                  <MenuItem value="score_desc">점수 높은순</MenuItem>
                  <MenuItem value="score_asc">점수 낮은순</MenuItem>
                  <MenuItem value="grade_asc">등급순</MenuItem>
                  <MenuItem value="uid_asc">ID순</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<TableIcon />}
                onClick={() => setVisualizationMode(visualizationMode === 'table' ? 'chart' : 'table')}
              >
                {visualizationMode === 'table' ? '차트' : '테이블'}
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Results Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>UID</TableCell>
                  <TableCell>이름</TableCell>
                  <TableCell>부서</TableCell>
                  <TableCell>직급</TableCell>
                  <TableCell align="center">종합 점수</TableCell>
                  <TableCell align="center">등급</TableCell>
                  <TableCell align="center">차원별 점수</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedResults.map((result) => (
                  <TableRow key={result.uid} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {result.uid}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2">
                        {result.name || '-'}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2">
                        {result.department || '-'}
                      </Typography>
                    </TableCell>
                    
                    <TableCell>
                      <Typography variant="body2">
                        {result.position || '-'}
                      </Typography>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Typography
                        variant="h6"
                        sx={{ color: getScoreColor(result.overall_score) }}
                      >
                        {result.overall_score ? result.overall_score.toFixed(1) : 'N/A'}
                      </Typography>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Chip
                        label={result.grade}
                        color={getGradeColor(result.grade) as any}
                        size="small"
                      />
                    </TableCell>
                    
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, justifyContent: 'center' }}>
                        {Object.entries(result.dimension_scores).slice(0, 3).map(([dim, score]) => (
                          <Tooltip key={dim} title={`${dim}: ${score.toFixed(1)}`}>
                            <Chip
                              label={`${dim.substring(0, 2)}: ${score.toFixed(1)}`}
                              size="small"
                              variant="outlined"
                            />
                          </Tooltip>
                        ))}
                        {Object.keys(result.dimension_scores).length > 3 && (
                          <Chip
                            label={`+${Object.keys(result.dimension_scores).length - 3}`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </TableCell>
                    
                    <TableCell align="center">
                      <Tooltip title="상세 보기">
                        <IconButton
                          size="small"
                          onClick={() => handleViewDetails(result)}
                        >
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          <TablePagination
            component="div"
            count={filteredResults.length}
            page={page}
            onPageChange={handleChangePage}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={handleChangeRowsPerPage}
            rowsPerPageOptions={[10, 25, 50, 100]}
            labelRowsPerPage="페이지당 행 수:"
            labelDisplayedRows={({ from, to, count }) => `${from}-${to} / ${count}`}
          />
        </Paper>

        {/* Employee Detail Dialog */}
        <Dialog
          open={detailDialogOpen}
          onClose={() => setDetailDialogOpen(false)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Person sx={{ mr: 1 }} />
              직원 상세 분석: {selectedEmployee?.uid}
            </Box>
          </DialogTitle>
          
          <DialogContent>
            {selectedEmployee && (
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        종합 평가
                      </Typography>
                      <Typography variant="h4" color="primary" gutterBottom>
                        {selectedEmployee.overall_score.toFixed(1)}점
                      </Typography>
                      <Chip
                        label={`등급 ${selectedEmployee.grade}`}
                        color={getGradeColor(selectedEmployee.grade) as any}
                      />
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} sm={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        차원별 점수
                      </Typography>
                      {Object.entries(selectedEmployee.dimension_scores).map(([dim, score]) => (
                        <Box key={dim} sx={{ mb: 1 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="body2">{dim}</Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {score.toFixed(1)}
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={score}
                            sx={{
                              height: 6,
                              borderRadius: 3,
                              bgcolor: 'grey.200',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: getScoreColor(score)
                              }
                            }}
                          />
                        </Box>
                      ))}
                    </CardContent>
                  </Card>
                </Grid>
                
                {selectedEmployee.ai_feedback && (
                  <Grid item xs={12}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" gutterBottom>
                          AI 피드백
                        </Typography>
                        <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                          {selectedEmployee.ai_feedback}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            )}
          </DialogContent>
          
          <DialogActions>
            <Button onClick={() => setDetailDialogOpen(false)}>
              닫기
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </DashboardLayout>
  );
};

export default ResultsViewer;