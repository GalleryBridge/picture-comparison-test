<template>
  <div class="upload-container">
    <div class="upload-header">
      <div class="logo">
        <el-icon><Document /></el-icon>
        <span>PDF图纸尺寸分析系统</span>
      </div>
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
      </el-card>
    </div>

    <!-- 分析结果展示 -->
    <div v-if="uploadStore.analysisResults.length > 0" class="results-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>分析结果</span>
            <el-button type="text" @click="copyAllResults">复制全部</el-button>
          </div>
        </template>

        <div class="results-list">
          <div
            v-for="(result, index) in uploadStore.analysisResults"
            :key="result.fileId"
            class="result-item"
          >
            <div class="result-header">
              <div class="result-info">
                <el-icon><Document /></el-icon>
                <div>
                  <div class="result-filename">{{ result.fileName }}</div>
                  <div class="result-time">{{ formatTime(result.timestamp) }}</div>
                </div>
              </div>
              <el-button type="text" size="small" @click="copyResult(result)">复制</el-button>
            </div>
            
            <div class="result-content">
              <!-- 处理状态信息 -->
              <div class="status-section" style="margin-bottom: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #409EFF;">
                <h5 style="margin: 0 0 10px 0; color: #333;">📊 分析结果统计</h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                  <div style="padding: 10px; background: white; border-radius: 4px;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">尺寸标注</div>
                    <div style="font-size: 20px; font-weight: bold; color: #409EFF;">
                      {{ getDimensions(result.result).length }} 项
                    </div>
                  </div>
                  <div style="padding: 10px; background: white; border-radius: 4px;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">检查清单</div>
                    <div style="font-size: 20px; font-weight: bold; color: #67C23A;">
                      {{ getTableItems(result.result).length }} 项
                    </div>
                  </div>
                </div>
                
                <div v-if="getDimensions(result.result).length === 0 && getTableItems(result.result).length === 0" 
                     style="padding: 10px; background: #fff3cd; border-radius: 4px; color: #856404;">
                  ⚠️ <strong>AI分析未识别到有效数据</strong><br>
                  可能原因：图纸不够清晰、没有标准格式的尺寸标注或表格
                </div>
                
                <details style="margin-top: 15px;">
                  <summary style="cursor: pointer; color: #409EFF; font-size: 14px;">🔍 查看详细数据结构</summary>
                  <pre style="font-size: 12px; margin-top: 10px; white-space: pre-wrap; background: white; padding: 10px; border-radius: 4px; max-height: 300px; overflow: auto;">{{ JSON.stringify(extractUsefulData(result.result), null, 2) }}</pre>
                </details>
              </div>

              <!-- 按页显示表格 -->
              <div v-for="(pageData, pageIndex) in getDimensionsByPage(result.result)" 
                   :key="pageIndex" 
                   class="page-section">
                
                <div class="page-header">
                  <h3 class="page-title">📄 第 {{ pageData.page_number }} 页分析结果</h3>
                  <div class="page-stats">
                    <span class="stat-item">尺寸标注: {{ pageData.dimensions.length }} 项</span>
                    <span class="stat-item">表格项目: {{ pageData.table_items.length }} 项</span>
                  </div>
                </div>

                <!-- 该页的尺寸标注表格 -->
                <div v-if="pageData.dimensions.length > 0" class="dimensions-section">
                  <h4 class="section-title">🔧 尺寸标注</h4>
                  <el-table 
                    :data="pageData.dimensions"
                    stripe
                    style="width: 100%"
                    size="small"
                  >
                    <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                    <el-table-column prop="value" label="数值" width="80" align="center" />
                    <el-table-column prop="unit" label="单位" width="60" align="center" />
                    <el-table-column prop="tolerance" label="公差" width="80" align="center" />
                    <el-table-column prop="confidence" label="置信度" width="80" align="center">
                      <template #default="scope">
                        <el-tag :type="getConfidenceType(scope.row.confidence)" size="small">
                          {{ (scope.row.confidence * 100).toFixed(0) }}%
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <!-- 该页的表格项目表格 -->
                <div v-if="pageData.table_items.length > 0" class="table-items-section">
                  <h4 class="section-title">📋 检查清单</h4>
                  <el-table 
                    :data="pageData.table_items"
                    stripe
                    style="width: 100%"
                    size="small"
                  >
                    <el-table-column prop="row_number" label="序号" width="60" align="center" />
                    <el-table-column prop="item_name" label="项目名称" min-width="150" show-overflow-tooltip />
                    <el-table-column prop="description" label="项目描述" min-width="200" show-overflow-tooltip />
                    <el-table-column prop="tolerance_value" label="公差值" width="100" align="center" />
                    <el-table-column prop="unit" label="单位" width="60" align="center" />
                    <el-table-column prop="confidence" label="置信度" width="80" align="center">
                      <template #default="scope">
                        <el-tag :type="getConfidenceType(scope.row.confidence)" size="small">
                          {{ (scope.row.confidence * 100).toFixed(0) }}%
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <!-- 该页无数据提示 -->
                <div v-if="pageData.dimensions.length === 0 && pageData.table_items.length === 0" 
                     class="no-page-data" 
                     style="text-align: center; padding: 20px; color: #999; background: #f9f9f9; border-radius: 6px; margin: 10px 0;">
                  📄 第 {{ pageData.page_number }} 页暂无识别到有效数据
                </div>
              </div>

              <!-- 无数据提示 -->
              <div v-if="getDimensions(result.result).length === 0 && getTableItems(result.result).length === 0" 
                   class="no-data-section" 
                   style="text-align: center; padding: 40px; color: #666;">
                <el-icon style="font-size: 48px; color: #ccc;"><Document /></el-icon>
                <h4 style="margin: 16px 0 8px 0; color: #999;">暂无识别到有效数据</h4>
                <p style="margin: 0;">请检查PDF是否包含清晰的尺寸标注或表格信息</p>
              </div>

              <!-- JSON 原始数据 (可折叠) -->
              <div class="raw-json-section">
                <el-collapse v-model="activeCollapse">
                  <el-collapse-item name="json" title="📄 查看完整 JSON 数据">
                    <el-scrollbar max-height="400px">
                      <pre class="json-content">{{ formatJSON(result.result) }}</pre>
                    </el-scrollbar>
                  </el-collapse-item>
                </el-collapse>
              </div>
            </div>
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
              <p>根据PDF页数和复杂度，通常需要1-10分钟</p>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  UploadFilled, 
  Document, 
  InfoFilled, 
  WarnTriangleFilled, 
  CircleCheckFilled, 
  Clock 
} from '@element-plus/icons-vue'
import { useUploadStore } from '@/stores/upload'
import type { UploadFile } from '@/types'

