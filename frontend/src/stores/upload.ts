import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UploadFile, TaskProgress } from '@/types'
import { uploadPDF, getUploadStatus } from '@/api/upload'
import { getTaskStatus } from '@/api/tasks'

export const useUploadStore = defineStore('upload', () => {
  // 状态
  const files = ref<UploadFile[]>([])
  const currentTaskId = ref<string>('')
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

      // 上传文件
      const response = await uploadPDF(file)
      
      updateFileStatus(uploadFile.id, 'processing', 50)
      uploadFile.taskId = response.task_id
      currentTaskId.value = response.task_id

      // 开始轮询任务状态
      await pollTaskStatus(uploadFile.id, response.task_id)
      
      return response.file_id
      
    } catch (error) {
      updateFileStatus(uploadFile.id, 'failed', 0)
      throw error
    } finally {
      isUploading.value = false
    }
  }

  const pollTaskStatus = async (fileId: string, taskId: string) => {
    const maxAttempts = 120 // 最多轮询2分钟
    let attempts = 0

    const poll = async (): Promise<void> => {
      try {
        const status = await getTaskStatus(taskId)
        
        if (status.state === 'PROGRESS') {
          const progress = status.current && status.total 
            ? Math.round((status.current / status.total) * 100)
            : 50
          updateFileProgress(fileId, Math.max(50, progress))
        } else if (status.state === 'SUCCESS') {
          updateFileStatus(fileId, 'completed', 100)
          return
        } else if (status.state === 'FAILURE') {
          updateFileStatus(fileId, 'failed', 0)
          throw new Error(status.error || '处理失败')
        }

        attempts++
        if (attempts < maxAttempts) {
          setTimeout(poll, 1000) // 1秒后再次轮询
        } else {
          updateFileStatus(fileId, 'failed', 0)
          throw new Error('处理超时')
        }
      } catch (error) {
        updateFileStatus(fileId, 'failed', 0)
        throw error
      }
    }

    await poll()
  }

  const removeFile = (fileId: string) => {
    const index = files.value.findIndex(f => f.id === fileId)
    if (index > -1) {
      files.value.splice(index, 1)
    }
  }

  const clearFiles = () => {
    files.value = []
    currentTaskId.value = ''
  }

  const retryUpload = async (fileId: string, originalFile: File) => {
    removeFile(fileId)
    return await uploadFile(originalFile)
  }

  return {
    // 状态
    files,
    currentTaskId,
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
    retryUpload,
    pollTaskStatus
  }
})
