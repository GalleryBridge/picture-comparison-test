// 通用类型定义

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginationParams {
  page: number
  size: number
}

export interface PaginationInfo {
  page: number
  size: number
  total: number
  pages: number
}

// 文件上传相关
export interface UploadFile {
  id: string
  name: string
  size: number
  type: string
  status: 'ready' | 'uploading' | 'processing' | 'completed' | 'failed'
  progress: number
}
// 尺寸信息
export interface DimensionInfo {
  value: string
  unit: string
  tolerance?: string
  position: {
    x: number
    y: number
  }
  confidence: number
  page?: number
}

// PDF页面信息
export interface PDFPageInfo {
  pageNumber: number
  imagePath: string
  dimensionsCount: number
  dimensions: DimensionInfo[]
}

// 分析结果
export interface AnalysisResultInfo {
  id: string
  filename: string
  fileSize: number
  pageCount: number
  totalDimensions: number
  pages: PDFPageInfo[]
  createdAt: string
  processingTime: number
  status: string
}
