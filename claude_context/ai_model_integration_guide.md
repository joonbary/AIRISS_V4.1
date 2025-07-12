# AIRISS AI 모델 통합 가이드

## 🧠 AI 모델 아키텍처 개요

### v4.1 현재 모델 (보존 필수)
```
텍스트 분석 → 키워드 매칭 + 가중치 계산
정량 분석 → 수치 데이터 직접 처리  
하이브리드 → 60% 텍스트 + 40% 정량
```
**제약**: 기존 분석 로직 100% 보존, 결과 호환성 유지

### v5.0 확장 모델 (추가 예정)
```
딥러닝 NLP → BERT/KoELECTRA 기반 의미 분석
편향 탐지 → 통계적 공정성 검증 모델
예측 분석 → XGBoost/LightGBM 기반 시계열 예측
```
**원칙**: 기존 모델과 병행 운영, 선택적 활성화

---

## 🔧 모델 통합 전략

### 1. 하이브리드 아키텍처
```python
class AIRISSModelManager:
    def __init__(self):
        # v4 모델 (항상 활성화)
        self.v4_text_analyzer = TextAnalyzer()
        self.v4_quant_analyzer = QuantitativeAnalyzer()
        
        # v5 모델 (선택적 활성화)
        self.v5_nlp_model = None
        self.v5_bias_detector = None
        self.v5_predictor = None
        
    def analyze(self, text, data, use_v5=False):
        # 기본 v4 분석 (필수)
        v4_result = self.v4_analyze(text, data)
        
        if use_v5 and self.v5_enabled:
            # v5 고급 분석 (추가)
            v5_result = self.v5_analyze(text, data)
            return self.merge_results(v4_result, v5_result)
        
        return v4_result
```

### 2. 점진적 도입 전략
```
Phase 1: v5 모델 개발 및 테스트 (내부)
Phase 2: A/B 테스트 (10% 트래픽)
Phase 3: 점진적 확대 (25% → 50% → 100%)
Phase 4: v4 모델 지원 유지 (안정성 보장)
```

---

## 🤖 딥러닝 NLP 모델

### 모델 선택 기준
```
1차 우선순위: 한국어 지원 품질
2차 우선순위: 추론 속도 (< 2초)
3차 우선순위: 메모리 효율성 (< 2GB)
4차 우선순위: 라이선스 호환성
```

### 추천 모델 후보
```python
# Option 1: 한국어 특화 모델 (추천)
model_name = "beomi/KcELECTRA-base"
pros = ["한국어 최적화", "빠른 추론", "상용 가능"]
cons = ["영어 성능 제한"]

# Option 2: 다국어 모델
model_name = "microsoft/mdeberta-v3-base" 
pros = ["다국어 지원", "높은 정확도"]
cons = ["더 큰 모델 크기", "느린 추론"]

# Option 3: 경량화 모델
model_name = "distilbert-base-multilingual-cased"
pros = ["빠른 속도", "적은 메모리"]
cons = ["정확도 트레이드오프"]
```

### 모델 통합 코드 구조
```python
# app/services/nlp_models.py
from transformers import AutoTokenizer, AutoModel
import torch

class AdvancedNLPAnalyzer:
    def __init__(self, model_name="beomi/KcELECTRA-base"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
    def analyze_sentiment(self, text):
        """감정 분석 (긍정/부정/중립)"""
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 감정 분류 로직
        return {"positive": 0.7, "negative": 0.2, "neutral": 0.1}
    
    def extract_keywords(self, text):
        """핵심 키워드 추출"""
        # 어텐션 가중치 기반 키워드 추출
        return ["성과", "협업", "리더십"]
    
    def calculate_dimension_score(self, text, dimension):
        """차원별 점수 계산 (v4 호환)"""
        sentiment = self.analyze_sentiment(text)
        keywords = self.extract_keywords(text)
        
        # v4 결과와 호환되는 형태로 반환
        return {
            "score": 85.2,
            "confidence": 0.91,
            "evidence": keywords,
            "sentiment": sentiment
        }
```

### 모델 성능 최적화
```python
# 1. 모델 양자화 (크기 축소)
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

# 2. 배치 처리 최적화
def batch_analyze(texts, batch_size=16):
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = model.analyze_batch(batch)
        results.extend(batch_results)
    return results

# 3. 캐싱 전략
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_analyze(text_hash):
    return model.analyze(text)
```

