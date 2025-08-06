# -*- coding: utf-8 -*-
"""
Column Name Mapper for AIRISS v4.0
컬럼명 자동 매핑 및 정규화 모듈
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ColumnMapper:
    """컬럼명 자동 매핑 및 정규화 클래스"""
    
    # UID 관련 컬럼명 매핑
    UID_MAPPINGS = {
        'uid': 'uid',
        'UID': 'uid',
        'id': 'uid',
        'ID': 'uid',
        '아이디': 'uid',
        '사번': 'uid',
        '직원번호': 'uid',
        '직원ID': 'uid',
        '사원번호': 'uid',
        '사원ID': 'uid',
        '피평가자ID': 'uid',
        '피평가자아이디': 'uid',
        '피평가자': 'uid',
        'employee_id': 'uid',
        'emp_id': 'uid',
        'user_id': 'uid',
        'userId': 'uid',
        'employeeId': 'uid',
        'empId': 'uid',
    }
    
    # Opinion 관련 컬럼명 매핑
    OPINION_MAPPINGS = {
        'opinion': 'opinion',
        'Opinion': 'opinion',
        'OPINION': 'opinion',
        '의견': 'opinion',
        '평가의견': 'opinion',
        '평가내용': 'opinion',
        '평가피드백': 'opinion',
        '피드백': 'opinion',
        '평가': 'opinion',
        '내용': 'opinion',
        '코멘트': 'opinion',
        'comment': 'opinion',
        'feedback': 'opinion',
        'review': 'opinion',
        'evaluation': 'opinion',
        'eval_opinion': 'opinion',
        'eval_feedback': 'opinion',
        '자유의견': 'opinion',
        '평가자의견': 'opinion',
        '상세의견': 'opinion',
        '종합의견': 'opinion',
    }
    
    # 추가 매핑 (이름, 부서 등)
    NAME_MAPPINGS = {
        'name': 'name',
        'Name': 'name',
        'NAME': 'name',
        '이름': 'name',
        '성명': 'name',
        '직원명': 'name',
        '사원명': 'name',
        '피평가자명': 'name',
        '피평가자이름': 'name',
        'employee_name': 'name',
        'emp_name': 'name',
    }
    
    @classmethod
    def normalize_column_name(cls, column_name: str) -> str:
        """컬럼명 정규화 (공백 제거, 소문자 변환 등)"""
        if not column_name:
            return column_name
        # 공백 제거, 언더스코어로 치환
        normalized = column_name.strip().replace(' ', '_').replace('\t', '_')
        # 특수문자 제거
        normalized = ''.join(c for c in normalized if c.isalnum() or c in ['_', '-'])
        return normalized
    
    @classmethod
    def map_column(cls, column_name: str, mapping_dict: Dict[str, str]) -> Optional[str]:
        """단일 컬럼명 매핑"""
        # 원본 그대로 확인
        if column_name in mapping_dict:
            return mapping_dict[column_name]
        
        # 정규화 후 확인
        normalized = cls.normalize_column_name(column_name)
        if normalized in mapping_dict:
            return mapping_dict[normalized]
        
        # 대소문자 무시 확인
        for key, value in mapping_dict.items():
            if column_name.lower() == key.lower():
                return value
            if normalized.lower() == key.lower():
                return value
        
        # 부분 문자열 매칭 (키워드 포함 여부)
        for key, value in mapping_dict.items():
            if key.lower() in column_name.lower():
                return value
            if column_name.lower() in key.lower():
                return value
        
        return None
    
    @classmethod
    def map_columns(cls, columns: List[str]) -> Tuple[Dict[str, str], List[str], Dict[str, str]]:
        """
        컬럼 리스트를 매핑
        
        Returns:
            mapped_columns: 매핑된 컬럼명 딕셔너리 {원본: 매핑}
            missing_required: 필수 컬럼 중 누락된 것들
            mapping_log: 매핑 과정 로그
        """
        mapped_columns = {}
        mapping_log = {}
        
        # 각 컬럼에 대해 매핑 시도
        for col in columns:
            # UID 매핑
            uid_mapped = cls.map_column(col, cls.UID_MAPPINGS)
            if uid_mapped:
                mapped_columns[col] = uid_mapped
                mapping_log[col] = f"UID로 매핑됨 ({col} → {uid_mapped})"
                logger.info(f"컬럼 매핑: {col} → {uid_mapped} (UID)")
                continue
            
            # Opinion 매핑
            opinion_mapped = cls.map_column(col, cls.OPINION_MAPPINGS)
            if opinion_mapped:
                mapped_columns[col] = opinion_mapped
                mapping_log[col] = f"Opinion으로 매핑됨 ({col} → {opinion_mapped})"
                logger.info(f"컬럼 매핑: {col} → {opinion_mapped} (Opinion)")
                continue
            
            # Name 매핑
            name_mapped = cls.map_column(col, cls.NAME_MAPPINGS)
            if name_mapped:
                mapped_columns[col] = name_mapped
                mapping_log[col] = f"Name으로 매핑됨 ({col} → {name_mapped})"
                logger.info(f"컬럼 매핑: {col} → {name_mapped} (Name)")
                continue
            
            # 매핑되지 않은 컬럼
            mapping_log[col] = f"매핑되지 않음 (원본 유지: {col})"
            logger.debug(f"컬럼 매핑 실패: {col} - 원본 유지")
        
        # 필수 컬럼 확인
        mapped_values = list(mapped_columns.values())
        missing_required = []
        
        if 'uid' not in mapped_values:
            missing_required.append('uid')
            logger.warning("UID 컬럼을 찾을 수 없습니다.")
            logger.warning(f"시도한 컬럼들: {columns}")
            logger.warning(f"UID 매핑 후보: {list(cls.UID_MAPPINGS.keys())}")
        
        if 'opinion' not in mapped_values:
            missing_required.append('opinion')
            logger.warning("Opinion 컬럼을 찾을 수 없습니다.")
            logger.warning(f"시도한 컬럼들: {columns}")
            logger.warning(f"Opinion 매핑 후보: {list(cls.OPINION_MAPPINGS.keys())}")
        
        return mapped_columns, missing_required, mapping_log
    
    @classmethod
    def rename_dataframe_columns(cls, df, mapped_columns: Dict[str, str]):
        """데이터프레임의 컬럼명을 매핑된 이름으로 변경"""
        rename_dict = {}
        for original, mapped in mapped_columns.items():
            if original in df.columns:
                rename_dict[original] = mapped
        
        if rename_dict:
            logger.info(f"데이터프레임 컬럼 리네임: {rename_dict}")
            df = df.rename(columns=rename_dict)
        
        return df
    
    @classmethod
    def get_mapping_report(cls, columns: List[str], mapped_columns: Dict[str, str], 
                          missing_required: List[str], mapping_log: Dict[str, str]) -> str:
        """매핑 결과 리포트 생성"""
        report = []
        report.append("=" * 60)
        report.append("컬럼 매핑 리포트")
        report.append("=" * 60)
        report.append(f"원본 컬럼 수: {len(columns)}")
        report.append(f"매핑된 컬럼 수: {len(mapped_columns)}")
        report.append(f"필수 컬럼 누락: {len(missing_required)}")
        report.append("")
        
        report.append("원본 컬럼 목록:")
        for col in columns:
            report.append(f"  - {col}")
        report.append("")
        
        report.append("매핑 결과:")
        for original, mapped in mapped_columns.items():
            report.append(f"  - {original} → {mapped}")
        report.append("")
        
        if missing_required:
            report.append("⚠️ 누락된 필수 컬럼:")
            for col in missing_required:
                report.append(f"  - {col}")
            report.append("")
            
            if 'uid' in missing_required:
                report.append("UID 컬럼 매핑 가능한 이름들:")
                for key in list(cls.UID_MAPPINGS.keys())[:10]:
                    report.append(f"  - {key}")
                report.append("  ... 등")
            
            if 'opinion' in missing_required:
                report.append("Opinion 컬럼 매핑 가능한 이름들:")
                for key in list(cls.OPINION_MAPPINGS.keys())[:10]:
                    report.append(f"  - {key}")
                report.append("  ... 등")
        
        report.append("=" * 60)
        
        return '\n'.join(report)