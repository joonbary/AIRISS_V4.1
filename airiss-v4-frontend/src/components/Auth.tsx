import React, { useState, useEffect } from 'react';
import { register, login, getMe, getPendingUsers, approveUser } from '../services/api';

const Auth: React.FC = () => {
  const [mode, setMode] = useState<'login' | 'register' | 'admin'>('login');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<any>(null);
  const [pendingUsers, setPendingUsers] = useState<any[]>([]);
  const [message, setMessage] = useState('');

  // 내 정보 불러오기
  useEffect(() => {
    if (token) {
      getMe(token)
        .then((u) => {
          setUser(u);
          if (u.is_admin) setMode('admin');
        })
        .catch((e) => {
          setUser(null);
          setMessage(e.message || '인증 정보가 만료되었습니다.');
          setToken(null);
          localStorage.removeItem('token');
        });
    }
  }, [token]);

  // 관리자 승인 대기 목록 불러오기
  useEffect(() => {
    if (user && user.is_admin && token) {
      getPendingUsers(token)
        .then(setPendingUsers)
        .catch(() => setPendingUsers([]));
    }
  }, [user, token]);

  // 회원가입
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register({ email, name, password });
      setMessage('회원가입 완료! 관리자 승인 후 로그인 가능합니다.');
      setMode('login');
    } catch (e: any) {
      setMessage(e.message || '회원가입 실패');
    }
  };

  // 로그인
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await login({ email, password });
      setToken(res.access_token);
      localStorage.setItem('token', res.access_token);
      setMessage('로그인 성공!');
    } catch (e: any) {
      setMessage(e.message || '로그인 실패');
    }
  };

  // 로그아웃
  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    setMessage('로그아웃 되었습니다.');
    setMode('login');
  };

  // 관리자 승인/거부
  const handleApprove = async (user_id: number, approve: boolean) => {
    if (!token) return;
    try {
      await approveUser(user_id, approve, token);
      setPendingUsers((prev) => prev.filter((u) => u.id !== user_id));
      setMessage(approve ? '승인 완료!' : '거부 처리됨');
    } catch (e: any) {
      setMessage(e.message || '처리 실패');
    }
  };

  // 승인 대기 안내
  if (user && !user.is_approved) {
    return (
      <div style={{ maxWidth: 400, margin: '40px auto', textAlign: 'center' }}>
        <h2>승인 대기 중</h2>
        <p>관리자 승인 후 로그인 가능합니다.</p>
        <button onClick={handleLogout}>로그아웃</button>
      </div>
    );
  }

  // 관리자 승인 페이지
  if (user && user.is_admin) {
    return (
      <div style={{ maxWidth: 600, margin: '40px auto' }}>
        <h2>관리자 승인 대기 목록</h2>
        {pendingUsers.length === 0 ? (
          <p>승인 대기 중인 사용자가 없습니다.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th>이메일</th>
                <th>이름</th>
                <th>가입일</th>
                <th>승인</th>
                <th>거부</th>
              </tr>
            </thead>
            <tbody>
              {pendingUsers.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>{u.name}</td>
                  <td>{new Date(u.created_at).toLocaleString()}</td>
                  <td>
                    <button onClick={() => handleApprove(u.id, true)}>승인</button>
                  </td>
                  <td>
                    <button onClick={() => handleApprove(u.id, false)}>거부</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        <button onClick={handleLogout} style={{ marginTop: 20 }}>로그아웃</button>
        {message && <div style={{ color: 'green', marginTop: 10 }}>{message}</div>}
      </div>
    );
  }

  // 로그인/회원가입 폼
  return (
    <div style={{ maxWidth: 400, margin: '40px auto' }}>
      <h2>{mode === 'login' ? '로그인' : '회원가입'}</h2>
      <form onSubmit={mode === 'login' ? handleLogin : handleRegister}>
        <input
          type="email"
          placeholder="이메일"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: '100%', marginBottom: 10 }}
        />
        {mode === 'register' && (
          <input
            type="text"
            placeholder="이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            style={{ width: '100%', marginBottom: 10 }}
          />
        )}
        <input
          type="password"
          placeholder="비밀번호"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', marginBottom: 10 }}
        />
        <button type="submit" style={{ width: '100%', marginBottom: 10 }}>
          {mode === 'login' ? '로그인' : '회원가입'}
        </button>
      </form>
      <button onClick={() => setMode(mode === 'login' ? 'register' : 'login')} style={{ width: '100%' }}>
        {mode === 'login' ? '회원가입' : '로그인'}으로 이동
      </button>
      {message && <div style={{ color: 'red', marginTop: 10 }}>{message}</div>}
    </div>
  );
};

export default Auth; 