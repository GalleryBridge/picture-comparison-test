"""
API数据模型

定义API请求和响应的数据结构。
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
from datetime import datetime

from ..comparison_engine import ComparisonMode, OutputFormat
from ..matching.similarity_calculator import SimilarityMethod
from ..visualization.pdf_highlighter import HighlightStyle
from ..visualization.diff_renderer import RenderFormat, ChartType
from ..visualization.report_generator import ReportFormat, ReportLevel


class ComparisonStatus(str, Enum):
    """比对状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ComparisonRequest(BaseModel):
    """比对请求"""
    file_a_path: str = Field(..., description="文件A路径")
    file_b_path: str = Field(..., description="文件B路径")
    mode: ComparisonMode = Field(ComparisonMode.STANDARD, description="比对模式")
    similarity_method: SimilarityMethod = Field(SimilarityMethod.WEIGHTED_COMBINED, description="相似度计算方法")
    tolerance_preset: str = Field("standard", description="容差预设")
    custom_tolerance: Optional[Dict[str, float]] = Field(None, description="自定义容差参数")
    output_formats: List[OutputFormat] = Field([OutputFormat.JSON], description="输出格式")
    include_visualization: bool = Field(True, description="是否包含可视化")
    include_report: bool = Field(False, description="是否包含报告")
    
    @validator('file_a_path', 'file_b_path')
    def validate_file_paths(cls, v):
        if not v or not v.strip():
            raise ValueError('文件路径不能为空')
        return v.strip()
    
    @validator('tolerance_preset')
    def validate_tolerance_preset(cls, v):
        allowed_presets = ['ultra_high', 'high', 'standard', 'loose']
        if v not in allowed_presets:
            raise ValueError(f'容差预设必须是: {", ".join(allowed_presets)}')
        return v


class ComparisonResponse(BaseModel):
    """比对响应"""
    comparison_id: str = Field(..., description="比对ID")
    status: ComparisonStatus = Field(..., description="比对状态")
    timestamp: datetime = Field(..., description="时间戳")
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")
    
    # 比对结果
    success: bool = Field(False, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 统计信息
    elements_a_count: Optional[int] = Field(None, description="文件A图元数量")
    elements_b_count: Optional[int] = Field(None, description="文件B图元数量")
    matched_pairs: Optional[int] = Field(None, description="匹配对数")
    average_similarity: Optional[float] = Field(None, description="平均相似度")
    total_differences: Optional[int] = Field(None, description="总差异数")
    change_rate: Optional[float] = Field(None, description="变化率")
    
    # 输出文件
    output_files: Dict[str, str] = Field(default_factory=dict, description="输出文件路径")
    
    # 原始数据
    raw_data: Optional[Dict[str, Any]] = Field(None, description="原始比对数据")


class HighlightRequest(BaseModel):
    """高亮请求"""
    comparison_id: str = Field(..., description="比对ID")
    highlight_style: HighlightStyle = Field(HighlightStyle.SOLID, description="高亮样式")
    include_legend: bool = Field(True, description="是否包含图例")
    include_overlay: bool = Field(False, description="是否生成叠加图")
    output_path: Optional[str] = Field(None, description="输出路径")
    
    @validator('comparison_id')
    def validate_comparison_id(cls, v):
        if not v or not v.strip():
            raise ValueError('比对ID不能为空')
        return v.strip()


class HighlightResponse(BaseModel):
    """高亮响应"""
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    output_files: Dict[str, str] = Field(default_factory=dict, description="输出文件路径")
    processing_time: float = Field(..., description="处理时间(秒)")


class RenderRequest(BaseModel):
    """渲染请求"""
    comparison_id: str = Field(..., description="比对ID")
    chart_types: List[ChartType] = Field([ChartType.SUMMARY], description="图表类型")
    render_format: RenderFormat = Field(RenderFormat.PNG, description="渲染格式")
    output_path: Optional[str] = Field(None, description="输出路径")
    dpi: int = Field(300, description="图像DPI")
    
    @validator('comparison_id')
    def validate_comparison_id(cls, v):
        if not v or not v.strip():
            raise ValueError('比对ID不能为空')
        return v.strip()
    
    @validator('dpi')
    def validate_dpi(cls, v):
        if v < 72 or v > 600:
            raise ValueError('DPI必须在72-600之间')
        return v


class RenderResponse(BaseModel):
    """渲染响应"""
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    output_files: Dict[str, str] = Field(default_factory=dict, description="输出文件路径")
    processing_time: float = Field(..., description="处理时间(秒)")


class ReportRequest(BaseModel):
    """报告请求"""
    comparison_id: str = Field(..., description="比对ID")
    report_format: ReportFormat = Field(ReportFormat.EXCEL, description="报告格式")
    report_level: ReportLevel = Field(ReportLevel.DETAILED, description="报告级别")
    include_charts: bool = Field(True, description="是否包含图表")
    include_images: bool = Field(True, description="是否包含图像")
    include_raw_data: bool = Field(False, description="是否包含原始数据")
    custom_title: Optional[str] = Field(None, description="自定义标题")
    output_path: Optional[str] = Field(None, description="输出路径")
    
    @validator('comparison_id')
    def validate_comparison_id(cls, v):
        if not v or not v.strip():
            raise ValueError('比对ID不能为空')
        return v.strip()


class ReportResponse(BaseModel):
    """报告响应"""
    success: bool = Field(..., description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    output_files: Dict[str, str] = Field(default_factory=dict, description="输出文件路径")
    processing_time: float = Field(..., description="处理时间(秒)")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="服务版本")
    uptime: float = Field(..., description="运行时间(秒)")
    memory_usage: Dict[str, Any] = Field(..., description="内存使用情况")
    disk_usage: Dict[str, Any] = Field(..., description="磁盘使用情况")


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误信息")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")


