"""
API模块

提供PDF比对系统的RESTful API接口。
"""

from .models import (
    ComparisonRequest, ComparisonResponse, ComparisonStatus,
    HighlightRequest, HighlightResponse, RenderRequest, RenderResponse,
    ReportRequest, ReportResponse, HealthResponse, ErrorResponse
)
from .endpoints import router

__all__ = [
    "ComparisonRequest", "ComparisonResponse", "ComparisonStatus",
    "HighlightRequest", "HighlightResponse", "RenderRequest", "RenderResponse", 
    "ReportRequest", "ReportResponse", "HealthResponse", "ErrorResponse",
    "router"
]
