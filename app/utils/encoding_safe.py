# -*- coding: utf-8 -*-
"""
AIRISS v4.1 - 인코딩 안전성 유틸리티
Windows/OneDrive 한글/특수문자 경로 대응
"""

import os
import sys
import logging
from pathlib import Path
from typing import Union, Optional

logger = logging.getLogger(__name__)

class EncodingSafeUtils:
    """Windows/OneDrive 인코딩 이슈 방지 유틸리티"""
    
    @staticmethod
    def safe_path_join(*args) -> str:
        """인코딩 안전한 경로 조합"""
        try:
            # Windows OneDrive 경로에서 안전하게 경로 조합
            path = os.path.join(*args)
            # Windows에서 백슬래시를 슬래시로 정규화
            if os.name == 'nt':
                path = path.replace('\\', '/')
            return path
        except Exception as e:
            logger.error(f"❌ 경로 조합 오류 (인코딩 이슈 가능): {e}")
            logger.error(f"입력값: {args}")
            raise ValueError(f"경로 조합 실패 - Windows/OneDrive 인코딩 문제 가능: {e}")

    @staticmethod
    def safe_file_read(file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """인코딩 안전한 파일 읽기"""
        try:
            # Path 객체를 문자열로 변환
            if isinstance(file_path, Path):
                file_path = str(file_path)
            
            # 경로 정규화
            file_path = os.path.normpath(file_path)
            
            # UTF-8 우선, 실패시 fallback 인코딩들 시도
            encodings = [encoding, "utf-8", "cp949", "euc-kr", "latin-1"]
            
            for enc in encodings:
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    logger.info(f"✅ 파일 읽기 성공 (인코딩: {enc}): {file_path}")
                    return content
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ 파일 읽기 실패 (인코딩: {enc}): {e}")
                    continue
            
            raise ValueError(f"모든 인코딩 시도 실패: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 파일 읽기 오류 - Windows/OneDrive 인코딩 문제 가능: {e}")
            logger.error(f"파일 경로: {file_path}")
            raise

    @staticmethod
    def safe_file_write(file_path: Union[str, Path], content: str, encoding: str = "utf-8") -> bool:
        """인코딩 안전한 파일 쓰기"""
        try:
            # Path 객체를 문자열로 변환
            if isinstance(file_path, Path):
                file_path = str(file_path)
            
            # 경로 정규화
            file_path = os.path.normpath(file_path)
            
            # 디렉토리 생성 (존재하지 않는 경우)
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"📁 디렉토리 생성: {dir_path}")
            
            # UTF-8로 파일 쓰기
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"✅ 파일 쓰기 성공 (인코딩: {encoding}): {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 쓰기 오류 - Windows/OneDrive 인코딩 문제 가능: {e}")
            logger.error(f"파일 경로: {file_path}")
            logger.error(f"내용 길이: {len(content) if content else 0}")
            return False

    @staticmethod
    def safe_exists_check(file_path: Union[str, Path]) -> bool:
        """인코딩 안전한 파일 존재 확인"""
        try:
            # Path 객체를 문자열로 변환
            if isinstance(file_path, Path):
                file_path = str(file_path)
            
            # 경로 정규화
            file_path = os.path.normpath(file_path)
            
            exists = os.path.exists(file_path)
            logger.debug(f"📁 파일 존재 확인: {file_path} → {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"❌ 파일 존재 확인 오류 - Windows/OneDrive 인코딩 문제 가능: {e}")
            logger.error(f"파일 경로: {file_path}")
            return False

    @staticmethod
    def get_safe_base_dir() -> str:
        """인코딩 안전한 기본 디렉토리 경로"""
        try:
            # 현재 파일의 상위 디렉토리들을 찾아서 프로젝트 루트 결정
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            
            # airiss_v4 폴더를 찾을 때까지 상위로 이동
            max_depth = 5
            for _ in range(max_depth):
                if os.path.basename(current_dir).lower() in ['airiss_v4', 'airiss', 'app']:
                    if os.path.basename(current_dir).lower() == 'app':
                        # app 폴더인 경우 한 단계 위로
                        current_dir = os.path.dirname(current_dir)
                    break
                parent_dir = os.path.dirname(current_dir)
                if parent_dir == current_dir:  # 루트에 도달
                    break
                current_dir = parent_dir
            
            logger.info(f"🏠 프로젝트 기본 디렉토리: {current_dir}")
            return current_dir
            
        except Exception as e:
            logger.error(f"❌ 기본 디렉토리 확인 오류: {e}")
            # fallback: 현재 작업 디렉토리
            return os.getcwd()

    @staticmethod
    def log_encoding_info():
        """현재 인코딩 정보 로깅"""
        try:
            logger.info("🔤 현재 인코딩 설정:")
            logger.info(f"  - 기본 인코딩: {sys.getdefaultencoding()}")
            logger.info(f"  - 파일시스템 인코딩: {sys.getfilesystemencoding()}")
            logger.info(f"  - OS: {os.name}")
            logger.info(f"  - 플랫폼: {sys.platform}")
            
            if hasattr(sys, 'stdout') and hasattr(sys.stdout, 'encoding'):
                logger.info(f"  - stdout 인코딩: {sys.stdout.encoding}")
            
        except Exception as e:
            logger.error(f"❌ 인코딩 정보 수집 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    utils = EncodingSafeUtils()
    
    # 인코딩 정보 출력
    utils.log_encoding_info()
    
    # 기본 디렉토리 확인
    base_dir = utils.get_safe_base_dir()
    print(f"Base directory: {base_dir}")
    
    # 경로 조합 테스트
    try:
        test_path = utils.safe_path_join(base_dir, "uploads", "test.txt")
        print(f"Test path: {test_path}")
        
        # 파일 존재 확인 테스트
        exists = utils.safe_exists_check(test_path)
        print(f"File exists: {exists}")
        
    except Exception as e:
        print(f"Error: {e}")