class BatchComparisonRequest(BaseModel):
    """批量比对请求"""
    comparisons: List[ComparisonRequest] = Field(..., description="比对请求列表")
    max_concurrent: int = Field(3, description="最大并发数")
    
    @validator('comparisons')
    def validate_comparisons(cls, v):
        if not v or len(v) == 0:
            raise ValueError('比对请求列表不能为空')
        if len(v) > 10:
            raise ValueError('批量比对最多支持10个文件')
        return v
    
    @validator('max_concurrent')
    def validate_max_concurrent(cls, v):
        if v < 1 or v > 5:
            raise ValueError('最大并发数必须在1-5之间')
        return v


class BatchComparisonResponse(BaseModel):
    """批量比对响应"""
    batch_id: str = Field(..., description="批量比对ID")
    total_count: int = Field(..., description="总数量")
    completed_count: int = Field(..., description="已完成数量")
    failed_count: int = Field(..., description="失败数量")
    results: List[ComparisonResponse] = Field(..., description="比对结果列表")
    processing_time: float = Field(..., description="总处理时间(秒)")


class ComparisonListResponse(BaseModel):
    """比对列表响应"""
    comparisons: List[ComparisonResponse] = Field(..., description="比对列表")
    total_count: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


class ComparisonDeleteRequest(BaseModel):
    """删除比对请求"""
    comparison_ids: List[str] = Field(..., description="要删除的比对ID列表")
    
    @validator('comparison_ids')
    def validate_comparison_ids(cls, v):
        if not v or len(v) == 0:
            raise ValueError('比对ID列表不能为空')
        if len(v) > 50:
            raise ValueError('批量删除最多支持50个比对')
        return v


class ComparisonDeleteResponse(BaseModel):
    """删除比对响应"""
    success: bool = Field(..., description="是否成功")
    deleted_count: int = Field(..., description="删除数量")
    failed_ids: List[str] = Field(default_factory=list, description="删除失败的ID列表")
    error_message: Optional[str] = Field(None, description="错误信息")
