import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Alert,
  Grid
} from '@mui/material';
import { getCurrentUser, changePassword } from '../services/api';

interface UserProfile {
  id: number;
  email: string;
  name: string;
  is_admin: boolean;
  is_approved: boolean;
  created_at: string;
}

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const data = await getCurrentUser();
      setProfile(data);
    } catch (error) {
      setMessage({ type: 'error', text: '프로필을 불러오는데 실패했습니다.' });
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: '새 비밀번호가 일치하지 않습니다.' });
      return;
    }
    if (newPassword.length < 6) {
      setMessage({ type: 'error', text: '비밀번호는 6자 이상이어야 합니다.' });
      return;
    }
    setLoading(true);
    try {
      await changePassword(currentPassword, newPassword);
      setMessage({ type: 'success', text: '비밀번호가 성공적으로 변경되었습니다.' });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || '비밀번호 변경에 실패했습니다.'
      });
    } finally {
      setLoading(false);
    }
  };

  if (!profile) {
    return <Typography>로딩 중...</Typography>;
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        내 프로필
      </Typography>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          기본 정보
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">이메일</Typography>
            <Typography variant="body1">{profile.email}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">이름</Typography>
            <Typography variant="body1">{profile.name}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">계정 유형</Typography>
            <Typography variant="body1">
              {profile.is_admin ? '관리자' : '일반 사용자'}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="body2" color="text.secondary">가입일</Typography>
            <Typography variant="body1">
              {new Date(profile.created_at).toLocaleDateString('ko-KR')}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          비밀번호 변경
        </Typography>
        {message && (
          <Alert
            severity={message.type}
            sx={{ mb: 2 }}
            onClose={() => setMessage(null)}
          >
            {message.text}
          </Alert>
        )}
        <Box component="form" onSubmit={handlePasswordChange}>
          <TextField
            fullWidth
            type="password"
            label="현재 비밀번호"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            margin="normal"
            required
          />
          <TextField
            fullWidth
            type="password"
            label="새 비밀번호"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            margin="normal"
            required
            helperText="6자 이상 입력해주세요"
          />
          <TextField
            fullWidth
            type="password"
            label="새 비밀번호 확인"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            margin="normal"
            required
          />
          <Button
            type="submit"
            variant="contained"
            sx={{ mt: 2 }}
            disabled={loading}
          >
            {loading ? '변경 중...' : '비밀번호 변경'}
          </Button>
        </Box>
      </Paper>
    </Container>
  );
};

export default Profile; 