---

## ⚖️ 편향 탐지 모델

### 편향 탐지 알고리즘
```python
# app/services/bias_detection.py
import pandas as pd
from scipy import stats

class BiasDetector:
    def __init__(self):
        self.protected_attributes = ['성별', '연령대', '부서', '직급']
        self.fairness_thresholds = {
            'demographic_parity': 0.8,  # 4/5 규칙
            'equal_opportunity': 0.8,
            'disparate_impact': 0.8
        }
    
    def detect_bias(self, df):
        """종합 편향 분석"""
        bias_report = {
            'overall_fairness_score': 0,
            'detected_biases': [],
            'recommendations': []
        }
        
        for attr in self.protected_attributes:
            if attr in df.columns:
                bias_metrics = self.analyze_attribute_bias(df, attr)
                bias_report['detected_biases'].append(bias_metrics)
        
        bias_report['overall_fairness_score'] = self.calculate_fairness_score(
            bias_report['detected_biases']
        )
        
        return bias_report
    
    def analyze_attribute_bias(self, df, attribute):
        """속성별 편향 분석"""
        groups = df.groupby(attribute)['score'].agg(['mean', 'count'])
        
        # 인구통계학적 동등성 검사
        max_mean = groups['mean'].max()
        min_mean = groups['mean'].min()
        demographic_parity = min_mean / max_mean
        
        # 통계적 유의성 검사
        group_scores = [group['score'].values for name, group in df.groupby(attribute)]
        _, p_value = stats.f_oneway(*group_scores)
        
        return {
            'attribute': attribute,
            'demographic_parity': demographic_parity,
            'is_biased': demographic_parity < self.fairness_thresholds['demographic_parity'],
            'p_value': p_value,
            'group_means': groups['mean'].to_dict()
        }
```

### 실시간 편향 모니터링
```python
class RealTimeBiasMonitor:
    def __init__(self):
        self.bias_detector = BiasDetector()
        self.alert_threshold = 0.7
        
    def monitor_analysis_batch(self, results_df):
        """분석 배치에 대한 실시간 편향 체크"""
        bias_report = self.bias_detector.detect_bias(results_df)
        
        if bias_report['overall_fairness_score'] < self.alert_threshold:
            self.send_bias_alert(bias_report)
        
        return bias_report
    
    def send_bias_alert(self, report):
        """편향 감지 시 알림 전송"""
        # 관리자에게 즉시 알림
        # 이메일, 슬랙, 대시보드 경고 등
        pass
```

---

## 📈 예측 분석 모델

### 예측 모델 구조
```python
# app/services/predictive_models.py
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
import joblib

class PerformancePredictor:
    def __init__(self):
        self.performance_model = None
        self.turnover_model = None
        self.growth_model = None
        self.scaler = None
        
    def train_models(self, historical_data):
        """과거 데이터로 예측 모델 학습"""
        # 특성 엔지니어링
        features = self.engineer_features(historical_data)
        
        # 성과 예측 모델 (회귀)
        self.performance_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1
        )
        
        # 이직 예측 모델 (분류)
        self.turnover_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=5
        )
        
        # 성장 잠재력 모델 (회귀)
        self.growth_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8
        )
    
    def predict_performance(self, employee_data):
        """6개월 후 성과 예측"""
        features = self.prepare_features(employee_data)
        prediction = self.performance_model.predict(features)[0]
        confidence = self.calculate_confidence(features)
        
        return {
            "predicted_score_6m": prediction,
            "confidence": confidence,
            "trend": "improving" if prediction > employee_data['current_score'] else "declining"
        }
    
    def predict_turnover_risk(self, employee_data):
        """이직 위험도 예측"""
        features = self.prepare_features(employee_data)
        risk_probability = self.turnover_model.predict_proba(features)[0][1]
        
        risk_level = "HIGH" if risk_probability > 0.7 else \
                    "MEDIUM" if risk_probability > 0.4 else "LOW"
        
        return {
            "risk_probability": risk_probability,
            "risk_level": risk_level,
            "key_risk_factors": self.identify_risk_factors(features)
        }
```

