"""
PDF解析器模块

专注于工程图纸的PDF解析，提取矢量图形、文本和表格等元素。
使用PyMuPDF和pdfplumber双库结合，确保解析精度和完整性。
"""

import fitz  # PyMuPDF
import pdfplumber
import math
from typing import List, Dict, Any, Optional, Tuple
from ..geometry.elements import Line, Circle, Arc, Text, Point, Element


class PDFParser:
    """PDF矢量图元解析器 - 专注于工程图纸解析"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
        self.supported_elements = ['line', 'circle', 'arc', 'text', 'polyline']
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文件，提取矢量图元和元数据"""
        try:
            # 使用PyMuPDF解析矢量图形
            fitz_doc = fitz.open(file_path)
            # 使用pdfplumber解析文本和表格
            plumber_doc = pdfplumber.open(file_path)
            
            result = {
                'elements': [],
                'metadata': self._extract_metadata(fitz_doc),
                'page_info': []
            }
            
            for page_num in range(len(fitz_doc)):
                fitz_page = fitz_doc[page_num]
                plumber_page = plumber_doc.pages[page_num]
                
                page_elements = self._parse_page(fitz_page, plumber_page, page_num)
                result['elements'].extend(page_elements)
                
                # 页面信息
                page_info = {
                    'page_num': page_num,
                    'bbox': list(fitz_page.rect),  # 转换为列表以便JSON序列化
                    'rotation': fitz_page.rotation,
                    'element_count': len(page_elements)
                }
                result['page_info'].append(page_info)
                
            fitz_doc.close()
            plumber_doc.close()
            
            print(f"PDF解析完成: {len(result['elements'])}个图元，{len(result['page_info'])}页")
            return result
            
        except Exception as e:
            raise ValueError(f"PDF解析失败: {e}")
    
    def _parse_page(self, fitz_page, plumber_page, page_num: int) -> List[Element]:
        """解析单页PDF，提取所有图元"""
        elements = []
        
        # 1. 解析矢量图形 (使用PyMuPDF)
        vector_elements = self._extract_vector_elements(fitz_page, page_num)
        elements.extend(vector_elements)
        
        # 2. 解析文本元素 (使用pdfplumber，精度更高)
        text_elements = self._extract_text_elements(plumber_page, page_num)
        elements.extend(text_elements)
        
        # 3. 解析表格和标注 (如果存在)
        table_elements = self._extract_table_elements(plumber_page, page_num)
        elements.extend(table_elements)
        
        return elements
    
    def _extract_vector_elements(self, page, page_num: int) -> List[Element]:
        """提取矢量图元 (线条、圆、弧等)"""
        elements = []
        
        try:
            # 方法1: 使用PyMuPDF的get_drawings()
            drawings = page.get_drawings()
            
            for drawing in drawings:
                # 解析每个绘图对象的路径项
                for path_item in drawing.get("items", []):
                    element = self._convert_path_to_element(path_item, page_num)
                    if element:
                        elements.append(element)
            
            # 方法2: 使用pdfplumber作为补充（通过page对象获取）
            # 这里我们先专注于PyMuPDF的结果
                        
        except Exception as e:
            print(f"矢量图元提取错误 (页面 {page_num}): {e}")
        
        return elements
    
    def _convert_path_to_element(self, path_item, page_num: int) -> Optional[Element]:
        """将PDF路径项转换为几何图元"""
        if not path_item or len(path_item) < 2:
            return None
            
        path_type = path_item[0] if isinstance(path_item, (list, tuple)) else None
        
        try:
            if path_type == "l":  # 直线 (lineto)
                # 格式: ('l', Point(x1, y1), Point(x2, y2))
                if len(path_item) >= 3:
                    start_point = path_item[1]
                    end_point = path_item[2]
                    return Line(
                        start=Point(float(start_point.x), float(start_point.y)),
                        end=Point(float(end_point.x), float(end_point.y)),
                        layer=f"page_{page_num}",
                        color="black"
                    )
                    
            elif path_type == "c":  # 三次贝塞尔曲线
                # 格式: ('c', Point(x1, y1), Point(x2, y2), Point(x3, y3), Point(x4, y4))
                if len(path_item) >= 5:
                    # 尝试转换为圆弧
                    points = [path_item[i] for i in range(1, min(5, len(path_item)))]
                    arc = self._bezier_to_arc_from_points(points, page_num)
                    if arc:
                        return arc
                        
            elif path_type == "re":  # 矩形
                # 格式: ('re', Rect(x, y, x+w, y+h), ?)
                if len(path_item) >= 2:
                    rect = path_item[1]
                    # 提取矩形的四个角点，这里返回一条边作为代表
                    return Line(
                        start=Point(float(rect.x0), float(rect.y0)),
                        end=Point(float(rect.x1), float(rect.y0)),
                        layer=f"page_{page_num}",
                        color="black",
                        line_type="rectangle_edge"
                    )
                    
            elif path_type == "m":  # moveto - 路径起点
                # 暂时跳过，等待后续的绘图指令
                pass
                
        except (ValueError, IndexError, TypeError, AttributeError) as e:
            print(f"路径转换错误: {e}, path_item: {path_item}")
            
        return None
    
    def _bezier_to_arc_from_points(self, points: List, page_num: int) -> Optional[Arc]:
        """从PyMuPDF Point对象列表转换为圆弧"""
        try:
            if len(points) < 4:
                return None
                
            # 提取坐标
            p1, p2, p3, p4 = points[:4]
            x1, y1 = float(p1.x), float(p1.y)
            x2, y2 = float(p2.x), float(p2.y)
            x3, y3 = float(p3.x), float(p3.y)
            x4, y4 = float(p4.x), float(p4.y)
            
            # 简化检测：检查是否为圆弧模式
            # 计算可能的中心点（使用起点和终点的中点作为估算）
            center_x = (x1 + x4) / 2
            center_y = (y1 + y4) / 2
            
            # 计算半径
            r1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
            r4 = math.sqrt((x4 - center_x)**2 + (y4 - center_y)**2)
            
            # 如果半径相近，可能是圆弧
            if abs(r1 - r4) < self.tolerance * 10:  # 放宽容差
                radius = (r1 + r4) / 2
                
                # 计算角度
                start_angle = math.atan2(y1 - center_y, x1 - center_x)
                end_angle = math.atan2(y4 - center_y, x4 - center_x)
                
                return Arc(
                    center=Point(center_x, center_y),
                    radius=radius,
                    start_angle=start_angle,
                    end_angle=end_angle,
                    layer=f"page_{page_num}",
                    color="black"
                )
                
        except Exception as e:
            print(f"贝塞尔转弧错误: {e}")
            
        return None
    
    def _bezier_to_arc(self, bezier_points: List[float], page_num: int) -> Optional[Arc]:
        """将贝塞尔曲线转换为圆弧 (如果可能)"""
        try:
            if len(bezier_points) < 6:
                return None
                
            x1, y1, x2, y2, x3, y3 = bezier_points[:6]
            
            # 简化检测：如果控制点形成圆弧模式
            # 计算可能的中心点和半径
            center_x = (x1 + x3) / 2
            center_y = (y1 + y3) / 2
            
            # 检查是否为圆弧（控制点应该在圆上）
            r1 = math.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
            r3 = math.sqrt((x3 - center_x)**2 + (y3 - center_y)**2)
            
            # 如果半径相近，可能是圆弧
            if abs(r1 - r3) < self.tolerance:
                radius = (r1 + r3) / 2
                
                # 计算角度
                start_angle = math.atan2(y1 - center_y, x1 - center_x)
                end_angle = math.atan2(y3 - center_y, x3 - center_x)
                
                return Arc(
                    center=Point(center_x, center_y),
                    radius=radius,
                    start_angle=start_angle,
                    end_angle=end_angle,
                    layer=f"page_{page_num}",
                    color="black"
                )
                
        except Exception as e:
            print(f"贝塞尔转弧错误: {e}")
            
        return None
    
    def _extract_text_elements(self, page, page_num: int) -> List[Text]:
        """提取文本元素 (使用pdfplumber获得更好的精度)"""
        elements = []
        
        try:
            # 获取所有文本字符
            chars = page.chars
            
            # 按行分组文本
            current_line = []
            current_y = None
            line_tolerance = 2.0  # 行间距容差
            
            for char in chars:
                if not char.get('text', '').strip():
                    continue
                    
                char_y = float(char['y0'])
                
                # 如果是新行
                if current_y is None or abs(char_y - current_y) > line_tolerance:
                    # 处理上一行
                    if current_line:
                        text_element = self._merge_line_chars(current_line, page_num)
                        if text_element:
                            elements.append(text_element)
                    
                    # 开始新行
                    current_line = [char]
                    current_y = char_y
                else:
                    # 同一行
                    current_line.append(char)
            
            # 处理最后一行
            if current_line:
                text_element = self._merge_line_chars(current_line, page_num)
                if text_element:
                    elements.append(text_element)
                    
        except Exception as e:
            print(f"文本提取错误 (页面 {page_num}): {e}")
            
        return elements
    
    def _merge_line_chars(self, chars: List[Dict], page_num: int) -> Optional[Text]:
        """合并同一行的字符为文本元素"""
        if not chars:
            return None
            
        try:
            # 按x坐标排序
            chars.sort(key=lambda c: c['x0'])
            
            # 合并文本内容
            text_content = ''.join(char['text'] for char in chars)
            
            # 使用第一个字符的位置和属性
            first_char = chars[0]
            
            return Text(
                position=Point(float(first_char['x0']), float(first_char['y0'])),
                content=text_content.strip(),
                height=float(first_char.get('size', 12)),
                rotation=0.0,
                layer=f"text_page_{page_num}",
                font=first_char.get('fontname', 'unknown'),
                color="black"
            )
            
        except Exception as e:
            print(f"字符合并错误: {e}")
            return None
    
    def _extract_table_elements(self, page, page_num: int) -> List[Element]:
        """提取表格元素"""
        elements = []
        
        try:
            tables = page.find_tables()
            
            for table in tables:
                # 将表格边框转换为线段
                bbox = table.bbox
                if bbox:
                    x0, y0, x1, y1 = bbox
                    layer_name = f"table_page_{page_num}"
                    
                    # 表格外框
                    elements.extend([
                        Line(Point(x0, y0), Point(x1, y0), layer_name, "black"),  # 上边
                        Line(Point(x1, y0), Point(x1, y1), layer_name, "black"),  # 右边
                        Line(Point(x1, y1), Point(x0, y1), layer_name, "black"),  # 下边
                        Line(Point(x0, y1), Point(x0, y0), layer_name, "black")   # 左边
                    ])
                    
        except Exception as e:
            print(f"表格提取错误 (页面 {page_num}): {e}")
            
        return elements
    
    def _extract_metadata(self, doc) -> Dict[str, Any]:
        """提取PDF元数据"""
        try:
            metadata = doc.metadata
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': doc.page_count,
                'is_pdf': doc.is_pdf,
                'needs_pass': doc.needs_pass,
                'is_encrypted': doc.is_encrypted
            }
        except Exception as e:
            print(f"元数据提取错误: {e}")
            return {
                'page_count': doc.page_count if hasattr(doc, 'page_count') else 0,
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return ['pdf']
    
    def validate_pdf(self, file_path: str) -> Dict[str, Any]:
        """验证PDF文件是否可以解析"""
        try:
            doc = fitz.open(file_path)
            
            validation = {
                'is_valid': True,
                'page_count': doc.page_count,
                'is_encrypted': doc.is_encrypted,
                'needs_password': doc.needs_pass,
                'has_drawings': False,
                'has_text': False,
                'error': None
            }
            
            # 检查第一页是否有内容
            if doc.page_count > 0:
                page = doc[0]
                
                # 检查是否有绘图
                drawings = page.get_drawings()
                validation['has_drawings'] = len(drawings) > 0
                
                # 检查是否有文本
                text = page.get_text()
                validation['has_text'] = len(text.strip()) > 0
            
            doc.close()
            return validation
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'page_count': 0,
                'is_encrypted': False,
                'needs_password': False,
                'has_drawings': False,
                'has_text': False
            }
