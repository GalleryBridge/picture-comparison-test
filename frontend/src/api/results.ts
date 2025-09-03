import api from './index'

export interface Dimension {
  page?: number
  value: string
  unit: string
  tolerance?: string
  position: { x: number; y: number }
  confidence: number
}

export interface PageResult {
  page_number: number
  image_path: string
  dimensions_count: number
}

export interface AnalysisResult {
  id: string
  filename: string
  file_size: number
  page_count: number
  dimensions: Dimension[]
  pages: PageResult[]
  created_at: string
  processing_time: number
  status: string
}

export interface ResultsListResponse {
  results: AnalysisResult[]
  pagination: {
    page: number
    size: number
    total: number
    pages: number
  }
}

export interface PageResultDetail {
  result_id: string
  page_number: number
  image_path: string
  dimensions: Dimension[]
}

/**
 * 获取分析结果列表
 */
export const getResultsList = async (page = 1, size = 20): Promise<ResultsListResponse> => {
  return api.get('/results/', {
    params: { page, size }
  })
}

/**
 * 获取单个分析结果详情
 */
export const getResultDetail = async (resultId: string): Promise<AnalysisResult> => {
  return api.get(`/results/${resultId}`)
}

/**
 * 获取特定页面的分析结果
 */
export const getPageResult = async (resultId: string, pageNumber: number): Promise<PageResultDetail> => {
  return api.get(`/results/${resultId}/pages/${pageNumber}`)
}

/**
 * 删除分析结果
 */
export const deleteResult = async (resultId: string): Promise<{ message: string }> => {
  return api.delete(`/results/${resultId}`)
}
