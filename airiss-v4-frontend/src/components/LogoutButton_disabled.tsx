import React from 'react';
import { Button } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';

// 인증 비활성화 - 로그아웃 버튼 숨김
const LogoutButton: React.FC = () => {
  // 로그아웃이 필요없으므로 빈 컴포넌트 반환
  return null;
  
  // 또는 비활성화된 버튼을 보여줄 수도 있음
  // return (
  //   <Button
  //     variant="outlined"
  //     startIcon={<LogoutIcon />}
  //     disabled
  //     title="인증이 비활성화되었습니다"
  //   >
  //     로그아웃 (비활성화됨)
  //   </Button>
  // );
};

export default LogoutButton;