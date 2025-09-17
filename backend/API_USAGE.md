# PDF图纸比对API使用指南

## 概述

PDF图纸比对API是一个基于传统算法的高精度PDF图纸比对系统，提供完整的RESTful API接口。

## 快速开始

### 1. 启动服务

```bash
# 方式1: 使用启动脚本
python start_api.py

# 方式2: 直接启动
python -m app.services.pdf_comparison.api.app

# 方式3: 使用uvicorn
uvicorn app.services.pdf_comparison.api.app:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 访问文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. 健康检查

```bash
curl http://localhost:8000/api/v1/pdf-comparison/health
```

## API端点

### 基础信息

- **基础URL**: `http://localhost:8000/api/v1/pdf-comparison`
- **认证**: 当前无需认证
- **数据格式**: JSON
- **字符编码**: UTF-8

### 核心端点

#### 1. 文件比对

**POST** `/compare`

执行PDF文件比对。

```json
{
  "file_a_path": "/path/to/file_a.pdf",
  "file_b_path": "/path/to/file_b.pdf",
  "mode": "standard",
  "similarity_method": "weighted_combined",
  "tolerance_preset": "standard",
  "output_formats": ["json"],
  "include_visualization": true,
  "include_report": false
}
```

**响应示例**:
```json
{
  "comparison_id": "comp_abc123def456",
  "status": "completed",
  "timestamp": "2024-01-01T12:00:00",
  "processing_time": 0.1234,
  "success": true,
  "elements_a_count": 150,
  "elements_b_count": 148,
  "matched_pairs": 145,
  "average_similarity": 0.987,
  "total_differences": 5,
  "change_rate": 0.033,
  "output_files": {
    "json": "/outputs/comp_abc123def456_result.json",
    "highlighted_pdf": "/outputs/comp_abc123def456_highlighted.pdf"
  }
}
```

#### 2. 批量比对

**POST** `/compare/batch`

批量执行PDF文件比对。

```json
{
  "comparisons": [
    {
      "file_a_path": "/path/to/file_a1.pdf",
      "file_b_path": "/path/to/file_b1.pdf",
      "mode": "quick"
    },
    {
      "file_a_path": "/path/to/file_a2.pdf", 
      "file_b_path": "/path/to/file_b2.pdf",
      "mode": "precise"
    }
  ],
  "max_concurrent": 3
}
```

#### 3. 获取比对结果

**GET** `/compare/{comparison_id}`

获取指定比对ID的结果。

#### 4. 列出比对结果

**GET** `/compare?page=1&page_size=20`

分页获取比对结果列表。

#### 5. 删除比对结果

**DELETE** `/compare`

删除指定的比对结果。

```json
{
  "comparison_ids": ["comp_abc123def456", "comp_xyz789uvw012"]
}
```

### 可视化端点

#### 1. 生成高亮PDF

**POST** `/highlight`

生成差异高亮的PDF文件。

```json
{
  "comparison_id": "comp_abc123def456",
  "highlight_style": "solid",
  "include_legend": true,
  "include_overlay": false
}
```

#### 2. 生成差异图像

**POST** `/render`

生成差异可视化图像。

```json
{
  "comparison_id": "comp_abc123def456",
  "chart_types": ["summary", "heatmap"],
  "render_format": "png",
  "dpi": 300
}
```

#### 3. 生成报告

**POST** `/report`

生成Excel或HTML格式的报告。

```json
{
  "comparison_id": "comp_abc123def456",
  "report_format": "excel",
  "report_level": "detailed",
  "include_charts": true,
  "include_images": true,
  "custom_title": "自定义报告标题"
}
```

### 工具端点

#### 1. 健康检查

**GET** `/health`

获取服务健康状态。

#### 2. 统计信息

**GET** `/statistics`

获取系统统计信息。

#### 3. 文件下载

**GET** `/files/{file_path}`

下载生成的文件。

