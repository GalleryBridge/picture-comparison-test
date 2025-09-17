<template>
  <div class="report-container">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-card class="loading-card">
        <div class="loading-content">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <h3>正在生成报告...</h3>
          <p>请稍候，系统正在生成详细的分析报告</p>
        </div>
      </el-card>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <el-card class="error-card">
        <div class="error-content">
          <el-icon class="error-icon"><Warning /></el-icon>
          <h3>报告生成失败</h3>
          <p>{{ error }}</p>
          <el-button type="primary" @click="goBack">返回比对结果</el-button>
        </div>
      </el-card>
    </div>

    <!-- 报告内容 -->
    <div v-else-if="comparison" class="report-content">
      <!-- 报告头部 -->
      <el-card class="report-header">
        <div class="header-content">
          <div class="report-title">
            <h1>PDF图纸比对分析报告</h1>
            <p class="report-subtitle">基于传统算法的高精度比对分析</p>
          </div>
          <div class="report-meta">
            <div class="meta-item">
              <span class="meta-label">比对ID:</span>
              <span class="meta-value">{{ comparison.comparison_id }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">生成时间:</span>
              <span class="meta-value">{{ formatDate(comparison.timestamp) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">处理时间:</span>
              <span class="meta-value">{{ formatTime(comparison.processing_time) }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 执行摘要 -->
      <el-card class="summary-card">
        <template #header>
          <div class="card-header">
            <el-icon><Document /></el-icon>
            <span>执行摘要</span>
          </div>
        </template>

        <div class="summary-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="summary-item">
                <h4>比对概况</h4>
                <p>本次比对分析了两个PDF文件，共检测到 <strong>{{ comparison.total_differences || 0 }}</strong> 个差异，匹配了 <strong>{{ comparison.matched_pairs || 0 }}</strong> 对图元。</p>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="summary-item">
                <h4>相似度分析</h4>
                <p>两个文件的平均相似度为 <strong>{{ formatSimilarity(comparison.average_similarity) }}</strong>，变化率为 <strong>{{ formatChangeRate(comparison.change_rate) }}</strong>。</p>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 详细统计 -->
      <el-card class="statistics-card">
        <template #header>
          <div class="card-header">
            <el-icon><PieChart /></el-icon>
            <span>详细统计</span>
          </div>
        </template>

        <div class="statistics-content">
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ comparison.elements_a_count || 0 }}</div>
                  <div class="stat-label">文件A图元数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ comparison.elements_b_count || 0 }}</div>
                  <div class="stat-label">文件B图元数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ comparison.matched_pairs || 0 }}</div>
                  <div class="stat-label">匹配对数</div>
                </div>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ comparison.total_differences || 0 }}</div>
                  <div class="stat-label">总差异数</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ formatSimilarity(comparison.average_similarity) }}</div>
                  <div class="stat-label">平均相似度</div>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-item">
                <div class="stat-icon">
                  <el-icon><PieChart /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ formatChangeRate(comparison.change_rate) }}</div>
                  <div class="stat-label">变化率</div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 可视化图表 -->
      <el-card class="charts-card">
        <template #header>
          <div class="card-header">
            <el-icon><Picture /></el-icon>
            <span>可视化分析</span>
          </div>
        </template>

        <div class="charts-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="chart-container">
                <h4>差异类型分布</h4>
                <div ref="diffChartRef" class="chart"></div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-container">
                <h4>相似度分析</h4>
                <div ref="similarityChartRef" class="chart"></div>
              </div>
            </el-col>
          </el-row>

          <el-row :gutter="20" style="margin-top: 20px;">
            <el-col :span="12">
              <div class="chart-container">
                <h4>图元数量对比</h4>
                <div ref="comparisonChartRef" class="chart"></div>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-container">
                <h4>处理时间分析</h4>
                <div ref="timeChartRef" class="chart"></div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 技术细节 -->
      <el-card class="technical-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            <span>技术细节</span>
          </div>
        </template>

        <div class="technical-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="tech-section">
                <h4>比对算法</h4>
                <ul>
                  <li>基于传统几何算法的精确比对</li>
                  <li>R-Tree空间索引优化</li>
                  <li>多维度相似度计算</li>
                  <li>智能容差匹配</li>
                </ul>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="tech-section">
                <h4>性能指标</h4>
                <ul>
                  <li>处理时间: {{ formatTime(comparison.processing_time) }}</li>
                  <li>匹配精度: 工业级精度</li>
                  <li>支持格式: PDF矢量图形</li>
                  <li>输出格式: 多种可视化格式</li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <!-- 结论和建议 -->
      <el-card class="conclusion-card">
        <template #header>
          <div class="card-header">
            <el-icon><DocumentCopy /></el-icon>
            <span>结论和建议</span>
          </div>
        </template>

        <div class="conclusion-content">
          <div class="conclusion-item">
            <h4>比对结论</h4>
            <p v-if="comparison.average_similarity > 0.95">
              两个PDF文件具有<strong>极高的相似度</strong>，差异很小，可以认为是基本一致的文件。
            </p>
            <p v-else-if="comparison.average_similarity > 0.8">
              两个PDF文件具有<strong>较高的相似度</strong>，存在一些差异，建议仔细检查差异内容。
            </p>
            <p v-else-if="comparison.average_similarity > 0.5">
              两个PDF文件具有<strong>中等相似度</strong>，存在较多差异，需要重点关注。
            </p>
            <p v-else>
              两个PDF文件<strong>相似度较低</strong>，存在大量差异，可能是不同的文件版本。
            </p>
          </div>

          <div class="conclusion-item">
            <h4>建议措施</h4>
            <ul>
              <li v-if="comparison.total_differences > 0">建议详细检查所有差异点，确认是否为预期变更</li>
              <li v-if="comparison.change_rate > 0.1">变化率较高，建议进行版本控制管理</li>
              <li>建议定期进行文件比对，确保文档一致性</li>
              <li>对于重要文档，建议建立标准化的比对流程</li>
            </ul>
          </div>
        </div>
      </el-card>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button 
          type="primary" 
          size="large"
          :icon="Download"
          @click="downloadReport"
        >
          下载报告
        </el-button>
        <el-button 
          type="success" 
          size="large"
          :icon="Printer"
          @click="printReport"
        >
          打印报告
        </el-button>
        <el-button 
          type="info" 
          size="large"
          :icon="Back"
          @click="goBack"
        >
          返回比对结果
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useComparisonStore } from '@/stores/comparison'
import { ElMessage } from 'element-plus'
import { 
  Loading, Warning, Document, PieChart, Picture, Setting, 
  DocumentCopy, Download, Printer, Back, Files, Connection, 
  TrendCharts
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const comparisonStore = useComparisonStore()

// 响应式数据
const diffChartRef = ref()
const similarityChartRef = ref()
const comparisonChartRef = ref()
const timeChartRef = ref()

// 计算属性
const comparisonId = computed(() => route.params.id)
const comparison = computed(() => comparisonStore.currentComparison)
const loading = computed(() => comparisonStore.loading)
const error = computed(() => comparisonStore.error)

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
      { value: comparison.value.total_differences || 0, name: '差异' },
      { value: comparison.value.matched_pairs || 0, name: '匹配' }
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

  // 相似度分析图
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

  // 图元数量对比图
  if (comparisonChartRef.value) {
    const comparisonChart = echarts.init(comparisonChartRef.value)
    
    comparisonChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      xAxis: {
        type: 'category',
        data: ['文件A', '文件B']
      },
      yAxis: {
        type: 'value'
      },
      series: [{
        name: '图元数量',
        type: 'bar',
        data: [
          comparison.value.elements_a_count || 0,
          comparison.value.elements_b_count || 0
        ],
        itemStyle: {
          color: '#409eff'
        }
      }]
    })
  }

  // 处理时间分析图
  if (timeChartRef.value) {
    const timeChart = echarts.init(timeChartRef.value)
    const processingTime = comparison.value.processing_time || 0
    
    timeChart.setOption({
      tooltip: {
        formatter: '{a} <br/>{b}: {c}秒'
      },
      series: [{
        name: '处理时间',
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: processingTime, name: '处理时间' },
          { value: Math.max(0, 1 - processingTime), name: '空闲时间' }
        ],
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
}

const downloadReport = () => {
  if (comparison.value?.output_files?.report) {
    comparisonStore.downloadFile(comparison.value.output_files.report)
  } else {
    ElMessage.warning('报告文件尚未生成')
  }
}

const printReport = () => {
  window.print()
}

const goBack = () => {
  router.push(`/comparison/${comparisonId.value}`)
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

// 生命周期
onMounted(() => {
  loadComparison()
})
</script>

<style scoped>
.report-container {
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

.report-header,
.summary-card,
.statistics-card,
.charts-card,
.technical-card,
.conclusion-card {
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

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-title h1 {
  color: #303133;
  margin-bottom: 10px;
}

.report-subtitle {
  color: #606266;
  font-size: 1.1rem;
}

.report-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.meta-item {
  display: flex;
  gap: 10px;
}

.meta-label {
  color: #909399;
  font-weight: 500;
}

.meta-value {
  color: #303133;
  font-weight: 600;
}

.summary-content {
  padding: 20px 0;
}

.summary-item h4 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.summary-item p {
  color: #606266;
  line-height: 1.6;
}

.statistics-content {
  padding: 20px 0;
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.stat-item:hover {
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

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 700;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  color: #606266;
  font-size: 0.9rem;
}

.charts-content {
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

.technical-content {
  padding: 20px 0;
}

.tech-section h4 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.tech-section ul {
  color: #606266;
  line-height: 1.8;
  padding-left: 20px;
}

.conclusion-content {
  padding: 20px 0;
}

.conclusion-item {
  margin-bottom: 30px;
}

.conclusion-item h4 {
  color: #303133;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.conclusion-item p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 15px;
}

.conclusion-item ul {
  color: #606266;
  line-height: 1.8;
  padding-left: 20px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 30px 0;
}

/* 打印样式 */
@media print {
  .action-buttons {
    display: none;
  }
  
  .report-container {
    padding: 0;
  }
  
  .report-header,
  .summary-card,
  .statistics-card,
  .charts-card,
  .technical-card,
  .conclusion-card {
    break-inside: avoid;
    margin-bottom: 20px;
    box-shadow: none;
    border: 1px solid #ddd;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .statistics-content .el-row {
    margin: 0 !important;
  }
  
  .statistics-content .el-col {
    margin-bottom: 15px;
  }
  
  .charts-content .el-col {
    margin-bottom: 20px;
  }
  
  .technical-content .el-col {
    margin-bottom: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}
</style>
