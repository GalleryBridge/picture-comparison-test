# PDF图纸比对系统

基于传统算法的高精度PDF图纸比对分析系统，采用 Vue3 + FastAPI 架构。

## 🚀 系统概述

本系统专注于PDF工程图纸的精确比对分析，基于传统几何算法和矢量图形处理技术，提供工业级精度的图纸比对功能。

### 核心功能

#### 图纸比对功能
- 📄 **PDF格式支持**：专业的PDF矢量图形解析
- 🔄 **传统算法比对**：基于几何特征的高精度比对
- 🎨 **差异可视化**：高亮PDF、差异图像、统计图表
- 📊 **多种输出格式**：JSON、PDF、PNG、Excel报告
- 💾 **完整结果导出**：比对结果、可视化图像、详细报告

#### 技术特色  
- ⚡ **高性能处理**：并行处理、缓存机制、空间索引优化
- 🎯 **工业级精度**：毫米级精度的图元匹配和差异检测
- 📈 **实时进度跟踪**：状态轮询、进度显示、超时保护
- 🔧 **灵活配置**：多种比对模式、容差设置、相似度方法

## 🏗️ 系统架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue3 前端     │    │   FastAPI 后端   │    │   比对引擎      │
│                 │    │                  │    │                 │
│ • 文件上传      │◄──►│ • RESTful API    │◄──►│ • PDF解析       │
│ • 比对展示      │    │ • 文件处理       │    │ • 图元匹配      │
│ • 差异可视化    │    │ • 状态管理       │    │ • 差异检测      │
│ • 进度跟踪      │    │ • 异步处理       │    │ • 相似度计算    │
│ • 结果导出      │    │ • 错误处理       │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌────────┴────────┐              │
         │              │   核心处理层    │              │
         │              │                 │              │
         │              │ • PyMuPDF       │              │
         │              │ • matplotlib    │              │
         │              │ • 几何算法      │              │
         │              │ • 空间索引      │              │
         │              └─────────────────┘              │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   可视化输出     │
                    │                  │
                    │ • 高亮PDF        │
                    │ • 差异图像       │
                    │ • 统计图表       │
                    │ • Excel报告      │
                    └──────────────────┘
