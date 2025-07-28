import React, { useState } from 'react';
import { Box, Paper, Typography, Tabs, Tab, Button, TextField, Card, CardContent, Chip, LinearProgress, Accordion, AccordionSummary, AccordionDetails, Stack, Modal, Table, TableBody, TableRow, TableCell } from '@mui/material';
import axios from 'axios';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DashboardLayout from '../Layout/DashboardLayout';

const AdvancedSearch: React.FC = () => {
  const [tab, setTab] = useState(0);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [detailData, setDetailData] = useState<any>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await axios.post('/search/results', {
        query,
        page: 1,
        page_size: 10,
        include_details: true
      });
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <Box sx={{ p: 3 }}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            🔍 AIRISS 고급 검색
          </Typography>
          <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
            <Tab label="기본 검색" />
            <Tab label="고급 검색" />
            <Tab label="직원 비교" />
          </Tabs>
          {tab === 0 && (
            <Box>
              <TextField
                label="통합 검색"
                fullWidth
                sx={{ mb: 2 }}
                value={query}
                onChange={e => setQuery(e.target.value)}
              />
              <Button variant="contained" onClick={handleSearch} disabled={loading}>
                {loading ? '검색 중...' : '검색'}
              </Button>
              {error && <Typography color="error" sx={{ mt: 2 }}>{error}</Typography>}
              {result && result.results && (
                <Box sx={{ mt: 2 }}>
                  {result.results.length === 0 ? (
                    <Typography>검색 결과가 없습니다.</Typography>
                  ) : (
                    <Stack spacing={2}>
                      {result.results.map((r: any, idx: number) => (
                        <Card key={idx} variant="outlined">
                          <CardContent>
                            <Stack direction="row" alignItems="center" spacing={2}>
                              <Typography variant="h6">{r.uid}</Typography>
                              <Chip label={r.grade || '등급없음'} color="primary" size="small" />
                              <Box sx={{ minWidth: 120 }}>
                                <LinearProgress variant="determinate" value={Number(r.score) || 0} sx={{ height: 10, borderRadius: 5 }} />
                                <Typography variant="caption">점수: {r.score}</Typography>
                              </Box>
                            </Stack>
                            <Typography variant="body2" sx={{ mt: 1 }}>분석일: {r.analysis_date}</Typography>
                            <Typography variant="body2">신뢰도: {r.confidence}</Typography>
                            <Button variant="outlined" sx={{ mt: 2 }} onClick={() => { setDetailData(r); setDetailOpen(true); }}>
                              상세 보기
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </Stack>
                  )}
                  {/* 상세 리포트 Modal */}
                  <Modal open={detailOpen} onClose={() => setDetailOpen(false)}>
                    <Box sx={{ p: 4, bgcolor: 'background.paper', borderRadius: 2, maxWidth: 500, mx: 'auto', my: 8 }}>
                      {detailData && (
                        <>
                          <Typography variant="h6">{detailData.uid} 상세 리포트</Typography>
                          <Chip label={detailData.grade} color="primary" sx={{ ml: 1 }} />
                          <Box sx={{ my: 2 }}>
                            <LinearProgress variant="determinate" value={Number(detailData.score) || 0} sx={{ height: 10, borderRadius: 5 }} />
                            <Typography variant="caption">점수: {detailData.score}</Typography>
                          </Box>
                          <Typography>분석일: {detailData.analysis_date}</Typography>
                          <Typography>신뢰도: {detailData.confidence}</Typography>
                          <Table size="small" sx={{ my: 2 }}>
                            <TableBody>
                              <TableRow>
                                <TableCell>업무성과</TableCell>
                                <TableCell>{detailData.full_data['업무성과_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>KPI달성</TableCell>
                                <TableCell>{detailData.full_data['KPI달성_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>태도마인드</TableCell>
                                <TableCell>{detailData.full_data['태도마인드_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>커뮤니케이션</TableCell>
                                <TableCell>{detailData.full_data['커뮤니케이션_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>리더십협업</TableCell>
                                <TableCell>{detailData.full_data['리더십협업_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>전문성학습</TableCell>
                                <TableCell>{detailData.full_data['전문성학습_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>창의혁신</TableCell>
                                <TableCell>{detailData.full_data['창의혁신_점수']}</TableCell>
                              </TableRow>
                              <TableRow>
                                <TableCell>조직적응</TableCell>
                                <TableCell>{detailData.full_data['조직적응_점수']}</TableCell>
                              </TableRow>
                            </TableBody>
                          </Table>
                          <Typography variant="body2" sx={{ mt: 2 }}>
                            {detailData.full_data['등급설명']}
                          </Typography>
                          <Button onClick={() => setDetailOpen(false)} variant="contained" sx={{ mt: 2 }}>닫기</Button>
                        </>
                      )}
                    </Box>
                  </Modal>
                </Box>
              )}
            </Box>
          )}
          {tab === 1 && (
            <Box>
              <TextField label="직원 ID" fullWidth sx={{ mb: 2 }} />
              <TextField label="부서" fullWidth sx={{ mb: 2 }} />
              <Button variant="contained">고급 검색</Button>
            </Box>
          )}
          {tab === 2 && (
            <Box>
              <TextField label="비교할 직원 ID (쉼표로 구분)" fullWidth sx={{ mb: 2 }} />
              <Button variant="contained">직원 비교</Button>
            </Box>
          )}
        </Paper>
        {/* 검색 결과, 즐겨찾기, 상세 모달 등은 추후 추가 */}
      </Box>
    </DashboardLayout>
  );
};

export default AdvancedSearch; 