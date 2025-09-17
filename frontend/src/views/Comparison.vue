<template>
  <div class="comparison-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-card class="loading-card">
        <div class="loading-content">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <h3>正在处理比对...</h3>
          <p>请稍候，系统正在分析PDF文件</p>
        </div>
      </el-card>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-card class="error-card">
        <div class="error-content">
          <el-icon class="error-icon"><Warning /></el-icon>
          <h3>比对失败</h3>
          <p>{{ error }}</p>
          <el-button type="primary" @click="goBack">返回首页</el-button>
        </div>
      </el-card>
    </div>

    <!-- 比对结果 -->
    <div v-else-if="comparison" class="result-container">
      <!-- 结果概览 -->
      <el-card class="overview-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>比对结果概览</span>
            <div class="header-actions">
              <el-button 
                type="primary" 
                :icon="Download"
                @click="downloadResults"
              >
                下载结果
              </el-button>
              <el-button 
                type="success" 
                :icon="DocumentCopy"
                @click="generateReport"
              >
                生成报告
              </el-button>
            </div>
          </div>
        </template>

        <div class="overview-content">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ comparison.elements_a_count || 0 }}</div>
                  <div class="stat-label">文件A图元数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ comparison.elements_b_count || 0 }}</div>
                  <div class="stat-label">文件B图元数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ comparison.matched_pairs || 0 }}</div>
                  <div class="stat-label">匹配对数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ formatSimilarity(comparison.average_similarity) }}</div>
                  <div class="stat-label">平均相似度</div>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ comparison.total_differences || 0 }}</div>
                  <div class="stat-label">总差异数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><PieChart /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ formatChangeRate(comparison.change_rate) }}</div>
                  <div class="stat-label">变化率</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Timer /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ formatTime(comparison.processing_time) }}</div>
                  <div class="stat-label">处理时间</div>
                </div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Calendar /></el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ formatDate(comparison.timestamp) }}</div>
                  <div class="stat-label">比对时间</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 差异分析 -->
      <el-card class="analysis-card">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>差异分析</span>
          </div>
        </template>

        <div class="analysis-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-container">
                <h4>差异类型分布</h4>
                <div ref="diffChartRef" class="chart"></div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-container">
                <h4>相似度分布</h4>
                <div ref="similarityChartRef" class="chart"></div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 可视化选项 -->
      <el-card class="visualization-card">
        <template #header>
          <div class="card-header">
            <el-icon><Picture /></el-icon>
            <span>可视化输出</span>
          </div>
        </template>

        <div class="visualization-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="viz-option">
                <h4>高亮PDF</h4>
                <p>生成差异高亮的PDF文件</p>
                <el-button 
                  type="primary" 
                  :loading="highlightLoading"
                  @click="generateHighlight"
                >
                  <el-icon><Document /></el-icon>
                  生成高亮PDF
                </el-button>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="viz-option">
                <h4>差异图像</h4>
                <p>生成差异可视化图像</p>
                <el-button 
                  type="success" 
                  :loading="renderLoading"
                  @click="generateRender"
                >
                  <el-icon><Picture /></el-icon>
                  生成差异图
                </el-button>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="viz-option">
                <h4>分析报告</h4>
                <p>生成详细的分析报告</p>
                <el-button 
                  type="warning" 
                  :loading="reportLoading"
                  @click="generateReport"
                >
                  <el-icon><DocumentCopy /></el-icon>
                  生成报告
                </el-button>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 输出文件列表 -->
      <el-card v-if="hasOutputFiles" class="files-card">
        <template #header>
          <div class="card-header">
            <el-icon><Folder /></el-icon>
            <span>输出文件</span>
          </div>
        </template>

        <div class="files-content">
          <div 
            v-for="(filePath, type) in comparison.output_files" 
            :key="type"
            class="file-item"
          >
            <div class="file-info">
              <el-icon class="file-icon">
                <Document v-if="type.includes('pdf')" />
                <Picture v-else-if="type.includes('image')" />
                <DocumentCopy v-else />
              </el-icon>
              <div class="file-details">
                <div class="file-name">{{ getFileName(filePath) }}</div>
                <div class="file-type">{{ getFileTypeName(type) }}</div>
              </div>
            </div>
            <div class="file-actions">
              <el-button 
                type="primary" 
                size="small"
                :icon="Download"
                @click="downloadFile(filePath)"
              >
                下载
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useComparisonStore } from '@/stores/comparison'
import { ElMessage } from 'element-plus'
import { 
  Loading, Warning, Document, Download, DocumentCopy, Files, 
  Connection, TrendCharts, PieChart, Timer, Calendar, Picture, Folder
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const comparisonStore = useComparisonStore()

// 响应式数据
const diffChartRef = ref()
const similarityChartRef = ref()
const highlightLoading = ref(false)
const renderLoading = ref(false)
const reportLoading = ref(false)

// 计算属性
const comparisonId = computed(() => route.params.id)
const comparison = computed(() => comparisonStore.currentComparison)
const loading = computed(() => comparisonStore.loading)
const error = computed(() => comparisonStore.error)

const hasOutputFiles = computed(() => {
  return comparison.value?.output_files && Object.keys(comparison.value.output_files).length > 0
})

// 方法
const loadComparison = async () => {
  try {
    await comparisonStore.getComparison(comparisonId.value)
    await nextTick()
    initCharts()
  } catch (err) {
    console.error('加载比对结果失败:', err)
  }
}

const initCharts = () => {
  if (!comparison.value) return

  // 差异类型分布图
  if (diffChartRef.value) {
    const diffChart = echarts.init(diffChartRef.value)
    const diffData = [
      { value: comparison.value.total_differences || 0, name: '总差异' },
      { value: comparison.value.matched_pairs || 0, name: '匹配' },
      { value: (comparison.value.elements_a_count || 0) + (comparison.value.elements_b_count || 0) - (comparison.value.matched_pairs || 0) * 2, name: '未匹配' }
    ]
    
    diffChart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      series: [{
        name: '差异分布',
        type: 'pie',
        radius: '70%',
        data: diffData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }

  // 相似度分布图
  if (similarityChartRef.value) {
    const similarityChart = echarts.init(similarityChartRef.value)
    const similarity = comparison.value.average_similarity || 0
    
    similarityChart.setOption({
      tooltip: {
        formatter: '{a} <br/>{b}: {c}%'
      },
      series: [{
        name: '相似度',
        type: 'gauge',
        radius: '80%',
        data: [{
          value: Math.round(similarity * 100),
          name: '相似度'
        }],
        axisLine: {
          lineStyle: {
            width: 10,
            color: [
              [0.3, '#FF6E76'],
              [0.7, '#FDDD60'],
              [1, '#58D9F9']
            ]
          }
        },
        pointer: {
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: {
          distance: -30,
          splitNumber: 5,
          lineStyle: {
            width: 2,
            color: '#999'
          }
        },
        splitLine: {
          distance: -30,
          length: 30,
          lineStyle: {
            width: 4,
            color: '#999'
          }
        },
        axisLabel: {
          color: 'auto',
          distance: 40,
          fontSize: 12
        },
        detail: {
          valueAnimation: true,
          formatter: '{value}%',
          color: 'auto',
          fontSize: 20
        }
      }]
    })
  }
}

const generateHighlight = async () => {
  highlightLoading.value = true
  try {
    await comparisonStore.generateHighlight(comparisonId.value, {
      highlight_style: 'solid',
      include_legend: true
    })
    ElMessage.success('高亮PDF生成成功!')
  } catch (err) {
    ElMessage.error(err.message || '生成高亮PDF失败')
  } finally {
    highlightLoading.value = false
  }
}

const generateRender = async () => {
  renderLoading.value = true
  try {
    await comparisonStore.generateRender(comparisonId.value, {
      chart_types: ['summary', 'heatmap'],
      render_format: 'png'
    })
    ElMessage.success('差异图像生成成功!')
  } catch (err) {
    ElMessage.error(err.message || '生成差异图像失败')
  } finally {
    renderLoading.value = false
  }
}

const generateReport = async () => {
  reportLoading.value = true
  try {
    await comparisonStore.generateReport(comparisonId.value, {
      report_format: 'excel',
      report_level: 'detailed',
      include_charts: true,
      include_images: true
    })
    ElMessage.success('分析报告生成成功!')
    router.push(`/report/${comparisonId.value}`)
  } catch (err) {
    ElMessage.error(err.message || '生成报告失败')
  } finally {
    reportLoading.value = false
  }
}

const downloadResults = () => {
  if (comparison.value?.output_files) {
    Object.values(comparison.value.output_files).forEach(filePath => {
      comparisonStore.downloadFile(filePath)
    })
  }
}

const downloadFile = (filePath) => {
  comparisonStore.downloadFile(filePath)
}

const goBack = () => {
  router.push('/')
}

const formatSimilarity = (similarity) => {
  return similarity ? `${(similarity * 100).toFixed(1)}%` : '0%'
}

const formatChangeRate = (rate) => {
  return rate ? `${(rate * 100).toFixed(1)}%` : '0%'
}

const formatTime = (time) => {
  return time ? `${(time * 1000).toFixed(0)}ms` : '0ms'
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getFileName = (filePath) => {
  return filePath.split('/').pop() || '未知文件'
}

const getFileTypeName = (type) => {
  const typeMap = {
    'json': 'JSON结果',
    'highlighted_pdf': '高亮PDF',
    'diff_image': '差异图像',
    'report': '分析报告'
  }
  return typeMap[type] || '未知类型'
}

// 生命周期
onMounted(() => {
  loadComparison()
})
</script>

<style scoped>
.comparison-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.loading-container,
.error-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-card,
.error-card {
  text-align: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.loading-icon,
.error-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.loading-icon {
  color: #409eff;
  animation: spin 1s linear infinite;
}

.error-icon {
  color: #f56c6c;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.overview-card,
.analysis-card,
.visualization-card,
.files-card {
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.overview-content {
  padding: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: #e3f2fd;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.stat-icon {
  font-size: 2rem;
  color: #409eff;
  margin-right: 15px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
  font-size: 0.9rem;
}

.analysis-content {
  padding: 20px 0;
}

.chart-container {
  text-align: center;
}

.chart-container h4 {
  margin-bottom: 20px;
  color: #303133;
}

.chart {
  height: 300px;
  width: 100%;
}

.visualization-content {
  padding: 20px 0;
}

.viz-option {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.viz-option:hover {
  background: #e3f2fd;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.viz-option h4 {
  margin-bottom: 10px;
  color: #303133;
}

.viz-option p {
  color: #606266;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.files-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.file-item:hover {
  background: #e3f2fd;
  border-color: #409eff;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  font-size: 1.5rem;
  color: #409eff;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.file-type {
  color: #909399;
  font-size: 0.9rem;
}

.file-actions {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .overview-content .el-row {
    margin: 0 !important;
  }
  
  .overview-content .el-col {
    margin-bottom: 15px;
  }
  
  .analysis-content .el-col {
    margin-bottom: 20px;
  }
  
  .visualization-content .el-col {
    margin-bottom: 20px;
  }
  
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .file-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
