"""
坐标标准化器模块

处理PDF坐标系统的标准化，包括：
1. PDF坐标系转换（左下角原点 -> 标准坐标系）
2. 单位转换（PDF点 -> 毫米）
3. 坐标对齐（最小值归零）
4. 页面尺寸标准化
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from .elements import Element, Point, Line, Circle, Arc, Text


class CoordinateNormalizer:
    """坐标系统标准化器 - 处理PDF坐标系差异"""
    
    def __init__(self):
        self.reference_dpi = 72  # PDF标准DPI
        self.target_unit = "mm"  # 目标单位：毫米
        self.point_to_mm = 25.4 / 72  # PDF点到毫米的转换系数
        
    def normalize(self, elements: List[Element], page_info: Optional[Dict] = None) -> List[Element]:
        """标准化图元坐标系统"""
        if not elements:
            return elements
            
        print(f"开始坐标标准化: {len(elements)}个图元")
        
        # 1. 坐标系转换 (PDF坐标系 -> 标准坐标系)
        elements = self._convert_coordinate_system(elements, page_info)
        
        # 2. 单位标准化 (点 -> 毫米)
        elements = self._convert_units(elements)
        
        # 3. 坐标对齐 (以最小值为原点)
        elements = self._align_coordinates(elements)
        
        print(f"坐标标准化完成: {len(elements)}个图元")
        return elements
    
    def _convert_coordinate_system(self, elements: List[Element], page_info: Optional[Dict] = None) -> List[Element]:
        """转换PDF坐标系 (左下角原点 -> 左上角原点)"""
        if not page_info or 'bbox' not in page_info:
            print("警告: 没有页面信息，跳过坐标系转换")
            return elements
            
        # 获取页面高度
        bbox = page_info['bbox']
        if isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
            page_height = bbox[3] - bbox[1]  # y_max - y_min
        else:
            print("警告: 页面边界框格式错误，跳过坐标系转换")
            return elements
        
        print(f"转换坐标系: 页面高度 {page_height:.1f} 点")
        
        normalized_elements = []
        for element in elements:
            try:
                if isinstance(element, Line):
                    normalized_elements.append(Line(
                        start=Point(element.start.x, page_height - element.start.y),
                        end=Point(element.end.x, page_height - element.end.y),
                        layer=element.layer,
                        color=element.color,
                        line_type=element.line_type,
                        thickness=element.thickness
                    ))
                elif isinstance(element, Circle):
                    normalized_elements.append(Circle(
                        center=Point(element.center.x, page_height - element.center.y),
                        radius=element.radius,
                        layer=element.layer,
                        color=element.color,
                        fill=element.fill
                    ))
                elif isinstance(element, Arc):
                    # 弧的坐标转换需要特别处理角度
                    new_center = Point(element.center.x, page_height - element.center.y)
                    # Y轴翻转会影响角度，需要调整
                    new_start_angle = -element.start_angle
                    new_end_angle = -element.end_angle
                    
                    normalized_elements.append(Arc(
                        center=new_center,
                        radius=element.radius,
                        start_angle=new_start_angle,
                        end_angle=new_end_angle,
                        layer=element.layer,
                        color=element.color
                    ))
                elif isinstance(element, Text):
                    normalized_elements.append(Text(
                        position=Point(element.position.x, page_height - element.position.y),
                        content=element.content,
                        height=element.height,
                        rotation=element.rotation,
                        layer=element.layer,
                        color=element.color,
                        font=element.font,
                        bold=element.bold,
                        italic=element.italic
                    ))
                else:
                    # 未知类型，直接添加
                    normalized_elements.append(element)
                    
            except Exception as e:
                print(f"坐标系转换错误: {e}, 元素: {element}")
                # 出错时保留原元素
                normalized_elements.append(element)
                
        return normalized_elements
    
    def _convert_units(self, elements: List[Element]) -> List[Element]:
        """单位转换：PDF点 -> 毫米"""
        print(f"单位转换: PDF点 -> 毫米 (转换系数: {self.point_to_mm:.4f})")
        
        converted_elements = []
        for element in elements:
            try:
                if isinstance(element, Line):
                    converted_elements.append(Line(
                        start=Point(
                            element.start.x * self.point_to_mm, 
                            element.start.y * self.point_to_mm
                        ),
                        end=Point(
                            element.end.x * self.point_to_mm, 
                            element.end.y * self.point_to_mm
                        ),
                        layer=element.layer,
                        color=element.color,
                        line_type=element.line_type,
                        thickness=element.thickness * self.point_to_mm
                    ))
                elif isinstance(element, Circle):
                    converted_elements.append(Circle(
                        center=Point(
                            element.center.x * self.point_to_mm, 
                            element.center.y * self.point_to_mm
                        ),
                        radius=element.radius * self.point_to_mm,
                        layer=element.layer,
                        color=element.color,
                        fill=element.fill
                    ))
                elif isinstance(element, Arc):
                    converted_elements.append(Arc(
                        center=Point(
                            element.center.x * self.point_to_mm, 
                            element.center.y * self.point_to_mm
                        ),
                        radius=element.radius * self.point_to_mm,
                        start_angle=element.start_angle,
                        end_angle=element.end_angle,
                        layer=element.layer,
                        color=element.color
                    ))
                elif isinstance(element, Text):
                    converted_elements.append(Text(
                        position=Point(
                            element.position.x * self.point_to_mm, 
                            element.position.y * self.point_to_mm
                        ),
                        content=element.content,
                        height=element.height * self.point_to_mm,
                        rotation=element.rotation,
                        layer=element.layer,
                        color=element.color,
                        font=element.font,
                        bold=element.bold,
                        italic=element.italic
                    ))
                else:
                    # 未知类型，直接添加
                    converted_elements.append(element)
                    
            except Exception as e:
                print(f"单位转换错误: {e}, 元素: {element}")
                # 出错时保留原元素
                converted_elements.append(element)
                
        return converted_elements
    
    def _align_coordinates(self, elements: List[Element]) -> List[Element]:
        """坐标对齐 - 将最小坐标设为原点"""
        if not elements:
            return elements
            
        # 找到最小坐标
        min_x = min_y = float('inf')
        
        for element in elements:
            try:
                if isinstance(element, Line):
                    min_x = min(min_x, element.start.x, element.end.x)
                    min_y = min(min_y, element.start.y, element.end.y)
                elif isinstance(element, (Circle, Arc)):
                    min_x = min(min_x, element.center.x - element.radius)
                    min_y = min(min_y, element.center.y - element.radius)
                elif isinstance(element, Text):
                    min_x = min(min_x, element.position.x)
                    min_y = min(min_y, element.position.y)
            except Exception as e:
                print(f"坐标范围计算错误: {e}, 元素: {element}")
        
        # 如果没有有效坐标，返回原始元素
        if min_x == float('inf') or min_y == float('inf'):
            print("警告: 没有找到有效坐标，跳过对齐")
            return elements
            
        print(f"坐标对齐: 偏移量 ({min_x:.2f}, {min_y:.2f}) mm")
        
        # 平移所有元素
        aligned_elements = []
        for element in elements:
            try:
                if isinstance(element, Line):
                    aligned_elements.append(Line(
                        start=Point(element.start.x - min_x, element.start.y - min_y),
                        end=Point(element.end.x - min_x, element.end.y - min_y),
                        layer=element.layer,
                        color=element.color,
                        line_type=element.line_type,
                        thickness=element.thickness
                    ))
                elif isinstance(element, Circle):
                    aligned_elements.append(Circle(
                        center=Point(element.center.x - min_x, element.center.y - min_y),
                        radius=element.radius,
                        layer=element.layer,
                        color=element.color,
                        fill=element.fill
                    ))
                elif isinstance(element, Arc):
                    aligned_elements.append(Arc(
                        center=Point(element.center.x - min_x, element.center.y - min_y),
                        radius=element.radius,
                        start_angle=element.start_angle,
                        end_angle=element.end_angle,
                        layer=element.layer,
                        color=element.color
                    ))
                elif isinstance(element, Text):
                    aligned_elements.append(Text(
                        position=Point(element.position.x - min_x, element.position.y - min_y),
                        content=element.content,
                        height=element.height,
                        rotation=element.rotation,
                        layer=element.layer,
                        color=element.color,
                        font=element.font,
                        bold=element.bold,
                        italic=element.italic
                    ))
                else:
                    # 未知类型，直接添加
                    aligned_elements.append(element)
                    
            except Exception as e:
                print(f"坐标对齐错误: {e}, 元素: {element}")
                # 出错时保留原元素
                aligned_elements.append(element)
                
        return aligned_elements
    
    def get_elements_bounds(self, elements: List[Element]) -> Tuple[float, float, float, float]:
        """获取图元集合的边界框 (xmin, ymin, xmax, ymax)"""
        if not elements:
            return (0, 0, 0, 0)
        
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for element in elements:
            try:
                if isinstance(element, Line):
                    min_x = min(min_x, element.start.x, element.end.x)
                    max_x = max(max_x, element.start.x, element.end.x)
                    min_y = min(min_y, element.start.y, element.end.y)
                    max_y = max(max_y, element.start.y, element.end.y)
                elif isinstance(element, (Circle, Arc)):
                    min_x = min(min_x, element.center.x - element.radius)
                    max_x = max(max_x, element.center.x + element.radius)
                    min_y = min(min_y, element.center.y - element.radius)
                    max_y = max(max_y, element.center.y + element.radius)
                elif isinstance(element, Text):
                    width = element.width_estimate()
                    min_x = min(min_x, element.position.x)
                    max_x = max(max_x, element.position.x + width)
                    min_y = min(min_y, element.position.y)
                    max_y = max(max_y, element.position.y + element.height)
            except Exception as e:
                print(f"边界框计算错误: {e}, 元素: {element}")
        
        if min_x == float('inf'):
            return (0, 0, 0, 0)
            
        return (min_x, min_y, max_x, max_y)
    
    def normalize_batch(self, elements_list: List[List[Element]], 
                       page_info_list: List[Dict]) -> List[List[Element]]:
        """批量标准化多个图元列表"""
        if len(elements_list) != len(page_info_list):
            raise ValueError("图元列表和页面信息列表长度不匹配")
        
        normalized_list = []
        for elements, page_info in zip(elements_list, page_info_list):
            normalized_elements = self.normalize(elements, page_info)
            normalized_list.append(normalized_elements)
        
        return normalized_list
    
    def get_conversion_info(self) -> Dict[str, Any]:
        """获取转换信息"""
        return {
            'reference_dpi': self.reference_dpi,
            'target_unit': self.target_unit,
            'point_to_mm_ratio': self.point_to_mm,
            'conversion_description': f"1 PDF点 = {self.point_to_mm:.4f} 毫米"
        }
