# app/api/upload.py
# AIRISS v4.0 파일 업로드 API - SQLiteService 메서드 호출 오류 완전 해결 버전
# async/await 처리 + 올바른 인자 전달

import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import pandas as pd
import io
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback
from sqlalchemy import text
import re
from sqlalchemy.orm import Session
from app.models.file import File as FileRecord
from app.db.database import get_db

# 프로젝트 내 모듈 import
from app.db import db_service
from app.schemas.schemas import FileUploadResponse, FileInfoResponse
from app.api.auth import get_current_user  # 경로 수정
from app.utils.encoding_safe import EncodingSafeUtils  # 인코딩 안전 유틸리티 추가

# 로깅 설정
logger = logging.getLogger(__name__)

# 업로드 라우터 생성
router = APIRouter() # prefix 제거
UPLOAD_DIR = Path("uploads") # Added UPLOAD_DIR
UPLOAD_DIR.mkdir(exist_ok=True) # Added UPLOAD_DIR

# 모든 엔드포인트에서 db_service를 직접 사용하도록 변경

def sanitize_filename(filename: str) -> str:
    """파일명을 안전하게 처리하여 인코딩 문제를 방지"""
    try:
        # 파일명에서 특수문자 제거 (한글은 유지)
        # Windows에서 문제가 되는 문자들 제거
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 연속된 언더스코어를 하나로 변환
        safe_filename = re.sub(r'_+', '_', safe_filename)
        
        # 앞뒤 공백 및 점 제거
        safe_filename = safe_filename.strip(' .')
        
        # 빈 파일명인 경우 기본값 설정
        if not safe_filename:
            safe_filename = "uploaded_file"
        
        logger.info(f"📝 파일명 안전화: '{filename}' → '{safe_filename}'")
        return safe_filename
        
    except Exception as e:
        logger.error(f"❌ 파일명 안전화 오류: {e}")
        # 오류 발생 시 기본 파일명 반환
        return f"file_{uuid.uuid4().hex[:8]}"

@router.post("/upload")
async def upload_file_public(
    file: UploadFile = File(...),
    request: Request = None
):
    """Public file upload endpoint without authentication"""
    try:
        # 기본 사용자 정보 (인증 없음)
        user_id = "anonymous"
        session_id = str(uuid.uuid4())
        logger.info(f"📁 Public 파일 업로드 - Session ID: {session_id}")

        # 파일명 안전화 처리
        safe_filename = sanitize_filename(file.filename)
        
        # 파일 저장
        file_id = generate_file_id()
        file_path = UPLOAD_DIR / f"{file_id}_{safe_filename}"
        
        # 파일 쓰기
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 파일 정보 반환
        return {
            "file_id": file_id,
            "filename": safe_filename,
            "size": len(content),
            "status": "uploaded"
        }
    except Exception as e:
        logger.error(f"업로드 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simple-upload")