### 모델 학습 데이터 생성
```python
# scripts/generate_training_data.py
def create_synthetic_training_data(n_employees=1000, n_months=24):
    """학습용 가상 데이터 생성"""
    data = []
    
    for emp_id in range(n_employees):
        for month in range(n_months):
            # 현실적인 패턴을 반영한 가상 데이터 생성
            base_score = np.random.normal(75, 15)
            trend = np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2])
            
            record = {
                'employee_id': f'EMP{emp_id:04d}',
                'month': month,
                'performance_score': max(0, min(100, base_score + trend * month * 0.5)),
                'tenure_months': month + np.random.randint(6, 60),
                'department': np.random.choice(['IT', '영업', '기획', '인사']),
                'age_group': np.random.choice(['20대', '30대', '40대', '50대']),
                # ... 기타 특성들
            }
            data.append(record)
    
    return pd.DataFrame(data)
```

---

## 🔄 모델 버전 관리

### MLOps 파이프라인
```python
class ModelManager:
    def __init__(self):
        self.model_registry = {}
        self.active_models = {}
        
    def register_model(self, model_name, model, version, metrics):
        """모델 등록 및 버전 관리"""
        self.model_registry[f"{model_name}_v{version}"] = {
            'model': model,
            'version': version,
            'metrics': metrics,
            'timestamp': datetime.now(),
            'status': 'registered'
        }
    
    def deploy_model(self, model_name, version):
        """모델 배포"""
        model_key = f"{model_name}_v{version}"
        if model_key in self.model_registry:
            self.active_models[model_name] = self.model_registry[model_key]
            return True
        return False
    
    def rollback_model(self, model_name, previous_version):
        """모델 롤백"""
        return self.deploy_model(model_name, previous_version)
```

### A/B 테스트 프레임워크
```python
class ModelABTester:
    def __init__(self):
        self.experiments = {}
        
    def start_experiment(self, model_a, model_b, traffic_split=0.5):
        """A/B 테스트 시작"""
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.experiments[experiment_id] = {
            'model_a': model_a,
            'model_b': model_b,
            'traffic_split': traffic_split,
            'metrics': {'a': [], 'b': []},
            'start_time': datetime.now()
        }
        
        return experiment_id
    
    def route_request(self, experiment_id):
        """요청을 A/B 모델로 라우팅"""
        exp = self.experiments[experiment_id]
        return 'a' if random.random() < exp['traffic_split'] else 'b'
    
    def collect_metrics(self, experiment_id, variant, metrics):
        """메트릭 수집"""
        self.experiments[experiment_id]['metrics'][variant].append(metrics)
```

---

## 📊 모델 성능 모니터링

### 핵심 메트릭
```python
class ModelMonitor:
    def __init__(self):
        self.metrics_history = []
        
    def track_model_performance(self, model_name, predictions, actuals):
        """모델 성능 추적"""
        from sklearn.metrics import mean_absolute_error, r2_score
        
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        
        metrics = {
            'model': model_name,
            'timestamp': datetime.now(),
            'mae': mae,
            'r2_score': r2,
            'sample_size': len(predictions)
        }
        
        self.metrics_history.append(metrics)
        
        # 성능 저하 감지
        if mae > self.acceptable_mae_threshold:
            self.trigger_model_retraining(model_name)
        
        return metrics
    
    def generate_performance_report(self):
        """성능 보고서 생성"""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        recent_metrics = self.metrics_history[-10:]  # 최근 10개
        
        return {
            "average_mae": np.mean([m['mae'] for m in recent_metrics]),
            "average_r2": np.mean([m['r2_score'] for m in recent_metrics]),
            "trend": "improving" if recent_metrics[-1]['mae'] < recent_metrics[0]['mae'] else "declining",
            "last_updated": recent_metrics[-1]['timestamp'].isoformat()
        }
```

---

## 🔧 모델 통합 체크리스트

### 개발 단계
- [ ] 모델 아키텍처 설계 완료
- [ ] 훈련 데이터 준비 완료
- [ ] 베이스라인 성능 달성
- [ ] 단위 테스트 작성 완료

### 통합 단계  
- [ ] v4 호환성 100% 확인
- [ ] API 응답 형식 일치
- [ ] 성능 벤치마크 통과
- [ ] 메모리 사용량 최적화

### 배포 단계
- [ ] A/B 테스트 설정
- [ ] 모니터링 대시보드 준비
- [ ] 롤백 프로세스 검증
- [ ] 문서화 완료

이제 AI 모델 통합을 위한 완전한 가이드가 준비되었습니다! 🧠✨
