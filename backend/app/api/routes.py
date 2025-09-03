"""
API路由配置
"""

from fastapi import APIRouter
from app.api.endpoints import upload, results

# 创建主路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(upload.router, prefix="/upload", tags=["文件上传"])
api_router.include_router(results.router, prefix="/results", tags=["结果查询"])
