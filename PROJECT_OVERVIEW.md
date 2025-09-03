# PDF图纸尺寸分析系统 - 项目概览

## 🎯 项目简介

这是一个基于 **Vue3 + TypeScript + FastAPI + Ollama** 架构的PDF图纸尺寸识别与分析系统。系统利用 **Qwen2.5-VL** 多模态大模型，实现对工程图纸的智能解析，自动提取尺寸标注信息。

## ✨ 核心特性

- 📄 **PDF上传**: 支持多页PDF文档上传和解析
- 🔄 **智能转换**: 自动将PDF页面转换为高质量图像
- 🤖 **AI识别**: 基于Qwen2.5-VL模型的尺寸标注识别
- 📊 **结果展示**: 结构化的尺寸数据表格与页面标注
- 🔍 **历史管理**: 分析历史记录查询和管理
- ⚡ **异步处理**: Celery任务队列，实时进度显示

## 🏗️ 技术架构

### 前端技术栈
- **Vue 3** - 现代化前端框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - 企业级UI组件库
- **Pinia** - 状态管理
- **Vite** - 快速构建工具

### 后端技术栈
- **FastAPI** - 高性能Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **Celery** - 异步任务队列
- **Redis** - 缓存与消息队列
- **PostgreSQL** - 主数据库

### AI模型服务
- **Ollama** - 本地大模型管理平台
- **Qwen2.5-VL** - 多模态视觉语言模型
- **PyMuPDF** - PDF文档解析
- **pdf2image** - PDF页面转图像

## 📁 项目结构

```
picture-comparison/
├── 📂 backend/                    # FastAPI后端
│   ├── 📂 app/
│   │   ├── 📂 api/               # API路由层
│   │   │   └── 📂 endpoints/     # 具体端点实现
│   │   ├── 📂 core/              # 核心配置
│   │   ├── 📂 services/          # 业务逻辑层
│   │   ├── 📂 tasks/             # Celery异步任务
│   │   └── 📂 models/            # 数据模型
│   ├── 📄 main.py                # 应用入口
│   ├── 📄 requirements.txt       # Python依赖
│   └── 📄 .env.example          # 环境配置模板
├── 📂 frontend/                   # Vue3前端
│   ├── 📂 src/
│   │   ├── 📂 views/             # 页面组件
│   │   ├── 📂 components/        # 通用组件
│   │   ├── 📂 stores/            # Pinia状态管理
│   │   ├── 📂 api/               # API接口封装
│   │   └── 📂 types/             # TypeScript类型定义
│   ├── 📄 package.json           # Node.js依赖
│   └── 📄 vite.config.ts         # Vite配置
├── 📄 start_backend.bat          # 后端启动脚本
├── 📄 start_frontend.bat         # 前端启动脚本
├── 📄 start_celery.bat           # Celery启动脚本
├── 📄 SETUP.md                   # 安装配置指南
├── 📄 README.md                  # 项目说明文档
└── 📄 cursor_task.md             # 开发任务清单
```

## 🔄 系统流程

```mermaid
graph TD
    A[用户上传PDF] --> B[后端接收文件]
    B --> C[PDF页面转换]
    C --> D[Celery异步任务]
    D --> E[Ollama AI分析]
    E --> F[尺寸信息提取]
    F --> G[结果存储]
    G --> H[前端展示结果]
```

## 🚀 快速启动

### 1. 环境准备
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+
- Ollama + Qwen2.5-VL模型

### 2. 一键启动
```bash
# 1. 启动后端服务
双击 start_backend.bat

# 2. 启动任务队列
双击 start_celery.bat

# 3. 启动前端服务
双击 start_frontend.bat
```

### 3. 访问系统
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs

## 📋 功能模块

### 1. 文件上传模块
- 支持PDF文件拖拽上传
- 文件类型和大小验证
- 上传进度实时显示

### 2. PDF处理模块
- PDF页面解析和转换
- 高质量图像生成(300DPI)
- 多页文档批量处理

### 3. AI分析模块
- Qwen2.5-VL模型调用
- 尺寸标注智能识别
- 结果结构化解析

### 4. 结果管理模块
- 分析结果列表展示
- 详细结果页面查看
- 历史记录搜索筛选

### 5. 任务队列模块
- 异步任务处理
- 实时进度更新
- 任务状态管理

## 🔧 配置要点

### 关键配置项
```env
# Ollama模型配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2-vl:7b

# PDF处理配置
PDF_DPI=300
PDF_MAX_PAGES=50
MAX_FILE_SIZE=104857600

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/pdf_analysis

# Redis配置
REDIS_URL=redis://localhost:6379/0
```

## 🎯 开发重点

### 已实现功能
✅ 项目架构搭建  
✅ 后端API框架  
✅ 前端界面框架  
✅ PDF处理服务  
✅ AI模型集成  
✅ 任务队列系统  
✅ 文件上传功能  
✅ 结果展示界面  

### 待完善功能
🔄 数据库模型实现  
🔄 实际AI模型调用测试  
🔄 结果数据持久化  
🔄 错误处理完善  
🔄 性能优化  

## 📊 技术亮点

1. **现代化架构**: 前后端分离，技术栈先进
2. **AI集成**: 本地部署大模型，数据安全可控
3. **异步处理**: Celery任务队列，用户体验流畅
4. **类型安全**: TypeScript + Pydantic，开发效率高
5. **组件化设计**: 模块化开发，易于维护扩展

## 🎨 界面预览

- **首页**: 系统介绍和快速导航
- **上传页**: PDF文件上传和处理进度
- **结果列表**: 历史分析记录管理
- **结果详情**: 详细的尺寸分析结果展示

## 📈 扩展方向

- 支持更多图纸格式(DWG, DXF等)
- 增加尺寸标注编辑功能
- 添加批量处理能力
- 集成更多AI模型选择
- 支持云端部署

---

*这是一个功能完整、架构清晰的PDF图纸分析系统，为工程设计领域提供了智能化的尺寸识别解决方案。*
