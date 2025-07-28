"""
Configuration Management
환경별 설정 관리
"""

import os
from .base import Settings
from .development import DevelopmentSettings
from .production import ProductionSettings
from .testing import TestingSettings

# 환경 결정
ENV = os.getenv("ENVIRONMENT", "development").lower()

# 환경에 따른 설정 선택
if ENV == "production":
    settings = ProductionSettings()
elif ENV == "testing":
    settings = TestingSettings()
else:
    settings = DevelopmentSettings()

__all__ = ["settings"]