#### 4. 文件上传

**POST** `/upload`

上传PDF文件。

## 参数说明

### 比对模式 (mode)

- `strict`: 严格模式，高精度比对
- `standard`: 标准模式，平衡精度和性能
- `relaxed`: 宽松模式，容错性强
- `custom`: 自定义模式

### 相似度方法 (similarity_method)

- `weighted_combined`: 加权相似度（推荐）
- `euclidean`: 欧几里得距离
- `manhattan`: 曼哈顿距离
- `cosine`: 余弦相似度
- `jaccard`: 杰卡德相似度
- `hausdorff`: 豪斯多夫距离

### 容差预设 (tolerance_preset)

- `ultra_high`: 超高精度（0.01mm）
- `high`: 高精度（0.1mm）
- `standard`: 标准精度（1mm）
- `loose`: 宽松精度（10mm）

### 输出格式 (output_formats)

- `json`: JSON格式结果
- `summary`: 摘要报告
- `detailed`: 详细报告

### 高亮样式 (highlight_style)

- `solid`: 实心填充
- `outline`: 轮廓线
- `dashed`: 虚线
- `thick`: 粗线

### 图表类型 (chart_types)

- `summary`: 比对摘要
- `heatmap`: 差异热力图
- `distribution`: 图元分布
- `similarity`: 相似度分析
- `geometric`: 几何可视化

### 渲染格式 (render_format)

- `png`: PNG图像
- `jpg`: JPEG图像
- `svg`: SVG矢量图
- `pdf`: PDF文档

### 报告格式 (report_format)

- `excel`: Excel格式
- `html`: HTML格式
- `both`: 两种格式

### 报告级别 (report_level)

- `summary`: 摘要报告
- `detailed`: 详细报告
- `comprehensive`: 综合报告

## 使用示例

### Python示例

```python
import requests
import json

# 基础URL
base_url = "http://localhost:8000/api/v1/pdf-comparison"

# 1. 执行比对
comparison_data = {
    "file_a_path": "/path/to/file_a.pdf",
    "file_b_path": "/path/to/file_b.pdf",
    "mode": "standard",
    "similarity_method": "weighted_combined",
    "tolerance_preset": "standard",
    "output_formats": ["json"],
    "include_visualization": True,
    "include_report": False
}

response = requests.post(f"{base_url}/compare", json=comparison_data)
result = response.json()

if result["success"]:
    comparison_id = result["comparison_id"]
    print(f"比对成功: {comparison_id}")
    
    # 2. 生成高亮PDF
    highlight_data = {
        "comparison_id": comparison_id,
        "highlight_style": "solid",
        "include_legend": True
    }
    
    highlight_response = requests.post(f"{base_url}/highlight", json=highlight_data)
    highlight_result = highlight_response.json()
    
    if highlight_result["success"]:
        print("高亮PDF生成成功")
        print(f"文件路径: {highlight_result['output_files']}")
    
    # 3. 生成差异图像
    render_data = {
        "comparison_id": comparison_id,
        "chart_types": ["summary", "heatmap"],
        "render_format": "png"
    }
    
    render_response = requests.post(f"{base_url}/render", json=render_data)
    render_result = render_response.json()
    
    if render_result["success"]:
        print("差异图像生成成功")
        print(f"文件路径: {render_result['output_files']}")
    
    # 4. 生成报告
    report_data = {
        "comparison_id": comparison_id,
        "report_format": "excel",
        "report_level": "detailed",
        "include_charts": True,
        "custom_title": "我的比对报告"
    }
    
    report_response = requests.post(f"{base_url}/report", json=report_data)
    report_result = report_response.json()
    
    if report_result["success"]:
        print("报告生成成功")
        print(f"文件路径: {report_result['output_files']}")

else:
    print(f"比对失败: {result['error_message']}")
```

### JavaScript示例

