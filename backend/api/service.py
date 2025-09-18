"""
API服务层

处理业务逻辑和状态管理。
"""

import os
import uuid
import time
import psutil
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import shutil

from core.comparison_engine import PDFComparisonEngine, ComparisonConfig, ComparisonResult
from visualization.pdf_highlighter import PDFHighlighter, HighlightConfig
from visualization.diff_renderer import DiffRenderer, RenderConfig
from visualization.report_generator import ReportGenerator, ReportConfig
from .models import (
    ComparisonRequest, ComparisonResponse, ComparisonStatus,
    HighlightRequest, HighlightResponse, RenderRequest, RenderResponse,
    ReportRequest, ReportResponse, HealthResponse, ErrorResponse,
    BatchComparisonRequest, BatchComparisonResponse
)


class ComparisonService:
    """比对服务"""
    
    def __init__(self, 
                 output_dir: str = "outputs",
                 max_concurrent: int = 3,
                 cache_size: int = 100,
                 cleanup_interval: int = 3600):
        """
        初始化比对服务
        
        Args:
            output_dir: 输出目录
            max_concurrent: 最大并发数
            cache_size: 缓存大小
            cleanup_interval: 清理间隔(秒)
        """
        self.output_dir = Path(output_dir)
        self.max_concurrent = max_concurrent
        self.cache_size = cache_size
        self.cleanup_interval = cleanup_interval
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 状态管理
        self.comparisons: Dict[str, ComparisonResponse] = {}
        self.comparison_results: Dict[str, ComparisonResult] = {}
        self.start_time = time.time()
        
        # 服务组件
        self.engine = PDFComparisonEngine(ComparisonConfig(debug_mode=False))
        self.highlighter = PDFHighlighter()
        self.renderer = DiffRenderer()
        self.report_generator = ReportGenerator()
        
        # 清理任务将在需要时启动
        self._cleanup_task = None
    
    def _start_cleanup_task(self):
        """启动清理任务"""
        if self._cleanup_task is None:
            async def cleanup_task():
                while True:
                    await asyncio.sleep(self.cleanup_interval)
                    self._cleanup_old_data()
            
            try:
                loop = asyncio.get_running_loop()
                self._cleanup_task = loop.create_task(cleanup_task())
            except RuntimeError:
                # 没有运行的事件循环，稍后启动
                pass
    
    def _cleanup_old_data(self):
        """清理旧数据"""
        try:
            current_time = time.time()
            cutoff_time = current_time - (24 * 3600)  # 24小时前
            
            # 清理过期的比对结果
            expired_ids = []
            for comp_id, comp in self.comparisons.items():
                # 将ISO格式字符串转换为时间戳进行比较
                from datetime import datetime
                comp_time = datetime.fromisoformat(comp.timestamp).timestamp()
                if comp_time < cutoff_time:
                    expired_ids.append(comp_id)
            
            for comp_id in expired_ids:
                self._delete_comparison(comp_id)
            
            # 清理输出文件
            for file_path in self.output_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                    except OSError:
                        pass
            
            print(f"清理完成: 删除了{len(expired_ids)}个过期比对")
            
        except Exception as e:
            print(f"清理任务异常: {e}")
    
    def _delete_comparison(self, comparison_id: str):
        """删除比对数据"""
        if comparison_id in self.comparisons:
            del self.comparisons[comparison_id]
        if comparison_id in self.comparison_results:
            del self.comparison_results[comparison_id]
    
    def _generate_comparison_id(self) -> str:
        """生成比对ID"""
        return f"comp_{uuid.uuid4().hex[:12]}"
    
    def _get_tolerance_config(self, preset: str, custom: Optional[Dict[str, float]] = None):
        """获取容差配置"""
        from matching.tolerance import ToleranceManager
        
        if custom:
            return ToleranceManager.create_custom_config(custom)
        else:
            return ToleranceManager.get_preset_config(preset)
    
    async def compare_files(self, request: ComparisonRequest) -> ComparisonResponse:
        """执行文件比对"""
        comparison_id = self._generate_comparison_id()
        start_time = time.time()
        
        try:
            # 创建比对响应
            response = ComparisonResponse(
                comparison_id=comparison_id,
                status=ComparisonStatus.PROCESSING,
                timestamp=datetime.now().isoformat(),
                success=False
            )
            
            # 存储到缓存
            self.comparisons[comparison_id] = response
            
            # 验证文件存在
            if not os.path.exists(request.file_a_path):
                raise FileNotFoundError(f"文件A不存在: {request.file_a_path}")
            if not os.path.exists(request.file_b_path):
                raise FileNotFoundError(f"文件B不存在: {request.file_b_path}")
            
            # 配置比对引擎
            tolerance_config = self._get_tolerance_config(
                request.tolerance_preset, 
                request.custom_tolerance
            )
            
            config = ComparisonConfig(
                mode=request.mode,
                similarity_method=request.similarity_method,
                tolerance_config=tolerance_config,
                output_formats=request.output_formats,
                debug_mode=False
            )
            
            engine = PDFComparisonEngine(config)
            
            # 执行比对
            result = engine.compare_files(request.file_a_path, request.file_b_path)
            
            # 更新响应
            response.status = ComparisonStatus.COMPLETED
            response.success = result.success
            response.error_message = result.error_message
            response.processing_time = time.time() - start_time
            
            if result.success:
                response.elements_a_count = result.elements_a_count
                response.elements_b_count = result.elements_b_count
                response.matched_pairs = result.matching_statistics.matched_pairs
                response.average_similarity = result.matching_statistics.average_similarity
                response.total_differences = result.difference_statistics.total_differences
                response.change_rate = result.difference_statistics.change_rate
                
                # 生成输出文件
                output_files = {}
                
                # JSON输出
                if OutputFormat.JSON in request.output_formats:
                    json_path = self.output_dir / f"{comparison_id}_result.json"
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
                    output_files['json'] = str(json_path)
                
                # 可视化输出
                if request.include_visualization:
                    # 高亮PDF
                    highlight_path = self.output_dir / f"{comparison_id}_highlighted.pdf"
                    highlight_config = HighlightConfig()
                    highlighter = PDFHighlighter(highlight_config)
                    
                    if highlighter.highlight_differences(
                        result, 
                        str(highlight_path),
                        request.file_a_path,
                        request.file_b_path
                    ):
                        output_files['highlighted_pdf'] = str(highlight_path)
                    
                    # 差异图像
                    render_path = self.output_dir / f"{comparison_id}_diff.png"
                    render_config = RenderConfig()
                    renderer = DiffRenderer(render_config)
                    
                    if renderer.render_comparison_summary(result, str(render_path)):
                        output_files['diff_image'] = str(render_path)
                
                # 报告输出
                if request.include_report:
                    report_path = self.output_dir / f"{comparison_id}_report.xlsx"
                    report_config = ReportConfig()
                    report_generator = ReportGenerator(report_config)
                    
                    if report_generator.generate_report(result, str(report_path)):
                        output_files['report'] = str(report_path)
                
                response.output_files = output_files
                
                # 存储结果
                self.comparison_results[comparison_id] = result
            
            # 更新缓存
            self.comparisons[comparison_id] = response
            
            return response
            
        except Exception as e:
            # 更新错误状态
            response.status = ComparisonStatus.FAILED
            response.success = False
            response.error_message = str(e)
            response.processing_time = time.time() - start_time
            
            self.comparisons[comparison_id] = response
            return response
    
    async def batch_compare(self, request: BatchComparisonRequest) -> BatchComparisonResponse:
        """批量比对"""
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        
        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(request.max_concurrent)
        
        async def compare_with_semaphore(comp_request):
            async with semaphore:
                return await self.compare_files(comp_request)
        
        # 执行批量比对
        tasks = [compare_with_semaphore(req) for req in request.comparisons]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        completed_results = []
        failed_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                failed_count += 1
                # 创建错误响应
                error_response = ComparisonResponse(
                    comparison_id=f"error_{uuid.uuid4().hex[:8]}",
                    status=ComparisonStatus.FAILED,
                    timestamp=datetime.now().isoformat(),
                    success=False,
                    error_message=str(result)
                )
                completed_results.append(error_response)
            else:
                completed_results.append(result)
                if not result.success:
                    failed_count += 1
        
        return BatchComparisonResponse(
            batch_id=batch_id,
            total_count=len(request.comparisons),
            completed_count=len(completed_results) - failed_count,
            failed_count=failed_count,
            results=completed_results,
            processing_time=time.time() - start_time
        )
    
    def get_comparison(self, comparison_id: str) -> Optional[ComparisonResponse]:
        """获取比对结果"""
        return self.comparisons.get(comparison_id)
    
    def list_comparisons(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """列出比对结果"""
        all_comparisons = list(self.comparisons.values())
        # 按时间戳排序，将ISO格式字符串转换为datetime对象进行比较
        from datetime import datetime
        all_comparisons.sort(key=lambda x: datetime.fromisoformat(x.timestamp), reverse=True)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_comparisons = all_comparisons[start_idx:end_idx]
        
        return {
            "comparisons": page_comparisons,
            "total_count": len(all_comparisons),
            "page": page,
            "page_size": page_size,
            "has_next": end_idx < len(all_comparisons),
            "has_prev": page > 1
        }
    
    def delete_comparisons(self, comparison_ids: List[str]) -> Dict[str, Any]:
        """删除比对结果"""
        deleted_count = 0
        failed_ids = []
        
        for comp_id in comparison_ids:
            try:
                if comp_id in self.comparisons:
                    # 删除相关文件
                    comp = self.comparisons[comp_id]
                    for file_path in comp.output_files.values():
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except OSError:
                            pass
                    
                    # 删除数据
                    self._delete_comparison(comp_id)
                    deleted_count += 1
                else:
                    failed_ids.append(comp_id)
            except Exception as e:
                failed_ids.append(comp_id)
        
        return {
            "success": deleted_count > 0,
            "deleted_count": deleted_count,
            "failed_ids": failed_ids,
            "error_message": f"成功删除{deleted_count}个，失败{len(failed_ids)}个" if failed_ids else None
        }
    
    async def generate_highlight(self, request: HighlightRequest) -> HighlightResponse:
        """生成高亮PDF"""
        start_time = time.time()
        
        try:
            # 获取比对结果
            comparison = self.comparisons.get(request.comparison_id)
            if not comparison:
                raise ValueError(f"比对ID不存在: {request.comparison_id}")
            
            if not comparison.success:
                raise ValueError(f"比对失败: {comparison.error_message}")
            
            result = self.comparison_results.get(request.comparison_id)
            if not result:
                raise ValueError("比对结果数据不存在")
            
            # 配置高亮器
            highlight_config = HighlightConfig(
                style=request.highlight_style,
                include_legend=request.include_legend,
                include_overlay=request.include_overlay
            )
            
            highlighter = PDFHighlighter(highlight_config)
            
            # 生成输出文件
            output_files = {}
            
            if request.output_path:
                output_path = Path(request.output_path)
            else:
                output_path = self.output_dir / f"{request.comparison_id}_highlighted.pdf"
            
            # 生成高亮PDF
            if highlighter.highlight_differences(
                result,
                str(output_path),
                result.file_a_path,
                result.file_b_path
            ):
                output_files['highlighted_pdf'] = str(output_path)
            
            # 生成叠加图
            if request.include_overlay:
                overlay_path = self.output_dir / f"{request.comparison_id}_overlay.pdf"
                if highlighter.generate_overlay(
                    result,
                    str(overlay_path),
                    result.file_a_path,
                    result.file_b_path
                ):
                    output_files['overlay_pdf'] = str(overlay_path)
            
            return HighlightResponse(
                success=True,
                output_files=output_files,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return HighlightResponse(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def generate_render(self, request: RenderRequest) -> RenderResponse:
        """生成差异图像"""
        start_time = time.time()
        
        try:
            # 获取比对结果
            comparison = self.comparisons.get(request.comparison_id)
            if not comparison:
                raise ValueError(f"比对ID不存在: {request.comparison_id}")
            
            if not comparison.success:
                raise ValueError(f"比对失败: {comparison.error_message}")
            
            result = self.comparison_results.get(request.comparison_id)
            if not result:
                raise ValueError("比对结果数据不存在")
            
            # 配置渲染器
            render_config = RenderConfig(
                dpi=request.dpi,
                format=request.render_format
            )
            
            renderer = DiffRenderer(render_config)
            
            # 生成输出文件
            output_files = {}
            
            for chart_type in request.chart_types:
                if request.output_path:
                    base_path = Path(request.output_path).with_suffix('')
                    output_path = f"{base_path}_{chart_type.value}.{request.render_format.value}"
                else:
                    output_path = self.output_dir / f"{request.comparison_id}_{chart_type.value}.{request.render_format.value}"
                
                # 根据图表类型生成图像
                success = False
                if chart_type.value == "summary":
                    success = renderer.render_comparison_summary(result, str(output_path))
                elif chart_type.value == "heatmap":
                    success = renderer.render_difference_heatmap(result, str(output_path))
                elif chart_type.value == "distribution":
                    success = renderer.render_element_distribution(result, str(output_path))
                elif chart_type.value == "similarity":
                    success = renderer.render_similarity_analysis(result, str(output_path))
                elif chart_type.value == "geometric":
                    success = renderer.render_geometric_visualization(result, str(output_path))
                
                if success:
                    output_files[chart_type.value] = str(output_path)
            
            return RenderResponse(
                success=True,
                output_files=output_files,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return RenderResponse(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def generate_report(self, request: ReportRequest) -> ReportResponse:
        """生成报告"""
        start_time = time.time()
        
        try:
            # 获取比对结果
            comparison = self.comparisons.get(request.comparison_id)
            if not comparison:
                raise ValueError(f"比对ID不存在: {request.comparison_id}")
            
            if not comparison.success:
                raise ValueError(f"比对失败: {comparison.error_message}")
            
            result = self.comparison_results.get(request.comparison_id)
            if not result:
                raise ValueError("比对结果数据不存在")
            
            # 配置报告生成器
            report_config = ReportConfig(
                title=request.custom_title or "PDF图纸比对报告",
                level=request.report_level,
                include_charts=request.include_charts,
                include_images=request.include_images,
                include_raw_data=request.include_raw_data
            )
            
            report_generator = ReportGenerator(report_config)
            
            # 生成输出文件
            output_files = {}
            
            if request.output_path:
                output_path = request.output_path
            else:
                if request.report_format.value == "excel":
                    output_path = self.output_dir / f"{request.comparison_id}_report.xlsx"
                else:
                    output_path = self.output_dir / f"{request.comparison_id}_report.html"
            
            # 生成报告
            if report_generator.generate_report(result, str(output_path), request.report_format):
                output_files['report'] = str(output_path)
            
            return ReportResponse(
                success=True,
                output_files=output_files,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return ReportResponse(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def get_health(self) -> HealthResponse:
        """获取健康状态"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        memory_usage = {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent
        }
        
        # 磁盘使用情况
        try:
            disk = psutil.disk_usage(str(self.output_dir))
            disk_usage = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percentage": (disk.used / disk.total) * 100
            }
        except Exception:
            disk_usage = {
                "total": 0,
                "used": 0,
                "free": 0,
                "percentage": 0
            }
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime=uptime,
            memory_usage=memory_usage,
            disk_usage=disk_usage
        )
