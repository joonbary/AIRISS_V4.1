# app/services/analysis_service.py
"""
AIRISS v4.0 분석 서비스
- 분석 작업 관리 및 처리
- WebSocket과 연동
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import pandas as pd
import io
import json

logger = logging.getLogger(__name__)

class AnalysisService:
    """분석 서비스 - 분석 작업의 라이프사이클 관리"""
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.active_jobs = {}
        self.uploaded_files = {}  # 업로드된 파일 정보 저장
        logger.info("✅ AnalysisService 초기화 완료")
    
    async def upload_file(self, file_contents: bytes, filename: str) -> Dict[str, Any]:
        """파일 업로드 처리"""
        try:
            import uuid
            from pathlib import Path
            
            # Generate file ID
            file_id = str(uuid.uuid4())
            
            # Save file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / f"{file_id}_{filename}"
            with open(file_path, "wb") as f:
                f.write(file_contents)
            
            # Store file info
            file_info = {
                "file_id": file_id,
                "filename": filename,
                "path": str(file_path),
                "size": len(file_contents),
                "uploaded_at": datetime.now().isoformat()
            }
            
            self.uploaded_files[file_id] = file_info
            
            logger.info(f"✅ 파일 업로드 완료: {filename} -> {file_id}")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "message": "File uploaded successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ 파일 업로드 오류: {e}")
            raise
    
    async def start_analysis(self, 
                           file_id: str,
                           sample_size: int = 10,
                           analysis_mode: str = "hybrid",
                           enable_ai_feedback: bool = False,
                           openai_api_key: Optional[str] = None,
                           openai_model: str = "gpt-3.5-turbo",
                           max_tokens: int = 1200) -> str:
        """분석 작업 시작"""
        try:
            # Generate job ID
            import uuid
            job_id = str(uuid.uuid4())
            
            # Store job data
            job_data = {
                'file_id': file_id,
                'sample_size': sample_size,
                'analysis_mode': analysis_mode,
                'enable_ai_feedback': enable_ai_feedback,
                'openai_api_key': openai_api_key,
                'openai_model': openai_model,
                'max_tokens': max_tokens
            }
            
            self.active_jobs[job_id] = {
                'status': 'processing',
                'start_time': datetime.now(),
                'data': job_data,
                'progress': 0
            }
            
            if self.websocket_manager:
                await self.websocket_manager.send_alert(
                    "info",
                    f"분석 시작: {job_id}",
                    {"job_id": job_id, "file_id": file_id}
                )
            
            logger.info(f"✅ 분석 작업 시작: job_id={job_id}, file_id={file_id}")
            
            # 실제 분석 작업을 비동기로 시작
            asyncio.create_task(self._process_analysis(job_id, job_data))
            
            return job_id
            
        except Exception as e:
            logger.error(f"❌ 분석 시작 오류: {e}")
            raise
    
    async def update_progress(self, job_id: str, progress: float, details: Dict = None):
        """분석 진행률 업데이트"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['progress'] = progress
                self.active_jobs[job_id]['last_update'] = datetime.now()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_analysis_progress(job_id, {
                        "progress": progress,
                        "details": details or {}
                    })
            
        except Exception as e:
            logger.error(f"❌ 진행률 업데이트 오류: {e}")
    
    async def complete_analysis(self, job_id: str, results: Dict[str, Any]):
        """분석 완료 처리"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'completed'
                self.active_jobs[job_id]['end_time'] = datetime.now()
                self.active_jobs[job_id]['results'] = results
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "success",
                        f"분석 완료: {job_id}",
                        {"job_id": job_id, "results_count": len(results.get('data', []))}
                    )
                
                logger.info(f"✅ 분석 완료: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ 분석 완료 처리 오류: {e}")
    
    async def fail_analysis(self, job_id: str, error: str):
        """분석 실패 처리"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'failed'
                self.active_jobs[job_id]['error'] = error
                self.active_jobs[job_id]['end_time'] = datetime.now()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "error",
                        f"분석 실패: {job_id}",
                        {"job_id": job_id, "error": error}
                    )
                
                logger.error(f"❌ 분석 실패: {job_id} - {error}")
            
        except Exception as e:
            logger.error(f"❌ 분석 실패 처리 오류: {e}")
    
    async def _process_analysis(self, job_id: str, job_data: Dict[str, Any]):
        """실제 분석 작업 처리 - HybridAnalyzer 통합"""
        try:
            file_id = job_data['file_id']
            logger.info(f"분석 처리 시작: job_id={job_id}, file_id={file_id}")
            
            # Progress updates
            await self.update_progress(job_id, 10, {"status": "파일 로드 중"})
            
            # 1. 파일 정보 가져오기
            if file_id not in self.uploaded_files:
                raise ValueError(f"파일을 찾을 수 없습니다: {file_id}")
            
            file_info = self.uploaded_files[file_id]
            file_path = file_info['path']
            filename = file_info['filename']
            
            # 2. 파일 읽기 및 데이터 로드
            import pandas as pd
            logger.info(f"Excel 파일 읽기: {file_path}")
            
            try:
                df = pd.read_excel(file_path)
                logger.info(f"데이터 로드 완료: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                logger.error(f"파일 읽기 오류: {e}")
                raise ValueError(f"Excel 파일 읽기 실패: {e}")
            
            await self.update_progress(job_id, 20, {
                "status": "데이터 검증 중",
                "rows": len(df),
                "columns": len(df.columns)
            })
            
            # 3. 필수 컬럼 확인
            required_columns = ['uid', 'opinion']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"필수 컬럼이 없습니다: {missing_columns}")
            
            # 4. HybridAnalyzer 초기화
            from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
            analyzer = AIRISSHybridAnalyzer()
            
            # 5. 샘플 크기 제한
            sample_size = min(job_data.get('sample_size', 10), len(df))
            df_sample = df.head(sample_size)
            logger.info(f"분석 대상: {sample_size}명")
            
            await self.update_progress(job_id, 30, {
                "status": "AI 분석 시작",
                "analyzing": sample_size
            })
            
            # 6. 각 행에 대해 분석 수행
            analysis_results = []
            for idx, (index, row) in enumerate(df_sample.iterrows()):
                try:
                    # 진행률 업데이트
                    progress = 30 + (idx / sample_size) * 50  # 30-80% 구간
                    await self.update_progress(job_id, progress, {
                        "status": f"분석 중: {idx+1}/{sample_size}",
                        "current_uid": row.get('uid', f'ROW_{idx+1}')
                    })
                    
                    # 분석 수행
                    uid = str(row.get('uid', f'EMP_{idx+1}'))
                    opinion = str(row.get('opinion', ''))
                    
                    # HybridAnalyzer로 종합 분석
                    result = await analyzer.comprehensive_analysis(
                        uid=uid,
                        opinion=opinion,
                        row_data=row,
                        save_to_storage=True,
                        file_id=file_id,
                        filename=filename,
                        enable_ai=job_data.get('enable_ai_feedback', False),
                        openai_api_key=job_data.get('openai_api_key'),
                        openai_model=job_data.get('openai_model', 'gpt-3.5-turbo'),
                        max_tokens=job_data.get('max_tokens', 1200)
                    )
                    
                    # 결과 정리
                    analysis_results.append({
                        "uid": uid,
                        "name": row.get('name', ''),
                        "opinion": opinion[:200] + '...' if len(opinion) > 200 else opinion,
                        "score": result['hybrid_analysis']['overall_score'],
                        "grade": result['hybrid_analysis']['grade'],
                        "confidence": result['hybrid_analysis']['confidence'],
                        "text_score": result['text_analysis']['overall_score'],
                        "quantitative_score": result['quantitative_analysis']['quantitative_score'],
                        "dimension_scores": result['text_analysis']['dimension_scores'],
                        "explainability": result['explainability']
                    })
                    
                except Exception as e:
                    logger.error(f"행 {idx+1} 분석 오류: {e}")
                    analysis_results.append({
                        "uid": row.get('uid', f'ROW_{idx+1}'),
                        "name": row.get('name', ''),
                        "score": 0,
                        "grade": "ERROR",
                        "error": str(e)
                    })
            
            await self.update_progress(job_id, 85, {"status": "결과 생성 중"})
            
            # 7. 분석 결과 요약
            valid_results = [r for r in analysis_results if 'error' not in r]
            if valid_results:
                avg_score = sum(r['score'] for r in valid_results) / len(valid_results)
                grade_distribution = {}
                for r in valid_results:
                    grade = r['grade']
                    grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
            else:
                avg_score = 0
                grade_distribution = {}
            
            # 8. 최종 결과 구성
            results = {
                "job_id": job_id,
                "file_id": file_id,
                "filename": filename,
                "data": analysis_results,
                "summary": {
                    "total_analyzed": len(analysis_results),
                    "successful": len(valid_results),
                    "failed": len(analysis_results) - len(valid_results),
                    "average_score": round(avg_score, 1),
                    "grade_distribution": grade_distribution,
                    "analysis_mode": job_data.get('analysis_mode', 'hybrid'),
                    "ai_enabled": job_data.get('enable_ai_feedback', False)
                },
                "metadata": {
                    "analyzer_version": "AIRISS v4.0",
                    "analysis_timestamp": datetime.now().isoformat(),
                    "system_status": analyzer.get_system_status()
                }
            }
            
            await self.update_progress(job_id, 95, {"status": "분석 완료"})
            
            # 9. 작업 완료 처리
            await self.complete_analysis(job_id, results)
            
            # 10. 분석 작업 정보 저장
            if hasattr(analyzer, 'save_analysis_job'):
                job_info = {
                    "job_id": job_id,
                    "file_id": file_id,
                    "filename": filename,
                    "sample_size": sample_size,
                    "analysis_mode": job_data.get('analysis_mode', 'hybrid'),
                    "status": "completed",
                    "results_summary": results['summary']
                }
                analyzer.save_analysis_job(job_info)
            
        except Exception as e:
            logger.error(f"분석 처리 중 오류: {e}")
            await self.fail_analysis(job_id, str(e))
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        return self.active_jobs.get(job_id)
    
    def list_active_jobs(self) -> Dict[str, Any]:
        """활성 작업 목록"""
        return {
            "active_jobs": len(self.active_jobs),
            "jobs": list(self.active_jobs.keys())
        }
    
    async def get_analysis_results(self, job_id: str) -> Optional[pd.DataFrame]:
        """분석 결과 조회"""
        try:
            # 1. 먼저 메모리에서 작업 확인
            job_info = self.active_jobs.get(job_id)
            if not job_info:
                logger.warning(f"job_id {job_id}에 대한 작업을 찾을 수 없습니다")
                return None
            
            # 2. 작업이 완료되었는지 확인
            if job_info['status'] != 'completed':
                logger.warning(f"작업 {job_id}가 아직 완료되지 않았습니다: {job_info['status']}")
                return None
            
            # 3. 결과 데이터 가져오기
            results = job_info.get('results', {})
            data = results.get('data', [])
            
            if not data:
                logger.warning(f"job_id {job_id}에 대한 분석 결과 데이터가 없습니다")
                return None
            
            # 4. DataFrame으로 변환
            df = pd.DataFrame(data)
            logger.info(f"✅ 분석 결과 조회 성공: {len(df)} 개의 결과")
            return df
            
        except Exception as e:
            logger.error(f"❌ 분석 결과 조회 오류: {e}")
            return None
    
    async def export_results(self, job_id: str, format: str = "excel") -> Optional[bytes]:
        """분석 결과 내보내기"""
        try:
            # 분석 결과 조회
            df = await self.get_analysis_results(job_id)
            
            if df is None or df.empty:
                logger.warning(f"job_id {job_id}에 대한 내보낼 데이터가 없습니다")
                return None
            
            # 작업 정보 가져오기
            job_info = self.active_jobs.get(job_id, {})
            results = job_info.get('results', {})
            summary = results.get('summary', {})
            metadata = results.get('metadata', {})
            
            # 형식에 따라 내보내기
            if format.lower() == "excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # 분석 결과 시트
                    df.to_excel(writer, sheet_name='Analysis_Results', index=False)
                    
                    # 요약 정보 시트
                    summary_df = pd.DataFrame([summary])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # 메타데이터 시트
                    metadata_df = pd.DataFrame([metadata])
                    metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                    
                    # 엑셀 파일 포맷팅
                    workbook = writer.book
                    for sheet_name in workbook.sheetnames:
                        worksheet = workbook[sheet_name]
                        # 열 너비 자동 조정
                        for column in worksheet.columns:
                            max_length = 0
                            column_letter = column[0].column_letter
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = min(max_length + 2, 50)
                            worksheet.column_dimensions[column_letter].width = adjusted_width
                
                output.seek(0)
                return output.getvalue()
                
            elif format.lower() == "csv":
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')
                return output.getvalue().encode('utf-8-sig')
                
            elif format.lower() == "json":
                export_data = {
                    "job_id": job_id,
                    "results": df.to_dict(orient='records'),
                    "summary": summary,
                    "metadata": metadata
                }
                return json.dumps(export_data, ensure_ascii=False, indent=2).encode('utf-8')
                
            else:
                logger.error(f"지원하지 않는 형식: {format}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 결과 내보내기 오류: {e}")
            return None