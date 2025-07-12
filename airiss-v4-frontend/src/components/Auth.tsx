import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Tabs, Tab, Alert } from '@mui/material';
import { register, login } from '../services/api';
import '../App.css'; // OK폰트 글로벌 적용을 위해 App.css import

const OK_ORANGE = "#ff8200";
const OK_GRAY = "#4d4d4d";

function Auth() {
  const [tab, setTab] = useState(0);
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTabChange = (_: any, newValue: number) => {
    setTab(newValue);
    setError('');
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력하세요.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await login({ email, password });
      if (res.access_token) {
        localStorage.setItem('token', res.access_token);
        window.location.href = '/dashboard';
      } else {
        setError('로그인 실패: 토큰이 없습니다.');
      }
    } catch (err: any) {
      setError(err.message || '로그인 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !name || !password) {
      setError('모든 항목을 입력하세요.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await register({ email, name, password });
      setError('회원가입이 완료되었습니다! 이제 로그인해 주세요.');
      setTab(0);
    } catch (err: any) {
      setError(err.message || '회원가입 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: `linear-gradient(135deg, ${OK_ORANGE} 0%, #fff7e6 100%)`, fontFamily: 'OKLight, OKMedium, OKBold, sans-serif' }}>
      <Card sx={{ minWidth: { xs: 0, sm: 320, md: 350 }, width: { xs: '90vw', sm: 400, md: 420 }, boxShadow: 6, borderRadius: 3, p: 2, background: '#fff', fontFamily: 'OKLight, OKMedium, OKBold, sans-serif' }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <img src="/ok_logo.svg" alt="OK금융그룹 로고" style={{ height: 48 }} />
          </Box>
          <Tabs value={tab} onChange={handleTabChange} centered sx={{ mb: 2, fontFamily: 'OKBold, OKMedium, OKLight, sans-serif' }}>
            <Tab label="로그인" sx={{ color: tab === 0 ? OK_ORANGE : OK_GRAY, fontWeight: 700, fontFamily: 'OKBold, OKMedium, OKLight, sans-serif' }} />
            <Tab label="회원가입" sx={{ color: tab === 1 ? OK_ORANGE : OK_GRAY, fontWeight: 700, fontFamily: 'OKBold, OKMedium, OKLight, sans-serif' }} />
          </Tabs>
          {error && <Alert severity={error.includes('완료') ? 'success' : 'error'} sx={{ mb: 2 }}>{error}</Alert>}
          {tab === 0 ? (
            <form onSubmit={handleLogin}>
              <TextField label="이메일" fullWidth margin="normal" variant="outlined" value={email} onChange={e => setEmail(e.target.value)} disabled={loading} />
              <TextField label="비밀번호" type="password" fullWidth margin="normal" variant="outlined" value={password} onChange={e => setPassword(e.target.value)} disabled={loading} />
              <Button type="submit" variant="contained" fullWidth sx={{ mt: 2, background: OK_ORANGE, color: '#fff', fontWeight: 700, '&:hover': { background: '#e67300' } }} disabled={loading}>
                {loading ? '로그인 중...' : '로그인'}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <TextField label="이메일" fullWidth margin="normal" variant="outlined" value={email} onChange={e => setEmail(e.target.value)} disabled={loading} />
              <TextField label="이름" fullWidth margin="normal" variant="outlined" value={name} onChange={e => setName(e.target.value)} disabled={loading} />
              <TextField label="비밀번호" type="password" fullWidth margin="normal" variant="outlined" value={password} onChange={e => setPassword(e.target.value)} disabled={loading} />
              <Button type="submit" variant="contained" fullWidth sx={{ mt: 2, background: OK_ORANGE, color: '#fff', fontWeight: 700, '&:hover': { background: '#e67300' } }} disabled={loading}>
                {loading ? '회원가입 중...' : '회원가입'}
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default Auth;