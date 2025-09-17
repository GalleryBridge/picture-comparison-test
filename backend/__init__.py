"""
PDF图纸比对模块

基于传统算法的PDF图纸比对系统，实现工业级精度的矢量图元比对。

核心流程:
输入PDF → 矢量解析 → 坐标标准化 → 图元匹配 → 差异输出
"""

__version__ = "1.0.0"
__author__ = "PDF Comparison Team"

from .core.comparison_engine import PDFComparisonEngine, ComparisonConfig, ComparisonMode, OutputFormat, ComparisonResult

__all__ = ["PDFComparisonEngine", "ComparisonConfig", "ComparisonMode", "OutputFormat", "ComparisonResult"]