```javascript
const baseUrl = 'http://localhost:8000/api/v1/pdf-comparison';

// 执行比对
async function compareFiles(fileAPath, fileBPath) {
    const response = await fetch(`${baseUrl}/compare`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file_a_path: fileAPath,
            file_b_path: fileBPath,
            mode: 'standard',
            similarity_method: 'weighted',
            tolerance_preset: 'standard',
            output_formats: ['json'],
            include_visualization: true,
            include_report: false
        })
    });
    
    return await response.json();
}

// 生成高亮PDF
async function generateHighlight(comparisonId) {
    const response = await fetch(`${baseUrl}/highlight`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            comparison_id: comparisonId,
            highlight_style: 'standard',
            include_legend: true
        })
    });
    
    return await response.json();
}

// 使用示例
compareFiles('/path/to/file_a.pdf', '/path/to/file_b.pdf')
    .then(result => {
        if (result.success) {
            console.log('比对成功:', result.comparison_id);
            return generateHighlight(result.comparison_id);
        } else {
            console.error('比对失败:', result.error_message);
        }
    })
    .then(highlightResult => {
        if (highlightResult.success) {
            console.log('高亮PDF生成成功:', highlightResult.output_files);
        } else {
            console.error('高亮PDF生成失败:', highlightResult.error_message);
        }
    })
    .catch(error => {
        console.error('请求失败:', error);
    });
```

### cURL示例

```bash
# 1. 健康检查
curl -X GET "http://localhost:8000/api/v1/pdf-comparison/health"

# 2. 执行比对
curl -X POST "http://localhost:8000/api/v1/pdf-comparison/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "file_a_path": "/path/to/file_a.pdf",
    "file_b_path": "/path/to/file_b.pdf",
    "mode": "standard",
    "similarity_method": "weighted_combined",
    "tolerance_preset": "standard",
    "output_formats": ["json"],
    "include_visualization": true
  }'

# 3. 获取比对结果
curl -X GET "http://localhost:8000/api/v1/pdf-comparison/compare/comp_abc123def456"

# 4. 生成高亮PDF
curl -X POST "http://localhost:8000/api/v1/pdf-comparison/highlight" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_id": "comp_abc123def456",
    "highlight_style": "solid",
    "include_legend": true
  }'

# 5. 生成差异图像
curl -X POST "http://localhost:8000/api/v1/pdf-comparison/render" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_id": "comp_abc123def456",
    "chart_types": ["summary", "heatmap"],
    "render_format": "png"
  }'

# 6. 生成报告
curl -X POST "http://localhost:8000/api/v1/pdf-comparison/report" \
  -H "Content-Type: application/json" \
  -d '{
    "comparison_id": "comp_abc123def456",
    "report_format": "excel",
    "report_level": "detailed",
    "include_charts": true
  }'
```

## 错误处理

### 常见错误码

- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "error": "ValidationError",
  "message": "文件路径不能为空",
  "details": {
    "field": "file_a_path"
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

## 性能优化

### 建议配置

1. **并发设置**: 根据服务器性能调整`max_concurrent`参数
2. **缓存大小**: 适当增加`cache_size`以提高响应速度
3. **清理间隔**: 设置合理的`cleanup_interval`避免磁盘空间不足

### 性能指标

- **处理速度**: 毫秒级响应
- **精度等级**: 工业级精度
- **并发支持**: 多文件并发处理
- **内存优化**: 智能缓存和清理机制

## 部署建议

### 生产环境

1. 使用反向代理（Nginx）
2. 配置HTTPS
3. 设置适当的CORS策略
4. 监控服务状态
5. 定期备份数据

### Docker部署

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "app.services.pdf_comparison.api.app"]
```

## 技术支持

如有问题，请参考：

1. API文档: http://localhost:8000/docs
2. 健康检查: http://localhost:8000/api/v1/pdf-comparison/health
3. 统计信息: http://localhost:8000/api/v1/pdf-comparison/statistics
