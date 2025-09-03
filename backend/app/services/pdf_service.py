"""
PDF处理服务
"""

import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image
import os
from typing import Dict, List, Any
from app.core.config import settings


class PDFService:
    """PDF处理服务类"""
    
    def __init__(self):
        self.dpi = settings.PDF_DPI
        self.max_pages = settings.PDF_MAX_PAGES
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        获取PDF基本信息
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", ""),
            }
            doc.close()
            return info
        except Exception as e:
            raise Exception(f"获取PDF信息失败: {str(e)}")
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: str) -> List[str]:
        """
        将PDF页面转换为图像
        """
        try:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取PDF信息
            pdf_info = self.get_pdf_info(pdf_path)
            page_count = min(pdf_info["page_count"], self.max_pages)
            
            # 转换PDF页面为图像
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                first_page=1,
                last_page=page_count,
                fmt='PNG'
            )
            
            image_paths = []
            for i, image in enumerate(images, 1):
                image_path = os.path.join(output_dir, f"page_{i}.png")
                image.save(image_path, 'PNG')
                image_paths.append(image_path)
            
            return image_paths
            
        except Exception as e:
            raise Exception(f"PDF转图像失败: {str(e)}")
    
    def extract_text_from_page(self, pdf_path: str, page_number: int) -> str:
        """
        从指定页面提取文本
        """
        try:
            doc = fitz.open(pdf_path)
            if page_number < 1 or page_number > len(doc):
                raise ValueError(f"页码 {page_number} 超出范围")
            
            page = doc[page_number - 1]  # PyMuPDF使用0基索引
            text = page.get_text()
            doc.close()
            
            return text
            
        except Exception as e:
            raise Exception(f"提取文本失败: {str(e)}")
    
    def get_page_dimensions(self, pdf_path: str, page_number: int) -> Dict[str, float]:
        """
        获取页面尺寸信息
        """
        try:
            doc = fitz.open(pdf_path)
            if page_number < 1 or page_number > len(doc):
                raise ValueError(f"页码 {page_number} 超出范围")
            
            page = doc[page_number - 1]
            rect = page.rect
            
            dimensions = {
                "width": rect.width,
                "height": rect.height,
                "width_mm": rect.width * 25.4 / 72,  # 转换为毫米
                "height_mm": rect.height * 25.4 / 72
            }
            
            doc.close()
            return dimensions
            
        except Exception as e:
            raise Exception(f"获取页面尺寸失败: {str(e)}")
    
    def preprocess_image(self, image_path: str, output_path: str = None) -> str:
        """
        图像预处理 - 增强图像质量
        """
        try:
            # 打开图像
            image = Image.open(image_path)
            
            # 转换为RGB模式（如果需要）
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # TODO: 添加更多图像预处理步骤
            # - 去噪
            # - 对比度增强
            # - 边缘锐化
            
            # 保存处理后的图像
            if output_path is None:
                output_path = image_path.replace('.png', '_processed.png')
            
            image.save(output_path, 'PNG', quality=95)
            return output_path
            
        except Exception as e:
            raise Exception(f"图像预处理失败: {str(e)}")
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """
        清理临时文件
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"清理文件失败 {file_path}: {str(e)}")
