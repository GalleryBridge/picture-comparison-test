"""
文件上传API端点
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.pdf_service import PDFService
from app.tasks.pdf_tasks import process_pdf_task
import os
import uuid
from typing import Dict, Any

router = APIRouter()


@router.post("/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    上传PDF文件并开始处理
    """
    # 验证文件类型
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="只支持PDF文件格式"
        )
    
    # 验证文件大小
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE / 1024 / 1024}MB)"
        )
    
    try:
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # 确保上传目录存在
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 创建PDF服务实例并获取基本信息
        pdf_service = PDFService()
        pdf_info = pdf_service.get_pdf_info(file_path)
        
        # TODO: 保存到数据库
        # pdf_record = PDFDocument(
        #     id=file_id,
        #     filename=file.filename,
        #     file_path=file_path,
        #     file_size=file.size,
        #     page_count=pdf_info["page_count"],
        #     status="uploaded"
        # )
        # db.add(pdf_record)
        # db.commit()
        
        # 启动异步处理任务
        task = process_pdf_task.delay(file_id, file_path)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_size": file.size,
            "page_count": pdf_info["page_count"],
            "task_id": task.id,
            "status": "processing",
            "message": "PDF文件上传成功，开始处理"
        }
        
    except Exception as e:
        # 清理已上传的文件
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"文件处理失败: {str(e)}"
        )


@router.get("/status/{file_id}")
async def get_upload_status(
    file_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取文件上传和处理状态
    """
    # TODO: 从数据库查询文件状态
    return {
        "file_id": file_id,
        "status": "processing",
        "message": "正在处理中..."
    }
