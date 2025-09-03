"""
Celery应用配置
"""

from celery import Celery
from app.core.config import settings

# 创建Celery应用实例
celery_app = Celery(
    "pdf_analysis",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.pdf_tasks", "app.tasks.ai_tasks"]
)

# Celery配置
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_routes={
        'app.tasks.pdf_tasks.*': {'queue': 'pdf_processing'},
        'app.tasks.ai_tasks.*': {'queue': 'ai_analysis'},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
)
