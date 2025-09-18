<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">PDF图纸比对系统</h1>
        <p class="welcome-subtitle">基于传统算法的高精度PDF图纸比对分析</p>
        <div class="features">
          <div class="feature-item">
            <el-icon class="feature-icon"><Document /></el-icon>
            <span>矢量图形精确比对</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><PieChart /></el-icon>
            <span>智能差异分析</span>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><DocumentCopy /></el-icon>
            <span>详细分析报告</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-section">
      <el-card class="upload-card">
        <template #header>
          <div class="card-header">
            <el-icon><Upload /></el-icon>
            <span>选择PDF文件进行比对</span>
          </div>
        </template>

        <div class="upload-content">
          <!-- 文件A上传 -->
          <div class="file-upload-area">
            <h3>文件A (基准文件)</h3>
            <el-upload
              ref="uploadRefA"
              class="upload-dragger"
              drag
              :auto-upload="false"
              :on-change="handleFileChangeA"
              :before-upload="beforeUpload"
              accept=".pdf"
              :limit="1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将PDF文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持PDF格式，文件大小不超过50MB
                </div>
              </template>
            </el-upload>
            <div v-if="fileA" class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ fileA.name }}</span>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete" 
                @click="removeFileA"
              />
            </div>
          </div>

          <!-- 文件B上传 -->
          <div class="file-upload-area">
            <h3>文件B (对比文件)</h3>
            <el-upload
              ref="uploadRefB"
              class="upload-dragger"
              drag
              :auto-upload="false"
              :on-change="handleFileChangeB"
              :before-upload="beforeUpload"
              accept=".pdf"
              :limit="1"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将PDF文件拖到此处，或<em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持PDF格式，文件大小不超过50MB
                </div>
              </template>
            </el-upload>
            <div v-if="fileB" class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ fileB.name }}</span>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Delete" 
                @click="removeFileB"
              />
            </div>
          </div>
        </div>

        <!-- 比对选项 -->
        <div class="comparison-options">
          <h3>比对选项</h3>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="比对模式">
                <el-select v-model="comparisonOptions.mode" placeholder="选择比对模式">
                  <el-option label="标准模式" value="standard" />
                  <el-option label="严格模式" value="strict" />
                  <el-option label="宽松模式" value="relaxed" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="容差预设">
                <el-select v-model="comparisonOptions.tolerance_preset" placeholder="选择容差预设">
                  <el-option label="标准精度" value="standard" />
                  <el-option label="高精度" value="high" />
                  <el-option label="超高精度" value="ultra_high" />
                  <el-option label="宽松精度" value="loose" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="相似度方法">
                <el-select v-model="comparisonOptions.similarity_method" placeholder="选择相似度方法">
                  <el-option label="加权相似度" value="weighted" />
                  <el-option label="欧几里得距离" value="euclidean" />
                  <el-option label="余弦相似度" value="cosine" />
                  <el-option label="曼哈顿距离" value="manhattan" />
                  <el-option label="雅卡尔相似度" value="jaccard" />
                  <el-option label="豪斯多夫距离" value="hausdorff" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="输出格式">
                <el-checkbox-group v-model="comparisonOptions.output_formats">
                  <el-checkbox label="json">JSON结果</el-checkbox>
                  <el-checkbox label="summary">摘要报告</el-checkbox>
                  <el-checkbox label="detailed">详细报告</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row>
            <el-col :span="24">
              <el-form-item label="可视化选项">
                <el-checkbox v-model="comparisonOptions.include_visualization">包含可视化</el-checkbox>
                <el-checkbox v-model="comparisonOptions.include_report">包含报告</el-checkbox>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 开始比对按钮 -->
        <div class="action-area">
          <el-button 
            type="primary" 
            size="large"
            :loading="loading"
            :disabled="!canStartComparison"
            @click="startComparison"
          >
            <el-icon><Search /></el-icon>开始比对
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 最近比对记录 -->
    <div v-if="hasComparisons" class="recent-section">
      <el-card class="recent-card">
        <template #header>
          <div class="card-header">
            <el-icon><Clock /></el-icon>
            <span>最近比对记录</span>
          </div>
        </template>
        
        <div class="recent-list">
          <div 
            v-for="comparison in recentComparisons" 
            :key="comparison.comparison_id"
            class="recent-item"
            @click="viewComparison(comparison.comparison_id)"
          >
            <div class="recent-info">
              <div class="recent-title">
                {{ comparison.file_a_path?.split('/').pop() || '文件A' }} vs 
                {{ comparison.file_b_path?.split('/').pop() || '文件B' }}
              </div>
              <div class="recent-meta">
                <el-tag :type="getStatusType(comparison.status)" size="small">
                  {{ getStatusText(comparison.status) }}
                </el-tag>
                <span class="recent-time">{{ formatTime(comparison.timestamp) }}</span>
              </div>
            </div>
            <div class="recent-actions">
              <el-button 
                type="primary" 
                size="small" 
                :icon="View"
                @click.stop="viewComparison(comparison.comparison_id)"
              >
                查看
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useComparisonStore } from '@/stores/comparison'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, PieChart, DocumentCopy, Upload, Delete, Search, 
  Clock, View, UploadFilled 
} from '@element-plus/icons-vue'

