import api from './index'

export interface TaskStatusResponse {
  task_id: string
  state: string
  status: string
  current?: number
  total?: number
  message: string
  result?: any
  error?: string
}

export interface ActiveTasksResponse {
  active_tasks: Record<string, any>
  message: string
}

/**
 * 获取任务状态
 */
export const getTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  return api.get(`/tasks/${taskId}`)
}

/**
 * 取消任务
 */
export const cancelTask = async (taskId: string): Promise<{ task_id: string; message: string }> => {
  return api.delete(`/tasks/${taskId}`)
}

/**
 * 获取活跃任务列表
 */
export const getActiveTasks = async (): Promise<ActiveTasksResponse> => {
  return api.get('/tasks/')
}
