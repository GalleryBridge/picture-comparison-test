"""
任务管理API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from typing import Dict, Any

router = APIRouter()


@router.get("/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    获取任务状态
    """
    try:
        result = AsyncResult(task_id, app=celery_app)
        
        if result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'pending',
                'message': '任务等待处理'
            }
        elif result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'processing',
                'current': result.info.get('current', 0),
                'total': result.info.get('total', 1),
                'message': result.info.get('message', '正在处理...')
            }
        elif result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'completed',
                'result': result.result,
                'message': '处理完成'
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'state': result.state,
                'status': 'failed',
                'error': str(result.info),
                'message': '处理失败'
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取任务状态失败: {str(e)}"
        )


@router.delete("/{task_id}")
async def cancel_task(task_id: str) -> Dict[str, Any]:
    """
    取消任务
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            'task_id': task_id,
            'message': '任务已取消'
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"取消任务失败: {str(e)}"
        )


@router.get("/")
async def list_active_tasks() -> Dict[str, Any]:
    """
    获取活跃任务列表
    """
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        return {
            'active_tasks': active_tasks or {},
            'message': '获取活跃任务成功'
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取任务列表失败: {str(e)}"
        )
