# PDF图纸尺寸分析系统

基于 Vue3 + TypeScript + FastAPI + Ollama 的智能PDF图纸尺寸识别与分析系统。

## 🚀 系统概述

本系统利用 Qwen2.5-VL 多模态大模型，实现对PDF工程图纸、技术图纸的智能解析，自动提取尺寸标注信息，并提供结构化的数据展示。支持多页PDF文档的批量处理和页面级别的精确分析。

### 核心功能
- 📄 **PDF上传**：支持单页和多页PDF图纸文件上传
- 🔄 **PDF转换**：自动将PDF页面转换为高质量图像进行分析
- 🤖 **智能解析**：基于 Qwen2.5-VL 模型的PDF图纸理解与尺寸提取
- 📑 **多页处理**：支持多页PDF文档的批量分析和页面管理
- 📊 **结果展示**：结构化的尺寸数据表格与PDF页面标注
- 🔍 **历史检索**：支持历史解析记录查询与相似PDF图纸搜索
- ⚡ **实时进度**：异步任务处理，实时显示PDF解析进度

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue3 前端     │    │   FastAPI 后端   │    │  Ollama 模型    │
│                 │    │                  │    │                 │
│ • PDF上传       │◄──►│ • 请求处理       │◄──►│ • Qwen2.5-VL    │
│ • 页面预览      │    │ • PDF转换        │    │ • 图纸理解      │
│ • 进度显示      │    │ • 任务调度       │    │ • 尺寸提取      │
│ • 结果展示      │    │ • 数据处理       │    │                 │
│ • 历史查询      │    │ • API 接口       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │   PDF处理层     │              │
         │              │                 │              │
         │              │ • PyMuPDF       │              │
         │              │ • pdf2image     │              │
         │              │ • 图像预处理    │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │  PostgreSQL +    │
                    │    pgvector      │
                    │                  │
                    │ • PDF任务记录    │
                    │ • 页面解析结果   │
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

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **Pydantic** - 数据验证与序列化
- **SQLAlchemy** - ORM 数据库操作
- **Celery** - 异步任务队列
- **Redis** - 缓存与消息队列

### AI 模型
- **Ollama** - 本地大模型管理平台
- **Qwen2.5-VL** - 多模态视觉语言模型
- **PyMuPDF** - PDF文档解析和处理
- **pdf2image** - PDF页面转图像
- **OpenCV** - 图像处理和优化
- **Pillow** - 图片操作和格式转换

### 数据库
- **PostgreSQL** - 主数据库
- **pgvector** - 向量相似度搜索

## 📋 系统要求

### 硬件要求
- **GPU**: NVIDIA RTX 3060 或更高 (推荐 RTX 4070+)
- **显存**: 至少 8GB VRAM
- **内存**: 16GB RAM 或更高
- **存储**: 50GB 可用空间

### 软件要求
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.9+
- **Node.js**: 16+
- **Docker**: 20.10+ (可选)
- **CUDA**: 11.8+ (GPU 加速)
- **Poppler**: PDF渲染支持 (pdf2image依赖)

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/picture-comparison.git
cd picture-comparison

# 创建 Python 虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装 Poppler (PDF处理依赖)
# Ubuntu/Debian: sudo apt-get install poppler-utils
# macOS: brew install poppler
# Windows: 下载并配置 poppler-utils 到 PATH
```

### 2. 安装 Ollama 和模型

```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 拉取 Qwen2.5-VL 模型
ollama pull qwen2-vl:7b
```

### 3. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 数据库迁移
alembic upgrade head

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 启动任务队列

```bash
# 启动 Redis (如果未安装，请先安装)
redis-server

# 启动 Celery Worker
cd backend
celery -A app.celery worker --loglevel=info

