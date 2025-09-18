"""
API端点

定义RESTful API接口。
"""

import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi import status as http_status

from .models import (
    ComparisonRequest, ComparisonResponse, ComparisonStatus,
    HighlightRequest, HighlightResponse, RenderRequest, RenderResponse,
    ReportRequest, ReportResponse, HealthResponse, ErrorResponse,
    BatchComparisonRequest, BatchComparisonResponse, ComparisonListResponse,
    ComparisonDeleteRequest, ComparisonDeleteResponse
)
from .service import ComparisonService

# 创建路由器
router = APIRouter(prefix="/api/v1/pdf-comparison", tags=["PDF比对"])

# 全局服务实例
comparison_service = ComparisonService()


@router.post("/compare", response_model=ComparisonResponse, status_code=http_status.HTTP_201_CREATED)
async def compare_files(
    file_a: UploadFile = File(..., description="文件A"),
    file_b: UploadFile = File(..., description="文件B"),
    mode: str = Form("standard", description="比对模式"),
    similarity_method: str = Form("weighted_combined", description="相似度计算方法"),
    tolerance_preset: str = Form("standard", description="容差预设"),
    output_formats: str = Form("json", description="输出格式"),
    include_visualization: bool = Form(True, description="是否包含可视化"),
    include_report: bool = Form(False, description="是否包含报告")
):
    """
    执行PDF文件比对
    
    - **file_a**: 文件A
    - **file_b**: 文件B
    - **mode**: 比对模式 (standard/quick/precise)
    - **similarity_method**: 相似度计算方法
    - **tolerance_preset**: 容差预设 (ultra_high/high/standard/loose)
    - **output_formats**: 输出格式
    - **include_visualization**: 是否包含可视化
    - **include_report**: 是否包含报告
    """
    try:
        # 保存上传的文件
        upload_dir = comparison_service.output_dir / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        import uuid
        file_a_extension = os.path.splitext(file_a.filename)[1]
        file_b_extension = os.path.splitext(file_b.filename)[1]
        
        file_a_id = f"{uuid.uuid4().hex[:8]}{file_a_extension}"
        file_b_id = f"{uuid.uuid4().hex[:8]}{file_b_extension}"
        
        file_a_path = upload_dir / file_a_id
        file_b_path = upload_dir / file_b_id
        
        # 保存文件A
        with open(file_a_path, "wb") as buffer:
            content = await file_a.read()
            buffer.write(content)
        
        # 保存文件B
        with open(file_b_path, "wb") as buffer:
            content = await file_b.read()
            buffer.write(content)
        
        # 创建比对请求
        from .models import ComparisonRequest, OutputFormat
        request = ComparisonRequest(
            file_a_path=str(file_a_path),
            file_b_path=str(file_b_path),
            mode=mode,
            similarity_method=similarity_method,
            tolerance_preset=tolerance_preset,
            output_formats=[OutputFormat.JSON] if output_formats == "json" else [OutputFormat.JSON],
            include_visualization=include_visualization,
            include_report=include_report
        )
        
        # 异步执行比对，避免阻塞
        result = await comparison_service.compare_files(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"比对失败: {str(e)}"
        )


@router.post("/compare/batch", response_model=BatchComparisonResponse, status_code=http_status.HTTP_201_CREATED)
async def batch_compare(request: BatchComparisonRequest):
    """
    批量PDF文件比对
    
    - **comparisons**: 比对请求列表
    - **max_concurrent**: 最大并发数 (1-5)
    """
    try:
        result = await comparison_service.batch_compare(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量比对失败: {str(e)}"
        )


@router.get("/compare/{comparison_id}", response_model=ComparisonResponse)
async def get_comparison(comparison_id: str):
    """
    获取比对结果
    
    - **comparison_id**: 比对ID
    """
    result = comparison_service.get_comparison(comparison_id)
    if not result:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"比对ID不存在: {comparison_id}"
        )
    return result


@router.get("/compare", response_model=ComparisonListResponse)
async def list_comparisons(
    page: int = 1,
    page_size: int = 20
):
    """
    列出比对结果
    
    - **page**: 页码 (从1开始)
    - **page_size**: 每页大小 (1-100)
    """
    if page < 1:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="页码必须大于0"
        )
    
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="每页大小必须在1-100之间"
        )
    
    try:
        result = comparison_service.list_comparisons(page, page_size)
        return ComparisonListResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取比对列表失败: {str(e)}"
        )