async def upload_file(
    file: UploadFile = File(...),
    request: Request = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        # 사용자 정보 확인
        user_id = None
        if current_user:
            user_id = current_user.get('id') or current_user.get('user_id')
        session_id = request.session.get('session_id') if request else None
        if not session_id and request:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
        logger.info(f"📁 파일 업로드 - User ID: {user_id}, Session ID: {session_id}")

        # 파일명 안전화 처리
        safe_filename = sanitize_filename(file.filename)
        
        # 파일 저장 (안전한 방식)
        file_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{file_id}_{safe_filename}"
        
        # EncodingSafeUtils를 사용하여 안전한 경로 생성
        try:
            safe_file_path = EncodingSafeUtils.safe_path_join(str(UPLOAD_DIR), f"{file_id}_{safe_filename}")
            file_path = Path(safe_file_path)
        except Exception as e:
            logger.error(f"❌ 안전한 경로 생성 실패: {e}")
            # fallback: 기본 경로 사용
            file_path = UPLOAD_DIR / f"{file_id}_{safe_filename}"
        
        # 파일을 한 번에 읽어서 안전하게 저장 (Excel 파일 손상 방지)
        try:
            # 파일 내용을 한 번에 읽기
            file_content = await file.read()
            
            # 파일 저장
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            # 파일 무결성 검증
            if file_path.exists():
                actual_size = file_path.stat().st_size
                expected_size = len(file_content)
                
                if actual_size != expected_size:
                    logger.error(f"❌ 파일 무결성 검증 실패: 예상 {expected_size} bytes, 실제 {actual_size} bytes")
                    # 파일 삭제 후 오류 발생
                    file_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=500, detail="파일 저장 중 손상이 발생했습니다")
                
                logger.info(f"✅ 파일 무결성 검증 통과: {actual_size} bytes")
            else:
                raise HTTPException(status_code=500, detail="파일이 저장되지 않았습니다")
                
        except Exception as e:
            logger.error(f"❌ 파일 저장 실패: {e}")
            # 저장 실패 시 파일 정리
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=500, detail=f"파일 저장 중 오류가 발생했습니다: {str(e)}")
        
        # 파일 크기 확인
        file_size = file_path.stat().st_size
        logger.info(f"📁 파일 저장 완료: {file_path} ({file_size} bytes)")
        
        # 파일 메타데이터
        file_metadata = {
            "id": file_id,
            "filename": file.filename,
            "size": file_size,
            "upload_time": datetime.now(),
            "user_id": user_id,
            "session_id": session_id,
            "file_path": str(file_path)
        }
        
        # DataFrame 생성 및 저장
        try:
            import pandas as pd
            
            # 파일 확장자에 따라 DataFrame 생성
            if file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file.filename.endswith('.csv'):
                # 여러 인코딩 시도
                encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']
                df = None
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except:
                        continue
                if df is None:
                    raise Exception("CSV 파일 인코딩을 인식할 수 없습니다")
            else:
                raise Exception("지원하지 않는 파일 형식입니다")
            
            # 컬럼 분석
            all_columns = list(df.columns)
            
            # UID 컬럼 감지
            uid_keywords = ['uid', 'id', '아이디', '사번', '직원', 'user', 'emp']
            uid_columns = [col for col in all_columns if any(keyword in col.lower() for keyword in uid_keywords)]
            
            # 의견 컬럼 감지
            opinion_keywords = ['의견', 'opinion', '평가', 'feedback', '내용', '코멘트', '피드백', 'comment', 'review']
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
            
            # DataFrame을 pickle로 저장
            import pickle
            df_path = file_path.with_suffix('.pkl')
            with open(df_path, 'wb') as f:
                pickle.dump(df, f)
            
            # 메타데이터에 DataFrame 정보 추가
            file_metadata.update({
                "dataframe_path": str(df_path),
                "total_records": len(df),
                "columns": all_columns,
                "uid_columns": uid_columns,
                "opinion_columns": opinion_columns,
                "quantitative_columns": quantitative_columns,
                "airiss_ready": len(uid_columns) > 0 and len(opinion_columns) > 0,
                "hybrid_ready": len(quantitative_columns) > 0
            })
            
            logger.info(f"✅ DataFrame 생성 완료: {len(df)}행, {len(df.columns)}열")
            logger.info(f"  - UID 컬럼: {uid_columns}")
            logger.info(f"  - 의견 컬럼: {opinion_columns}")
            logger.info(f"  - 정량 컬럼: {quantitative_columns}")
            
        except Exception as e:
            logger.error(f"❌ DataFrame 생성 실패: {e}")
            # DataFrame 생성 실패해도 파일 메타데이터는 저장
            file_metadata.update({
                "total_records": 0,
                "columns": [],
                "uid_columns": [],
                "opinion_columns": [],
                "quantitative_columns": [],
                "airiss_ready": False,
                "hybrid_ready": False
            })
        
        # DB에 파일 정보 저장
        db_save_success = False
        try:
            if db_service:
                # DB 초기화 확인
                await db_service.init_database()
                # files 테이블에 저장
                await db_service.save_file(file_metadata)
                db_save_success = True
                logger.info(f"✅ DB에 파일 정보 저장 완료: {file.filename}")
        except Exception as e:
            logger.error(f"❌ DB 저장 실패: {str(e)}")
            db_save_success = False
        
        # DB 저장 실패 시 세션에 저장
        if not db_save_success and request:
            # datetime 객체를 문자열로 변환하여 세션에 저장
            session_file_metadata = file_metadata.copy()
            if isinstance(session_file_metadata.get('upload_time'), datetime):
                session_file_metadata['upload_time'] = session_file_metadata['upload_time'].isoformat()
            
            files_in_session = request.session.get('files', [])
            files_in_session.append(session_file_metadata)
            request.session['files'] = files_in_session
            logger.info(f"📋 세션에 파일 정보 저장: {file.filename}")
        
        return JSONResponse(content={
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "user_id": user_id,
            "session_id": session_id,
            "message": "파일이 성공적으로 업로드되었습니다."
        })
        
    except Exception as e:
        logger.error(f"❌ 업로드 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upload/{file_id}", response_model=FileInfoResponse)
