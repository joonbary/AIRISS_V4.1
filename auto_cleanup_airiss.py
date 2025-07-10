# -*- coding: utf-8 -*-
"""
AIRISS v4.1 자동 정리 스크립트
Windows/OneDrive 인코딩 안전 모드
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cleanup_log.txt', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class AirissProjectCleaner:
    """AIRISS v4.1 프로젝트 자동 정리"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.backup_dir = self.project_path / "cleanup_backup"
        self.stats = {
            "files_removed": 0,
            "dirs_removed": 0,
            "files_backed_up": 0,
            "bytes_saved": 0
        }
        
        logger.info(f"🧹 AIRISS v4.1 프로젝트 정리 시작: {self.project_path}")
    
    def get_safe_removal_patterns(self) -> Dict[str, List[str]]:
        """안전하게 제거할 수 있는 파일/폴더 패턴들"""
        return {
            # 임시 배치 파일들
            "temp_batch_files": [
                "*.bat",
                "*_fix.bat", 
                "*_deploy.bat",
                "*emergency*.bat",
                "*_safe.bat",
                "*_test*.bat",
                "quick_*.bat",
                "ultra_*.bat",
                "nuclear_*.bat"
            ],
            
            # 임시 Python 스크립트들
            "temp_python_files": [
                "*emergency*.py",
                "*diagnosis*.py", 
                "*_test*.py",
                "*debug*.py",
                "simple_*.py",
                "*_backup*.py",
                "cleanup_*.py"
            ],
            
            # 설정 백업 파일들
            "config_backups": [
                "*.json.backup",
                "*.json.broken", 
                "Dockerfile_*",
                "Dockerfile.*",
                "vercel_*.json",
                "railway.json.*"
            ],
            
            # 로그 및 임시 파일들
            "logs_and_temp": [
                "*.log",
                "*.tmp",
                "*.temp",
                "*_LOG.txt",
                "manual_commands.txt",
                "MANUAL_*.txt"
            ],
            
            # 임시 디렉토리들
            "temp_directories": [
                "__pycache__",
                "venv_backup",
                "venv_new", 
                "cleanup_backup",
                ".pytest_cache",
                "test_data"
            ],
            
            # 문서 백업들
            "doc_backups": [
                "*_BACKUP*.md",
                "*_OLD*.md", 
                "*_TEMP*.md",
                "CLEANUP_*.md",
                "CRITICAL_*.md",
                "EMERGENCY_*.md"
            ]
        }
    
    def get_keep_patterns(self) -> List[str]:
        """반드시 보존해야 할 파일/폴더 패턴들"""
        return [
            # 핵심 애플리케이션 파일들
            "app/",
            "airiss-v4-frontend/", 
            "frontend/",
            "static/",
            
            # 핵심 설정 파일들
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "package.json",
            "railway.json",
            
            # 환경 설정
            ".env",
            ".env.example",
            ".gitignore",
            
            # Git 관련
            ".git/",
            ".github/",
            
            # 문서 (메인)
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            
            # 데이터베이스
            "*.db",
            "alembic/",
            
            # 업로드 폴더
            "uploads/",
            
            # Node modules (크지만 필요)
            "node_modules/",
            
            # 테스트 (핵심)
            "tests/"
        ]
    
    def create_backup_dir(self):
        """백업 디렉토리 생성"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 백업 디렉토리 생성: {self.backup_dir}")
            else:
                logger.info(f"📁 기존 백업 디렉토리 사용: {self.backup_dir}")
        except Exception as e:
            logger.error(f"❌ 백업 디렉토리 생성 실패: {e}")
            raise
    
    def should_keep_file(self, file_path: Path) -> bool:
        """파일을 보존해야 하는지 확인"""
        try:
            relative_path = file_path.relative_to(self.project_path)
            relative_str = str(relative_path).replace('\\', '/')
            
            # 보존 패턴 확인
            keep_patterns = self.get_keep_patterns()
            for pattern in keep_patterns:
                if pattern.endswith('/'):
                    # 디렉토리 패턴
                    if relative_str.startswith(pattern.rstrip('/')):
                        return True
                else:
                    # 파일 패턴
                    if relative_str == pattern or relative_str.endswith('/' + pattern):
                        return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ 파일 보존 확인 오류: {file_path} - {e}")
            return True  # 오류시 안전하게 보존
    
    def should_remove_file(self, file_path: Path) -> bool:
        """파일을 제거해야 하는지 확인"""
        try:
            relative_path = file_path.relative_to(self.project_path)
            relative_str = str(relative_path).replace('\\', '/')
            filename = file_path.name
            
            # 제거 패턴 확인
            removal_patterns = self.get_safe_removal_patterns()
            
            for category, patterns in removal_patterns.items():
                for pattern in patterns:
                    # 와일드카드 패턴 매칭
                    if '*' in pattern:
                        if pattern.startswith('*') and filename.endswith(pattern[1:]):
                            return True
                        if pattern.endswith('*') and filename.startswith(pattern[:-1]):
                            return True
                        if '*' in pattern and pattern.replace('*', '') in filename:
                            return True
                    else:
                        # 정확한 매칭
                        if filename == pattern or relative_str == pattern:
                            return True
            
            return False
            
        except Exception as e:
            logger.warning(f"⚠️ 파일 제거 확인 오류: {file_path} - {e}")
            return False  # 오류시 안전하게 보존
    
    def backup_file(self, file_path: Path) -> bool:
        """파일을 백업 디렉토리로 이동"""
        try:
            relative_path = file_path.relative_to(self.project_path)
            backup_path = self.backup_dir / relative_path
            
            # 백업 디렉토리 생성
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 파일 이동 (또는 복사)
            if file_path.is_file():
                file_size = file_path.stat().st_size
                shutil.move(str(file_path), str(backup_path))
                self.stats["files_backed_up"] += 1
                self.stats["bytes_saved"] += file_size
                logger.debug(f"📦 파일 백업: {relative_path} ({file_size} bytes)")
                return True
            elif file_path.is_dir():
                shutil.move(str(file_path), str(backup_path))
                self.stats["dirs_removed"] += 1
                logger.debug(f"📦 디렉토리 백업: {relative_path}")
                return True
                
        except Exception as e:
            logger.error(f"❌ 백업 실패: {file_path} - {e}")
            return False
    
    def remove_file_safely(self, file_path: Path) -> bool:
        """파일을 안전하게 제거 (백업 후 삭제)"""
        try:
            if self.backup_file(file_path):
                self.stats["files_removed"] += 1
                logger.info(f"🗑️ 제거됨: {file_path.relative_to(self.project_path)}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ 파일 제거 실패: {file_path} - {e}")
            return False
    
    def scan_and_clean(self, dry_run: bool = True) -> Dict:
        """프로젝트 스캔 및 정리"""
        logger.info(f"🔍 프로젝트 스캔 시작 (dry_run: {dry_run})")
        
        if not dry_run:
            self.create_backup_dir()
        
        files_to_remove = []
        dirs_to_remove = []
        total_size = 0
        
        try:
            # 모든 파일/디렉토리 스캔
            for item in self.project_path.rglob("*"):
                try:
                    # 백업 디렉토리는 제외
                    if self.backup_dir in item.parents or item == self.backup_dir:
                        continue
                    
                    # .git 디렉토리는 제외
                    if ".git" in item.parts:
                        continue
                    
                    # 보존해야 할 파일인지 확인
                    if self.should_keep_file(item):
                        continue
                    
                    # 제거해야 할 파일인지 확인
                    if self.should_remove_file(item):
                        if item.is_file():
                            file_size = item.stat().st_size
                            files_to_remove.append((item, file_size))
                            total_size += file_size
                        elif item.is_dir():
                            # 빈 디렉토리이거나 제거 대상 파일들만 있는 경우
                            dirs_to_remove.append(item)
                
                except Exception as e:
                    logger.warning(f"⚠️ 항목 스캔 오류: {item} - {e}")
                    continue
        
        except Exception as e:
            logger.error(f"❌ 프로젝트 스캔 실패: {e}")
            return {"error": str(e)}
        
        # 결과 요약
        summary = {
            "total_files_to_remove": len(files_to_remove),
            "total_dirs_to_remove": len(dirs_to_remove), 
            "total_size_mb": round(total_size / (1024*1024), 2),
            "files_to_remove": [str(f[0].relative_to(self.project_path)) for f in files_to_remove[:20]],  # 처음 20개만
            "dirs_to_remove": [str(d.relative_to(self.project_path)) for d in dirs_to_remove[:10]]   # 처음 10개만
        }
        
        if dry_run:
            logger.info(f"📊 정리 예상 결과:")
            logger.info(f"  - 제거할 파일: {summary['total_files_to_remove']}개")
            logger.info(f"  - 제거할 디렉토리: {summary['total_dirs_to_remove']}개") 
            logger.info(f"  - 절약될 용량: {summary['total_size_mb']} MB")
            return summary
        
        # 실제 정리 실행
        logger.info(f"🧹 실제 정리 시작...")
        
        # 파일들 제거
        for file_path, file_size in files_to_remove:
            self.remove_file_safely(file_path)
        
        # 빈 디렉토리들 제거
        for dir_path in dirs_to_remove:
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    self.backup_file(dir_path)
            except Exception as e:
                logger.warning(f"⚠️ 디렉토리 제거 실패: {dir_path} - {e}")
        
        # 최종 통계
        final_stats = {
            **summary,
            "actual_files_removed": self.stats["files_removed"],
            "actual_dirs_removed": self.stats["dirs_removed"],
            "files_backed_up": self.stats["files_backed_up"],
            "bytes_saved": self.stats["bytes_saved"],
            "backup_location": str(self.backup_dir)
        }
        
        logger.info(f"✅ 정리 완료!")
        logger.info(f"  - 제거된 파일: {final_stats['actual_files_removed']}개")
        logger.info(f"  - 제거된 디렉토리: {final_stats['actual_dirs_removed']}개")
        logger.info(f"  - 백업된 파일: {final_stats['files_backed_up']}개")
        logger.info(f"  - 절약된 용량: {round(final_stats['bytes_saved']/(1024*1024), 2)} MB")
        logger.info(f"  - 백업 위치: {final_stats['backup_location']}")
        
        return final_stats

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIRISS v4.1 프로젝트 자동 정리")
    parser.add_argument("--path", default=".", help="프로젝트 경로 (기본: 현재 디렉토리)")
    parser.add_argument("--dry-run", action="store_true", help="실제 삭제 없이 미리보기만")
    parser.add_argument("--force", action="store_true", help="확인 없이 바로 실행")
    
    args = parser.parse_args()
    
    try:
        # 프로젝트 경로 확인
        project_path = Path(args.path).resolve()
        if not project_path.exists():
            logger.error(f"❌ 프로젝트 경로가 존재하지 않습니다: {project_path}")
            return
        
        logger.info(f"🎯 AIRISS v4.1 프로젝트 정리 도구")
        logger.info(f"📁 대상 경로: {project_path}")
        
        # 정리 도구 생성
        cleaner = AirissProjectCleaner(str(project_path))
        
        # dry-run 먼저 실행
        if args.dry_run:
            logger.info("🔍 미리보기 모드로 실행...")
            result = cleaner.scan_and_clean(dry_run=True)
            print("\n📋 정리 예상 결과:")
            print(f"제거할 파일: {result['total_files_to_remove']}개")
            print(f"제거할 디렉토리: {result['total_dirs_to_remove']}개")
            print(f"절약될 용량: {result['total_size_mb']} MB")
            
            if result['files_to_remove']:
                print(f"\n제거될 파일 예시 (처음 20개):")
                for f in result['files_to_remove']:
                    print(f"  - {f}")
            
            print(f"\n실제 정리를 원하면 --force 옵션을 추가하세요.")
            return
        
        # 실제 정리 실행
        if not args.force:
            # 사용자 확인
            answer = input(f"\n⚠️ {project_path}의 임시 파일들을 정리하시겠습니까? (y/N): ")
            if answer.lower() != 'y':
                logger.info("🚫 정리가 취소되었습니다.")
                return
        
        logger.info("🧹 정리를 시작합니다...")
        result = cleaner.scan_and_clean(dry_run=False)
        
        print(f"\n✅ 정리 완료!")
        print(f"제거된 파일: {result['actual_files_removed']}개")
        print(f"절약된 용량: {round(result['bytes_saved']/(1024*1024), 2)} MB")
        print(f"백업 위치: {result['backup_location']}")
        
    except KeyboardInterrupt:
        logger.info("🚫 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"❌ 정리 도구 실행 오류: {e}")
        raise

if __name__ == "__main__":
    main()
