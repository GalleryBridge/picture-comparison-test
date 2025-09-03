import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UploadFile } from '@/types'
import { uploadPDF } from '@/api/upload'

export const useUploadStore = defineStore('upload', () => {
  // 状态
  const files = ref<UploadFile[]>([])
  const isUploading = ref(false)

  // 计算属性
  const uploadProgress = computed(() => {
    if (files.value.length === 0) return 0
    const totalProgress = files.value.reduce((sum, file) => sum + file.progress, 0)
    return Math.round(totalProgress / files.value.length)
  })

  const hasActiveUploads = computed(() => {
    return files.value.some(file => 
      file.status === 'uploading' || file.status === 'processing'
    )
  })

  // 方法
  const addFile = (file: File): UploadFile => {
    const uploadFile: UploadFile = {
      id: Date.now().toString(),
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'ready',
      progress: 0
    }
    
    files.value.push(uploadFile)
    return uploadFile
  }

  const updateFileStatus = (fileId: string, status: UploadFile['status'], progress = 0) => {
    const file = files.value.find(f => f.id === fileId)
    if (file) {
      file.status = status
      file.progress = progress
    }
  }

  const updateFileProgress = (fileId: string, progress: number) => {
    const file = files.value.find(f => f.id === fileId)
    if (file) {
      file.progress = progress
    }
  }

  const uploadFile = async (file: File): Promise<string> => {
    const uploadFile = addFile(file)
    
    try {
      isUploading.value = true
      updateFileStatus(uploadFile.id, 'uploading', 10)

      // 上传文件并直接处理
      const response = await uploadPDF(file)
      
      // 直接标记为完成，因为现在是同步处理
      updateFileStatus(uploadFile.id, 'completed', 100)
      
      return response.file_id
      
    } catch (error) {
      updateFileStatus(uploadFile.id, 'failed', 0)
      throw error
    } finally {
      isUploading.value = false
    }
  }



  const removeFile = (fileId: string) => {
    const index = files.value.findIndex(f => f.id === fileId)
    if (index > -1) {
      files.value.splice(index, 1)
    }
  }

  const clearFiles = () => {
    files.value = []
  }

  const retryUpload = async (fileId: string, originalFile: File) => {
    removeFile(fileId)
    return await uploadFile(originalFile)
  }

  return {
    // 状态
    files,
    isUploading,
    
    // 计算属性
    uploadProgress,
    hasActiveUploads,
    
    // 方法
    addFile,
    updateFileStatus,
    updateFileProgress,
    uploadFile,
    removeFile,
    clearFiles,
    retryUpload
  }
})
