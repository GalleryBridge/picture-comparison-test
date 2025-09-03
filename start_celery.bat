@echo off
echo 启动PDF图纸尺寸分析系统 - Celery任务队列
echo ==========================================

cd backend

echo 激活虚拟环境...
call venv\Scripts\activate

echo 启动Celery Worker...
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo

pause
