-- PostgreSQL数据库初始化脚本
-- 数据库名称: pdf_analysis
-- 创建时间: 2024年

-- 创建数据库（如果不存在）
-- 注意：需要在PostgreSQL中手动执行：CREATE DATABASE pdf_analysis;

-- 连接到pdf_analysis数据库后执行以下脚本

-- 启用UUID扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建PDF文档表
CREATE TABLE IF NOT EXISTS pdf_documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    page_count INTEGER NOT NULL,
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'uploaded',
    error_message TEXT,
    
    -- 文档信息
    title VARCHAR(500),
    author VARCHAR(255),
    subject VARCHAR(500),
    keywords TEXT,
    
    -- 处理参数
    dpi INTEGER DEFAULT 300,
    max_pages INTEGER DEFAULT 50,
    
    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES pdf_documents(id) ON DELETE CASCADE,
    task_id VARCHAR(255) NOT NULL,
    
    -- 分析状态
    status VARCHAR(50) DEFAULT 'processing',
    progress DECIMAL(5,2) DEFAULT 0.0,
    error_message TEXT,
    
    -- 分析结果（JSON格式）
    dimensions JSONB,
    annotations JSONB,
    measurements JSONB,
    confidence_scores JSONB,
    
    -- 处理信息
    processing_time DECIMAL(10,3),
    ai_model_used VARCHAR(100),
    model_version VARCHAR(50),
    
    -- 时间戳
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建任务状态表
CREATE TABLE IF NOT EXISTS task_statuses (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    task_name VARCHAR(100) NOT NULL,
    
    -- 任务状态
    status VARCHAR(50) DEFAULT 'pending',
    progress DECIMAL(5,2) DEFAULT 0.0,
    current_step VARCHAR(100),
    
    -- 任务信息
    args JSONB,
    kwargs JSONB,
    result JSONB,
    error TEXT,
    
    -- 时间信息
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 性能指标
    execution_time DECIMAL(10,3),
    memory_usage DECIMAL(10,2)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_pdf_documents_filename ON pdf_documents(filename);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_status ON pdf_documents(status);
CREATE INDEX IF NOT EXISTS idx_pdf_documents_upload_time ON pdf_documents(upload_time);

CREATE INDEX IF NOT EXISTS idx_analysis_results_document_id ON analysis_results(document_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_task_id ON analysis_results(task_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_status ON analysis_results(status);

CREATE INDEX IF NOT EXISTS idx_task_statuses_task_id ON task_statuses(task_id);
CREATE INDEX IF NOT EXISTS idx_task_statuses_status ON task_statuses(status);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_pdf_documents_updated_at 
    BEFORE UPDATE ON pdf_documents 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_statuses_updated_at 
    BEFORE UPDATE ON task_statuses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
