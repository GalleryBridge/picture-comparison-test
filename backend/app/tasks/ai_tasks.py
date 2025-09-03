"""
AI分析相关的Celery任务
"""

from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.ollama_service import OllamaService
import asyncio
from typing import Dict, Any, List


@celery_app.task(bind=True)
def analyze_images_task(self, file_id: str, image_paths: List[str]) -> Dict[str, Any]:
    """
    分析图像并提取尺寸信息的任务
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'message': '开始AI分析...'}
        )
        
        # 创建Ollama服务实例
        ollama_service = OllamaService()
        
        # 检查模型可用性
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        model_available = loop.run_until_complete(
            ollama_service.check_model_availability()
        )
        
        if not model_available:
            raise Exception("Ollama模型不可用，请检查服务状态")
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'message': '模型检查完成，开始分析图像...'}
        )
        
        # 批量分析图像
        results = loop.run_until_complete(
            ollama_service.batch_analyze_images(image_paths)
        )
        
        # 处理分析结果
        total_dimensions = 0
        all_dimensions = []
        
        for i, result in enumerate(results):
            progress = 20 + (i + 1) * 60 // len(image_paths)
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': progress, 
                    'total': 100, 
                    'message': f'分析第 {i+1}/{len(image_paths)} 页...'
                }
            )
            
            if result.get("success"):
                # 解析尺寸信息
                dimensions = ollama_service.parse_dimensions_from_response(
                    result.get("response", "")
                )
                total_dimensions += len(dimensions)
                all_dimensions.extend(dimensions)
                
                result["parsed_dimensions"] = dimensions
            else:
                result["parsed_dimensions"] = []
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'message': '分析完成，整理结果...'}
        )
        
        # 整理最终结果
        final_result = {
            "file_id": file_id,
            "total_pages": len(image_paths),
            "total_dimensions": total_dimensions,
            "page_results": results,
            "all_dimensions": all_dimensions,
            "summary": {
                "pages_analyzed": len(image_paths),
                "successful_pages": sum(1 for r in results if r.get("success")),
                "failed_pages": sum(1 for r in results if not r.get("success")),
                "total_dimensions_found": total_dimensions
            },
            "status": "completed"
        }
        
        loop.close()
        
        return final_result
        
    except Exception as e:
        if 'loop' in locals():
            loop.close()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'message': f'AI分析失败: {str(e)}'}
        )
        raise


@celery_app.task(bind=True)
def analyze_single_image_task(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
    """
    分析单个图像的任务
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'message': '开始分析图像...'}
        )
        
        ollama_service = OllamaService()
        
        # 异步分析图像
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            ollama_service.analyze_image(image_path, prompt)
        )
        
        if result.get("success"):
            # 解析尺寸信息
            dimensions = ollama_service.parse_dimensions_from_response(
                result.get("response", "")
            )
            result["parsed_dimensions"] = dimensions
        
        loop.close()
        
        return result
        
    except Exception as e:
        if 'loop' in locals():
            loop.close()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise


@celery_app.task(bind=True)
def batch_reanalyze_task(self, file_id: str, image_paths: List[str], new_prompt: str) -> Dict[str, Any]:
    """
    使用新提示词重新分析图像的任务
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'message': '开始重新分析...'}
        )
        
        ollama_service = OllamaService()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 使用新提示词批量分析
        results = loop.run_until_complete(
            ollama_service.batch_analyze_images(image_paths, new_prompt)
        )
        
        # 处理结果
        for result in results:
            if result.get("success"):
                dimensions = ollama_service.parse_dimensions_from_response(
                    result.get("response", "")
                )
                result["parsed_dimensions"] = dimensions
        
        loop.close()
        
        return {
            "file_id": file_id,
            "reanalysis_results": results,
            "status": "completed"
        }
        
    except Exception as e:
        if 'loop' in locals():
            loop.close()
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
