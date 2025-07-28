# app/services/analysis_service_fixed.py
"""
AIRISS v4.0 Fixed Analysis Service
- Persists job data to database
- Properly tracks job lifecycle
"""

import logging
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime
import pandas as pd
import io
import json
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.job import Job
from app.db.database import get_db
from app.core.config import settings
from app.exceptions import (
    AnalysisError, 
    FileProcessingError, 
    ValidationError, 
    ResourceNotFoundError,
    InternalServiceError
)

logger = logging.getLogger(__name__)

class AnalysisServiceFixed:
    """Fixed Analysis Service with proper database persistence"""
    
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.uploaded_files = {}  # Keep file info in memory for quick access
        
        # Create database session factory
        # Use DATABASE_URL from settings or fallback to SQLite
        database_url = settings.DATABASE_URL or "sqlite:///./airiss.db"
        
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False}
            )
        else:
            self.engine = create_engine(database_url)
            
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info("✅ AnalysisServiceFixed initialized with database persistence")
    
    def _get_db(self):
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        finally:
            pass  # Don't close here, let caller handle it
    
    async def upload_file(self, file_contents: bytes, filename: str) -> Dict[str, Any]:
        """Upload file and store reference with enhanced validation"""
        try:
            from pathlib import Path
            import pandas as pd
            import io
            import os
            
            # Generate file ID
            file_id = str(uuid.uuid4())
            
            # Save file
            upload_dir = Path("uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / f"{file_id}_{filename}"
            logger.info(f"📁 Saving file to: {file_path}")
            
            with open(file_path, "wb") as f:
                written_bytes = f.write(file_contents)
                logger.info(f"💾 Written {written_bytes} bytes to disk")
            
            # Verify file was saved
            if not os.path.exists(file_path):
                raise FileProcessingError(f"File was not saved properly: {file_path}")
            
            saved_size = os.path.getsize(file_path)
            logger.info(f"✔️ File verified on disk: {saved_size} bytes")
            
            # Read file to get record count and columns
            total_records = 0
            columns = []
            column_mapping_info = {}
            sample_data = None
            
            try:
                logger.info(f"📖 Reading file for validation: {filename}")
                
                if filename.lower().endswith(('.xlsx', '.xls')):
                    # Try reading with different engines and options
                    try:
                        df = pd.read_excel(io.BytesIO(file_contents))
                        logger.info(f"[DEBUG] Excel 읽기 성공 - shape: {df.shape}")
                    except Exception as e1:
                        logger.warning(f"⚠️ Default Excel read failed: {e1}")
                        try:
                            # Try with openpyxl explicitly
                            df = pd.read_excel(io.BytesIO(file_contents), engine='openpyxl')
                            logger.info(f"[DEBUG] Openpyxl Excel 읽기 성공 - shape: {df.shape}")
                        except Exception as e2:
                            logger.warning(f"⚠️ Openpyxl read failed: {e2}")
                            # Try reading from saved file
                            df = pd.read_excel(file_path)
                            logger.info(f"[DEBUG] 파일 경로로 Excel 읽기 성공 - shape: {df.shape}")
                            
                elif filename.lower().endswith('.csv'):
                    # Try different encodings
                    for encoding in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']:
                        try:
                            df = pd.read_csv(io.BytesIO(file_contents), encoding=encoding)
                            logger.info(f"✅ CSV read successful with encoding: {encoding}")
                            logger.info(f"[DEBUG] CSV 읽기 성공 - shape: {df.shape}")
                            break
                        except:
                            continue
                    else:
                        raise FileProcessingError("Could not read CSV with any common encoding")
                else:
                    raise FileProcessingError(f"Unsupported file type: {filename}")
                
                # [DEBUG] 빈 DataFrame 방지 - 업로드 시점 검증
                logger.info("=" * 60)
                logger.info("[DEBUG] 업로드 파일 검증 시작")
                logger.info(f"[DEBUG] 읽기 직후 shape: {df.shape}")
                logger.info(f"[DEBUG] 읽기 직후 empty: {df.empty}")
                
                # 읽기 직후 즉시 체크
                if df.shape[0] == 0:
                    logger.error(f"[ERROR] 업로드된 파일이 비어있음 - shape: {df.shape}")
                    raise ValidationError("업로드된 파일에 데이터가 없습니다. 빈 파일은 처리할 수 없습니다.")
                
                # Remove any completely empty rows/columns
                df = df.dropna(how='all').dropna(axis=1, how='all')
                
                # [DEBUG] 정리 후 재검증
                original_shape_before_clean = df.shape
                df_cleaned = df.dropna(how='all').dropna(axis=1, how='all')
                cleaned_shape = df_cleaned.shape
                
                logger.info(f"[DEBUG] 정리 전후 shape: {original_shape_before_clean} → {cleaned_shape}")
                
                total_records = len(df)
                columns = list(df.columns)
                
                # [DEBUG] 빈 DataFrame 강화 검증
                if total_records == 0 or df.shape[0] == 0 or df.empty:
                    logger.error(f"[ERROR] 빈 DataFrame 감지!")
                    logger.error(f"[ERROR] total_records: {total_records}")
                    logger.error(f"[ERROR] df.shape: {df.shape}")
                    logger.error(f"[ERROR] df.empty: {df.empty}")
                    logger.error(f"[ERROR] 정리 전: {original_shape_before_clean}, 정리 후: {cleaned_shape}")
                    raise ValidationError("파일에 유효한 데이터가 없습니다. 모든 행이 비어있거나 제거되었습니다.")
                
                if len(columns) == 0 or df.shape[1] == 0:
                    logger.error(f"[ERROR] 컬럼이 없는 DataFrame!")
                    logger.error(f"[ERROR] columns 길이: {len(columns)}")
                    logger.error(f"[ERROR] df.shape[1]: {df.shape[1]}")
                    raise ValidationError("파일에 유효한 컬럼이 없습니다.")
                
                logger.info("=" * 60)
                
                # Log first few rows for debugging
                if total_records > 0:
                    sample_data = df.head(3).to_dict('records')
                    logger.info(f"📊 File analysis: {total_records} records, {len(columns)} columns")
                    logger.info(f"📋 Columns: {columns}")
                    logger.info(f"🔍 Sample data (first 3 rows): {sample_data}")
                else:
                    logger.warning(f"⚠️ File appears to be empty: 0 records found")
                
                # Validate data quality - 최종 검증
                if total_records == 0:
                    raise ValidationError("파일에 데이터가 없습니다. 빈 파일은 분석할 수 없습니다.")
                
                if len(columns) == 0:
                    raise ValidationError("파일에 컬럼이 없습니다. 올바른 형식의 파일인지 확인해주세요.")
                
                # 컬럼 매핑 미리 확인
                from app.core.column_mapper import ColumnMapper
                mapped_cols, missing_req, mapping_log = ColumnMapper.map_columns(columns)
                column_mapping_info = {
                    'original_columns': columns,
                    'mapped_columns': mapped_cols,
                    'has_uid': 'uid' in mapped_cols.values(),
                    'has_opinion': 'opinion' in mapped_cols.values(),
                    'ready_for_analysis': len(missing_req) == 0,
                    'missing_required': missing_req
                }
                logger.info(f"📋 컬럼 매핑 상태: UID={column_mapping_info['has_uid']}, Opinion={column_mapping_info['has_opinion']}")
                
                if not column_mapping_info['ready_for_analysis']:
                    logger.warning(f"⚠️ 필수 컬럼 누락: {missing_req}")
                
            except Exception as read_error:
                logger.error(f"❌ File read error: {read_error}")
                logger.error(f"File path: {file_path}")
                logger.error(f"File size: {len(file_contents)} bytes")
                
                # 에러 발생 시 Exception raise
                raise FileProcessingError(f"파일 읽기 실패: {str(read_error)}")
            
            # Store file info with enhanced metadata
            file_info = {
                "file_id": file_id,
                "filename": filename,
                "path": str(file_path),
                "absolute_path": str(file_path.absolute()),
                "size": len(file_contents),
                "saved_size": saved_size,
                "total_records": total_records,
                "columns": columns,
                "column_mapping_info": column_mapping_info,
                "sample_data": sample_data,
                "uploaded_at": datetime.now().isoformat()
            }
            
            self.uploaded_files[file_id] = file_info
            
            logger.info(f"✅ File uploaded successfully: {filename} -> {file_id}")
            logger.info(f"📊 Summary: {total_records} records, {len(columns)} columns, {saved_size} bytes")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "total_records": total_records,
                "columns": columns,
                "column_mapping_ready": column_mapping_info.get('ready_for_analysis', False),
                "message": f"파일 업로드 성공: {total_records}개 레코드"
            }
            
        except Exception as e:
            logger.error(f"❌ File upload error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def start_analysis(self, 
                           file_id: str,
                           sample_size: int = 10,
                           analysis_mode: str = "hybrid",
                           enable_ai_feedback: bool = False,
                           openai_api_key: Optional[str] = None,
                           openai_model: str = "gpt-3.5-turbo",
                           max_tokens: int = 1200) -> str:
        """Start analysis job and persist to database"""
        # [DEBUG] 파일 매핑/전달 로깅 - 분석 시작 시 파일 정보 검증
        logger.info("=" * 60)
        logger.info("[DEBUG] 분석 시작 요청")
        logger.info(f"[DEBUG] file_id: {file_id}")
        
        # 파일 정보 검증
        if file_id in self.uploaded_files:
            file_info = self.uploaded_files[file_id]
            file_path = file_info['path']
            import os
            exists = os.path.exists(file_path)
            logger.info(f"[DEBUG] 파일 경로: {file_path}")
            logger.info(f"[DEBUG] 파일 존재 여부: {exists}")
            logger.info(f"[DEBUG] 파일명: {file_info['filename']}")
            logger.info(f"[DEBUG] 총 레코드 수: {file_info.get('total_records', 0)}")
            
            if not exists:
                logger.error(f"[ERROR] 파일이 디스크에 존재하지 않음: {file_path}")
                raise ResourceNotFoundError(f"파일이 존재하지 않습니다: {file_path}")
        else:
            logger.error(f"[ERROR] file_id가 메모리에 없음: {file_id}")
            logger.error(f"[ERROR] 현재 메모리의 file_id 목록: {list(self.uploaded_files.keys())}")
            raise ResourceNotFoundError(f"업로드된 파일을 찾을 수 없습니다: {file_id}")
        
        logger.info("=" * 60)
        
        db = self._get_db()
        try:
            # Generate job ID
            job_id = str(uuid.uuid4())
            
            # Create job data JSON
            job_data = json.dumps({
                'file_id': file_id,
                'sample_size': sample_size,
                'analysis_mode': analysis_mode,
                'enable_ai_feedback': enable_ai_feedback,
                'openai_api_key': openai_api_key,
                'openai_model': openai_model,
                'max_tokens': max_tokens
            })
            
            # Create job in database
            job = Job(
                id=job_id,
                file_id=file_id,
                status='processing',
                sample_size=sample_size,
                analysis_mode=analysis_mode,
                enable_ai_feedback=enable_ai_feedback,
                openai_model=openai_model,
                max_tokens=max_tokens,
                progress=0.0,
                job_data=job_data
            )
            
            db.add(job)
            db.commit()
            db.refresh(job)
            
            if self.websocket_manager:
                await self.websocket_manager.send_alert(
                    "info",
                    f"Analysis started: {job_id}",
                    {"job_id": job_id, "file_id": file_id}
                )
            
            logger.info(f"✅ Analysis job created in DB: job_id={job_id}, file_id={file_id}")
            
            # Start actual analysis in background
            asyncio.create_task(self._process_analysis(job_id))
            
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Analysis start error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    async def update_progress(self, job_id: str, progress: float, details: Dict = None):
        """Update analysis progress in database"""
        db = self._get_db()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.progress = progress
                job.updated_at = datetime.now()
                db.commit()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_analysis_progress(job_id, {
                        "progress": progress,
                        "details": details or {}
                    })
                
                logger.info(f"Progress updated: job_id={job_id}, progress={progress}")
            else:
                logger.warning(f"Job not found for progress update: {job_id}")
                
        except Exception as e:
            logger.error(f"❌ Progress update error: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def complete_analysis(self, job_id: str, results: Dict[str, Any]):
        """Complete analysis and update database"""
        db = self._get_db()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = 'completed'
                job.end_time = datetime.now()
                job.progress = 100.0
                job.total_records = len(results.get('data', []))
                
                # Store results data as JSON
                job.results_data = json.dumps(results, ensure_ascii=False)
                
                db.commit()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "success",
                        f"Analysis completed: {job_id}",
                        {"job_id": job_id, "results_count": job.total_records}
                    )
                
                logger.info(f"✅ Analysis completed: {job_id}")
            else:
                logger.warning(f"Job not found for completion: {job_id}")
                
        except Exception as e:
            logger.error(f"❌ Analysis completion error: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def fail_analysis(self, job_id: str, error: str):
        """Mark analysis as failed in database"""
        db = self._get_db()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                job.status = 'failed'
                job.error = error
                job.end_time = datetime.now()
                db.commit()
                
                if self.websocket_manager:
                    await self.websocket_manager.send_alert(
                        "error",
                        f"Analysis failed: {job_id}",
                        {"job_id": job_id, "error": error}
                    )
                
                logger.error(f"❌ Analysis failed: {job_id} - {error}")
            else:
                logger.warning(f"Job not found for failure update: {job_id}")
                
        except Exception as e:
            logger.error(f"❌ Analysis failure update error: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _process_analysis(self, job_id: str):
        """Process analysis with proper database updates"""
        try:
            # Get job data from database
            db = self._get_db()
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job:
                logger.error(f"Job not found: {job_id}")
                return
                
            job_data = json.loads(job.job_data) if job.job_data else {}
            file_id = job.file_id
            db.close()
            
            logger.info(f"Processing analysis: job_id={job_id}, file_id={file_id}")
            
            # Progress updates
            await self.update_progress(job_id, 10, {"status": "파일 로드 중"})
            
            # 1. 파일 정보 가져오기
            if file_id not in self.uploaded_files:
                logger.error(f"❌ File ID not found in memory: {file_id}")
                logger.error(f"Available file IDs: {list(self.uploaded_files.keys())}")
                raise ResourceNotFoundError(f"파일을 찾을 수 없습니다: {file_id}")
            
            file_info = self.uploaded_files[file_id]
            file_path = file_info['path']
            filename = file_info['filename']
            expected_records = file_info.get('total_records', 0)
            
            logger.info(f"📂 File info retrieved: {filename}")
            logger.info(f"📍 Path: {file_path}")
            logger.info(f"📊 Expected records: {expected_records}")
            
            # Verify file exists on disk
            import os
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found on disk: {file_path}")
                raise ResourceNotFoundError(f"파일이 디스크에 없습니다: {file_path}")
            
            file_size = os.path.getsize(file_path)
            logger.info(f"✅ File exists on disk: {file_size} bytes")
            
            # 2. 파일 읽기 및 데이터 로드
            import pandas as pd
            logger.info(f"📖 Reading file: {file_path}")
            
            # [DEBUG] 파일 로딩 강제 검증
            logger.info("=" * 60)
            logger.info("[DEBUG] 파일 로딩 시작")
            logger.info(f"[DEBUG] 파일 경로: {file_path}")
            logger.info(f"[DEBUG] 파일 크기: {file_size} bytes")
            
            # 파일 열기 전 재확인
            if not os.path.exists(file_path):
                logger.error(f"[ERROR] 파일 읽기 직전 재확인 - 파일이 없음: {file_path}")
                raise ResourceNotFoundError(f"파일이 삭제되었습니다: {file_path}")
            
            try:
                if filename.lower().endswith('.csv'):
                    # Try multiple encodings for CSV
                    for encoding in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding)
                            logger.info(f"✅ CSV read successful with encoding: {encoding}")
                            logger.info(f"[DEBUG] CSV 읽기 직후 shape: {df.shape}")
                            break
                        except Exception as e:
                            logger.warning(f"[DEBUG] {encoding} 인코딩 실패: {str(e)}")
                            continue
                    else:
                        raise FileProcessingError("Could not read CSV with any encoding")
                else:
                    # Excel files
                    df = pd.read_excel(file_path)
                    logger.info(f"[DEBUG] Excel 읽기 직후 shape: {df.shape}")
                
                # [DEBUG] 읽기 직후 즉시 shape 확인
                logger.info(f"[DEBUG] 파일 읽기 성공 - shape: {df.shape}")
                logger.info(f"[DEBUG] 빈 DataFrame 여부: {df.empty}")
                
                # Remove completely empty rows and columns
                original_shape = df.shape
                df = df.dropna(how='all').dropna(axis=1, how='all')
                cleaned_shape = df.shape
                
                logger.info(f"📊 Data loaded - Original: {original_shape}, Cleaned: {cleaned_shape}")
                logger.info(f"📋 Columns: {list(df.columns)}")
                logger.info("=" * 60)
                
                # Log sample data
                if len(df) > 0:
                    logger.info(f"🔍 First row data: {df.iloc[0].to_dict()}")
                    logger.info(f"📈 Data types: {df.dtypes.to_dict()}")
                
                # Validate data
                if len(df) == 0:
                    logger.error("❌ DataFrame is empty after loading")
                    logger.error(f"[ERROR] Original shape: {original_shape}, Cleaned shape: {cleaned_shape}")
                    logger.error(f"[ERROR] 파일 경로: {file_path}")
                    logger.error(f"[ERROR] 파일 크기: {file_size} bytes")
                    raise ValidationError(f"파일에 유효한 데이터가 없습니다. 빈 행이 제거된 후 0개 레코드")
                
                if len(df.columns) == 0:
                    logger.error("❌ DataFrame has no columns")
                    raise ValidationError(f"파일에 유효한 컬럼이 없습니다")
                
                # Compare with expected records
                if expected_records > 0 and len(df) != expected_records:
                    logger.warning(f"⚠️ Record count mismatch - Expected: {expected_records}, Actual: {len(df)}")
                
            except Exception as e:
                logger.error(f"❌ File read error: {e}")
                logger.error(f"File path: {file_path}")
                logger.error(f"File size: {file_size} bytes")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise FileProcessingError(f"파일 읽기 실패: {str(e)}")
            
            await self.update_progress(job_id, 20, {
                "status": "데이터 검증 중",
                "rows": len(df),
                "columns": len(df.columns)
            })
            
            # 3. 컬럼명 자동 매핑
            from app.core.column_mapper import ColumnMapper
            
            original_columns = list(df.columns)
            logger.info(f"원본 컬럼: {original_columns}")
            
            # 컬럼 매핑 수행
            mapped_columns, missing_required, mapping_log = ColumnMapper.map_columns(original_columns)
            
            # 매핑 리포트 생성
            mapping_report = ColumnMapper.get_mapping_report(
                original_columns, mapped_columns, missing_required, mapping_log
            )
            logger.info(f"\n{mapping_report}")
            
            # 필수 컬럼 누락 시 상세 오류 메시지
            if missing_required:
                error_msg = f"필수 컬럼이 없습니다: {missing_required}\n"
                error_msg += f"파일의 실제 컬럼: {original_columns}\n"
                error_msg += "매핑 시도 결과:\n"
                for col, log in mapping_log.items():
                    error_msg += f"  - {col}: {log}\n"
                
                if 'uid' in missing_required:
                    error_msg += "\n💡 UID 컬럼으로 인식 가능한 이름: UID, ID, 아이디, 사번, 직원번호, 피평가자ID 등"
                if 'opinion' in missing_required:
                    error_msg += "\n💡 Opinion 컬럼으로 인식 가능한 이름: 의견, 평가의견, 평가내용, 피드백, comment 등"
                
                logger.error(error_msg)
                raise ValidationError(error_msg)
            
            # 데이터프레임 컬럼명 변경
            df = ColumnMapper.rename_dataframe_columns(df, mapped_columns)
            logger.info(f"매핑 후 컬럼: {list(df.columns)}")
            
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
                        "current_uid": str(row.get('uid', f'ROW_{idx+1}'))
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
                    
                    # 결과 정리 - AI 피드백 포함
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
                        "explainability": result['explainability'],
                        # AI 피드백 추가
                        "ai_strengths": result.get('ai_feedback', {}).get('ai_strengths', ''),
                        "ai_weaknesses": result.get('ai_feedback', {}).get('ai_weaknesses', ''),
                        "ai_feedback": result.get('ai_feedback', {}).get('ai_feedback', ''),
                        "ai_recommendations": result.get('ai_feedback', {}).get('ai_recommendations', [])
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
            
            logger.info(f"✅ 분석 완료: {job_id} - {len(valid_results)}개 성공, {len(analysis_results) - len(valid_results)}개 실패")
            
        except Exception as e:
            logger.error(f"Analysis processing error: {e}")
            await self.fail_analysis(job_id, str(e))
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status from database"""
        db = self._get_db()
        try:
            job = db.query(Job).filter(Job.id == job_id).first()
            if job:
                return {
                    "job_id": job.id,
                    "file_id": job.file_id,
                    "status": job.status,
                    "progress": job.progress,
                    "start_time": job.start_time.isoformat() if job.start_time else None,
                    "end_time": job.end_time.isoformat() if job.end_time else None,
                    "total_records": job.total_records,
                    "processed_records": job.processed_records,
                    "failed_records": job.failed_records,
                    "error": job.error
                }
            return None
        except Exception as e:
            logger.error(f"Error getting job status: {e}")
            return None
        finally:
            db.close()
    
    def list_active_jobs(self) -> Dict[str, Any]:
        """List active jobs from database"""
        db = self._get_db()
        try:
            active_jobs = db.query(Job).filter(
                Job.status.in_(['pending', 'processing'])
            ).all()
            
            return {
                "active_jobs": len(active_jobs),
                "jobs": [job.id for job in active_jobs]
            }
        except Exception as e:
            logger.error(f"Error listing active jobs: {e}")
            return {"active_jobs": 0, "jobs": []}
        finally:
            db.close()
    
    async def get_analysis_results(self, job_id: str) -> Optional[pd.DataFrame]:
        """Get analysis results for a job"""
        try:
            # Check if job exists and is completed
            db = self._get_db()
            job = db.query(Job).filter(Job.id == job_id).first()
            if not job or job.status != 'completed':
                logger.warning(f"Job {job_id} not found or not completed")
                return None
            db.close()
            
            # 실제 결과 데이터 가져오기
            if job.results_data:
                # JSON 문자열에서 데이터 파싱
                results = json.loads(job.results_data)
                analysis_data = results.get('data', [])
                
                if analysis_data:
                    df = pd.DataFrame(analysis_data)
                    logger.info(f"✅ Analysis results retrieved: {len(df)} records")
                    return df
                else:
                    logger.warning(f"No analysis data found for job {job_id}")
                    return None
            else:
                logger.warning(f"No results data found for job {job_id}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Error getting analysis results: {e}")
            return None
    
    async def export_results(self, job_id: str, format: str = "excel") -> Optional[bytes]:
        """Export analysis results in specified format"""
        try:
            # Get results
            df = await self.get_analysis_results(job_id)
            
            if df is None or df.empty:
                logger.warning(f"No data to export for job {job_id}")
                return None
            
            # Export based on format
            if format.lower() == "excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Analysis_Results', index=False)
                output.seek(0)
                return output.getvalue()
                
            elif format.lower() == "csv":
                output = io.StringIO()
                df.to_csv(output, index=False, encoding='utf-8-sig')
                return output.getvalue().encode('utf-8-sig')
                
            elif format.lower() == "json":
                return json.dumps(df.to_dict(orient='records'), ensure_ascii=False, indent=2).encode('utf-8')
                
            else:
                logger.error(f"Unsupported format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            return None