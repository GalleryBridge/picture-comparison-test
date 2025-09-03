# PDF图纸尺寸分析系统 - 安装配置指南

## 🚀 快速开始

### 1. 环境要求

确保您的系统已安装以下软件：

- **Python 3.9+** 
- **Node.js 16+**
- **PostgreSQL 12+**
- **Redis 6+**
- **Ollama** (用于运行Qwen2.5-VL模型)

### 2. 安装Ollama和模型

```bash
# 下载并安装Ollama
# 访问 https://ollama.ai 下载对应系统版本

# 拉取Qwen2.5-VL模型
ollama pull qwen2.5vl:72b
```

### 3. 数据库配置

#### PostgreSQL配置
```sql
-- 创建数据库
CREATE DATABASE pdf_analysis;

-- 创建用户（可选）
CREATE USER pdf_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE pdf_analysis TO pdf_user;
```

#### Redis配置
确保Redis服务正在运行：
```bash
# Windows: 启动Redis服务
redis-server

# 或使用Windows服务管理器启动Redis
```

### 4. 后端配置

1. **进入后端目录**
```bash
cd backend
```

2. **创建虚拟环境**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
# 复制配置文件
copy .env.example .env

# 编辑 .env 文件，修改以下配置：
DATABASE_URL=postgresql://postgres:password@localhost:5432/pdf_analysis
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11434
```

5. **数据库迁移**
```bash
# 如果使用Alembic（后续添加）
alembic upgrade head
```

### 5. 前端配置

1. **进入前端目录**
```bash
cd frontend
```

2. **安装依赖**
```bash
npm install
```

### 6. 启动服务

#### 方法一：使用批处理脚本（推荐）

1. **启动后端服务**
   - 双击 `start_backend.bat`

2. **启动Celery任务队列**
   - 双击 `start_celery.bat`

3. **启动前端服务**
   - 双击 `start_frontend.bat`

#### 方法二：手动启动

1. **启动后端**
```bash
cd backend
venv\Scripts\activate
python main.py
```

2. **启动Celery**
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

3. **启动前端**
```bash
cd frontend
npm run dev
```

### 7. 访问系统

- **前端界面**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **API接口**: http://localhost:8000/api/v1

## 🔧 配置说明

### 后端环境变量 (.env)

```env
# 应用配置
APP_NAME=PDF图纸尺寸分析系统
DEBUG=True

# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/pdf_analysis

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5vl:72b

# 文件存储配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=104857600  # 100MB
SUPPORTED_FORMATS=pdf

# PDF处理配置
PDF_DPI=300
PDF_MAX_PAGES=50

# CORS配置
ALLOWED_HOSTS=http://localhost:3000,http://127.0.0.1:3000

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

## 🐛 常见问题

### 1. Ollama模型加载失败
```bash
# 检查Ollama服务状态
ollama list

# 重新拉取模型
ollama pull qwen2.5vl:72b
```

### 2. 数据库连接失败
- 检查PostgreSQL服务是否启动
- 确认数据库URL配置正确
- 检查防火墙设置

### 3. Redis连接失败
- 检查Redis服务是否启动
- 确认Redis URL配置正确

### 4. PDF处理失败
- 确保已安装Poppler工具
- Windows: 下载poppler-utils并添加到PATH

### 5. 前端无法访问后端
- 检查后端服务是否在8000端口运行
- 确认CORS配置包含前端地址

## 📁 项目结构

```
picture-comparison/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── tasks/          # Celery任务
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue3前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # 状态管理
│   │   ├── api/            # API接口
│   │   └── types/          # 类型定义
│   └── package.json        # Node.js依赖
├── start_backend.bat       # 后端启动脚本
├── start_frontend.bat      # 前端启动脚本
├── start_celery.bat        # Celery启动脚本
└── README.md              # 项目说明
```

## 🔄 开发流程

1. **上传PDF** → 前端上传PDF文件到后端
2. **PDF解析** → 后端将PDF转换为图像
3. **AI分析** → Celery任务调用Ollama进行尺寸识别
4. **结果存储** → 将识别结果保存到数据库
5. **结果展示** → 前端展示结构化的尺寸信息

## 📞 技术支持

如遇到问题，请检查：
1. 所有服务是否正常启动
2. 环境变量配置是否正确
3. 依赖包是否完整安装
4. 网络连接是否正常

---

*安装完成后，您就可以开始使用PDF图纸尺寸分析系统了！*


Celery工作进程

cd backend
celery -A app.tasks.celery_app worker --loglevel=info

前端

cd backend
python main.py

前端服务

cd frontend
npm run dev