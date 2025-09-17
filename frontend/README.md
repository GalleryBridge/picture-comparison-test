# PDF图纸比对前端系统

基于Vue3的现代化PDF图纸比对前端应用，提供直观的用户界面和丰富的可视化功能。

## 功能特性

### 🎯 核心功能
- **PDF文件上传**: 支持拖拽上传，文件格式验证
- **智能比对**: 基于传统算法的高精度PDF图纸比对
- **实时分析**: 实时显示比对进度和结果
- **差异可视化**: 多种图表展示差异分析结果

### 📊 分析报告
- **详细统计**: 图元数量、匹配对数、相似度等统计信息
- **可视化图表**: 差异分布、相似度分析、对比图表
- **技术细节**: 算法说明、性能指标、处理时间
- **结论建议**: 智能分析结论和改进建议

### 🎨 用户体验
- **现代化UI**: 基于Element Plus的响应式设计
- **流畅动画**: 平滑的页面切换和交互动画
- **多端适配**: 支持桌面端和移动端访问
- **主题支持**: 支持明暗主题切换

## 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **路由**: Vue Router 4.2+
- **状态管理**: Pinia 2.1+
- **UI组件**: Element Plus 2.4+
- **图表库**: ECharts 5.4+
- **HTTP客户端**: Axios 1.6+
- **构建工具**: Vite 5.0+
- **开发语言**: JavaScript ES6+

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API接口
│   │   └── comparison.js  # 比对相关API
│   ├── components/        # 公共组件
│   │   ├── FileUpload.vue # 文件上传组件
│   │   └── ComparisonChart.vue # 图表组件
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── stores/            # 状态管理
│   │   └── comparison.js  # 比对状态
│   ├── views/             # 页面组件
│   │   ├── Home.vue       # 首页
│   │   ├── Comparison.vue # 比对结果页
│   │   └── Report.vue     # 分析报告页
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── index.html             # HTML模板
├── package.json           # 依赖配置
├── vite.config.js         # Vite配置
└── README.md              # 项目说明
```

## 快速开始

### 环境要求
- Node.js 16.0+
- npm 8.0+ 或 yarn 1.22+

### 安装依赖
```bash
cd frontend
npm install
```

### 开发模式
```bash
npm run dev
```
访问 http://localhost:3000

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

## 页面说明

### 首页 (Home.vue)
- **文件上传区域**: 支持拖拽上传两个PDF文件
- **比对选项配置**: 比对模式、容差预设、相似度方法等
- **最近比对记录**: 显示最近的比对历史

### 比对结果页 (Comparison.vue)
- **结果概览**: 统计卡片展示关键指标
- **差异分析**: 图表展示差异类型分布和相似度
- **可视化选项**: 生成高亮PDF、差异图像、分析报告
- **输出文件**: 下载生成的各种文件

### 分析报告页 (Report.vue)
- **执行摘要**: 比对概况和相似度分析
- **详细统计**: 完整的统计数据展示
- **可视化图表**: 多种图表类型展示分析结果
- **技术细节**: 算法说明和性能指标
- **结论建议**: 智能分析结论和改进建议

## API集成

### 后端服务
前端通过代理配置连接到后端API服务：
- 开发环境: `http://localhost:8000`
- API路径: `/api/v1/pdf-comparison`

### 主要接口
- `POST /compare` - 文件比对
- `GET /compare/{id}` - 获取比对结果
- `POST /highlight` - 生成高亮PDF
- `POST /render` - 生成差异图像
- `POST /report` - 生成分析报告

## 组件说明

### FileUpload.vue
文件上传组件，支持：
- 拖拽上传
- 文件格式验证
- 文件大小限制
- 上传进度显示

### ComparisonChart.vue
图表组件，支持：
- 饼图 (pie)
- 柱状图 (bar)
- 仪表盘 (gauge)
- 折线图 (line)

## 状态管理

使用Pinia进行状态管理，主要状态：
- `comparisons`: 比对结果列表
- `currentComparison`: 当前比对结果
- `loading`: 加载状态
- `error`: 错误信息

## 样式设计

### 设计原则
- **现代化**: 采用现代化的设计语言
- **响应式**: 支持多种屏幕尺寸
- **一致性**: 统一的设计规范和交互模式
- **可访问性**: 良好的可访问性支持

### 主题色彩
- 主色调: #409eff (Element Plus 蓝色)
- 成功色: #67c23a
- 警告色: #e6a23c
- 危险色: #f56c6c
- 信息色: #909399

## 性能优化

### 代码分割
- 路由级别的代码分割
- 组件懒加载
- 第三方库按需引入

### 资源优化
- 图片压缩和懒加载
- CSS和JS压缩
- 静态资源CDN

### 缓存策略
- HTTP缓存
- 浏览器缓存
- 应用状态缓存

## 部署说明

### 开发环境
```bash
npm run dev
```

### 生产环境
```bash
npm run build
```

构建后的文件在 `dist/` 目录，可以部署到任何静态文件服务器。

### Docker部署
```dockerfile
FROM nginx:alpine
COPY dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 浏览器支持

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## 开发指南

### 代码规范
- 使用ESLint进行代码检查
- 遵循Vue 3 Composition API规范
- 组件命名使用PascalCase
- 文件命名使用kebab-case

### 提交规范
- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 代码格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 常见问题

### Q: 如何修改API地址？
A: 在 `vite.config.js` 中修改 `proxy.target` 配置。

### Q: 如何添加新的图表类型？
A: 在 `ComparisonChart.vue` 中添加新的case分支。

### Q: 如何自定义主题？
A: 在 `main.js` 中修改Element Plus的主题配置。

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: support@pdfcomparison.com
- 项目地址: https://github.com/pdfcomparison/frontend
