import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Typography,
  Alert
} from '@mui/material';
import { getPendingUsers, approveUser } from '../services/api';

interface PendingUser {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

const AdminDashboard: React.FC = () => {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const fetchPendingUsers = async () => {
    try {
      setLoading(true);
      console.log('Calling getPendingUsers...');
      const users = await getPendingUsers();
      console.log('Pending users:', users);
      setPendingUsers(users);
    } catch (error: any) {
      console.error('Error fetching pending users:', error);
      console.error('Error response:', error.response);
      setMessage({ type: 'error', text: '사용자 목록을 불러오는데 실패했습니다.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    console.log('Token before API call:', localStorage.getItem('token'));
    fetchPendingUsers();
  }, []);

  const handleApprove = async (userId: number, approve: boolean) => {
    try {
      // 승인 API 호출 전 토큰 확인 (디버깅)
      const token = localStorage.getItem('token');
      console.log('Token before approve:', token);
      if (!token) {
        setMessage({ type: 'error', text: '토큰이 없습니다. 다시 로그인 해주세요.' });
        return;
      }
      await approveUser(userId, approve);
      setMessage({ 
        type: 'success', 
        text: approve ? '사용자가 승인되었습니다.' : '사용자가 거부되었습니다.' 
      });
      fetchPendingUsers();
    } catch (error) {
      setMessage({ type: 'error', text: '처리 중 오류가 발생했습니다.' });
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        관리자 대시보드
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          승인 대기 사용자 목록
        </Typography>
        {message && (
          <Alert severity={message.type} sx={{ mb: 2 }} onClose={() => setMessage(null)}>
            {message.text}
          </Alert>
        )}
        {loading ? (
          <Typography>로딩 중...</Typography>
        ) : pendingUsers.length === 0 ? (
          <Typography>승인 대기 중인 사용자가 없습니다.</Typography>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>이메일</TableCell>
                  <TableCell>이름</TableCell>
                  <TableCell>가입일</TableCell>
                  <TableCell align="center">작업</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pendingUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{new Date(user.created_at).toLocaleDateString('ko-KR')}</TableCell>
                    <TableCell align="center">
                      <Button
                        variant="contained"
                        color="primary"
                        size="small"
                        onClick={() => handleApprove(user.id, true)}
                        sx={{ mr: 1 }}
                      >
                        승인
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        onClick={() => handleApprove(user.id, false)}
                      >
                        거부
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Container>
  );
};

export default AdminDashboard; 