#!/usr/bin/env python3
"""
AIRISS v4 백업 및 정리 스크립트
Phase 1: 전체 백업 후 불필요한 파일 제거
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
import json

class BackupAndCleanup:
    def __init__(self):
        self.project_root = Path("C:/Users/apro/OneDrive/Desktop/AIRISS/airiss_v4")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.project_root.parent / f"airiss_v4_backup_{self.timestamp}"
        
        # 삭제할 파일 패턴
        self.files_to_delete = [
            # 중복 메인 파일들
            "app/main_complex.py",
            "app/main_no_sqlalchemy.py",
            "app/main_smart.py",
            "app/main_sqlalchemy_issue.py",
            "application.py",
            "simple_server.py",
            
            # 중복 테스트 파일들
            "test_*.py",
            "integration_test*.py",
            "debug_*.py",
            "check_*.py",
            "verify_*.py",
            
            # 임시 파일들
            "*.bat",
            "*.bak",
            "*.tmp",
            "*.log",
            
            # 백업 파일들
            "*_backup.py",
            "*_old.py",
            "*_temp.py",
        ]
        
        # 정리할 디렉토리
        self.dirs_to_clean = [
            "uploads/",  # 테스트 업로드 파일들
            ".cleanup/",  # 임시 정리 폴더
        ]
        
        # 보존할 중요 파일들
        self.keep_files = [
            "app/main.py",
            "app/api/v1/api.py",
            "app/db/__init__.py",
            "app/core/config.py",
            "app/services/hybrid_analyzer.py",
            "requirements.txt",
            ".env.example",
            "alembic.ini",
        ]

    def backup_project(self):
        """프로젝트 전체 백업"""
        print(f"[BACKUP] 백업 시작: {self.backup_dir}")
        
        # .git 폴더 제외하고 백업
        def ignore_patterns(path, names):
            return ['.git', '__pycache__', '*.pyc', '.pytest_cache', 'node_modules']
        
        shutil.copytree(
            self.project_root,
            self.backup_dir,
            ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '.pytest_cache', 'node_modules')
        )
        
        print(f"[COMPLETE] 백업 완료: {self.backup_dir}")
        
        # 백업 정보 저장
        backup_info = {
            "timestamp": self.timestamp,
            "backup_dir": str(self.backup_dir),
            "original_dir": str(self.project_root),
            "files_backed_up": len(list(self.backup_dir.rglob("*")))
        }
        
        with open(self.backup_dir / "backup_info.json", "w", encoding="utf-8") as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)

    def clean_duplicate_files(self):
        """중복 파일 제거"""
        print("\n[CLEANUP] 중복 파일 정리 시작")
        
        removed_count = 0
        
        for pattern in self.files_to_delete:
            for file_path in self.project_root.glob(f"**/{pattern}"):
                # 보존할 파일인지 확인
                relative_path = file_path.relative_to(self.project_root).as_posix()
                if relative_path in self.keep_files:
                    continue
                
                try:
                    if file_path.is_file():
                        print(f"  삭제: {relative_path}")
                        file_path.unlink()
                        removed_count += 1
                except Exception as e:
                    print(f"  [WARNING] 삭제 실패: {relative_path} - {e}")
        
        print(f"[COMPLETE] {removed_count}개 파일 삭제 완료")

    def clean_directories(self):
        """불필요한 디렉토리 정리"""
        print("\n[DIRECTORY] 디렉토리 정리 시작")
        
        for dir_pattern in self.dirs_to_clean:
            dir_path = self.project_root / dir_pattern
            if dir_path.exists() and dir_path.is_dir():
                try:
                    # uploads 폴더는 내용만 삭제
                    if dir_pattern == "uploads/":
                        for item in dir_path.iterdir():
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        print(f"  [OK] {dir_pattern} 내용 삭제 완료")
                    else:
                        # 다른 폴더는 전체 삭제
                        shutil.rmtree(dir_path)
                        print(f"  [OK] {dir_pattern} 폴더 삭제 완료")
                except Exception as e:
                    print(f"  [WARNING] 정리 실패: {dir_pattern} - {e}")

    def create_new_structure(self):
        """새로운 디렉토리 구조 생성"""
        print("\n[CREATE] 새로운 디렉토리 구조 생성")
        
        new_dirs = [
            "backend/app/api/v1",
            "backend/app/core",
            "backend/app/models",
            "backend/app/schemas",
            "backend/app/services",
            "backend/app/db/repositories",
            "backend/migrations/versions",
            "backend/tests/unit",
            "backend/tests/integration",
            "backend/tests/e2e",
            "backend/scripts",
            "docs",
        ]
        
        for dir_path in new_dirs:
            full_path = self.project_root.parent / "airiss_v4_refactored" / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            # __init__.py 생성
            init_file = full_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
        
        print("[COMPLETE] 새로운 디렉토리 구조 생성 완료")

    def generate_cleanup_report(self):
        """정리 리포트 생성"""
        report_path = self.project_root / "cleanup_report.json"
        
        # 현재 파일 통계
        current_files = list(self.project_root.rglob("*.py"))
        
        report = {
            "timestamp": self.timestamp,
            "backup_location": str(self.backup_dir),
            "statistics": {
                "python_files": len(current_files),
                "total_files": len(list(self.project_root.rglob("*"))),
                "directories": len([p for p in self.project_root.rglob("*") if p.is_dir()]),
            },
            "cleaned_patterns": self.files_to_delete,
            "cleaned_directories": self.dirs_to_clean,
        }
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n[REPORT] 정리 리포트 생성: {report_path}")

    def run(self):
        """전체 백업 및 정리 프로세스 실행"""
        print("[START] AIRISS v4 백업 및 정리 시작\n")
        
        # 1. 백업
        self.backup_project()
        
        # 2. 중복 파일 제거
        self.clean_duplicate_files()
        
        # 3. 디렉토리 정리
        self.clean_directories()
        
        # 4. 새 구조 생성
        self.create_new_structure()
        
        # 5. 리포트 생성
        self.generate_cleanup_report()
        
        print("\n[DONE] 백업 및 정리 완료!")
        print(f"백업 위치: {self.backup_dir}")
        print("\n다음 단계: Phase 2 - 데이터베이스 레이어 통합")


if __name__ == "__main__":
    cleanup = BackupAndCleanup()
    cleanup.run()