const router = useRouter()
const comparisonStore = useComparisonStore()

// 响应式数据
const fileA = ref(null)
const fileB = ref(null)
const uploadRefA = ref()
const uploadRefB = ref()

// 比对选项
const comparisonOptions = ref({
  mode: 'standard',
  tolerance_preset: 'standard',
  similarity_method: 'weighted',
  output_formats: ['json'],
  include_visualization: true,
  include_report: false
})

// 计算属性
const loading = computed(() => comparisonStore.loading)
const hasComparisons = computed(() => comparisonStore.hasComparisons)
const recentComparisons = computed(() => comparisonStore.comparisons.slice(0, 5))

const canStartComparison = computed(() => {
  return fileA.value && fileB.value && !loading.value
})

// 方法
const beforeUpload = (file) => {
  const isPDF = file.type === 'application/pdf'
  const isLt50M = file.size / 1024 / 1024 < 50

  if (!isPDF) {
    ElMessage.error('只能上传PDF文件!')
    return false
  }
  if (!isLt50M) {
    ElMessage.error('文件大小不能超过50MB!')
    return false
  }
  return false // 阻止自动上传
}

const handleFileChangeA = (file) => {
  fileA.value = file.raw
}

const handleFileChangeB = (file) => {
  fileB.value = file.raw
}

const removeFileA = () => {
  fileA.value = null
  uploadRefA.value?.clearFiles()
}

const removeFileB = () => {
  fileB.value = null
  uploadRefB.value?.clearFiles()
}

const startComparison = async () => {
  if (!canStartComparison.value) return

  try {
    const result = await comparisonStore.compareFiles(
      fileA.value,
      fileB.value,
      comparisonOptions.value
    )

    ElMessage.success('比对完成!')
    
    // 跳转到比对结果页面
    router.push(`/comparison/${result.comparison_id}`)
  } catch (error) {
    ElMessage.error(error.message || '比对失败')
  }
}

const viewComparison = (comparisonId) => {
  router.push(`/comparison/${comparisonId}`)
}

const getStatusType = (status) => {
  const statusMap = {
    'completed': 'success',
    'processing': 'warning',
    'failed': 'danger',
    'pending': 'info'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    'completed': '已完成',
    'processing': '处理中',
    'failed': '失败',
    'pending': '等待中'
  }
  return statusMap[status] || '未知'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

// 生命周期
onMounted(async () => {
  try {
    await comparisonStore.listComparisons(1, 10)
  } catch (error) {
    console.error('获取比对列表失败:', error)
  }
})
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 60px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  backdrop-filter: blur(10px);
}

.welcome-content {
  color: white;
}

.welcome-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
  background: linear-gradient(45deg, #fff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 1.2rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.features {
  display: flex;
  justify-content: center;
  gap: 40px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.1rem;
}

.feature-icon {
  font-size: 1.5rem;
  color: #409eff;
}

.upload-section {
  margin-bottom: 40px;
}

.upload-card {
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

.upload-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
}

.file-upload-area h3 {
  margin-bottom: 15px;
  color: #606266;
  font-size: 1.1rem;
}

.upload-dragger {
  width: 100%;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.comparison-options {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e4e7ed;
}

.comparison-options h3 {
  margin-bottom: 20px;
  color: #303133;
  font-size: 1.1rem;
}

.action-area {
  text-align: center;
  padding: 20px 0;
}

.recent-section {
  margin-bottom: 40px;
}

.recent-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recent-item:hover {
  background: #e3f2fd;
  border-color: #409eff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
}

.recent-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.recent-time {
  color: #909399;
  font-size: 0.9rem;
}

.recent-actions {
  display: flex;
  gap: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 2rem;
  }
  
  .features {
    flex-direction: column;
    gap: 20px;
  }
  
  .upload-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .recent-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .recent-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
