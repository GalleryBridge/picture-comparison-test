<template>
  <div class="results-container">
    <div class="results-header">
      <h1>分析结果</h1>
      <p>查看和管理您的PDF图纸分析历史记录</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-section">
      <el-card>
        <div class="search-controls">
          <div class="search-input">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文件名..."
              :prefix-icon="Search"
              clearable
              @input="handleSearch"
            />
          </div>
          <div class="search-actions">
            <el-button 
              type="primary" 
              :icon="Refresh"
              @click="refreshResults"
              :loading="resultsStore.loading"
            >
              刷新
            </el-button>
            <el-button 
              :icon="Upload"
              @click="$router.push('/upload')"
            >
              新建分析
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ resultsStore.results.length }}</div>
            <div class="stat-label">总文件数</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ resultsStore.completedResults.length }}</div>
            <div class="stat-label">已完成</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ resultsStore.totalDimensions }}</div>
            <div class="stat-label">识别尺寸</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 结果列表 -->
    <div class="results-section">
      <el-card>
        <template #header>
          <div class="results-header-actions">
            <span>分析结果 ({{ resultsStore.filteredResults.length }})</span>
            <div class="header-actions">
              <el-select 
                v-model="pageSize" 
                @change="handlePageSizeChange"
                style="width: 120px"
              >
                <el-option label="10条/页" :value="10" />
                <el-option label="20条/页" :value="20" />
                <el-option label="50条/页" :value="50" />
              </el-select>
            </div>
          </div>
        </template>

        <div v-loading="resultsStore.loading" class="results-list">
          <div 
            v-for="result in paginatedResults" 
            :key="result.id"
            class="result-item"
            @click="viewResult(result.id)"
          >
            <div class="result-info">
              <div class="result-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="result-details">
                <div class="result-title">{{ result.filename }}</div>
                <div class="result-meta">
                  <span class="meta-item">
                    <el-icon><Files /></el-icon>
                    {{ result.pageCount }} 页
                  </span>
                  <span class="meta-item">
                    <el-icon><DataAnalysis /></el-icon>
                    {{ result.totalDimensions }} 个尺寸
                  </span>
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    {{ formatDate(result.createdAt) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="result-status">
              <el-tag 
                :type="getStatusType(result.status)"
                size="small"
              >
                {{ getStatusText(result.status) }}
              </el-tag>
            </div>

            <div class="result-actions" @click.stop>
              <el-button 
                type="primary" 
                size="small"
                @click="viewResult(result.id)"
              >
                查看详情
              </el-button>
              <el-dropdown @command="handleAction">
                <el-button size="small">
                  更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :command="`reanalyze:${result.id}`">
                      重新分析
                    </el-dropdown-item>
                    <el-dropdown-item :command="`download:${result.id}`">
                      下载结果
                    </el-dropdown-item>
                    <el-dropdown-item 
                      :command="`delete:${result.id}`"
                      divided
                    >
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="resultsStore.filteredResults.length === 0 && !resultsStore.loading" class="empty-state">
            <el-empty 
              description="暂无分析结果"
              :image-size="120"
            >
              <el-button 
                type="primary" 
                @click="$router.push('/upload')"
              >
                开始分析
              </el-button>
            </el-empty>
          </div>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination-section">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="resultsStore.filteredResults.length"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
          />
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Upload,
  Document,
  CircleCheckFilled,
  DataAnalysis,
  Files,
  Clock,
  ArrowDown
} from '@element-plus/icons-vue'
import { useResultsStore } from '@/stores/results'
import type { TaskStatus } from '@/types'

const router = useRouter()
const resultsStore = useResultsStore()

// 响应式数据
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 计算属性
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return resultsStore.filteredResults.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(resultsStore.filteredResults.length / pageSize.value)
})

// 方法
const handleSearch = () => {
  resultsStore.setSearchKeyword(searchKeyword.value)
  currentPage.value = 1
}

const refreshResults = async () => {
  try {
    await resultsStore.refreshResults()
    ElMessage.success('刷新成功')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const viewResult = (resultId: string) => {
  router.push(`/results/${resultId}`)
}

const handleAction = async (command: string) => {
  const [action, resultId] = command.split(':')
  
  switch (action) {
    case 'reanalyze':
      await handleReanalyze(resultId)
      break
    case 'download':
      await handleDownload(resultId)
      break
    case 'delete':
      await handleDelete(resultId)
      break
  }
}

const handleReanalyze = async (resultId: string) => {
  ElMessage.info('重新分析功能开发中...')
}

const handleDownload = async (resultId: string) => {
  ElMessage.info('下载功能开发中...')
}

const handleDelete = async (resultId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个分析结果吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await resultsStore.deleteResultById(resultId)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 工具函数
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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

// 生命周期
onMounted(async () => {
  try {
    await resultsStore.fetchResults()
  } catch (error) {
    ElMessage.error('获取结果列表失败')
  }
})
</script>

<style scoped>
.results-container {
  max-width: 1200px;
  margin: 0 auto;
}

.results-header {
  text-align: center;
  margin-bottom: 30px;
}

.results-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
}

.results-header p {
  color: #666;
  font-size: 16px;
}

.search-section {
  margin-bottom: 20px;
}

.search-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.search-actions {
  display: flex;
  gap: 12px;
}

.stats-section {
  margin-bottom: 30px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  gap: 16px;
}

.stat-icon {
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

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.results-section {
  margin-bottom: 30px;
}

.results-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-list {
  min-height: 400px;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.3s ease;
  gap: 20px;
}

.result-item:hover {
  background-color: #f8f9fa;
}

.result-item:last-child {
  border-bottom: none;
}

.result-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 16px;
}

.result-icon {
  font-size: 32px;
  color: #409EFF;
}

.result-details {
  flex: 1;
}

.result-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.result-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.result-status {
  margin-right: 16px;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .search-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .result-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .results-header-actions {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
}
</style>
