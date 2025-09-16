# PDF图纸比对分析系统

基于 Vue3 + TypeScript + FastAPI + Ollama 的智能PDF/DWG图纸比对与尺寸分析系统。

## 🚀 系统概述

本系统集成图纸比对和尺寸分析两大核心功能，利用 Qwen2.5-VL 多模态大模型和先进的图像处理算法，实现对PDF/DWG工程图纸的智能解析、比对分析和尺寸提取。

### 核心功能

#### 图纸比对功能
- 📄 **多格式支持**：支持PDF和DWG图纸格式的上传和处理
- 🔄 **智能比对**：像素级和图元级两种比对模式
- 🎨 **差异可视化**：颜色标记和闪烁效果突出显示差异区域
- 📊 **批量处理**：支持单一和批量图纸比对
- 💾 **结果导出**：在线预览和本地下载比对结果

#### 尺寸分析功能  
- 🤖 **智能识别**：基于 Qwen2.5-VL 模型的图纸理解与尺寸提取
- 📑 **多页处理**：支持多页PDF文档的批量分析和页面管理
- 📊 **结果展示**：结构化的尺寸数据表格与PDF页面标注
- 🔍 **历史检索**：支持历史解析记录查询与相似PDF图纸搜索
- ⚡ **实时进度**：异步任务处理，实时显示处理进度

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue3 前端     │    │   FastAPI 后端   │    │  Ollama 模型    │
│                 │    │                  │    │                 │
│ • 图纸上传      │◄──►│ • 请求处理       │◄──►│ • Qwen2.5-VL    │
│ • 比对展示      │    │ • 图纸转换       │    │ • 图纸理解      │
│ • 差异可视化    │    │ • 比对算法       │    │ • 尺寸提取      │
│ • 进度显示      │    │ • 任务调度       │    │                 │
│ • 结果导出      │    │ • API 接口       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │   图纸处理层    │              │
         │              │                 │              │
         │              │ • PyMuPDF       │              │
         │              │ • ezdxf (DWG)   │              │
         │              │ • OpenCV        │              │
         │              │ • 图像比对      │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │  PostgreSQL +    │
                    │    pgvector      │
                    │                  │
                    │ • 比对任务记录   │
                    │ • 图纸解析结果   │
                    │ • 向量索引       │
                    └──────────────────┘
```

## 🛠️ 技术栈

### 前端
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全的 JavaScript
- **Element Plus** - 企业级 UI 组件库
- **Vite** - 快速构建工具
- **Pinia** - 状态管理
- **Fabric.js** - Canvas绘图和差异标注
- **ViewerJS** - 图像查看器

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **Pydantic** - 数据验证与序列化
- **SQLAlchemy** - ORM 数据库操作
- **Celery** - 异步任务队列
- **Redis** - 缓存与消息队列

### 图纸处理
- **PyMuPDF** - PDF文档解析和处理
- **ezdxf** - DWG/DXF文件处理
- **OpenCV** - 图像处理和比对算法
- **Pillow** - 图片操作和格式转换
- **scikit-image** - 高级图像处理算法
- **SimpleITK** - 图像配准和变换

### AI 模型
- **Ollama** - 本地大模型管理平台
- **Qwen2.5-VL** - 多模态视觉语言模型

### 数据库
- **PostgreSQL** - 主数据库
- **pgvector** - 向量相似度搜索

## 📋 系统要求

### 硬件要求
- **GPU**: NVIDIA RTX 3060 或更高 (推荐 RTX 4070+，用于AI模型加速)
- **显存**: 至少 8GB VRAM (AI尺寸分析功能)
- **内存**: 16GB RAM 或更高 (图纸比对需要大量内存)
- **存储**: 50GB 可用空间

### 软件要求
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.9+
- **Node.js**: 16+
- **Docker**: 20.10+ (可选)
- **CUDA**: 11.8+ (GPU 加速)
- **Poppler**: PDF渲染支持

## 📁 项目结构

```
picture-comparison/
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   │   ├── ComparisonViewer.vue    # 比对结果查看器
│   │   │   ├── DiffHighlight.vue       # 差异高亮组件
│   │   │   └── BatchUpload.vue         # 批量上传组件
│   │   ├── views/          # 页面
│   │   │   ├── Home.vue               # 首页
│   │   │   ├── Upload.vue             # 上传页面
│   │   │   ├── Comparison.vue         # 比对页面
│   │   │   ├── Results.vue            # 结果列表
│   │   │   └── ResultDetail.vue       # 结果详情
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── api/            # API 接口
│   │   └── types/          # TypeScript 类型定义
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   │   └── endpoints/
│   │   │       ├── upload.py          # 文件上传
│   │   │       ├── comparison.py      # 图纸比对
│   │   │       ├── results.py         # 结果查询
│   │   │       └── download.py        # 文件下载
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── pdf_service.py         # PDF处理服务
│   │   │   ├── dwg_service.py         # DWG处理服务
│   │   │   ├── comparison_service.py  # 图纸比对服务
│   │   │   ├── ollama_service.py      # AI模型调用
│   │   │   └── visualization_service.py # 差异可视化
│   │   ├── tasks/          # Celery 任务
│   │   └── utils/          # 工具函数
│   ├── requirements.txt
│   └── alembic/            # 数据库迁移
├── uploads/                 # 文件上传目录
└── README.md

## 🔧 配置说明

### 后端环境变量 (.env)

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/picture_analysis

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5vl:72b

# 文件存储
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100MB
SUPPORTED_FORMATS=pdf,dwg,dxf

# 图纸处理配置
PDF_DPI=300
PDF_MAX_PAGES=50
DWG_RENDER_DPI=300

# 比对算法配置
COMPARISON_THRESHOLD=0.95
PIXEL_DIFF_SENSITIVITY=10
ENABLE_IMAGE_REGISTRATION=true

# JWT 配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端配置 (vite.config.ts)

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'fabric': ['fabric'],
          'viewer': ['viewerjs']
        }
      }
    }
  }
})
```

