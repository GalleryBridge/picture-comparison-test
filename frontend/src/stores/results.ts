import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { AnalysisResultInfo, PaginationInfo } from '@/types'
import { getResultsList, getResultDetail, deleteResult } from '@/api/results'

export const useResultsStore = defineStore('results', () => {
  // 状态
  const results = ref<AnalysisResultInfo[]>([])
  const currentResult = ref<AnalysisResultInfo | null>(null)
  const pagination = ref<PaginationInfo>({
    page: 1,
    size: 20,
    total: 0,
    pages: 0
  })
  const loading = ref(false)
  const searchKeyword = ref('')

  // 计算属性
  const filteredResults = computed(() => {
    if (!searchKeyword.value) return results.value
    
    return results.value.filter(result =>
      result.filename.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  })

  const totalDimensions = computed(() => {
    return results.value.reduce((sum, result) => sum + result.totalDimensions, 0)
  })

  const completedResults = computed(() => {
    return results.value.filter(result => result.status === 'completed')
  })

  // 方法
  const fetchResults = async (page = 1, size = 20) => {
    try {
      loading.value = true
      const response = await getResultsList(page, size)
      
      // 转换数据格式
      results.value = response.results.map(item => ({
        id: item.id,
        filename: item.filename,
        fileSize: item.file_size,
        pageCount: item.page_count,
        totalDimensions: item.dimensions?.length || 0,
        pages: item.pages?.map(page => ({
          pageNumber: page.page_number,
          imagePath: page.image_path,
          dimensionsCount: page.dimensions_count,
          dimensions: []
        })) || [],
        createdAt: item.created_at,
        processingTime: item.processing_time,
        status: item.status as any
      }))
      
      pagination.value = response.pagination
      
    } catch (error) {
      console.error('获取结果列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const fetchResultDetail = async (resultId: string) => {
    try {
      loading.value = true
      const result = await getResultDetail(resultId)
      
      // 转换数据格式
      currentResult.value = {
        id: result.id,
        filename: result.filename,
        fileSize: result.file_size,
        pageCount: result.page_count,
        totalDimensions: result.dimensions?.length || 0,
        pages: result.pages?.map(page => ({
          pageNumber: page.page_number,
          imagePath: page.image_path,
          dimensionsCount: page.dimensions_count,
          dimensions: result.dimensions?.filter(d => d.page === page.page_number) || []
        })) || [],
        createdAt: result.created_at,
        processingTime: result.processing_time,
        status: result.status as any
      }
      
      return currentResult.value
      
    } catch (error) {
      console.error('获取结果详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteResultById = async (resultId: string) => {
    try {
      await deleteResult(resultId)
      
      // 从列表中移除
      const index = results.value.findIndex(r => r.id === resultId)
      if (index > -1) {
        results.value.splice(index, 1)
      }
      
      // 如果是当前查看的结果，清空
      if (currentResult.value?.id === resultId) {
        currentResult.value = null
      }
      
    } catch (error) {
      console.error('删除结果失败:', error)
      throw error
    }
  }

  const setSearchKeyword = (keyword: string) => {
    searchKeyword.value = keyword
  }

  const clearCurrentResult = () => {
    currentResult.value = null
  }

  const refreshResults = async () => {
    await fetchResults(pagination.value.page, pagination.value.size)
  }

  // 分页相关
  const goToPage = async (page: number) => {
    if (page >= 1 && page <= pagination.value.pages) {
      await fetchResults(page, pagination.value.size)
    }
  }

  const changePageSize = async (size: number) => {
    await fetchResults(1, size)
  }

  return {
    // 状态
    results,
    currentResult,
    pagination,
    loading,
    searchKeyword,
    
    // 计算属性
    filteredResults,
    totalDimensions,
    completedResults,
    
    // 方法
    fetchResults,
    fetchResultDetail,
    deleteResultById,
    setSearchKeyword,
    clearCurrentResult,
    refreshResults,
    goToPage,
    changePageSize
  }
})