@router.delete("/compare", response_model=ComparisonDeleteResponse)
async def delete_comparisons(request: ComparisonDeleteRequest):
    """
    删除比对结果
    
    - **comparison_ids**: 要删除的比对ID列表
    """
    try:
        result = comparison_service.delete_comparisons(request.comparison_ids)
        return ComparisonDeleteResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除比对失败: {str(e)}"
        )


@router.post("/highlight", response_model=HighlightResponse)
async def generate_highlight(request: HighlightRequest):
    """
    生成高亮PDF
    
    - **comparison_id**: 比对ID
    - **highlight_style**: 高亮样式
    - **include_legend**: 是否包含图例
    - **include_overlay**: 是否生成叠加图
    - **output_path**: 输出路径
    """
    try:
        result = await comparison_service.generate_highlight(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成高亮PDF失败: {str(e)}"
        )


@router.post("/render", response_model=RenderResponse)
async def generate_render(request: RenderRequest):
    """
    生成差异图像
    
    - **comparison_id**: 比对ID
    - **chart_types**: 图表类型列表
    - **render_format**: 渲染格式
    - **output_path**: 输出路径
    - **dpi**: 图像DPI (72-600)
    """
    try:
        result = await comparison_service.generate_render(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成差异图像失败: {str(e)}"
        )


@router.post("/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    生成报告
    
    - **comparison_id**: 比对ID
    - **report_format**: 报告格式 (excel/html/both)
    - **report_level**: 报告级别 (summary/detailed/comprehensive)
    - **include_charts**: 是否包含图表
    - **include_images**: 是否包含图像
    - **include_raw_data**: 是否包含原始数据
    - **custom_title**: 自定义标题
    - **output_path**: 输出路径
    """
    try:
        result = await comparison_service.generate_report(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成报告失败: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查
    
    返回服务状态、版本信息、运行时间、内存和磁盘使用情况。
    """
    try:
        result = comparison_service.get_health()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"健康检查失败: {str(e)}"
        )


@router.get("/files/{file_path:path}")
async def download_file(file_path: str):
    """
    下载文件
    
    - **file_path**: 文件路径
    """
    try:
        full_path = os.path.join(comparison_service.output_dir, file_path)
        
        if not os.path.exists(full_path):
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="文件不存在"
            )
        
        if not os.path.isfile(full_path):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="路径不是文件"
            )
        
        return FileResponse(
            path=full_path,
            filename=os.path.basename(full_path),
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载文件失败: {str(e)}"
        )


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件
    
    - **file**: 上传的文件
    """
    try:
        # 创建上传目录
        upload_dir = comparison_service.output_dir / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        # 生成唯一文件名
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "filename": file.filename,
            "saved_path": str(file_path),
            "file_size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败: {str(e)}"
        )


@router.get("/status/{comparison_id}")
async def get_comparison_status(comparison_id: str):
    """
    获取比对状态
    
    - **comparison_id**: 比对ID
    """
    result = comparison_service.get_comparison(comparison_id)
    if not result:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"比对ID不存在: {comparison_id}"
        )
    
    return {
        "comparison_id": comparison_id,
        "status": result.status,
        "success": result.success,
        "processing_time": result.processing_time,
        "error_message": result.error_message,
        "progress": result.processing_time / 300.0 if result.processing_time else 0.0  # 进度百分比
    }


@router.get("/statistics")
async def get_statistics():
    """
    获取统计信息
    
    返回系统统计信息，包括比对数量、成功率、平均处理时间等。
    """
    try:
        comparisons = list(comparison_service.comparisons.values())
        
        total_count = len(comparisons)
        completed_count = sum(1 for c in comparisons if c.status == ComparisonStatus.COMPLETED)
        failed_count = sum(1 for c in comparisons if c.status == ComparisonStatus.FAILED)
        processing_count = sum(1 for c in comparisons if c.status == ComparisonStatus.PROCESSING)
        
        success_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        processing_times = [c.processing_time for c in comparisons if c.processing_time is not None]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "total_comparisons": total_count,
            "completed_comparisons": completed_count,
            "failed_comparisons": failed_count,
            "processing_comparisons": processing_count,
            "success_rate": round(success_rate, 2),
            "average_processing_time": round(avg_processing_time, 4),
            "uptime": time.time() - comparison_service.start_time
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计信息失败: {str(e)}"
        )


# 错误处理将在主应用中定义
