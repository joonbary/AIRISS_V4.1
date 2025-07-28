# AIRISS v4.0 빠른 시작 가이드

## 🚀 3분 안에 시작하기

### 1️⃣ 환경 설정 (최초 1회만)
```batch
setup_test_env.bat
```
- OpenAI API 키 입력
- 필요한 디렉토리 자동 생성

### 2️⃣ 테스트 계정 생성
```batch
python create_test_admin.py
```
생성되는 계정:
- 관리자: `admin@okfn.com` / `admin123`
- 사용자: `test@okfn.com` / `password123`

### 3️⃣ 서버 시작
```batch
start_all_v4.bat
```
자동으로 두 개의 창이 열립니다:
- 백엔드 서버 (포트 8006)
- 프론트엔드 서버 (포트 3000)

### 4️⃣ 브라우저 접속
- 자동으로 브라우저가 열립니다
- 또는 직접 접속: http://localhost:3000

## 📝 테스트 순서

### 1. 로그인
- Email: `test@okfn.com`
- Password: `password123`

### 2. 파일 업로드
1. 좌측 메뉴에서 "파일 업로드" 클릭
2. Excel 또는 CSV 파일 드래그앤드롭
3. 업로드 완료 확인

### 3. 분석 실행
1. "지금 분석하기" 버튼 클릭
2. 실시간 진행률 확인:
   - WebSocket 연결 상태
   - 진행률 바
   - 처리 속도
   - 예상 완료 시간

### 4. 결과 확인
1. 분석 완료 후 자동으로 결과 페이지 이동
2. 등급 분포 및 통계 확인
3. 개별 직원 상세 정보 조회

### 5. 결과 다운로드
1. "다운로드" 버튼 클릭
2. Excel 형식 선택
3. 파일 저장

## 🛠️ 문제 해결

### 서버가 시작되지 않을 때
```batch
# 백엔드 문제
python --version  # 3.8 이상 확인
pip install -r requirements.txt

# 프론트엔드 문제
node --version   # 14 이상 확인
cd airiss-v4-frontend
npm install
```

### 포트 충돌
```batch
# 8006 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8006

# 3000 포트 사용 중인 프로세스 확인
netstat -ano | findstr :3000
```

### API 키 오류
```batch
# 환경 변수 확인
echo %OPENAI_API_KEY%

# 다시 설정
set OPENAI_API_KEY=your-api-key-here
```

## 📋 체크포인트

✅ 백엔드 서버 실행 중 (http://localhost:8006)  
✅ 프론트엔드 서버 실행 중 (http://localhost:3000)  
✅ 로그인 성공  
✅ 파일 업로드 완료  
✅ WebSocket 연결 확인  
✅ 실시간 진행률 표시  
✅ 결과 다운로드 성공  

## 💡 추가 테스트

### API 문서 확인
http://localhost:8006/docs

### 연결 테스트
```batch
python test_connection.py
```

### 테스트 데이터 생성
```python
# create_test_data.py 작성 후
python create_test_data.py
```

---

**도움이 필요하신가요?**  
각 서버 콘솔의 로그를 확인하거나, `TEST_GUIDE.md`의 상세 가이드를 참조하세요.