<template>
  <div class="result-detail-container">
    <div v-if="resultsStore.loading" class="loading-section">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="result" class="detail-content">
      <!-- 头部信息 -->
      <div class="detail-header">
        <div class="header-info">
          <el-button 
            :icon="ArrowLeft" 
            @click="$router.back()"
            circle
          />
          <div class="title-section">
            <h1>{{ result.filename }}</h1>
            <div class="meta-info">
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatDate(result.createdAt) }}
              </span>
              <span class="meta-item">
                <el-icon><Timer /></el-icon>
                处理时间: {{ result.processingTime }}s
              </span>
              <el-tag 
                :type="getStatusType(result.status)"
                size="large"
              >
                {{ getStatusText(result.status) }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div class="header-actions">
          <el-button :icon="Refresh" @click="refreshResult">
            刷新
          </el-button>
          <el-button :icon="Download">
            下载结果
          </el-button>
          <el-dropdown @command="handleAction">
            <el-button>
              更多操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="reanalyze">重新分析</el-dropdown-item>
                <el-dropdown-item command="export-json">导出JSON</el-dropdown-item>
                <el-dropdown-item command="export-csv">导出CSV</el-dropdown-item>
                <el-dropdown-item command="delete" divided>删除结果</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 统计概览 -->
      <div class="overview-section">
        <div class="overview-cards">
          <div class="overview-card">
            <div class="card-icon">
              <el-icon><Files /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ result.pageCount }}</div>
              <div class="card-label">总页数</div>
            </div>
          </div>
          
          <div class="overview-card">
            <div class="card-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ result.totalDimensions }}</div>
              <div class="card-label">识别尺寸</div>
            </div>
          </div>
          
          <div class="overview-card">
            <div class="card-icon">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ avgConfidence }}%</div>
              <div class="card-label">平均置信度</div>
            </div>
          </div>
          
          <div class="overview-card">
            <div class="card-icon">
              <el-icon><DocumentCopy /></el-icon>
            </div>
            <div class="card-content">
              <div class="card-number">{{ formatFileSize(result.fileSize) }}</div>
              <div class="card-label">文件大小</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 页面导航 -->
      <div class="pages-navigation">
        <el-card>
          <template #header>
            <span>页面导航</span>
          </template>
          
          <div class="pages-tabs">
            <div 
              v-for="page in result.pages" 
              :key="page.pageNumber"
              class="page-tab"
              :class="{ active: currentPage === page.pageNumber }"
              @click="currentPage = page.pageNumber"
            >
              <div class="tab-title">第 {{ page.pageNumber }} 页</div>
              <div class="tab-meta">{{ page.dimensionsCount }} 个尺寸</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 页面详情 -->
      <div class="page-detail-section">
        <el-row :gutter="20">
          <!-- 图像预览 -->
          <el-col :xs="24" :lg="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>图像预览 - 第 {{ currentPage }} 页</span>
                  <div class="image-controls">
                    <el-button-group size="small">
                      <el-button :icon="ZoomOut" @click="zoomOut" />
                      <el-button @click="resetZoom">{{ Math.round(zoomLevel * 100) }}%</el-button>
                      <el-button :icon="ZoomIn" @click="zoomIn" />
                    </el-button-group>
                  </div>
                </div>
              </template>
              
              <div class="image-container">
                <div 
                  class="image-wrapper"
                  :style="{ transform: `scale(${zoomLevel})` }"
                >
                  <img 
                    :src="currentPageData?.imagePath" 
                    :alt="`第${currentPage}页`"
                    class="page-image"
                    @load="onImageLoad"
                  />
                  
                  <!-- 尺寸标注点 -->
                  <div 
                    v-for="(dimension, index) in currentPageDimensions" 
                    :key="index"
                    class="dimension-marker"
                    :style="getDimensionStyle(dimension)"
                    @click="selectDimension(index)"
                  >
                    <div class="marker-dot"></div>
                    <div class="marker-label">{{ dimension.value }}{{ dimension.unit }}</div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 尺寸列表 -->
          <el-col :xs="24" :lg="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>尺寸信息 ({{ currentPageDimensions.length }})</span>
                  <el-input
                    v-model="dimensionSearch"
                    placeholder="搜索尺寸..."
                    size="small"
                    style="width: 200px"
                    clearable
                  />
                </div>
              </template>
              
              <div class="dimensions-list">
                <div 
                  v-for="(dimension, index) in filteredDimensions" 
                  :key="index"
                  class="dimension-item"
                  :class="{ selected: selectedDimension === index }"
                  @click="selectDimension(index)"
                >
                  <div class="dimension-info">
                    <div class="dimension-value">
                      {{ dimension.value }}{{ dimension.unit }}
                      <span v-if="dimension.tolerance" class="tolerance">
                        {{ dimension.tolerance }}
                      </span>
                    </div>
                    <div class="dimension-meta">
                      <span class="confidence">
                        置信度: {{ Math.round(dimension.confidence * 100) }}%
                      </span>
                      <span class="position">
                        位置: ({{ dimension.position.x }}, {{ dimension.position.y }})
                      </span>
                    </div>
                  </div>
                  
                  <div class="dimension-actions">
                    <el-button size="small" type="text">
                      编辑
                    </el-button>
                  </div>
                </div>

                <div v-if="filteredDimensions.length === 0" class="empty-dimensions">
                  <el-empty 
                    description="当前页面暂无尺寸信息" 
                    :image-size="80"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 汇总表格 -->
      <div class="summary-section">
        <el-card>
          <template #header>
            <span>全部尺寸汇总</span>
          </template>
          
          <el-table 
            :data="allDimensions" 
            stripe
            :default-sort="{ prop: 'page', order: 'ascending' }"
          >
            <el-table-column prop="page" label="页码" width="80" sortable />
            <el-table-column prop="value" label="数值" width="100" />
            <el-table-column prop="unit" label="单位" width="80" />
            <el-table-column prop="tolerance" label="公差" width="100">
              <template #default="{ row }">
                {{ row.tolerance || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="置信度" width="100">
              <template #default="{ row }">
                <el-progress 
                  :percentage="Math.round(row.confidence * 100)"
                  :show-text="false"
                  :stroke-width="6"
                />
                <span class="confidence-text">{{ Math.round(row.confidence * 100) }}%</span>
              </template>
            </el-table-column>
            <el-table-column label="位置" min-width="120">
              <template #default="{ row }">
                ({{ row.position.x }}, {{ row.position.y }})
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else class="error-section">
      <el-result
        icon="error"
        title="加载失败"
        sub-title="无法获取分析结果详情"
      >
        <template #extra>
          <el-button type="primary" @click="$router.back()">
            返回列表
          </el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Clock,
  Timer,
  Refresh,
  Download,
  ArrowDown,
  Files,
  DataAnalysis,
  PieChart,
  DocumentCopy,
  ZoomIn,
  ZoomOut
} from '@element-plus/icons-vue'
import { useResultsStore } from '@/stores/results'
import type { AnalysisResultInfo, DimensionInfo, TaskStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const resultsStore = useResultsStore()

// 响应式数据
const currentPage = ref(1)
const selectedDimension = ref<number | null>(null)
const dimensionSearch = ref('')
const zoomLevel = ref(1)

// 计算属性
const result = computed(() => resultsStore.currentResult)

const currentPageData = computed(() => {
  return result.value?.pages.find(p => p.pageNumber === currentPage.value)
})

const currentPageDimensions = computed(() => {
  return currentPageData.value?.dimensions || []
})

const filteredDimensions = computed(() => {
  if (!dimensionSearch.value) return currentPageDimensions.value
  
  return currentPageDimensions.value.filter(d =>
    d.value.includes(dimensionSearch.value) ||
    d.unit.includes(dimensionSearch.value)
  )
})

const allDimensions = computed(() => {
  const dimensions: (DimensionInfo & { page: number })[] = []
  
  result.value?.pages.forEach(page => {
    page.dimensions.forEach(dimension => {
      dimensions.push({
        ...dimension,
        page: page.pageNumber
      })
    })
  })
  
  return dimensions
})

const avgConfidence = computed(() => {
  if (allDimensions.value.length === 0) return 0
  
  const total = allDimensions.value.reduce((sum, d) => sum + d.confidence, 0)
  return Math.round((total / allDimensions.value.length) * 100)
})

// 方法
const refreshResult = async () => {
  try {
    await resultsStore.fetchResultDetail(route.params.id as string)
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

const handleAction = (command: string) => {
  switch (command) {
    case 'reanalyze':
      ElMessage.info('重新分析功能开发中...')
      break
    case 'export-json':
    case 'export-csv':
      ElMessage.info('导出功能开发中...')
      break
    case 'delete':
      // TODO: 实现删除功能
      break
  }
}

const selectDimension = (index: number) => {
  selectedDimension.value = selectedDimension.value === index ? null : index
}

const getDimensionStyle = (dimension: DimensionInfo) => {
  return {
    left: `${dimension.position.x}px`,
    top: `${dimension.position.y}px`
  }
}

const zoomIn = () => {
  zoomLevel.value = Math.min(zoomLevel.value * 1.2, 3)
}

const zoomOut = () => {
  zoomLevel.value = Math.max(zoomLevel.value / 1.2, 0.5)
}

const resetZoom = () => {
  zoomLevel.value = 1
}

const onImageLoad = () => {
  // 图像加载完成后的处理
}

// 工具函数
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusText = (status: TaskStatus): string => {
  const statusMap = {
    pending: '等待中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消'
  }
  return statusMap[status] || '未知'
}

const getStatusType = (status: TaskStatus) => {
  const typeMap = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info'
  }
  return typeMap[status] || 'info'
}

// 监听器
watch(() => route.params.id, async (newId) => {
  if (newId) {
    try {
      await resultsStore.fetchResultDetail(newId as string)
      currentPage.value = 1
    } catch (error) {
      ElMessage.error('获取结果详情失败')
    }
  }
}, { immediate: true })

// 生命周期
onMounted(async () => {
  const resultId = route.params.id as string
  if (resultId && !result.value) {
    try {
      await resultsStore.fetchResultDetail(resultId)
    } catch (error) {
      ElMessage.error('获取结果详情失败')
    }
  }
})
</script>

<style scoped>
.result-detail-container {
  max-width: 1400px;
  margin: 0 auto;
}

.loading-section {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  gap: 20px;
}

.header-info {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.title-section h1 {
  font-size: 24px;
  margin-bottom: 8px;
  color: #333;
}

.meta-info {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.overview-section {
  margin-bottom: 30px;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.overview-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  background: #409EFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.card-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  color: #666;
}

.pages-navigation {
  margin-bottom: 30px;
}

.pages-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.page-tab {
  padding: 12px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  min-width: 100px;
}

.page-tab:hover,
.page-tab.active {
  border-color: #409EFF;
  background-color: #f0f9ff;
}

.tab-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.tab-meta {
  font-size: 12px;
  color: #666;
}

.page-detail-section {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-container {
  position: relative;
  overflow: auto;
  max-height: 600px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
}

.image-wrapper {
  position: relative;
  transform-origin: top left;
  transition: transform 0.3s ease;
}

.page-image {
  width: 100%;
  height: auto;
  display: block;
}

.dimension-marker {
  position: absolute;
  cursor: pointer;
  z-index: 10;
}

.marker-dot {
  width: 8px;
  height: 8px;
  background: #409EFF;
  border: 2px solid white;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.marker-label {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.dimension-marker:hover .marker-label {
  opacity: 1;
}

.dimensions-list {
  max-height: 600px;
  overflow-y: auto;
}

.dimension-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.dimension-item:hover,
.dimension-item.selected {
  background-color: #f8f9fa;
}

.dimension-value {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.tolerance {
  color: #E6A23C;
  font-size: 14px;
}

.dimension-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #666;
}

.confidence {
  color: #67C23A;
}

.empty-dimensions {
  padding: 40px 20px;
  text-align: center;
}

.summary-section {
  margin-bottom: 30px;
}

.confidence-text {
  margin-left: 8px;
  font-size: 12px;
  color: #666;
}

.error-section {
  padding: 60px 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .meta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .pages-tabs {
    justify-content: center;
  }
}
</style>
