<template>
  <div class="upload-container">
    <div class="upload-header">
      <h1>PDF图纸上传分析</h1>
      <p>上传您的PDF图纸文件，系统将自动识别其中的尺寸标注信息</p>
    </div>

    <!-- 上传区域 -->
    <div class="upload-section">
      <el-card class="upload-card">
        <template #header>
          <div class="card-header">
            <span>文件上传</span>
            <el-button 
              v-if="uploadStore.files.length > 0" 
              type="text" 
              @click="uploadStore.clearFiles"
            >
              清空列表
            </el-button>
          </div>
        </template>

        <!-- 拖拽上传区域 -->
        <div 
          class="upload-dragger"
          :class="{ 'is-dragover': isDragover }"
          @drop="handleDrop"
          @dragover="handleDragover"
          @dragleave="handleDragleave"
          @click="triggerFileInput"
        >
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <div class="upload-text">
            <p>将PDF文件拖拽到此处，或<em>点击上传</em></p>
            <p class="upload-tip">支持单个PDF文件，最大100MB</p>
          </div>
        </div>

        <!-- 隐藏的文件输入 -->
        <input
          ref="fileInput"
          type="file"
          accept=".pdf"
          style="display: none"
          @change="handleFileSelect"
        />
      </el-card>
    </div>

    <!-- 文件列表 -->
    <div v-if="uploadStore.files.length > 0" class="files-section">
      <el-card>
        <template #header>
          <span>上传文件列表</span>
        </template>

        <div class="files-list">
          <div 
            v-for="file in uploadStore.files" 
            :key="file.id" 
            class="file-item"
          >
            <div class="file-info">
              <div class="file-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  {{ formatFileSize(file.size) }} • 
                  <span :class="getStatusClass(file.status)">
                    {{ getStatusText(file.status) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="file-progress">
              <el-progress 
                :percentage="file.progress" 
                :status="getProgressStatus(file.status)"
                :show-text="false"
              />
              <div class="progress-text">{{ file.progress }}%</div>
            </div>

            <div class="file-actions">
              <el-button 
                v-if="file.status === 'failed'" 
                type="primary" 
                size="small"
                @click="retryUpload(file)"
              >
                重试
              </el-button>
              <el-button 
                v-if="file.status === 'completed'" 
                type="success" 
                size="small"
                @click="viewResult(file)"
              >
                查看结果
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="removeFile(file.id)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 处理进度 -->
    <div v-if="uploadStore.hasActiveUploads" class="progress-section">
      <el-card>
        <template #header>
          <span>处理进度</span>
        </template>

        <div class="overall-progress">
          <div class="progress-info">
            <span>总体进度</span>
            <span>{{ uploadStore.uploadProgress }}%</span>
          </div>
          <el-progress 
            :percentage="uploadStore.uploadProgress" 
            :show-text="false"
          />
        </div>

        <div v-if="currentTaskStatus" class="task-status">
          <div class="status-message">
            <el-icon><Loading /></el-icon>
            {{ currentTaskStatus.message }}
          </div>
        </div>
      </el-card>
    </div>

    <!-- 使用说明 -->
    <div class="help-section">
      <el-card>
        <template #header>
          <span>使用说明</span>
        </template>

        <div class="help-content">
          <div class="help-item">
            <el-icon class="help-icon"><InfoFilled /></el-icon>
            <div>
              <h4>支持的文件格式</h4>
              <p>仅支持PDF格式的图纸文件</p>
            </div>
          </div>

          <div class="help-item">
            <el-icon class="help-icon"><WarnTriangleFilled /></el-icon>
            <div>
              <h4>文件大小限制</h4>
              <p>单个文件最大不超过100MB</p>
            </div>
          </div>

          <div class="help-item">
            <el-icon class="help-icon"><CircleCheckFilled /></el-icon>
            <div>
              <h4>识别效果最佳</h4>
              <p>清晰的工程图纸，尺寸标注明确的PDF文件</p>
            </div>
          </div>

          <div class="help-item">
            <el-icon class="help-icon"><Clock /></el-icon>
            <div>
              <h4>处理时间</h4>
              <p>根据PDF页数和复杂度，通常需要1-5分钟</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, 
  Document, 
  Loading, 
  InfoFilled, 
  WarnTriangleFilled, 
  CircleCheckFilled, 
  Clock 
} from '@element-plus/icons-vue'
import { useUploadStore } from '@/stores/upload'
import { getTaskStatus } from '@/api/tasks'
import type { UploadFile, TaskStatusResponse } from '@/types'

const router = useRouter()
const uploadStore = useUploadStore()

// 响应式数据
const fileInput = ref<HTMLInputElement>()
const isDragover = ref(false)
const currentTaskStatus = ref<TaskStatusResponse | null>(null)
const statusPollingTimer = ref<number>()

// 文件拖拽处理
const handleDragover = (e: DragEvent) => {
  e.preventDefault()
  isDragover.value = true
}

const handleDragleave = (e: DragEvent) => {
  e.preventDefault()
  isDragover.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragover.value = false
  
  const files = Array.from(e.dataTransfer?.files || [])
  handleFiles(files)
}

// 文件选择处理
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  handleFiles(files)
  target.value = '' // 清空input，允许重复选择同一文件
}