```

## 🛠️ 技术栈

### 前端
- **Vue 3** - 现代化前端框架
- **Element Plus** - 企业级 UI 组件库
- **Vite** - 快速构建工具
- **Pinia** - 状态管理
- **Axios** - HTTP 客户端
- **Vue Router** - 路由管理

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **Pydantic** - 数据验证与序列化
- **Uvicorn** - ASGI 服务器
- **Python 3.9+** - 编程语言

### 图纸处理
- **PyMuPDF (fitz)** - PDF文档解析和处理
- **pdfplumber** - PDF文本和表格提取
- **matplotlib** - 图表生成和可视化
- **seaborn** - 统计图表美化
- **numpy** - 数值计算
- **psutil** - 系统监控

### 核心算法
- **几何算法** - 图元匹配和相似度计算
- **空间索引** - 高效的图元搜索
- **容差管理** - 精度控制和误差处理
- **差异检测** - 变化识别和分类

## 📋 系统要求

### 硬件要求
- **CPU**: 多核处理器 (推荐 4核+)
- **内存**: 8GB RAM 或更高 (大型PDF需要更多内存)
- **存储**: 10GB 可用空间
- **网络**: 稳定的网络连接

### 软件要求
- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.9+
- **Node.js**: 16+
- **Git**: 版本控制

## 📁 项目结构

```
picture-comparison-test/
├── frontend/                    # Vue3 前端应用
│   ├── src/
│   │   ├── api/                # API 接口
│   │   │   └── comparison.js   # 比对API调用
│   │   ├── components/         # Vue 组件
│   │   │   ├── ComparisonChart.vue  # 比对图表组件
│   │   │   └── FileUpload.vue       # 文件上传组件
│   │   ├── views/              # 页面视图
│   │   │   ├── Home.vue        # 主页 - 文件上传和比对
│   │   │   ├── Comparison.vue  # 比对结果页面
│   │   │   └── Report.vue      # 报告页面
│   │   ├── stores/             # Pinia 状态管理
│   │   │   └── comparison.js   # 比对状态管理
│   │   ├── router/             # 路由配置
│   │   │   └── index.js        # 路由定义
│   │   ├── App.vue             # 根组件
│   │   └── main.js             # 应用入口
│   ├── index.html              # HTML 模板
│   ├── package.json            # 前端依赖
│   ├── vite.config.js          # Vite 配置
│   └── README.md               # 前端说明
├── backend/                     # FastAPI 后端应用
│   ├── api/                    # API 层
│   │   ├── app.py              # FastAPI 应用
│   │   ├── endpoints.py        # API 端点
│   │   ├── models.py           # 数据模型
│   │   └── service.py          # 业务服务
│   ├── core/                   # 核心比对引擎
│   │   └── comparison_engine.py # 比对引擎主类
│   ├── parser/                 # PDF 解析模块
│   │   └── pdf_parser.py       # PDF 解析器
│   ├── geometry/               # 几何处理模块
│   │   ├── elements.py         # 几何图元定义
│   │   ├── normalizer.py       # 坐标标准化
│   │   └── spatial_index.py    # 空间索引
│   ├── matching/               # 匹配算法模块
│   │   ├── element_matcher.py  # 图元匹配器
│   │   ├── similarity_calculator.py # 相似度计算
│   │   ├── diff_detector.py    # 差异检测
│   │   └── tolerance.py        # 容差管理
│   ├── visualization/          # 可视化模块
│   │   ├── pdf_highlighter.py  # PDF 高亮标注
│   │   ├── diff_renderer.py    # 差异图像渲染
│   │   └── report_generator.py # 报告生成
│   ├── test/                   # 测试文件
│   │   ├── test_*.py           # 各模块测试
│   │   └── test_drawing.pdf    # 测试用PDF
│   ├── outputs/                # 输出目录
│   │   ├── uploads/            # 上传文件
│   │   ├── comparisons/        # 比对结果
│   │   ├── highlights/         # 高亮PDF
│   │   ├── renders/            # 渲染图像
│   │   └── reports/            # 生成报告
│   ├── requirements_pdf_comparison.txt # Python 依赖
│   ├── start_api.py            # API 启动脚本
│   └── API_USAGE.md            # API 使用说明
├── outputs/                     # 全局输出目录
├── README.md                    # 项目说明文档
├── task.md                      # 任务说明
└── Cursor.md                    # 开发记录
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/picture-comparison-test.git
cd picture-comparison-test
```

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements_pdf_comparison.txt

# 启动后端API服务
python start_api.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 启动前端开发服务器
npm run dev
```

前端应用将在 `http://localhost:3000` 启动

### 4. 访问应用

打开浏览器访问 `http://localhost:3000`，即可开始使用PDF图纸比对功能。

## 🔧 配置说明

### 前端配置 (vite.config.js)

```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  }
})
```

### 后端配置

后端服务配置在 `backend/start_api.py` 中：

```python
uvicorn.run(
    "api.app:app",
    host="0.0.0.0",
    port=8000,
    reload=True,
    timeout_keep_alive=300,  # 5分钟连接保持
    timeout_graceful_shutdown=30
)
```

## 📖 使用说明

### 基本使用流程

1. **上传PDF文件**：在主页选择两个要比对的PDF文件
2. **配置比对参数**：选择比对模式、相似度方法、容差设置等
3. **开始比对**：点击"开始比对"按钮，系统将自动处理
4. **查看结果**：比对完成后查看详细的比对结果和可视化图像
5. **导出结果**：下载高亮PDF、差异图像或详细报告

### 比对参数说明

- **比对模式**：
  - 标准模式：平衡精度和性能
  - 严格模式：高精度比对
  - 宽松模式：容错性强

- **相似度方法**：
  - 加权相似度：综合多种特征
  - 欧几里得距离：基于坐标距离
  - 余弦相似度：基于向量角度

- **容差预设**：
  - 超高精度：0.01mm 容差
  - 高精度：0.1mm 容差
  - 标准精度：1mm 容差
  - 宽松精度：5mm 容差

## 🔍 API 文档

后端提供完整的RESTful API接口，启动后端服务后可访问：

- **API文档**: `http://localhost:8000/docs`
- **交互式文档**: `http://localhost:8000/redoc`
- **健康检查**: `http://localhost:8000/api/v1/pdf-comparison/health`

详细的API使用说明请参考 `backend/API_USAGE.md`

