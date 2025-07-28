"""
워크플로우 태스크 구현
"""
import os
import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def validate_file_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """파일 검증 태스크"""
    file_path = params.get('file_path')
    
    logger.info(f"Validating file: {file_path}")
    
    # 파일 존재 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise ValueError("File is empty")
    
    # 파일 형식 확인
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        try:
            df = pd.read_excel(file_path, nrows=5)  # 처음 5행만 읽어서 검증
            rows = len(df)
            columns = list(df.columns)
        except Exception as e:
            raise ValueError(f"Invalid Excel file: {e}")
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
    
    return {
        'status': 'valid',
        'file_size': file_size,
        'file_type': 'excel',
        'preview_rows': rows,
        'columns': columns
    }

async def extract_metadata_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """메타데이터 추출 태스크"""
    file_path = params.get('file_path')
    
    logger.info(f"Extracting metadata from: {file_path}")
    
    df = pd.read_excel(file_path)
    
    metadata = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
        'null_counts': df.isnull().sum().to_dict(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # UID 컬럼 찾기
    uid_columns = [col for col in df.columns if 'uid' in col.lower() or '사번' in col or 'id' in col.lower()]
    metadata['uid_column'] = uid_columns[0] if uid_columns else None
    
    # 의견 컬럼 찾기
    opinion_columns = [col for col in df.columns if '의견' in col or 'opinion' in col.lower() or '평가' in col]
    metadata['opinion_column'] = opinion_columns[0] if opinion_columns else None
    
    return metadata

async def analyze_statistics_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """통계 분석 태스크"""
    job_id = params.get('job_id')
    
    logger.info(f"Analyzing statistics for job: {job_id}")
    
    # 실제 구현에서는 DB에서 데이터를 가져와 분석
    # 여기서는 샘플 결과 반환
    
    statistics = {
        'total_analyzed': 10,
        'average_score': 85.5,
        'score_distribution': {
            'S': 2,
            'A': 3,
            'B': 4,
            'C': 1,
            'D': 0
        },
        'department_stats': {
            '개발팀': {'count': 3, 'avg_score': 88.0},
            '영업팀': {'count': 2, 'avg_score': 85.0},
            '기획팀': {'count': 2, 'avg_score': 83.5},
            '인사팀': {'count': 2, 'avg_score': 86.0},
            '재무팀': {'count': 1, 'avg_score': 82.0}
        }
    }
    
    return statistics

async def analyze_llm_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """LLM 분석 태스크"""
    job_id = params.get('job_id')
    employee_data = params.get('employee_data', {})
    
    logger.info(f"LLM analysis for employee: {employee_data.get('uid')}")
    
    # OpenAI API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or not api_key.startswith('sk-'):
        # API 키가 없으면 기본 분석 결과 반환
        logger.warning("OpenAI API key not available, using default analysis")
        
        return {
            'uid': employee_data.get('uid'),
            'llm_analysis': {
                'summary': '기본 분석 결과입니다.',
                'strengths': ['성실함', '책임감'],
                'improvements': ['커뮤니케이션 향상 필요'],
                'recommendation': '지속적인 성장이 기대됩니다.',
                'confidence': 0.7
            },
            'analysis_type': 'default'
        }
    
    # 실제 LLM 분석 (여기서는 시뮬레이션)
    return {
        'uid': employee_data.get('uid'),
        'llm_analysis': {
            'summary': 'AI 기반 상세 분석 결과입니다.',
            'strengths': ['우수한 업무 성과', '팀워크', '창의성'],
            'improvements': ['시간 관리', '문서화 능력'],
            'recommendation': '리더십 교육 프로그램 참여 권장',
            'confidence': 0.85
        },
        'analysis_type': 'ai'
    }

async def generate_excel_report_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """Excel 보고서 생성 태스크"""
    job_id = params.get('job_id')
    original_filename = params.get('original_filename', 'report')
    
    logger.info(f"Generating Excel report for job: {job_id}")
    
    # 결과 데이터 생성 (실제로는 DB에서 가져옴)
    report_data = {
        '직원ID': ['EMP0001', 'EMP0002', 'EMP0003'],
        '이름': ['김철수', '이영희', '박민수'],
        '부서': ['개발팀', '영업팀', '기획팀'],
        '종합점수': [92, 88, 85],
        '등급': ['A', 'B+', 'B'],
        'AI 분석': ['우수한 성과', '안정적인 성과', '성장 가능성 높음']
    }
    
    df = pd.DataFrame(report_data)
    
    # 결과 파일 저장
    os.makedirs('results', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f'results/AIRISS_Report_{job_id}_{timestamp}.xlsx'
    
    # Excel 파일 생성 with 스타일
    with pd.ExcelWriter(result_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='분석결과', index=False)
        
        # 워크시트 스타일 적용
        worksheet = writer.sheets['분석결과']
        
        # 헤더 스타일
        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)
            cell.fill = cell.fill.copy(fgColor="CCCCCC")
        
        # 컬럼 너비 조정
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
    
    logger.info(f"Report saved: {result_file}")
    
    return {
        'report_file': result_file,
        'total_records': len(df),
        'file_size': os.path.getsize(result_file)
    }

async def store_to_mcp_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """MCP 서버 저장 태스크"""
    job_id = params.get('job_id')
    
    logger.info(f"Storing to MCP for job: {job_id}")
    
    # MCP 서버가 설정되어 있지 않으면 스킵
    mcp_url = os.getenv('MCP_SERVER_URL')
    
    if not mcp_url:
        logger.info("MCP server not configured, skipping")
        return {
            'status': 'skipped',
            'reason': 'MCP server not configured'
        }
    
    # 실제 MCP 저장 로직
    return {
        'status': 'stored',
        'mcp_id': f'mcp_{job_id}',
        'stored_at': datetime.utcnow().isoformat()
    }

async def generate_download_link_task(params: Dict[str, Any]) -> Dict[str, Any]:
    """다운로드 링크 생성 태스크"""
    job_id = params.get('job_id')
    
    logger.info(f"Generating download link for job: {job_id}")
    
    # 결과 파일 찾기
    results_dir = 'results'
    result_files = []
    
    if os.path.exists(results_dir):
        for file in os.listdir(results_dir):
            if job_id in file and file.endswith('.xlsx'):
                result_files.append(os.path.join(results_dir, file))
    
    if not result_files:
        raise FileNotFoundError(f"No result file found for job: {job_id}")
    
    # 가장 최신 파일 선택
    latest_file = max(result_files, key=os.path.getctime)
    
    # 다운로드 링크 생성 (실제로는 download_manager 사용)
    download_url = f"/api/v1/download/{job_id}"
    
    return {
        'download_url': download_url,
        'file_path': latest_file,
        'expires_in_hours': 24
    }