// 文件处理
const handleFiles = async (files: File[]) => {
  for (const file of files) {
    if (!validateFile(file)) continue
    
    try {
      await uploadStore.uploadFile(file)
      ElMessage.success(`${file.name} 上传成功`)
    } catch (error) {
      ElMessage.error(`${file.name} 上传失败: ${error}`)
    }
  }
}

// 文件验证
const validateFile = (file: File): boolean => {
  if (file.type !== 'application/pdf') {
    ElMessage.error('只支持PDF格式的文件')
    return false
  }
  
  if (file.size > 100 * 1024 * 1024) { // 100MB
    ElMessage.error('文件大小不能超过100MB')
    return false
  }
  
  return true
}

// 工具函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusText = (status: UploadFile['status']): string => {
  const statusMap = {
    ready: '准备上传',
    uploading: '上传中',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status]
}

const getStatusClass = (status: UploadFile['status']): string => {
  const classMap = {
    ready: 'status-ready',
    uploading: 'status-uploading',
    processing: 'status-processing',
    completed: 'status-completed',
    failed: 'status-failed'
  }
  return classMap[status]
}

const getProgressStatus = (status: UploadFile['status']) => {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'exception'
  return undefined
}

// 操作方法
const removeFile = (fileId: string) => {
  uploadStore.removeFile(fileId)
}

const retryUpload = async (file: UploadFile) => {
  // TODO: 需要保存原始File对象才能重试
  ElMessage.info('重试功能开发中...')
}

const viewResult = (file: UploadFile) => {
  // TODO: 跳转到结果详情页
  router.push(`/results/${file.id}`)
}

// 状态轮询
const startStatusPolling = () => {
  if (uploadStore.currentTaskId) {
    statusPollingTimer.value = window.setInterval(async () => {
      try {
        const status = await getTaskStatus(uploadStore.currentTaskId)
        currentTaskStatus.value = status
        
        if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
          stopStatusPolling()
        }
      } catch (error) {
        console.error('获取任务状态失败:', error)
      }
    }, 2000)
  }
}

const stopStatusPolling = () => {
  if (statusPollingTimer.value) {
    clearInterval(statusPollingTimer.value)
    statusPollingTimer.value = undefined
  }
}

// 生命周期
onMounted(() => {
  if (uploadStore.hasActiveUploads) {
    startStatusPolling()
  }
})

onUnmounted(() => {
  stopStatusPolling()
})
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
}

.upload-header {
  text-align: center;
  margin-bottom: 30px;
}

.upload-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
}

.upload-header p {
  color: #666;
  font-size: 16px;
}

.upload-section {
  margin-bottom: 30px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-dragger {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.upload-dragger:hover,
.upload-dragger.is-dragover {
  border-color: #409EFF;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 8px 0;
  color: #606266;
}

.upload-text em {
  color: #409EFF;
  font-style: normal;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
}

.files-section,
.progress-section,
.help-section {
  margin-bottom: 30px;
}

.files-list {
  space-y: 16px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 12px;
}

.file-icon {
  font-size: 24px;
  color: #409EFF;
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: #909399;
}

.file-progress {
  width: 200px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 12px;
  color: #909399;
  min-width: 35px;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.overall-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.task-status {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.help-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.help-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.help-icon {
  font-size: 20px;
  color: #409EFF;
  margin-top: 2px;
}

.help-item h4 {
  margin-bottom: 4px;
  color: #333;
}

.help-item p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* 状态样式 */
.status-ready { color: #909399; }
.status-uploading { color: #409EFF; }
.status-processing { color: #E6A23C; }
.status-completed { color: #67C23A; }
.status-failed { color: #F56C6C; }
</style>
