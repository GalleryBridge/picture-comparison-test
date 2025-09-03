import api from './index'

export interface UploadResponse {
  file_id: string
  filename: string
  file_size: number
  page_count: number
  status: string
  message: string
  result?: any
}

export interface UploadStatusResponse {
  file_id: string
  status: string
  message: string
}

/**
 * 上传PDF文件
 */
export const uploadPDF = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData()
  formData.append('file', file)
  
  return api.post('/upload/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 获取上传状态
 */
export const getUploadStatus = async (fileId: string): Promise<UploadStatusResponse> => {
  return api.get(`/upload/status/${fileId}`)
}