async def get_file_info(
    file_id: str,
):
    """
    업로드된 파일 정보 조회
    - SQLiteService에서 파일 메타데이터 조회
    - DataFrame 기본 정보 제공
    """
    
    try:
        logger.info(f"📋 파일 정보 조회 요청: {file_id}")
        
        # 🔥 수정된 호출: await 추가
        file_record = await db_service.get_file(file_id)
        
        if not file_record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # get_file에서 이미 dataframe을 포함해서 반환하므로 별도 로드 불필요
        df = file_record.get('dataframe')
        
        if df is None:
            raise HTTPException(status_code=404, detail="파일 데이터를 로드할 수 없습니다")
        
        # 실시간 데이터 상태 확인
        current_records = len(df)
        current_columns = len(df.columns)
        
        # datetime 객체를 안전하게 문자열로 변환하는 함수
        def safe_convert_datetime(value):
            if isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, str):
                return value
            else:
                return datetime.now().isoformat()
        
        # 응답 데이터 구성 (datetime 안전 처리)
        response_data = {
            "file_id": file_id,
            "filename": file_record.get('filename', 'Unknown'),
            "total_records": current_records,
            "column_count": current_columns,
            "columns": [str(col) for col in df.columns.tolist()],
            "uid_columns": file_record.get('uid_columns', []),
            "opinion_columns": file_record.get('opinion_columns', []),
            "quantitative_columns": file_record.get('quantitative_columns', []),
            "upload_time": safe_convert_datetime(file_record.get('upload_time')),
            "file_size": file_record.get('file_size', 0),
            "airiss_ready": file_record.get('airiss_ready', False),
            "hybrid_ready": file_record.get('hybrid_ready', False),
            "data_quality": {
                "text_completeness": file_record.get('text_completeness', 0),
                "quant_completeness": file_record.get('quant_completeness', 0),
                "total_records": current_records
            }
        }
        
        logger.info(f"✅ 파일 정보 조회 성공: {file_id}")
        return FileInfoResponse(**response_data)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"파일 정보 조회 오류: {str(e)}")
        logger.error(f"상세 오류: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"파일 정보 조회 중 오류가 발생했습니다: {str(e)}")

@router.delete("/upload/{file_id}")
async def delete_file(
    file_id: str,
):
    """
    업로드된 파일 삭제
    - SQLiteService에서 파일 및 DataFrame 데이터 완전 삭제
    """
    
    try:
        logger.info(f"🗑️ 파일 삭제 요청: {file_id}")
        
        # 파일 존재 여부 확인 (🔥 await 추가)
        file_record = await db_service.get_file(file_id)
        if not file_record:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 파일 삭제 (🔥 await 추가)
        success = await db_service.delete_file(file_id)
        
        if success:
            logger.info(f"✅ 파일 삭제 완료: {file_id}")
            return {"message": f"파일이 성공적으로 삭제되었습니다", "file_id": file_id}
        else:
            raise HTTPException(status_code=500, detail="파일 삭제에 실패했습니다")
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"파일 삭제 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 삭제 중 오류가 발생했습니다: {str(e)}")

@router.get("/files")
async def list_files_pg(db: Session = Depends(get_db)):
    try:
        files = db.query(FileRecord).order_by(FileRecord.upload_time.desc()).all()
        formatted_files = []
        for f in files:
            # columns 정보 파싱
            columns_list = []
            if f.columns:
                try:
                    columns_list = json.loads(f.columns) if isinstance(f.columns, str) else f.columns
                except:
                    columns_list = []
                    
            formatted_files.append({
                "id": f.id,
                "filename": f.filename,
                "upload_time": f.upload_time.isoformat() if f.upload_time else None,
                "total_records": f.total_records,
                "column_count": len(columns_list),
                "columns": columns_list,  # 컬럼 정보 추가
                "user_id": f.user_id,
                "session_id": f.session_id
            })
        return JSONResponse(content={
            "status": "success",
            "files": formatted_files,
            "total": len(formatted_files)
        })
    except Exception as e:
        logger.error(f"❌ 파일 목록 조회 오류: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

# 디버깅 엔드포인트 제거 (SessionMiddleware datetime 직렬화 문제로 인해)
# 대신 간단한 상태 확인 엔드포인트 제공
@router.get("/status")
async def file_api_status():
    """파일 API 상태 확인 (SessionMiddleware 오류 없음)"""
    return JSONResponse(content={
        "status": "success",
        "message": "파일 업로드/목록 조회 API가 정상 동작합니다",
        "endpoints": {
            "upload": "/api/upload",
            "files": "/api/files",
            "status": "/api/status"
        },
        "note": "실제 파일 업로드와 목록 조회는 정상적으로 작동합니다"
    })