const uploadStore = useUploadStore()

// 响应式数据
const fileInput = ref<HTMLInputElement>()
const isDragover = ref(false)
const activeCollapse = ref<string[]>([]) // 控制折叠面板

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

// 结果处理方法
const formatTime = (timestamp: Date): string => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const extractUsefulData = (result: any): any => {
  if (!result || !result.ai_analysis) {
    return { message: '数据格式错误', data: result }
  }

  const analysis = result.ai_analysis
  const usefulData = {
    file_info: {
      file_id: result.file_id,
      pdf_info: {
        page_count: result.pdf_info?.page_count,
        title: result.pdf_info?.title
      }
    },
    analysis_summary: {
      total_pages: analysis.total_pages,
      total_dimensions: analysis.total_dimensions || 0,
      total_table_items: analysis.total_table_items || 0,
      total_items_found: analysis.summary?.total_items_found || 0
    },
    page_results: []
  }

  // 提取每页的有用信息 - 只包含解析后的数据，不包含原始response
  if (analysis.page_results) {
    usefulData.page_results = analysis.page_results
      .map((page: any) => {
        const pageData: any = {
          page_number: page.page_number,
          image_path: page.image_path ? page.image_path.replace(/.*[\\\/]/, '') : undefined // 只保留文件名
        }

        // 只添加解析出的尺寸标注（parsed_dimensions）
        if (page.parsed_dimensions && page.parsed_dimensions.length > 0) {
          pageData.dimensions = page.parsed_dimensions.map((dim: any) => ({
            value: dim.value,
            unit: dim.unit,
            tolerance: dim.tolerance,
            dimension_type: dim.dimension_type,
            prefix: dim.prefix,
            description: dim.description,
            confidence: dim.confidence
          }))
        }

        // 只添加解析出的表格项目（parsed_table_items）
        if (page.parsed_table_items && page.parsed_table_items.length > 0) {
          pageData.table_items = page.parsed_table_items.map((item: any) => ({
            item_name: item.item_name,
            description: item.description,
            tolerance_value: item.tolerance_value,
            unit: item.unit,
            row_number: item.row_number,
            confidence: item.confidence
          }))
        }

        // 添加统计信息
        pageData.counts = {
          dimensions_count: pageData.dimensions ? pageData.dimensions.length : 0,
          table_items_count: pageData.table_items ? pageData.table_items.length : 0
        }

        return pageData
      })
      .filter((page: any) => page.dimensions || page.table_items) // 只保留有数据的页面
  }

  return usefulData
}

const formatJSON = (obj: any): string => {
  const usefulData = extractUsefulData(obj)
  return JSON.stringify(usefulData, null, 2)
}

