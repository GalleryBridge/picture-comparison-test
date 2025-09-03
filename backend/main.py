"""
PDF图纸尺寸分析系统 - 主应用入口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router

# 创建FastAPI应用实例
app = FastAPI(
    title="PDF图纸尺寸分析系统",
    description="基于Qwen2.5-VL的PDF图纸尺寸识别与分析系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "PDF图纸尺寸分析系统",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """系统健康检查"""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: 实际检查数据库连接
        "redis": "connected",     # TODO: 实际检查Redis连接
        "ollama": "connected"     # TODO: 实际检查Ollama服务
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
