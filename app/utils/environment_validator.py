"""
환경 변수 및 외부 API 검증 유틸리티
"""
import os
import logging
import asyncio
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import aiohttp
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """환경 설정 검증기"""
    
    def __init__(self):
        load_dotenv()  # .env 파일 로드
        self.validation_results = {}
        
    async def validate_all(self) -> Dict:
        """모든 환경 설정 검증"""
        logger.info("Starting environment validation...")
        
        # 검증 항목들
        validations = [
            self._validate_required_env_vars(),
            self._validate_openai_api(),
            self._validate_database_connection(),
            self._validate_file_directories(),
            self._validate_external_services()
        ]
        
        # 비동기 실행
        results = await asyncio.gather(*validations, return_exceptions=True)
        
        # 결과 종합
        all_valid = True
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Validation error: {result}")
                all_valid = False
            elif isinstance(result, dict) and not result.get('valid', False):
                all_valid = False
                
        self.validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'all_valid': all_valid,
            'details': {
                'env_vars': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
                'openai_api': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
                'database': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
                'directories': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
                'external_services': results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])}
            }
        }
        
        return self.validation_results
        
    async def _validate_required_env_vars(self) -> Dict:
        """필수 환경 변수 검증"""
        required_vars = {
            'OPENAI_API_KEY': {
                'description': 'OpenAI API key for LLM analysis',
                'pattern': 'sk-',
                'optional': False
            },
            'DATABASE_URL': {
                'description': 'Database connection string',
                'pattern': None,
                'optional': False
            },
            'SECRET_KEY': {
                'description': 'JWT secret key',
                'pattern': None,
                'optional': False
            },
            'REACT_APP_API_URL': {
                'description': 'Frontend API URL',
                'pattern': 'http',
                'optional': True
            }
        }
        
        results = {
            'valid': True,
            'missing': [],
            'invalid': [],
            'warnings': []
        }
        
        for var_name, config in required_vars.items():
            value = os.getenv(var_name)
            
            if not value:
                if not config['optional']:
                    results['missing'].append(var_name)
                    results['valid'] = False
                else:
                    results['warnings'].append(f"{var_name} is not set (optional)")
            elif config['pattern'] and config['pattern'] not in value:
                results['invalid'].append({
                    'name': var_name,
                    'reason': f"Does not contain expected pattern '{config['pattern']}'"
                })
                results['valid'] = False
                
        logger.info(f"Environment variables validation: {'PASSED' if results['valid'] else 'FAILED'}")
        return results
        
    async def _validate_openai_api(self) -> Dict:
        """OpenAI API 키 유효성 검증"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return {
                'valid': False,
                'error': 'OPENAI_API_KEY not set',
                'can_use_llm': False
            }
            
        try:
            # OpenAI API 키 형식 검증만 수행
            if api_key.startswith('sk-') and len(api_key) > 20:
                return {
                    'valid': True,
                    'can_use_llm': True,
                    'key_prefix': api_key[:10] + '...',
                    'note': 'Key format valid (actual API call skipped)'
                }
            else:
                return {
                    'valid': False,
                    'error': 'Invalid key format',
                    'can_use_llm': False,
                    'key_prefix': api_key[:10] + '...' if api_key else None
                }
            
        except Exception as e:
            logger.error(f"OpenAI API validation error: {e}")
            return {
                'valid': False,
                'error': str(e),
                'can_use_llm': False
            }
            
    async def _validate_database_connection(self) -> Dict:
        """데이터베이스 연결 검증"""
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError
        
        db_url = os.getenv('DATABASE_URL')
        
        if not db_url:
            return {
                'valid': False,
                'error': 'DATABASE_URL not set'
            }
            
        try:
            # 연결 테스트
            engine = create_engine(db_url)
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                
            # 테이블 존재 확인
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            return {
                'valid': True,
                'database_type': 'postgresql' if 'postgresql' in db_url else 'sqlite',
                'tables_count': len(tables),
                'tables': tables[:10]  # 처음 10개만
            }
            
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            return {
                'valid': False,
                'error': 'Connection failed',
                'details': str(e)
            }
            
        except Exception as e:
            logger.error(f"Database validation error: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
            
    async def _validate_file_directories(self) -> Dict:
        """필수 디렉토리 검증 및 생성"""
        required_dirs = {
            'uploads': 'File upload directory',
            'results': 'Analysis results directory',
            'downloads': 'Download files directory',
            'logs': 'Log files directory',
            'temp': 'Temporary files directory'
        }
        
        results = {
            'valid': True,
            'created': [],
            'errors': []
        }
        
        for dir_name, description in required_dirs.items():
            dir_path = Path(dir_name)
            
            try:
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    results['created'].append(dir_name)
                    logger.info(f"Created directory: {dir_name}")
                    
                # 쓰기 권한 확인
                test_file = dir_path / '.write_test'
                test_file.write_text('test')
                test_file.unlink()
                
            except Exception as e:
                results['errors'].append({
                    'directory': dir_name,
                    'error': str(e)
                })
                results['valid'] = False
                logger.error(f"Directory validation failed for {dir_name}: {e}")
                
        return results
        
    async def _validate_external_services(self) -> Dict:
        """외부 서비스 연결 확인"""
        results = {
            'valid': True,
            'services': {}
        }
        
        # MCP 서버 확인 (있는 경우)
        mcp_url = os.getenv('MCP_SERVER_URL')
        if mcp_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{mcp_url}/health", timeout=5) as response:
                        if response.status == 200:
                            results['services']['mcp'] = {
                                'status': 'healthy',
                                'url': mcp_url
                            }
                        else:
                            results['services']['mcp'] = {
                                'status': 'unhealthy',
                                'http_status': response.status
                            }
                            results['valid'] = False
                            
            except Exception as e:
                results['services']['mcp'] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
                results['valid'] = False
                
        return results
        
    def get_validation_report(self) -> str:
        """검증 결과 리포트 생성"""
        if not self.validation_results:
            return "No validation results available. Run validate_all() first."
            
        report = []
        report.append("="*60)
        report.append("ENVIRONMENT VALIDATION REPORT")
        report.append("="*60)
        report.append(f"Timestamp: {self.validation_results['timestamp']}")
        report.append(f"Overall Status: {'PASSED' if self.validation_results['all_valid'] else 'FAILED'}")
        report.append("")
        
        details = self.validation_results['details']
        
        # 환경 변수
        report.append("1. Environment Variables:")
        env_vars = details.get('env_vars', {})
        if env_vars.get('missing'):
            report.append(f"   - Missing: {', '.join(env_vars['missing'])}")
        if env_vars.get('invalid'):
            report.append(f"   - Invalid: {len(env_vars['invalid'])} variables")
        if env_vars.get('valid'):
            report.append("   - Status: OK")
            
        # OpenAI API
        report.append("\n2. OpenAI API:")
        openai_status = details.get('openai_api', {})
        if openai_status.get('valid'):
            report.append(f"   - Status: OK")
            report.append(f"   - Key: {openai_status.get('key_prefix', 'N/A')}")
        else:
            report.append(f"   - Status: FAILED")
            report.append(f"   - Error: {openai_status.get('error', 'Unknown')}")
            
        # 데이터베이스
        report.append("\n3. Database:")
        db_status = details.get('database', {})
        if db_status.get('valid'):
            report.append(f"   - Status: OK")
            report.append(f"   - Type: {db_status.get('database_type', 'Unknown')}")
            report.append(f"   - Tables: {db_status.get('tables_count', 0)}")
        else:
            report.append(f"   - Status: FAILED")
            report.append(f"   - Error: {db_status.get('error', 'Unknown')}")
            
        # 디렉토리
        report.append("\n4. Directories:")
        dir_status = details.get('directories', {})
        if dir_status.get('created'):
            report.append(f"   - Created: {', '.join(dir_status['created'])}")
        if dir_status.get('errors'):
            report.append(f"   - Errors: {len(dir_status['errors'])}")
            
        # 외부 서비스
        report.append("\n5. External Services:")
        services = details.get('external_services', {}).get('services', {})
        if services:
            for service_name, status in services.items():
                report.append(f"   - {service_name}: {status.get('status', 'Unknown')}")
        else:
            report.append("   - No external services configured")
            
        report.append("\n" + "="*60)
        
        return "\n".join(report)

# 전역 검증기 인스턴스
_validator = None

def get_validator() -> EnvironmentValidator:
    """싱글톤 검증기 인스턴스 반환"""
    global _validator
    if _validator is None:
        _validator = EnvironmentValidator()
    return _validator
    
async def validate_environment() -> bool:
    """환경 검증 실행 (간단한 인터페이스)"""
    validator = get_validator()
    results = await validator.validate_all()
    
    if not results['all_valid']:
        logger.error("Environment validation failed!")
        print(validator.get_validation_report())
        
    return results['all_valid']