# 启动 Celery Beat (定时任务)
celery -A app.celery beat --loglevel=info
```

## 📁 项目结构

```
picture-comparison/
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── api/            # API 接口
│   │   └── types/          # TypeScript 类型定义
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   │   ├── pdf/        # PDF处理服务
│   │   │   ├── ai/         # AI模型调用
│   │   │   └── analysis/   # 尺寸分析
│   │   ├── tasks/          # Celery 任务
│   │   └── utils/          # 工具函数
│   ├── requirements.txt
│   └── alembic/            # 数据库迁移
├── docs/                     # 文档
├── docker-compose.yml        # Docker 配置
└── README.md
```

## 🔧 配置说明

### 后端环境变量 (.env)

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/picture_analysis

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2-vl:7b

# 文件存储
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100MB
SUPPORTED_FORMATS=pdf

# PDF处理配置
PDF_DPI=300
PDF_MAX_PAGES=50

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
  }
})
```

## 📖 API 文档

启动后端服务后，访问以下地址查看 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要 API 端点

```
POST /api/v1/upload          # 上传PDF文件
GET  /api/v1/tasks/{task_id} # 查询任务状态
GET  /api/v1/pdf/{id}/pages  # 获取PDF页面列表
GET  /api/v1/results         # 获取解析结果列表
GET  /api/v1/results/{id}    # 获取单个结果详情
POST /api/v1/search          # 相似PDF图纸搜索
```

## 🎯 使用流程

1. **上传PDF**: 在前端界面选择并上传PDF工程图纸
2. **PDF解析**: 系统自动解析PDF并提取各个页面
3. **页面转换**: 将PDF页面转换为高质量图像
4. **任务提交**: 创建解析任务并加入队列处理
5. **模型处理**: Qwen2.5-VL 模型分析每个页面内容
6. **结果解析**: 提取尺寸信息并结构化存储
7. **结果展示**: 在界面中查看解析结果和标注页面

## 🔍 功能特性

### PDF处理能力
- 支持多页PDF文档批量处理
- 高质量PDF页面图像转换 (300DPI)
- 智能页面分割和内容识别
- 支持加密PDF的解锁处理

### 智能尺寸识别
- 支持多种尺寸标注格式 (mm, cm, inch)
- 识别公差标注 (±0.25mm)
- 提取角度和半径信息
- 支持复杂图纸的多尺寸批量识别
- 页面级别的精确定位和标注

### 结果管理
- 按PDF文档和页面组织的层级结构
- 历史记录查询和筛选
- 结果导出 (JSON, CSV, Excel)
- PDF页面标注和高亮显示
- 批量处理和对比分析

### 性能优化
- 异步任务处理，避免接口超时
- PDF页面并行转换和处理
- 图像预处理和压缩优化
- 结果缓存和增量更新
- GPU 加速推理

## 🐳 Docker 部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🧪 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test

# E2E 测试
npm run test:e2e
```

## 📊 性能监控

系统提供多种监控指标：

- **任务处理速度**: 平均每张图片处理时间
- **模型准确率**: 尺寸识别准确度统计
- **系统资源**: GPU/CPU/内存使用率
- **API 响应时间**: 接口性能监控

## 🛡️ 安全考虑

- 文件类型和大小限制
- 用户认证和权限管理
- API 请求频率限制
- 敏感数据加密存储

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 常见问题

### Q: 模型加载失败怎么办？
A: 确保 Ollama 服务正常运行，并且已正确拉取 Qwen2.5-VL 模型。

### Q: GPU 内存不足？
A: 可以调整模型参数或使用 CPU 模式，但处理速度会较慢。

### Q: PDF上传失败？
A: 检查PDF文件格式和大小限制（最大100MB），确保PDF未损坏且网络连接正常。

### Q: PDF页面转换失败？
A: 确保已正确安装 Poppler 工具，检查PDF是否加密或损坏。

### Q: 识别准确率不高？
A: 尝试提高图片质量，或者调整模型 prompt 参数。

## 📞 联系方式

- 项目主页: https://github.com/your-username/picture-comparison
- 问题反馈: https://github.com/your-username/picture-comparison/issues
- 邮箱: your-email@example.com

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！
