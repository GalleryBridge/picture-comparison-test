"""
核心比对引擎模块

包含PDF图纸比对的核心引擎和配置。
"""

from .comparison_engine import PDFComparisonEngine, ComparisonConfig, ComparisonMode, OutputFormat, ComparisonResult

__all__ = ["PDFComparisonEngine", "ComparisonConfig", "ComparisonMode", "OutputFormat", "ComparisonResult"]
