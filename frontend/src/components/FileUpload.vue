<template>
  <div class="file-upload">
    <el-upload
      ref="uploadRef"
      class="upload-dragger"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :before-upload="beforeUpload"
      :accept="accept"
      :limit="limit"
      :multiple="multiple"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        {{ dragText }}
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ tipText }}
        </div>
      </template>
    </el-upload>
    
    <div v-if="file" class="file-info">
      <div class="file-details">
        <el-icon class="file-icon">
          <Document v-if="file.type === 'application/pdf'" />
          <Picture v-else />
        </el-icon>
        <div class="file-meta">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatFileSize(file.size) }}</div>
        </div>
      </div>
      <el-button 
        type="danger" 
        size="small" 
        :icon="Delete" 
        @click="removeFile"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Picture, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  accept: {
    type: String,
    default: '.pdf'
  },
  limit: {
    type: Number,
    default: 1
  },
  multiple: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: 50 // MB
  },
  dragText: {
    type: String,
    default: '将文件拖到此处，或<em>点击上传</em>'
  },
  tipText: {
    type: String,
    default: '支持PDF格式，文件大小不超过50MB'
  }
})

const emit = defineEmits(['change', 'remove'])

const uploadRef = ref()
const file = ref(null)

const beforeUpload = (file) => {
  const isValidType = props.accept.includes(file.type) || 
    props.accept.split(',').some(ext => file.name.toLowerCase().endsWith(ext.toLowerCase()))
  const isLtMaxSize = file.size / 1024 / 1024 < props.maxSize

  if (!isValidType) {
    ElMessage.error(`只能上传${props.accept}格式的文件!`)
    return false
  }
  if (!isLtMaxSize) {
    ElMessage.error(`文件大小不能超过${props.maxSize}MB!`)
    return false
  }
  return false // 阻止自动上传
}

const handleFileChange = (fileObj) => {
  file.value = fileObj.raw
  emit('change', fileObj.raw)
}

const removeFile = () => {
  file.value = null
  uploadRef.value?.clearFiles()
  emit('remove')
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

defineExpose({
  clearFiles: () => {
    file.value = null
    uploadRef.value?.clearFiles()
  }
})
</script>

<style scoped>
.file-upload {
  width: 100%;
}

.upload-dragger {
  width: 100%;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.file-details {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;
}

.file-icon {
  font-size: 1.5rem;
  color: #409eff;
}

.file-meta {
  flex: 1;
}

.file-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 5px;
  word-break: break-all;
}

.file-size {
  color: #909399;
  font-size: 0.9rem;
}
</style>
