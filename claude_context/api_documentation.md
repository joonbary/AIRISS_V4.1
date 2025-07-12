# AIRISS API 문서

## 🌐 기존 API 엔드포인트 (v4.1) - 절대 변경 금지

### 파일 업로드 관련
```
POST /api/upload
- 기능: Excel/CSV 파일 업로드
- 입력: multipart/form-data (file)
- 출력: {"success": true, "file_id": "unique_id", "message": "업로드 성공"}
- 제약: 절대 변경 불가, 기존 프론트엔드와 완벽 호환 필요
```

```
GET /api/files
- 기능: 업로드된 파일 목록 조회
- 출력: [{"id": "file_id", "filename": "example.xlsx", "timestamp": "2024-01-01"}]
- 제약: 스키마 변경 금지
```

### 분석 관련
```
POST /api/analyze
- 기능: 파일 분석 실행 (핵심 엔드포인트)
- 입력: {"file_id": "unique_id", "options": {...}}
- 출력: 분석 결과 JSON (8대 차원 점수)
- 제약: 응답 형식 절대 변경 금지, 기존 차트 연동 유지
```

```
GET /api/results/{file_id}
- 기능: 분석 결과 조회
- 출력: 상세 분석 결과
- 제약: 기존 대시보드 호환성 유지
```

### 실시간 통신
```
WebSocket /ws
- 기능: 분석 진행률 실시간 전송
- 메시지 형식: {"progress": 50, "message": "분석 중..."}
- 제약: 기존 progress bar와 완벽 호환
```

### 시스템 상태
```
GET /health
- 기능: 시스템 상태 확인
- 출력: {"status": "healthy", "version": "v4.1"}
```

---

## 🔮 새로운 API 엔드포인트 (v5.0) - 추가 예정

### v2 API (기존과 분리)
```
POST /api/v2/analyze/advanced
- 기능: AI 고급 분석 (딥러닝 NLP)
- 입력: {"file_id": "id", "use_deep_learning": true}
- 출력: v4 결과 + v5 고급 분석
```

```
GET /api/v2/bias-check/{file_id}
- 기능: 편향 탐지 분석
- 출력: {"fairness_score": 85, "bias_detected": false}
```

```
GET /api/v2/predictions/{file_id}
- 기능: 성과 예측 분석
- 출력: {"performance_forecast": {...}, "turnover_risk": {...}}
```

---

## 📋 API 개발 가이드라인

### 절대 원칙
1. **기존 v1 API는 절대 변경 금지**
2. **새 기능은 v2 네임스페이스 사용**
3. **응답 시간 5초 이내 유지**
4. **에러 처리 표준화**

### 표준 응답 형식
```json
{
  "success": true/false,
  "data": {...},
  "message": "설명",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "v5.0"
}
```

### 에러 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "ANALYSIS_FAILED",
    "message": "분석 중 오류 발생",
    "details": "상세 에러 정보"
  }
}
```
