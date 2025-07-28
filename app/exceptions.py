"""
AIRISS v4.0 Custom Exceptions
서비스 레이어 에러 처리를 위한 커스텀 예외 클래스
"""


class AnalysisError(Exception):
    """분석 서비스 관련 에러"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class FileProcessingError(AnalysisError):
    """파일 처리 관련 에러"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class ValidationError(AnalysisError):
    """데이터 검증 관련 에러"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class ResourceNotFoundError(AnalysisError):
    """리소스를 찾을 수 없는 경우"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)


class InternalServiceError(AnalysisError):
    """내부 서비스 에러"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)