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
        """파일 업로드 처리 및 컬럼 분석"""
        try:
            import uuid
            from pathlib import Path
            import pandas as pd
            import io
            
            # Generate file ID
            file_id = str(uuid.uuid4())
            
            # Save file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / f"{file_id}_{filename}"
            
            # 디버깅 로그 추가
            import os
            logger.info(f"📁 현재 작업 디렉토리: {os.getcwd()}")
            logger.info(f"📁 uploads 디렉토리 경로: {upload_dir.absolute()}")
            logger.info(f"📁 파일 저장 경로: {file_path.absolute()}")
            
            with open(file_path, "wb") as f:
                f.write(file_contents)
            
            logger.info(f"📁 파일 저장 완료: {file_path}")
            logger.info(f"📁 파일 크기: {os.path.getsize(file_path)} bytes")
            logger.info(f"📁 파일 존재 확인: {os.path.exists(file_path)}")
            
            # Excel 파일 분석
            df = None
            try:
                if filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(file_contents))
                    logger.info(f"📊 Excel 파일 읽기 완료: {len(df)} rows, {len(df.columns)} columns")
                elif filename.endswith('.csv'):
                    # 여러 인코딩 시도
                    encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(io.StringIO(file_contents.decode(encoding)))
                            logger.info(f"📊 CSV 파일 읽기 완료 (인코딩: {encoding}): {len(df)} rows, {len(df.columns)} columns")
                            break
                        except:
                            continue
                    
                    if df is None:
                        raise ValueError("CSV 파일 인코딩을 인식할 수 없습니다")
                else:
                    raise ValueError("지원되지 않는 파일 형식입니다. CSV 또는 Excel 파일만 가능합니다.")
                
                logger.info(f"📋 파일 컬럼명: {list(df.columns)}")
                logger.info(f"📄 첫 3행 데이터 미리보기:\n{df.head(3)}")
                
            except Exception as e:
                logger.error(f"❌ 파일 읽기 오류: {e}")
                raise ValueError(f"파일 읽기 실패: {e}")
            
            # 데이터 프레임이 비어있는지 확인
            if df.empty:
                logger.error(f"❌ 파일에 데이터가 없습니다: {file_path}")
                raise ValueError("파일에 데이터가 없습니다. 다른 파일을 선택해주십시오.")
            
            # 컬럼 분석
            all_columns = list(df.columns)
            
            # UID 컬럼 감지
            uid_keywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp', 'employee']
            uid_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in uid_keywords)]
            
            # 의견 컬럼 감지
            opinion_keywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review', '자료', '텍스트', 'text']
            opinion_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in opinion_keywords)]
            
            # 정량데이터 컬럼 감지
            quant_keywords = ['점수', 'score', '평점', 'rating', '등급', 'grade', 'level', '달성률', '비율', 'rate', '%', 'percent']
            quantitative_columns = []
            
            for col in all_columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in quant_keywords):
                    # 실제 데이터 확인
                    sample_data = df[col].dropna().head(10)
                    if len(sample_data) > 0:
                        quantitative_columns.append(col)
            
            logger.info(f"🎯 컬럼 분석 결과:")
            logger.info(f"   - 전체 컬럼: {len(all_columns)}개")
            logger.info(f"   - UID 컬럼: {uid_columns}")
            logger.info(f"   - 의견 컬럼: {opinion_columns}")
            logger.info(f"   - 정량 컬럼: {quantitative_columns}")
            
            # Store file info with analysis results
            file_info = {
                "file_id": file_id,
                "filename": filename,
                "path": str(file_path.absolute()),  # 절대 경로 저장
                "size": len(file_contents),
                "total_records": len(df),
                "columns": all_columns,
                "uid_columns": uid_columns,
                "opinion_columns": opinion_columns,
                "quantitative_columns": quantitative_columns,
                "uploaded_at": datetime.now().isoformat()
            }
            
            self.uploaded_files[file_id] = file_info
            
            logger.info(f"✅ 파일 업로드 및 분석 완료: {filename} -> {file_id}")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "total_records": len(df),
                "column_count": len(all_columns),
                "columns": all_columns,
                "uid_columns": uid_columns,
                "opinion_columns": opinion_columns,
                "quantitative_columns": quantitative_columns,
                "airiss_ready": len(uid_columns) > 0 and len(opinion_columns) > 0,
                "hybrid_ready": len(quantitative_columns) > 0,
                "data_quality": {
                    "non_empty_records": len(df.dropna()),
                    "completeness": round((len(df.dropna()) / len(df)) * 100, 1) if len(df) > 0 else 0,
                    "quantitative_completeness": round((len(quantitative_columns) / len(all_columns)) * 100, 1) if len(all_columns) > 0 else 0
                },
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
            logger.info(f"🎯 분석 시작 요청 - enable_ai_feedback: {enable_ai_feedback}")
            logger.info(f"🎯 OpenAI API 키 전달 여부: {'있음' if openai_api_key else '없음'}")
            
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
            
            # 데이터베이스에 Job 레코드 생성
            await self._create_job_record(job_id, job_data)
            
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
    
    async def _create_job_record(self, job_id: str, job_data: Dict[str, Any]):
        """데이터베이스에 Job 레코드 생성"""
        try:
            from app.db.database import get_db
            from app.models.job import Job
            import json
            
            def create_job():
                db = next(get_db())
                try:
                    # 파일 정보 가져오기
                    file_id = job_data['file_id']
                    file_info = self.uploaded_files.get(file_id, {})
                    
                    job = Job(
                        id=job_id,
                        file_id=file_id,
                        filename=file_info.get('filename'),
                        status='processing',
                        sample_size=job_data['sample_size'],
                        analysis_mode=job_data['analysis_mode'],
                        enable_ai_feedback=job_data['enable_ai_feedback'],
                        openai_model=job_data.get('openai_model'),
                        max_tokens=job_data.get('max_tokens'),
                        total_records=file_info.get('total_records', 0),
                        job_data=json.dumps(job_data)
                    )
                    db.add(job)
                    db.commit()
                    logger.info(f"✅ Job 레코드 생성 완료: {job_id}")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ Job 레코드 생성 오류: {e}")
                    raise
                finally:
                    db.close()
            
            # 동기 함수를 비동기로 실행
            import asyncio
            await asyncio.to_thread(create_job)
            
        except Exception as e:
            logger.error(f"❌ Job 레코드 생성 중 오류: {e}")
            raise
    
    async def update_progress(self, job_id: str, progress: float, details: Dict = None):
        """분석 진행률 업데이트"""
        try:
            # 메모리 업데이트
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['progress'] = progress
                self.active_jobs[job_id]['last_update'] = datetime.now()
            
            # 데이터베이스 업데이트
            from app.db.database import get_db
            from app.models.job import Job
            
            def update_job_progress():
                db = next(get_db())
                try:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        job.progress = progress
                        job.updated_at = datetime.now()
                        db.commit()
                        logger.info(f"📊 진행률 업데이트: {job_id} - {progress}%")
                finally:
                    db.close()
            
            await asyncio.to_thread(update_job_progress)
            
            # WebSocket 알림
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
                
                # 데이터베이스 Job 레코드 업데이트
                await self._update_job_completion(job_id, results)
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "success",
                        f"분석 완료: {job_id}",
                        {"job_id": job_id, "results_count": len(results.get('data', []))}
                    )
                
                logger.info(f"✅ 분석 완료: {job_id}")
            
        except Exception as e:
            logger.error(f"❌ 분석 완료 처리 오류: {e}")
    
    async def _update_job_completion(self, job_id: str, results: Dict[str, Any]):
        """데이터베이스 Job 레코드 완료 업데이트"""
        try:
            from app.db.database import get_db
            from app.models.job import Job
            import json
            
            def update_job():
                db = next(get_db())
                try:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        job.status = 'completed'
                        job.end_time = datetime.now()
                        job.progress = 100.0
                        job.processed_records = len(results.get('analysis_results', results.get('data', [])))
                        job.average_score = results.get('summary', {}).get('average_score', 0.0)
                        job.results_data = json.dumps(results)
                        
                        db.commit()
                        logger.info(f"✅ Job 완료 업데이트: {job_id}")
                    else:
                        logger.warning(f"⚠️ Job 레코드를 찾을 수 없음: {job_id}")
                        
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ Job 완료 업데이트 오류: {e}")
                    raise
                finally:
                    db.close()
            
            # 동기 함수를 비동기로 실행
            import asyncio
            await asyncio.to_thread(update_job)
            
        except Exception as e:
            logger.error(f"❌ Job 완료 업데이트 중 오류: {e}")
    
    async def fail_analysis(self, job_id: str, error: str):
        """분석 실패 처리"""
        try:
            if job_id in self.active_jobs:
                self.active_jobs[job_id]['status'] = 'failed'
                self.active_jobs[job_id]['error'] = error
                self.active_jobs[job_id]['end_time'] = datetime.now()
                
                # 데이터베이스 업데이트
                from app.db.database import get_db
                from app.models.job import Job
                
                def update_job_failure():
                    db = next(get_db())
                    try:
                        job = db.query(Job).filter(Job.id == job_id).first()
                        if job:
                            job.status = 'failed'
                            job.error_message = error[:500] if error else None  # 에러 메시지 길이 제한
                            job.end_time = datetime.now()
                            db.commit()
                            logger.info(f"🔄 Job 실패 업데이트: {job_id}")
                    except Exception as e:
                        db.rollback()
                        logger.error(f"❌ Job 실패 업데이트 오류: {e}")
                    finally:
                        db.close()
                
                await asyncio.to_thread(update_job_failure)
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "error",
                        f"분석 실패: {job_id}",
                        {"job_id": job_id, "error": error}
                    )
                
                logger.error(f"❌ 분석 실패: {job_id} - {error}")
            
        except Exception as e:
            logger.error(f"❌ 분석 실패 처리 오류: {e}")
            import traceback
            logger.error(f"트레이스백:\n{traceback.format_exc()}")
    
    async def _process_analysis(self, job_id: str, job_data: Dict[str, Any]):
        """실제 분석 작업 처리 - HybridAnalyzer 통합"""
        logger.info("="*60)
        logger.info(f"🚀 _process_analysis 시작")
        logger.info(f"🆔 job_id: {job_id}")
        logger.info(f"📁 job_data: {job_data}")
        logger.info("="*60)
        
        try:
            file_id = job_data['file_id']
            logger.info(f"분석 처리 시작: job_id={job_id}, file_id={file_id}")
            
            # Progress updates
            await self.update_progress(job_id, 10, {"status": "파일 로드 중"})
            
            # 1. 파일 정보 가져오기 - 먼저 데이터베이스에서 확인
            file_info = None
            file_path = None
            filename = None
            
            # 데이터베이스에서 파일 정보 조회
            from app.db.database import get_db
            from app.models.file import File as FileModel
            import json
            
            db = next(get_db())
            try:
                file_record = db.query(FileModel).filter(FileModel.id == file_id).first()
                if file_record:
                    logger.info(f"✅ 데이터베이스에서 파일 정보 찾음: {file_id}")
                    file_path = file_record.file_path
                    filename = file_record.filename
                    
                    # 메모리 캐시에 저장
                    self.uploaded_files[file_id] = {
                        'path': file_path,
                        'filename': filename,
                        'total_records': file_record.total_records,
                        'columns': json.loads(file_record.columns) if file_record.columns else []
                    }
                    file_info = self.uploaded_files[file_id]
                else:
                    # 메모리에서 확인 (fallback)
                    if file_id in self.uploaded_files:
                        logger.info(f"📦 메모리 캐시에서 파일 정보 찾음: {file_id}")
                        file_info = self.uploaded_files[file_id]
                        file_path = file_info['path']
                        filename = file_info['filename']
                    else:
                        logger.error(f"❌ 파일을 찾을 수 없습니다: {file_id}")
                        logger.error(f"📁 현재 업로드된 파일 목록: {list(self.uploaded_files.keys())}")
                        raise ValueError(f"파일을 찾을 수 없습니다: {file_id}")
            finally:
                db.close()
            
            # 파일 존재 여부 확인
            import os
            if not os.path.exists(file_path):
                logger.error(f"❌ 파일이 파일시스템에 존재하지 않습니다: {file_path}")
                logger.error(f"📁 uploads 디렉토리 내용: {os.listdir('uploads') if os.path.exists('uploads') else '디렉토리 없음'}")
                raise ValueError(f"파일이 존재하지 않습니다: {file_path}")
            
            # 2. 파일 읽기 및 데이터 로드
            import pandas as pd
            logger.info(f"파일 읽기 시작: {file_path}")
            
            try:
                # pickle 파일로 저장된 경우
                if file_path.endswith('.pkl'):
                    df = pd.read_pickle(file_path)
                    logger.info(f"📊 Pickle 파일 로드 완료: {len(df)} rows, {len(df.columns)} columns")
                # Excel 파일인 경우
                elif file_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(file_path)
                    logger.info(f"📊 Excel 파일 로드 완료: {len(df)} rows, {len(df.columns)} columns")
                # CSV 파일인 경우
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    logger.info(f"📊 CSV 파일 로드 완료: {len(df)} rows, {len(df.columns)} columns")
                else:
                    raise ValueError(f"지원되지 않는 파일 형식: {file_path}")
                
                logger.info(f"📋 파일 컬럼명: {list(df.columns)}")
                logger.info(f"📄 첫 5행 데이터 미리보기:\n{df.head()}")
            except Exception as e:
                logger.error(f"❌ 파일 읽기 오류: {e}")
                raise ValueError(f"파일 읽기 실패: {e}")
            
            # 데이터 프레임이 비어있는지 확인
            if df.empty:
                logger.error(f"❌ 파일에 데이터가 없습니다: {file_path}")
                raise ValueError("파일에 데이터가 없습니다. 다른 파일을 선택해주십시오.")
            
            await self.update_progress(job_id, 20, {
                "status": "데이터 검증 중",
                "rows": len(df),
                "columns": len(df.columns)
            })
            
            # 3. 필수 컬럼 확인 (유연한 컬럼명 매칭)
            column_names = [col.lower().strip() for col in df.columns]
            logger.info(f"🔍 소문자 변환된 컬럼명: {column_names}")
            
            # uid 컬럼 찾기
            uid_column = None
            for col in df.columns:
                if col.lower().strip() in ['uid', 'id', '직원번호', 'employee_id', '사번']:
                    uid_column = col
                    break
            
            # opinion 컬럼 찾기  
            opinion_column = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(keyword in col_lower for keyword in ['opinion', '의견', '평가', 'comment', '코멘트', 'feedback', '리뷰', 'review', '자료', '내용', 'content', '텍스트', 'text']):
                    opinion_column = col
                    break
            
            # 필수 컬럼 확인
            if uid_column is None:
                logger.error(f"❌ UID 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")
                raise ValueError("필수 컬럼 'UID' 또는 '직원번호'를 찾을 수 없습니다.")
                
            if opinion_column is None:
                logger.error(f"❌ 평가의견 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")
                raise ValueError("필수 컬럼 '평가의견' 또는 'Opinion'을 찾을 수 없습니다.")
            
            # 이름 컬럼 찾기
            name_column = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(keyword in col_lower for keyword in ['name', '이름', '성명', '직원명']):
                    name_column = col
                    break
            
            # 부서 컬럼 찾기
            department_column = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(keyword in col_lower for keyword in ['department', '부서', 'dept', '소속', '팀']):
                    department_column = col
                    break
            
            # 직급 컬럼 찾기
            position_column = None
            for col in df.columns:
                col_lower = col.lower().strip()
                if any(keyword in col_lower for keyword in ['position', '직급', '직위', 'title', 'grade', '등급']):
                    position_column = col
                    break
            
            logger.info(f"📦 컬럼 매핑 결과:")
            logger.info(f"  - UID: {uid_column}")
            logger.info(f"  - Opinion: {opinion_column}")
            logger.info(f"  - Name: {name_column or '없음'}")
            logger.info(f"  - Department: {department_column or '없음'}")
            logger.info(f"  - Position: {position_column or '없음'}")
                
            if not opinion_column:
                logger.error(f"❌ 의견 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {list(df.columns)}")
                raise ValueError("의견 컬럼(opinion, 의견, 평가 등)을 찾을 수 없습니다.")
            
            logger.info(f"✅ 컬럼 매칭 성공: uid='{uid_column}', opinion='{opinion_column}'")
            if name_column:
                logger.info(f"✅ 이름 컬럼 발견: '{name_column}'")
            if department_column:
                logger.info(f"✅ 부서 컬럼 발견: '{department_column}'")
            if position_column:
                logger.info(f"✅ 직급 컬럼 발견: '{position_column}'")
            
            # 4. HybridAnalyzer 초기화
            from app.services.hybrid_analyzer import AIRISSHybridAnalyzer
            analyzer = AIRISSHybridAnalyzer()
            
            # 5. 샘플 크기 제한
            sample_size = min(job_data.get('sample_size', 10), len(df))
            df_sample = df.head(sample_size)
            logger.info(f"📊 분석 대상: {sample_size}명 (전체: {len(df)}명)")
            logger.info(f"📋 분석할 컬럼: uid={uid_column}, opinion={opinion_column}")
            
            await self.update_progress(job_id, 30, {
                "status": "AI 분석 시작",
                "analyzing": sample_size
            })
            
            # 6. 각 행에 대해 분석 수행
            analysis_results = []
            logger.info(f"🔄 분석 루프 시작: {sample_size}개 레코드")
            
            for idx, (index, row) in enumerate(df_sample.iterrows()):
                try:
                    logger.info(f"📊 레코드 {idx+1}/{sample_size} 분석 시작")
                    
                    # 진행률 업데이트 - 더 세밀하게
                    progress = 30 + ((idx + 0.5) / sample_size) * 50  # 30-80% 구간
                    await self.update_progress(job_id, progress, {
                        "status": f"분석 중: {idx+1}/{sample_size}",
                        "current_uid": row.get(uid_column, f'ROW_{idx+1}'),
                        "processed": idx + 1,
                        "total": sample_size
                    })
                    
                    # 분석 수행 (실제 컬럼명 사용)
                    uid = str(row.get(uid_column, f'EMP_{idx+1}'))  
                    opinion = str(row.get(opinion_column, ''))
                    
                    # 메타데이터 추출
                    name = str(row.get(name_column, '')) if name_column else ''
                    department = str(row.get(department_column, '')) if department_column else ''
                    position = str(row.get(position_column, '')) if position_column else ''
                    
                    # API 키 처리: 클라이언트 제공 키 우선, 없으면 환경변수 사용
                    from app.core.config import settings
                    api_key = job_data.get('openai_api_key')
                    
                    logger.info(f"🔑 API 키 처리 - enable_ai_feedback: {job_data.get('enable_ai_feedback')}")
                    logger.info(f"🔑 클라이언트 제공 API 키: {'있음' if api_key else '없음'}")
                    
                    if not api_key and job_data.get('enable_ai_feedback', False):
                        api_key = settings.OPENAI_API_KEY
                        if api_key:
                            logger.info(f"✅ 환경변수에서 OpenAI API 키를 사용합니다: {api_key[:7]}...{api_key[-4:]}")
                        else:
                            logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다")
                    
                    logger.info(f"🔑 최종 API 키 사용: {'있음' if api_key else '없음'}")
                    
                    # HybridAnalyzer로 종합 분석
                    logger.info(f"🔬 HybridAnalyzer 호출 시작 - UID: {uid}")
                    result = await analyzer.comprehensive_analysis(
                        uid=uid,
                        opinion=opinion,
                        row_data=row,
                        save_to_storage=True,
                        file_id=file_id,
                        filename=filename,
                        enable_ai=job_data.get('enable_ai_feedback', False),
                        openai_api_key=api_key,
                        openai_model=job_data.get('openai_model', 'gpt-3.5-turbo'),
                        max_tokens=job_data.get('max_tokens', 1200)
                    )
                    
                    logger.info(f"✅ HybridAnalyzer 분석 완료 - UID: {uid}")
                    
                    # 결과 정리
                    ai_feedback_data = result.get('ai_feedback', {})
                    analysis_results.append({
                        "uid": uid,
                        "name": name,
                        "department": department,
                        "position": position,
                        "opinion": opinion[:200] + '...' if len(opinion) > 200 else opinion,
                        "score": result['hybrid_analysis']['overall_score'],
                        "grade": result['hybrid_analysis']['grade'],
                        "confidence": result['hybrid_analysis']['confidence'],
                        "text_score": result['text_analysis']['overall_score'],
                        "quantitative_score": result['quantitative_analysis']['quantitative_score'],
                        "dimension_scores": result['text_analysis']['dimension_scores'],
                        "explainability": result['explainability'],
                        "ai_feedback": {
                            'strengths': self._extract_strengths(ai_feedback_data),
                            'improvements': self._extract_improvements(ai_feedback_data),
                            'overall_comment': ai_feedback_data.get('ai_feedback', '')
                        }
                    })
                    
                except Exception as e:
                    logger.error(f"행 {idx+1} 분석 오류: {e}")
                    logger.error(f"오류 상세: {type(e).__name__}: {str(e)}")
                    import traceback
                    logger.error(f"트레이스백:\n{traceback.format_exc()}")
                    
                    analysis_results.append({
                        "uid": row.get(uid_column, f'ROW_{idx+1}'),
                        "name": row.get('name', ''),
                        "score": 0,
                        "grade": "ERROR",
                        "error": str(e)
                    })
                    
                    # 오류가 발생해도 진행률은 계속 업데이트
                    progress = 30 + ((idx + 1) / sample_size) * 50  # 30-80% 구간
                    await self.update_progress(job_id, progress, {
                        "processed": idx + 1,
                        "total": sample_size,
                        "current_uid": row.get(uid_column, f'ROW_{idx+1}'),
                        "error": str(e)
                    })
            
            await self.update_progress(job_id, 85, {
                "status": "결과 생성 중",
                "processed": sample_size,
                "total": sample_size
            })
            
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
                "analysis_results": analysis_results,  # 프론트엔드 호환성
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
            
            # 10. EmployeeResult 테이블에 각 직원 결과 저장
            logger.info(f"🔥 EmployeeResult 저장 함수 호출 전: job_id={job_id}, 결과 개수={len(analysis_results)}")
            try:
                await self._save_employee_results(job_id, analysis_results)
            except Exception as save_error:
                logger.error(f"❌ EmployeeResult 저장 중 예외 발생: {save_error}")
                # 저장 실패해도 분석은 성공으로 처리
            
            # 11. 분석 작업 정보는 이미 complete_analysis에서 저장됨
            logger.info(f"✅ 분석 처리 완료: job_id={job_id}, 총 {len(analysis_results)}명 분석")
            
        except Exception as e:
            import traceback
            logger.error(f"❌ 분석 처리 중 오류: {e}")
            logger.error(f"🔍 상세 오류:\n{traceback.format_exc()}")
            await self.fail_analysis(job_id, str(e))
    
    async def _save_employee_results(self, job_id: str, analysis_results: list):
        """분석 결과를 EmployeeResult 테이블에 저장"""
        try:
            logger.info(f"🔄 EmployeeResult 저장 시작: job_id={job_id}, 결과 개수={len(analysis_results)}")
            from app.db.database import get_db
            from app.models.employee import EmployeeResult
            import uuid
            
            # 동기 DB 세션 생성
            def save_results():
                db = next(get_db())
                try:
                    logger.info(f"📊 DB 세션 생성 완료, EmployeeResult 테이블에 저장 시작")
                    
                    # 기존 결과 삭제 (job_id 기준)
                    deleted_count = db.query(EmployeeResult).filter(EmployeeResult.job_id == job_id).delete()
                    logger.info(f"🗑️ 기존 결과 {deleted_count}개 삭제됨")
                    
                    # 새 결과 저장
                    saved_count = 0
                    for i, result in enumerate(analysis_results):
                        if 'error' not in result:
                            logger.info(f"💾 저장 중 [{i+1}/{len(analysis_results)}]: uid={result.get('uid')}, score={result.get('score')}")
                            employee_result = EmployeeResult(
                                id=str(uuid.uuid4()),
                                job_id=job_id,
                                uid=result['uid'],
                                overall_score=result['score'],
                                grade=result['grade'],
                                text_score=result.get('text_score', 0),
                                quantitative_score=result.get('quantitative_score', 0),
                                confidence=result.get('confidence', 0),
                                dimension_scores=result.get('dimension_scores', {}),
                                ai_feedback={
                                    'strengths': result.get('ai_feedback', {}).get('strengths', []),
                                    'improvements': result.get('ai_feedback', {}).get('improvements', []),
                                    'overall_comment': result.get('ai_feedback', {}).get('overall_comment', '')
                                },
                                employee_metadata={
                                    'name': result.get('name', ''),
                                    'department': result.get('department', ''),
                                    'position': result.get('position', '')
                                }
                            )
                            db.add(employee_result)
                            saved_count += 1
                        else:
                            logger.warning(f"⚠️ 오류가 있는 결과 건너뜀 [{i+1}]: {result.get('error')}")
                    
                    db.commit()
                    logger.info(f"✅ {saved_count}개의 직원 분석 결과를 EmployeeResult 테이블에 저장 완료")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ EmployeeResult 저장 오류: {e}")
                finally:
                    db.close()
            
            # 동기 함수를 비동기로 실행 - Python 3.9 호환
            import asyncio
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, save_results)
            
        except Exception as e:
            logger.error(f"❌ EmployeeResult 저장 중 오류: {e}")
    
    def _extract_strengths(self, ai_feedback_data: dict) -> list:
        """펼드백에서 강점 추출"""
        if not ai_feedback_data:
            return []
        
        # ai_strengths 필드가 있으면 사용
        if 'ai_strengths' in ai_feedback_data:
            strengths_text = ai_feedback_data.get('ai_strengths', '')
            if strengths_text:
                # 문자열에서 강점 추출 (콤마로 구분)
                return [s.strip() for s in strengths_text.split(',') if s.strip()][:3]
        
        # ai_feedback 필드에서 강점 추출
        feedback_text = ai_feedback_data.get('ai_feedback', '')
        if '강점' in feedback_text:
            # 간단한 패턴 매칭
            import re
            strengths_match = re.search(r'강점[:은]([^\n치]+)', feedback_text)
            if strengths_match:
                strengths = strengths_match.group(1).strip()
                return [s.strip() for s in strengths.split(',') if s.strip()][:3]
        
        # 기본값
        return ["팀워크 우수", "성실한 업무 태도"]
    
    def _extract_improvements(self, ai_feedback_data: dict) -> list:
        """피드백에서 개선점 추출"""
        if not ai_feedback_data:
            return []
        
        # ai_weaknesses 필드가 있으면 사용
        if 'ai_weaknesses' in ai_feedback_data:
            weaknesses_text = ai_feedback_data.get('ai_weaknesses', '')
            if weaknesses_text:
                # 문자열에서 개선점 추출 (콤마로 구분)
                return [w.strip() for w in weaknesses_text.split(',') if w.strip()][:2]
        
        # ai_feedback 필드에서 개선점 추출
        feedback_text = ai_feedback_data.get('ai_feedback', '')
        if '개선' in feedback_text or '보완' in feedback_text:
            # 간단한 패턴 매칭
            import re
            improvements_match = re.search(r'(개선|보완)[:점이]([^\n강]+)', feedback_text)
            if improvements_match:
                improvements = improvements_match.group(2).strip()
                return [i.strip() for i in improvements.split(',') if i.strip()][:2]
        
        # 기본값
        return ["전문성 향상 필요"]
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """작업 상태 조회"""
        # 먼저 메모리에서 확인
        job_info = self.active_jobs.get(job_id)
        if job_info:
            return job_info
        
        # 메모리에 없으면 데이터베이스에서 확인
        try:
            from app.db.database import get_db
            from app.models.job import Job
            import json
            
            db = next(get_db())
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    # 데이터베이스 정보를 메모리 형식으로 변환
                    job_info = {
                        'status': job.status,
                        'start_time': job.created_at,
                        'progress': 100 if job.status == 'completed' else 0,
                        'data': json.loads(job.job_data) if job.job_data else {}
                    }
                    
                    # 결과가 있으면 추가
                    if job.results_data:
                        results = json.loads(job.results_data) if isinstance(job.results_data, str) else job.results_data
                        job_info['results'] = results
                    
                    logger.info(f"✅ 데이터베이스에서 작업 찾음: {job_id}, 상태: {job.status}")
                    return job_info
                else:
                    logger.warning(f"❌ 작업을 찾을 수 없습니다: {job_id}")
                    return None
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"데이터베이스 조회 오류: {e}")
            return None
    
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
    
    def _get_db(self):
        """데이터베이스 세션 반환"""
        from app.db.database import get_db
        return next(get_db())