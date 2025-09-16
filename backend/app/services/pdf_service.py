"""
PDF处理服务
"""

import fitz  # PyMuPDF
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
        使用PyMuPDF将PDF页面转换为图像
        """
        try:
            import fitz  # PyMuPDF
            
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            
            # 获取PDF信息
            pdf_info = self.get_pdf_info(pdf_path)
            page_count = min(pdf_info["page_count"], self.max_pages)
            
            image_paths = []
            doc = fitz.open(pdf_path)
            
            for page_num in range(page_count):
                page = doc[page_num]
                # 渲染页面为图像
                mat = fitz.Matrix(self.dpi/72, self.dpi/72)  # DPI转换
                pix = page.get_pixmap(matrix=mat)
                
                image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
                pix.save(image_path)
                image_paths.append(image_path)
            
            doc.close()
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
    
    def enhance_for_engineering_drawing(self, image_path: str, output_path: str = None) -> str:
        """
        专门针对工程图纸的图像增强处理
        """
        try:
            # 尝试导入OpenCV，如果失败则使用基础处理
            try:
                import cv2
                import numpy as np
            except ImportError as e:
                print(f"⚠️ OpenCV导入失败，使用基础图像处理: {str(e)}")
                return self._basic_image_enhancement(image_path, output_path)
            except AttributeError as e:
                print(f"⚠️ NumPy兼容性问题，使用基础图像处理: {str(e)}")
                return self._basic_image_enhancement(image_path, output_path)
            
            print(f"🖼️ 开始增强工程图纸: {image_path}")
            
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                raise Exception(f"无法读取图像: {image_path}")
            
            print(f"📏 原始图像尺寸: {img.shape}")
            
            # 转换为灰度图
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            
            # 1. 自适应直方图均衡化 - 增强对比度
            print("🔧 应用自适应直方图均衡化...")
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # 2. 双边滤波 - 去噪但保留边缘
            print("🔧 应用双边滤波去噪...")
            denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # 3. 锐化滤波 - 增强文字和线条清晰度
            print("🔧 应用锐化滤波...")
            kernel_sharpen = np.array([
                [-1, -1, -1],
                [-1,  9, -1], 
                [-1, -1, -1]
            ])
            sharpened = cv2.filter2D(denoised, -1, kernel_sharpen)
            
            # 4. 形态学操作 - 增强细线条
            print("🔧 应用形态学操作...")
            kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            morphed = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel_morph)
            
            # 5. 可选：二值化处理（对某些图纸有效）
            # 先检查图像是否适合二值化
            mean_intensity = np.mean(morphed)
            if mean_intensity > 200:  # 背景较亮的图纸
                print("🔧 应用自适应二值化...")
                # 使用自适应阈值
                binary = cv2.adaptiveThreshold(
                    morphed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                final_image = binary
            else:
                final_image = morphed
            
            # 6. 可选：边缘增强
            print("🔧 应用边缘增强...")
            edges = cv2.Canny(final_image, 50, 150)
            # 将边缘信息融合回原图
            final_image = cv2.addWeighted(final_image, 0.8, edges, 0.2, 0)
            
            # 保存增强后的图像
            if output_path is None:
                output_path = image_path.replace('.png', '_enhanced.png')
            
            success = cv2.imwrite(output_path, final_image)
            if not success:
                raise Exception("保存增强图像失败")
            
            print(f"✅ 图像增强完成: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 工程图纸增强失败: {str(e)}")
            # 如果增强失败，返回原图像路径
            return image_path
    
    def enhance_image_quality(self, image_path: str, enhancement_level: str = "medium") -> str:
        """
        多级图像质量增强
        
        Args:
            image_path: 输入图像路径
            enhancement_level: 增强级别 ("light", "medium", "strong")
        """
        try:
            import cv2
            import numpy as np
            
            img = cv2.imread(image_path)
            if img is None:
                return image_path
            
            # 转为灰度
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            
            if enhancement_level == "light":
                # 轻度增强：仅对比度调整
                enhanced = cv2.convertScaleAbs(gray, alpha=1.2, beta=10)
                
            elif enhancement_level == "medium":
                # 中度增强：对比度 + 锐化
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                enhanced = cv2.filter2D(enhanced, -1, kernel)
                
            elif enhancement_level == "strong":
                # 强度增强：全套处理
                return self.enhance_for_engineering_drawing(image_path)
            
            # 保存结果
            output_path = image_path.replace('.png', f'_enhanced_{enhancement_level}.png')
            cv2.imwrite(output_path, enhanced)
            return output_path
            
        except Exception as e:
            print(f"图像增强失败: {str(e)}")
            return image_path
    
    def _basic_image_enhancement(self, image_path: str, output_path: str = None) -> str:
        """
        基础图像增强 - 不依赖OpenCV的回退方案
        """
        try:
            from PIL import Image, ImageEnhance, ImageFilter
            
            print(f"🖼️ 使用基础方法增强图像: {image_path}")
            
            # 打开图像
            image = Image.open(image_path)
            
            # 转换为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 1. 增强对比度
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.3)  # 增强30%对比度
            
            # 2. 增强锐度
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)  # 增强20%锐度
            
            # 3. 应用锐化滤镜
            image = image.filter(ImageFilter.SHARPEN)
            
            # 4. 微调亮度
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # 增强10%亮度
            
            # 保存增强后的图像
            if output_path is None:
                output_path = image_path.replace('.png', '_enhanced.png')
            
            image.save(output_path, 'PNG', quality=95)
            print(f"✅ 基础图像增强完成: {output_path}")
            
            return output_path
            
        except Exception as e:
            print(f"❌ 基础图像增强失败: {str(e)}")
            return image_path
    
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
