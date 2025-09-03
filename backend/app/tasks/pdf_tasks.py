"""
PDF处理相关的Celery任务
"""

from celery import current_task
from app.tasks.celery_app import celery_app
from app.services.pdf_service import PDFService
from app.services.ollama_service import OllamaService
from app.core.config import settings
import os
import asyncio
from typing import Dict, Any


@celery_app.task(bind=True)
def process_pdf_task(self, file_id: str, pdf_path: str) -> Dict[str, Any]:
    """
    处理PDF文件的主任务
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'message': '开始处理PDF文件...'}
        )
        
        # 创建服务实例
        pdf_service = PDFService()
        
        # 获取PDF信息
        pdf_info = pdf_service.get_pdf_info(pdf_path)
        page_count = pdf_info["page_count"]
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 10, 'total': 100, 'message': f'PDF包含 {page_count} 页，开始转换图像...'}
        )
        
        # 创建输出目录
        output_dir = os.path.join(settings.UPLOAD_DIR, "images", file_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换PDF为图像
        image_paths = pdf_service.convert_pdf_to_images(pdf_path, output_dir)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 40, 'total': 100, 'message': f'图像转换完成，开始AI分析...'}
        )
        
        # 启动AI分析任务
        from app.tasks.ai_tasks import analyze_images_task
        ai_task = analyze_images_task.delay(file_id, image_paths)
        
        # 等待AI分析完成
        ai_result = ai_task.get(timeout=600)  # 10分钟超时
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 90, 'total': 100, 'message': '分析完成，保存结果...'}
        )
        
        # TODO: 保存结果到数据库
        
        result = {
            "file_id": file_id,
            "pdf_info": pdf_info,
            "image_paths": image_paths,
            "ai_analysis": ai_result,
            "status": "completed"
        }
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'message': '处理完成！'}
        )
        
        return result
        
    except Exception as e:
        # 清理临时文件
        try:
            if 'image_paths' in locals():
                pdf_service.cleanup_temp_files(image_paths)
        except:
            pass
        
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'message': f'处理失败: {str(e)}'}
        )
        raise


@celery_app.task(bind=True)
def convert_pdf_pages_task(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
    """
    转换PDF页面为图像的任务
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'message': '开始转换PDF页面...'}
        )
        
        pdf_service = PDFService()
        image_paths = pdf_service.convert_pdf_to_images(pdf_path, output_dir)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'message': '页面转换完成'}
        )
        
        return {
            "image_paths": image_paths,
            "page_count": len(image_paths),
            "status": "completed"
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e), 'message': f'转换失败: {str(e)}'}
        )
        raise


@celery_app.task(bind=True)
def cleanup_files_task(self, file_paths: list) -> Dict[str, Any]:
    """
    清理临时文件的任务
    """
    try:
        pdf_service = PDFService()
        pdf_service.cleanup_temp_files(file_paths)
        
        return {
            "cleaned_files": len(file_paths),
            "status": "completed"
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
