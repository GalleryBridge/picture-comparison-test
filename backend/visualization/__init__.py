"""
可视化输出模块

包含PDF高亮标注、差异渲染和报告生成等功能。
"""

from visualization.pdf_highlighter import PDFHighlighter, HighlightConfig, HighlightStyle
from visualization.diff_renderer import DiffRenderer, RenderConfig, RenderFormat, ChartType
from visualization.report_generator import ReportGenerator, ReportConfig, ReportFormat, ReportLevel

__all__ = ["PDFHighlighter", "HighlightConfig", "HighlightStyle", "DiffRenderer", "RenderConfig", "RenderFormat", "ChartType", "ReportGenerator", "ReportConfig", "ReportFormat", "ReportLevel"]
