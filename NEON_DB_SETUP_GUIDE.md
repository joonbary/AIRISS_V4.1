# Neon DB 설정 가이드

## 1. Neon DB 연결 정보 확인

1. [Neon Console](https://console.neon.tech)에 로그인
2. 프로젝트 선택
3. "Connection Details" 확인
4. 패스워드 확인 (Show password 클릭)

## 2. .env 파일 설정

```bash
# .env 파일 편집
DATABASE_URL=postgresql://neondb_owner:YOUR_PASSWORD@ep-summer-surf-a153am7x-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

### 주의사항:
- 패스워드에 특수문자가 있는 경우 URL 인코딩 필요
  - `@` → `%40`
  - `#` → `%23`
  - `&` → `%26`
  - `!` → `%21`

## 3. 연결 테스트

```bash
# Neon DB 연결 테스트
python migrate_to_neon.py test
```

## 4. 데이터베이스 전환

### 옵션 1: 새로운 Neon DB 사용
```bash
# .env 파일에서 DATABASE_URL을 Neon DB로 변경
# SQLite 라인을 주석 처리하고 Neon DB 라인 활성화
```

### 옵션 2: 기존 데이터 마이그레이션
```bash
# SQLite 데이터를 Neon DB로 마이그레이션
python migrate_to_neon.py
```

## 5. 서버 재시작

```bash
python -m app.main
```

## 문제 해결

### "password authentication failed" 오류
- Neon Console에서 패스워드 재확인
- URL 인코딩이 올바른지 확인
- 패스워드 리셋 고려

### "could not translate host name" 오류
- 호스트 이름이 올바른지 확인
- 네트워크 연결 확인

### 테이블이 생성되지 않는 경우
- 서버 시작 시 로그 확인
- `Database tables created successfully` 메시지 확인