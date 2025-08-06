# app/api/v1/endpoints/__init__.py
"""
AIRISS v4.0 API 엔드포인트 모듈
"""

from . import analysis, analysis_opinion, employee, analysis_opinion_simple, config

__all__ = ["analysis", "analysis_opinion", "employee", "analysis_opinion_simple", "config"]