/**
 * AIRISS v4.2 전체 직원 대시보드 테이블
 * Employee Dashboard Table with Filtering, Searching, and Sorting
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
  TableSortLabel,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Avatar,
  IconButton,
  Typography,
  Grid,
  InputAdornment,
  Button,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Visibility as ViewIcon,
  Clear as ClearIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { visuallyHidden } from '@mui/utils';

interface EmployeeAIAnalysisSummary {
  employee_id: string;
  name: string;
  department: string;
  position: string;
  profile_image?: string;
  ai_score: number;
  grade: string;
  strengths_summary: string;
  improvements_summary: string;
  ai_comment_preview: string;
}

interface EmployeeDashboardTableProps {
  onViewDetail?: (employeeId: string) => void;
  onExportData?: () => void;
}

type Order = 'asc' | 'desc';

interface HeadCell {
  id: keyof EmployeeAIAnalysisSummary;
  label: string;
  numeric: boolean;
}

const headCells: readonly HeadCell[] = [
  { id: 'name', numeric: false, label: '이름' },
  { id: 'department', numeric: false, label: '부서' },
  { id: 'position', numeric: false, label: '직급' },
  { id: 'ai_score', numeric: true, label: 'AI 점수' },
  { id: 'grade', numeric: false, label: '등급' },
  { id: 'strengths_summary', numeric: false, label: '강점' },
  { id: 'improvements_summary', numeric: false, label: '개발필요' },
  { id: 'ai_comment_preview', numeric: false, label: 'AI 코멘트' },
];

const EmployeeDashboardTable: React.FC<EmployeeDashboardTableProps> = ({
  onViewDetail,
  onExportData,
}) => {
  // State
  const [employees, setEmployees] = useState<EmployeeAIAnalysisSummary[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [order, setOrder] = useState<Order>('desc');
  const [orderBy, setOrderBy] = useState<keyof EmployeeAIAnalysisSummary>('ai_score');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filterPosition, setFilterPosition] = useState('');
  const [filterGrade, setFilterGrade] = useState('');

  // 부서 및 직급 목록 (실제로는 API에서 가져와야 함)
  const departments = ['IT부', '인사부', '영업부', '마케팅부', '재무부'];
  const positions = ['사원', '대리', '과장', '차장', '부장'];
  const grades = ['S', 'A+', 'A', 'B', 'C', 'D'];

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

  // 데이터 로드
  useEffect(() => {
    fetchEmployees();
  }, [page, rowsPerPage, searchTerm, filterDepartment, filterPosition, filterGrade, order, orderBy]);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page + 1),
        page_size: String(rowsPerPage),
        sort_by: orderBy,
        sort_order: order,
      });

      if (searchTerm) params.append('search', searchTerm);
      if (filterDepartment) params.append('department', filterDepartment);
      if (filterPosition) params.append('position', filterPosition);
      if (filterGrade) params.append('grade', filterGrade);

      // 백엔드 URL 사용
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8006';
      const response = await fetch(`${API_BASE_URL}/api/v1/employees/ai-analysis/list?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });
      
      console.log('직원 목록 API 응답:', response.status);
      console.log('요청 URL:', `${API_BASE_URL}/api/v1/employees/ai-analysis/list?${params}`);
      console.log('현재 페이지:', page + 1);
      
      if (response.ok) {
        const data = await response.json();
        console.log('받은 직원 데이터:', data);
        console.log('받은 직원 수:', data.items?.length || 0);
        console.log('전체 직원 수:', data.total || 0);
        console.log('첫 3명:', data.items?.slice(0, 3).map((e: any) => `${e.name} (${e.employee_id})`));
        setEmployees(data.items || []);
        setTotalCount(data.total || 0);
      } else {
        console.error('API 오류:', response.status, response.statusText);
        setEmployees([]);
      }
    } catch (error) {
      console.error('Failed to fetch employees:', error);
      setEmployees([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestSort = (property: keyof EmployeeAIAnalysisSummary) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setFilterDepartment('');
    setFilterPosition('');
    setFilterGrade('');
  };

  const createSortHandler = (property: keyof EmployeeAIAnalysisSummary) => (event: React.MouseEvent<unknown>) => {
    handleRequestSort(property);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ width: '100%', mb: 2, p: 2 }}>
        {/* 필터 및 검색 영역 */}
        <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="이름 또는 직원번호 검색"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>부서</InputLabel>
              <Select
                value={filterDepartment}
                onChange={(e) => setFilterDepartment(e.target.value)}
                label="부서"
              >
                <MenuItem value="">전체</MenuItem>
                {departments.map((dept) => (
                  <MenuItem key={dept} value={dept}>
                    {dept}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>직급</InputLabel>
              <Select
                value={filterPosition}
                onChange={(e) => setFilterPosition(e.target.value)}
                label="직급"
              >
                <MenuItem value="">전체</MenuItem>
                {positions.map((pos) => (
                  <MenuItem key={pos} value={pos}>
                    {pos}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>등급</InputLabel>
              <Select
                value={filterGrade}
                onChange={(e) => setFilterGrade(e.target.value)}
                label="등급"
              >
                <MenuItem value="">전체</MenuItem>
                {grades.map((grade) => (
                  <MenuItem key={grade} value={grade}>
                    {grade}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<ClearIcon />}
                onClick={handleClearFilters}
              >
                필터 초기화
              </Button>
              <Button
                variant="contained"
                startIcon={<DownloadIcon />}
                onClick={onExportData}
              >
                엑셀 다운로드
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* 테이블 */}
        <TableContainer>
          <Table sx={{ minWidth: 750 }} aria-labelledby="tableTitle" size="medium">
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  {/* 프로필 이미지 열 */}
                </TableCell>
                {headCells.map((headCell) => (
                  <TableCell
                    key={headCell.id}
                    align={headCell.numeric ? 'right' : 'left'}
                    sortDirection={orderBy === headCell.id ? order : false}
                  >
                    <TableSortLabel
                      active={orderBy === headCell.id}
                      direction={orderBy === headCell.id ? order : 'asc'}
                      onClick={createSortHandler(headCell.id)}
                    >
                      {headCell.label}
                      {orderBy === headCell.id ? (
                        <Box component="span" sx={visuallyHidden}>
                          {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                        </Box>
                      ) : null}
                    </TableSortLabel>
                  </TableCell>
                ))}
                <TableCell align="center">액션</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {employees.map((employee) => (
                <TableRow
                  hover
                  key={employee.employee_id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell padding="checkbox">
                    <Avatar
                      src={employee.profile_image}
                      alt={employee.name}
                      sx={{ width: 40, height: 40 }}
                    >
                      {employee.name[0]}
                    </Avatar>
                  </TableCell>
                  <TableCell component="th" scope="row">
                    <Typography variant="body2" fontWeight="medium">
                      {employee.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {employee.employee_id}
                    </Typography>
                  </TableCell>
                  <TableCell>{employee.department}</TableCell>
                  <TableCell>{employee.position}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      {employee.ai_score}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={employee.grade}
                      size="small"
                      sx={{
                        backgroundColor: getGradeColor(employee.grade),
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                      {employee.strengths_summary}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                      {employee.improvements_summary}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title={employee.ai_comment_preview}>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {employee.ai_comment_preview}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center">
                    <Tooltip title="상세보기">
                      <IconButton
                        size="small"
                        onClick={() => onViewDetail?.(employee.employee_id)}
                      >
                        <ViewIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
              {employees.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={10} align="center">
                    <Typography variant="body2" color="text.secondary" py={3}>
                      데이터가 없습니다.
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="페이지당 행 수:"
        />
      </Paper>
    </Box>
  );
};

export default EmployeeDashboardTable;