const copyResult = async (result: any) => {
  try {
    const usefulData = extractUsefulData(result.result)
    await navigator.clipboard.writeText(JSON.stringify(usefulData, null, 2))
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const copyAllResults = async () => {
  try {
    const allUsefulData = uploadStore.analysisResults.map(r => extractUsefulData(r.result))
    await navigator.clipboard.writeText(JSON.stringify(allUsefulData, null, 2))
    ElMessage.success('全部结果复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 提取尺寸标注数据 - 按页分组
const getDimensionsByPage = (inputData: any): any[] => {
  console.log('🔍 检查输入数据结构:', inputData)
  
  // 智能检测数据结构，支持多种可能的数据路径
  let analysisData = null
  
  // 情况1: 直接就是包含 ai_analysis 的对象
  if (inputData?.ai_analysis) {
    analysisData = inputData.ai_analysis
    console.log('✅ 方式1: 直接从 ai_analysis 获取数据')
  }
  // 情况2: 嵌套在 result 字段中
  else if (inputData?.result?.ai_analysis) {
    analysisData = inputData.result.ai_analysis
    console.log('✅ 方式2: 从 result.ai_analysis 获取数据')
  } 
  // 情况3: 直接就是 page_results 数组
  else if (Array.isArray(inputData)) {
    console.log('✅ 方式3: 直接处理 page_results 数组')
    return inputData.map((page: any, index: number) => ({
      page_number: page.page_number || (index + 1),
      dimensions: page.parsed_dimensions || [],
      table_items: page.parsed_table_items || []
    }))
  }
  else {
    console.log('❌ 无法找到有效的数据结构')
    console.log('📊 输入数据详情:', JSON.stringify(inputData, null, 2))
    return []
  }
  
  if (!analysisData?.page_results) {
    console.log('❌ page_results 不存在')
    console.log('📊 analysisData:', analysisData)
    return []
  }
  
  if (!Array.isArray(analysisData.page_results)) {
    console.log('❌ page_results 不是数组')
    return []
  }
  
  console.log(`📄 找到 ${analysisData.page_results.length} 页数据`)
  
  const pageData = analysisData.page_results.map((page: any, index: number) => {
    console.log(`📄 第${index + 1}页数据:`, page)
    console.log(`📄 第${index + 1}页 parsed_dimensions:`, page.parsed_dimensions)
    
    return {
      page_number: page.page_number || (index + 1),
      dimensions: page.parsed_dimensions || [],
      table_items: page.parsed_table_items || []
    }
  })
  
  console.log('🎯 按页组织的数据:', pageData)
  return pageData
}

// 提取所有尺寸标注数据用于统计
const getDimensions = (resultData: any): any[] => {
  const dimensions: any[] = []
  const pageData = getDimensionsByPage(resultData)
  
  pageData.forEach((page) => {
    page.dimensions.forEach((dim: any) => {
      dimensions.push({
        ...dim,
        page_number: page.page_number
      })
    })
  })
  
  return dimensions
}

// 提取所有表格项目数据用于统计  
const getTableItems = (resultData: any): any[] => {
  const tableItems: any[] = []
  const pageData = getDimensionsByPage(resultData)
  
  pageData.forEach((page) => {
    page.table_items.forEach((item: any) => {
      tableItems.push({
        ...item,
        page_number: page.page_number
      })
    })
  })
  
  return tableItems.sort((a, b) => (a.row_number || 0) - (b.row_number || 0))
}

// 根据置信度获取标签类型
const getConfidenceType = (confidence: number): string => {
  if (confidence >= 0.9) return 'success'
  if (confidence >= 0.7) return 'warning'
  return 'danger'
}
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

/* 头部logo样式 */
.upload-header .logo {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 10px;
}

.upload-header .logo .el-icon {
  margin-right: 12px;
  font-size: 32px;
  color: #409EFF;
}

/* 结果展示区域样式 */
.results-section {
  margin-bottom: 30px;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.result-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-info .el-icon {
  font-size: 20px;
  color: #409EFF;
}

.result-filename {
  font-weight: 600;
  color: #333;
}

.result-time {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.result-content {
  background: #fff;
}

.json-content {
  padding: 16px;
  margin: 0;
  background: #f8f9fa;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #333;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 页面级表格区域样式 */
.page-section {
  margin-bottom: 30px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.page-header {
  background: linear-gradient(135deg, #409EFF 0%, #36a3ff 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.page-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
}

.dimensions-section,
.table-items-section {
  margin: 20px;
  margin-bottom: 25px;
}

.section-title {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.raw-json-section {
  margin-top: 20px;
}

.raw-json-section :deep(.el-collapse-item__header) {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 0 12px;
  font-size: 14px;
  color: #666;
}

.raw-json-section :deep(.el-collapse-item__content) {
  padding: 0;
}

/* 表格样式优化 */
.result-content :deep(.el-table) {
  border-radius: 6px;
  overflow: hidden;
}

.result-content :deep(.el-table__header) {
  background: #f8f9fa;
}

.result-content :deep(.el-table th) {
  background: #f8f9fa;
  color: #333;
  font-weight: 600;
}

.result-content :deep(.el-table td) {
  vertical-align: middle;
}

.result-content :deep(.el-tag--success) {
  background: #f0f9ff;
  color: #0369a1;
  border-color: #7dd3fc;
}

.result-content :deep(.el-tag--warning) {
  background: #fef3c7;
  color: #d97706;
  border-color: #fde047;
}

.result-content :deep(.el-tag--danger) {
  background: #fef2f2;
  color: #dc2626;
  border-color: #fca5a5;
}

/* 状态样式 */
.status-ready { color: #909399; }
.status-uploading { color: #409EFF; }
.status-processing { color: #E6A23C; }
.status-completed { color: #67C23A; }
.status-failed { color: #F56C6C; }
</style>
