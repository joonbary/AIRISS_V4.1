# AIRISS v4.0 - No Authentication Version

## 개요
이 버전은 인증(로그인/회원가입) 기능이 완전히 제거된 버전입니다.
모든 API와 기능이 인증 없이 접근 가능합니다.

## 변경사항

### 백엔드
- ✅ `/api/v1/auth/*` 라우터 제거
- ✅ JWT 토큰 검증 미들웨어 제거
- ✅ `get_current_user`, `get_admin_user` 등 인증 데코레이터 제거
- ✅ 모든 엔드포인트가 Public Access로 전환
- ✅ 401 Unauthorized, 403 Forbidden 에러 없음

### 프론트엔드
- ✅ 로그인/회원가입 화면 제거
- ✅ 토큰 저장/관리 로직 제거
- ✅ Authorization 헤더 제거
- ✅ 인증 관련 라우트 가드 제거
- ✅ 모든 페이지 직접 접근 가능

## 실행 방법

### 백엔드 시작
```bash
# 인증 없는 서버 시작
python -m app.main_no_auth

# 또는 배치 파일 사용
start_server_no_auth.bat
```

### 프론트엔드 시작
```bash
cd airiss-v4-frontend
npm start
```

## 접근 가능한 기능

1. **파일 업로드**: `/api/v1/analysis/upload`
2. **분석 시작**: `/api/v1/analysis/analyze/{file_id}`
3. **상태 확인**: `/api/v1/analysis/status/{job_id}`
4. **결과 다운로드**: `/api/v1/analysis/download/{job_id}/{format}`
5. **파일 목록**: `/api/v1/files/list`
6. **직원 검색**: `/api/v1/employee/{job_id}`
7. **대시보드**: `/api/v1/dashboard/stats`

## 테스트

E2E 테스트 실행:
```bash
python test_no_auth_e2e.py
```

## 주의사항

⚠️ **보안 경고**: 이 버전은 인증이 없으므로 프로덕션 환경에서는 사용하지 마세요.
- 모든 사용자가 모든 데이터에 접근 가능
- 파일 업로드/삭제 제한 없음
- 관리자 기능도 모두 공개

## 원래 버전으로 복구

인증이 필요한 원래 버전으로 돌아가려면:
```bash
# 원래 main.py 사용
python -m app.main
```