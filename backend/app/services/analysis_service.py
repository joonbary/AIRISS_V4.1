"""
Analysis Service
분석 작업 관리 및 처리를 담당하는 서비스
"""

from typing import Dict, Any, List, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from datetime import datetime
import uuid

from .base import BaseService
from app.db.repositories import AnalysisRepository, FileRepository
from app.services.ai_service import AIService
from app.core.config import settings
from app.api.v1.websocket import manager as ws_manager


class AnalysisService(BaseService):
    """분석 서비스"""
    
    def __init__(self, db):
        super().__init__(db)
        self.analysis_repo = AnalysisRepository(db)
        self.file_repo = FileRepository(db)
        self.ai_service = AIService()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def create_analysis_job(
        self,
        file_id: str,
        analysis_config: Dict[str, Any],
        user_id: int
    ) -> str:
        """분석 작업 생성 및 시작"""
        # 파일 정보 조회
        file_info = self.file_repo.get_file(file_id)
        if not file_info:
            raise ValueError(f"File not found: {file_id}")
        
        # 작업 생성
        job_data = {
            "file_id": file_id,
            "user_id": user_id,
            "total_records": file_info.get("total_records", 0),
            **analysis_config
        }
        
        job_id = self.analysis_repo.create_job(job_data)
        
        # 비동기로 분석 시작
        asyncio.create_task(self._run_analysis(job_id, file_info, analysis_config))
        
        return job_id
    
    async def _run_analysis(
        self,
        job_id: str,
        file_info: Dict[str, Any],
        config: Dict[str, Any]
    ):
        """실제 분석 작업 실행"""
        try:
            # 상태 업데이트: processing
            self.analysis_repo.update_job(job_id, {"status": "processing"})
            await self._notify_progress(job_id, 0, "Analysis started")
            
            # DataFrame 로드
            df = file_info.get('dataframe')
            if df is None:
                raise ValueError("Failed to load DataFrame")
            
            # 샘플링
            sample_size = config.get('sample_size')
            if sample_size and sample_size < len(df):
                df_sample = df.sample(n=sample_size, random_state=42)
            else:
                df_sample = df
            
            # 분석 실행
            results = []
            total = len(df_sample)
            
            for idx, row in df_sample.iterrows():
                try:
                    # 진행률 업데이트
                    progress = (idx / total) * 100
                    if idx % 10 == 0:
                        self.analysis_repo.update_job(job_id, {
                            "progress": progress,
                            "processed_records": idx
                        })
                        await self._notify_progress(job_id, progress, f"Processing {idx}/{total}")
                    
                    # 분석 실행
                    result = await self._analyze_single_record(
                        row,
                        job_id,
                        file_info,
                        config
                    )
                    
                    if result:
                        results.append(result)
                        # 결과 저장
                        self.analysis_repo.save_result(result)
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze record {idx}: {e}")
                    self.analysis_repo.update_job(job_id, {
                        "failed_records": self.analysis_repo.get_job(job_id).get("failed_records", 0) + 1
                    })
            
            # 완료 처리
            self.analysis_repo.update_job(job_id, {
                "status": "completed",
                "progress": 100,
                "processed_records": total,
                "end_time": datetime.utcnow()
            })
            
            await self._notify_progress(job_id, 100, "Analysis completed")
            
        except Exception as e:
            self.logger.error(f"Analysis failed for job {job_id}: {e}")
            self.analysis_repo.update_job(job_id, {
                "status": "failed",
                "error": str(e),
                "end_time": datetime.utcnow()
            })
            await self._notify_progress(job_id, -1, f"Analysis failed: {e}")
    
    async def _analyze_single_record(
        self,
        record: pd.Series,
        job_id: str,
        file_info: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """단일 레코드 분석"""
        try:
            # UID 추출
            uid = None
            for col in file_info.get('uid_columns', []):
                if col in record and pd.notna(record[col]):
                    uid = str(record[col])
                    break
            
            if not uid:
                return None
            
            # Opinion 추출
            opinion = ""
            for col in file_info.get('opinion_columns', []):
                if col in record and pd.notna(record[col]):
                    opinion = str(record[col])
                    break
            
            # 분석 모드에 따른 처리
            analysis_mode = config.get('analysis_mode', 'hybrid')
            
            # 텍스트 분석
            text_score = 0
            if analysis_mode in ['hybrid', 'text_only'] and opinion:
                text_analysis = await self._analyze_text(opinion)
                text_score = text_analysis.get('score', 0)
            
            # 정량 분석
            quant_score = 0
            if analysis_mode in ['hybrid', 'quantitative_only']:
                quant_cols = file_info.get('quantitative_columns', [])
                quant_data = {col: record.get(col) for col in quant_cols if col in record}
                quant_analysis = self._analyze_quantitative(quant_data)
                quant_score = quant_analysis.get('score', 0)
            
            # 하이브리드 점수 계산
            if analysis_mode == 'hybrid':
                hybrid_score = (text_score * 0.6) + (quant_score * 0.4)
            elif analysis_mode == 'text_only':
                hybrid_score = text_score
            else:
                hybrid_score = quant_score
            
            # 등급 계산
            grade_info = self._calculate_grade(hybrid_score)
            
            # AI 피드백 (옵션)
            ai_feedback = {}
            if config.get('enable_ai_feedback') and opinion:
                ai_feedback = await self.ai_service.generate_feedback(
                    opinion,
                    hybrid_score,
                    config.get('openai_model'),
                    config.get('max_tokens')
                )
            
            # 결과 구성
            result = {
                'analysis_id': str(uuid.uuid4()),
                'job_id': job_id,
                'uid': uid,
                'file_id': file_info['id'],
                'filename': file_info['filename'],
                'opinion': opinion,
                'hybrid_score': round(hybrid_score, 2),
                'text_score': round(text_score, 2),
                'quantitative_score': round(quant_score, 2),
                'ok_grade': grade_info['grade'],
                'grade_description': grade_info['description'],
                'confidence': 0.85,
                'analysis_mode': analysis_mode,
                **ai_feedback
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze record: {e}")
            return None
    
    async def _analyze_text(self, text: str) -> Dict[str, float]:
        """텍스트 분석 (간단한 버전)"""
        # 실제로는 HybridAnalyzer를 사용
        # 여기서는 간단한 예제
        if not text:
            return {'score': 0}
        
        # 긍정/부정 키워드 기반 간단한 분석
        positive_keywords = ['excellent', 'great', 'good', '우수', '훌륭', '좋은']
        negative_keywords = ['poor', 'bad', 'terrible', '나쁜', '별로', '부족']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # 점수 계산
        base_score = 70
        score = base_score + (positive_count * 5) - (negative_count * 10)
        score = max(0, min(100, score))
        
        return {'score': score}
    
    def _analyze_quantitative(self, data: Dict[str, Any]) -> Dict[str, float]:
        """정량 데이터 분석"""
        if not data:
            return {'score': 0}
        
        # 숫자 데이터만 추출
        numeric_values = []
        for key, value in data.items():
            try:
                numeric_values.append(float(value))
            except:
                pass
        
        if not numeric_values:
            return {'score': 0}
        
        # 평균 기반 점수 (0-100 정규화)
        avg_value = sum(numeric_values) / len(numeric_values)
        score = min(100, max(0, avg_value))
        
        return {'score': score}
    
    def _calculate_grade(self, score: float) -> Dict[str, str]:
        """점수 기반 등급 계산"""
        if score >= 90:
            return {'grade': 'S', 'description': '최우수'}
        elif score >= 80:
            return {'grade': 'A', 'description': '우수'}
        elif score >= 70:
            return {'grade': 'B', 'description': '양호'}
        elif score >= 60:
            return {'grade': 'C', 'description': '보통'}
        else:
            return {'grade': 'D', 'description': '미흡'}
    
    async def _notify_progress(self, job_id: str, progress: float, message: str):
        """WebSocket을 통한 진행 상황 알림"""
        try:
            await ws_manager.broadcast({
                "type": "analysis_progress",
                "job_id": job_id,
                "progress": progress,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            self.logger.warning(f"Failed to send WebSocket notification: {e}")
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """작업 상태 조회"""
        job = self.analysis_repo.get_job(job_id)
        if not job:
            return None
        
        # 결과 수 조회
        results = self.analysis_repo.get_results(job_id=job_id)
        
        return {
            "job_id": job_id,
            "status": job.get("status"),
            "progress": job.get("progress", 0),
            "total_records": job.get("total_records", 0),
            "processed_records": job.get("processed_records", 0),
            "failed_records": job.get("failed_records", 0),
            "result_count": len(results),
            "start_time": job.get("start_time"),
            "end_time": job.get("end_time"),
            "error": job.get("error")
        }
    
    def get_analysis_results(self, job_id: str) -> List[Dict[str, Any]]:
        """분석 결과 조회"""
        return self.analysis_repo.get_results(job_id=job_id)