"""
PDF比对API应用

FastAPI主应用程序。
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import time
import os
from contextlib import asynccontextmanager

from .endpoints import router
from .models import ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 PDF比对API服务启动中...")
    
    # 创建必要的目录
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/uploads", exist_ok=True)
    os.makedirs("outputs/comparisons", exist_ok=True)
    os.makedirs("outputs/highlights", exist_ok=True)
    os.makedirs("outputs/renders", exist_ok=True)
    os.makedirs("outputs/reports", exist_ok=True)
    
    print("✅ 目录结构创建完成")
    print("✅ PDF比对API服务启动完成")
    
    yield
    
    # 关闭时执行
    print("🛑 PDF比对API服务关闭中...")
    print("✅ PDF比对API服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="PDF图纸比对API",
    description="基于传统算法的高精度PDF图纸比对系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 添加请求处理中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """添加处理时间头"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# 注册路由
app.include_router(router)

# 根路径
@app.get("/", tags=["根路径"])
async def root():
    """API根路径"""
    return {
        "message": "PDF图纸比对API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/pdf-comparison/health"
    }

# 自定义OpenAPI文档
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="PDF图纸比对API",
        version="1.0.0",
        description="""
## PDF图纸比对API

基于传统算法的高精度PDF图纸比对系统，提供完整的RESTful API接口。

### 主要功能

- **PDF文件比对**: 支持矢量图形、文本、表格的精确比对
- **可视化输出**: 生成高亮PDF、差异图像、统计图表
- **报告生成**: 支持Excel和HTML格式的详细报告
- **批量处理**: 支持批量文件比对和并发处理
- **状态管理**: 实时跟踪比对状态和进度

### 技术特性

- **高精度算法**: 基于几何特征的传统算法，工业级精度
- **多格式支持**: 支持多种输出格式和可视化方式
- **性能优化**: 空间索引、缓存机制、并发处理
- **容错处理**: 完善的错误处理和状态管理

### 使用说明

1. 上传PDF文件或提供文件路径
2. 配置比对参数（容差、相似度方法等）
3. 执行比对并获取结果
4. 生成可视化输出和报告

### 支持的文件格式

- **输入**: PDF文件
- **输出**: JSON、PDF、PNG、JPG、SVG、Excel、HTML

### 性能指标

- 处理速度: 毫秒级响应
- 精度等级: 工业级精度
- 并发支持: 多文件并发处理
- 内存优化: 智能缓存和清理机制
        """,
        routes=app.routes,
    )
    
    # 添加自定义信息
    openapi_schema["info"]["contact"] = {
        "name": "PDF Comparison Team",
        "email": "support@pdfcomparison.com"
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
    
    # 添加服务器信息
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:8000",
            "description": "开发服务器"
        },
        {
            "url": "https://api.pdfcomparison.com",
            "description": "生产服务器"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 自定义文档页面
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API文档",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

# 健康检查端点（简化版）
@app.get("/health", tags=["健康检查"])
async def simple_health_check():
    """简单健康检查"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "PDF图纸比对API"
    }

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="服务器内部错误",
            details={"path": str(request.url), "method": request.method}
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
