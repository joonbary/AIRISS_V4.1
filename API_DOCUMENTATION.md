# AIRISS v4 API Documentation

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://api.airiss.example.com/api/v1
```

## Authentication
모든 API 요청은 JWT 토큰을 사용한 인증이 필요합니다.

### 헤더 설정
```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Authentication

#### 회원가입
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "full_name": "string",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-07-21T10:00:00"
}
```

#### 로그인
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=string&password=string
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "string",
    "email": "user@example.com"
  }
}
```

### 2. File Management

#### 파일 업로드
```http
POST /files/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "data.xlsx",
  "total_records": 100,
  "columns": ["employee_id", "name", "opinion", "score"],
  "uid_columns": ["employee_id"],
  "opinion_columns": ["opinion"],
  "quantitative_columns": ["score"],
  "message": "File uploaded successfully"
}
```

#### 파일 목록 조회
```http
GET /files/list
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "data.xlsx",
    "upload_time": "2024-07-21T10:00:00",
    "total_records": 100,
    "size": 1048576
  }
]
```

#### 파일 삭제
```http
DELETE /files/{file_id}
Authorization: Bearer <token>
```

### 3. Analysis

#### 분석 작업 생성
```http
POST /analysis/create
Authorization: Bearer <token>
Content-Type: application/json

{
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "sample_size": 100,
  "analysis_mode": "hybrid",
  "enable_ai_feedback": true,
  "openai_model": "gpt-3.5-turbo",
  "max_tokens": 1200
}
```

**Parameters:**
- `analysis_mode`: "hybrid" | "text_only" | "quantitative_only"
- `sample_size`: 1-10000 (optional)
- `enable_ai_feedback`: boolean (optional)

**Response:**
```json
{
  "job_id": "456e7890-e89b-12d3-a456-426614174000",
  "status": "created",
  "progress": 0.0,
  "message": "Analysis job created and started"
}
```

#### 작업 상태 조회
```http
GET /analysis/status/{job_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "job_id": "456e7890-e89b-12d3-a456-426614174000",
  "status": "processing",
  "progress": 45.5,
  "processed_records": 45,
  "total_records": 100,
  "message": "Processing..."
}
```

**Status Values:**
- `created`: 작업 생성됨
- `processing`: 처리 중
- `completed`: 완료
- `failed`: 실패

#### 분석 결과 조회
```http
GET /analysis/results/{job_id}
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "analysis_id": "789a0123-e89b-12d3-a456-426614174000",
    "uid": "EMP001",
    "opinion": "Excellent performance...",
    "overall_score": 85.5,
    "text_score": 88.0,
    "quantitative_score": 82.0,
    "ok_grade": "A",
    "grade_description": "우수",
    "confidence": 0.92,
    "percentile": 85.0,
    "dimension_scores": {
      "leadership": 85,
      "communication": 90,
      "problem_solving": 88,
      "teamwork": 82,
      "innovation": 80,
      "execution": 85
    },
    "ai_feedback": {
      "strengths": ["Strong leadership", "Excellent communication"],
      "weaknesses": ["Time management"],
      "recommendations": ["Focus on delegation", "Use time tracking tools"]
    },
    "created_at": "2024-07-21T10:30:00"
  }
]
```

#### 결과 다운로드
```http
GET /analysis/download/{job_id}?format=excel
Authorization: Bearer <token>
```

**Parameters:**
- `format`: "excel" | "csv" | "json"

**Response:** Binary file download

### 4. Users

#### 현재 사용자 정보
```http
GET /users/me
Authorization: Bearer <token>
```

#### 사용자 정보 수정
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "New Name"
}
```

#### 사용자 목록 (관리자 전용)
```http
GET /users?skip=0&limit=100
Authorization: Bearer <admin_token>
```

### 5. WebSocket

#### 실시간 분석 진행 상황
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/connect?client_id=123&user_id=1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_progress') {
    console.log(`Progress: ${data.progress}%`);
  }
};
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## Rate Limiting
운영 환경에서는 분당 60개 요청으로 제한됩니다.

## Pagination
목록 조회 API는 다음 파라미터를 지원합니다:
- `skip`: 건너뛸 항목 수 (기본값: 0)
- `limit`: 반환할 최대 항목 수 (기본값: 100)

## SDK Examples

### Python
```python
import requests

# 로그인
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# 파일 업로드
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("data.xlsx", "rb")}
response = requests.post(
    "http://localhost:8000/api/v1/files/upload",
    headers=headers,
    files=files
)
```

### JavaScript
```javascript
// 로그인
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/x-www-form-urlencoded'},
  body: 'username=user&password=pass'
});
const { access_token } = await loginResponse.json();

// 파일 업로드
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('/api/v1/files/upload', {
  method: 'POST',
  headers: {'Authorization': `Bearer ${access_token}`},
  body: formData
});
```