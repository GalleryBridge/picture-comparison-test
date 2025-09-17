"""
PDF高亮标注模块

基于比对结果生成高亮标注的PDF文件，直观显示差异。
支持新增、删除、修改图元的不同颜色标注。
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from geometry.elements import Element, Point, Line, Circle, Arc, Text
from matching.diff_detector import DifferenceDetail, DifferenceType
from core.comparison_engine import ComparisonResult


class HighlightStyle(Enum):
    """高亮样式"""
    SOLID = "solid"           # 实心填充
    OUTLINE = "outline"       # 轮廓线
    DASHED = "dashed"         # 虚线
    THICK = "thick"          # 粗线


@dataclass
class HighlightConfig:
    """高亮配置"""
    # 颜色配置 (RGB值 0-1)
    added_color: Tuple[float, float, float] = (0.0, 1.0, 0.0)      # 绿色 - 新增
    deleted_color: Tuple[float, float, float] = (1.0, 0.0, 0.0)    # 红色 - 删除
    modified_color: Tuple[float, float, float] = (0.0, 0.0, 1.0)   # 蓝色 - 修改
    unchanged_color: Tuple[float, float, float] = (0.5, 0.5, 0.5)  # 灰色 - 未变化
    
    # 样式配置
    added_style: HighlightStyle = HighlightStyle.SOLID
    deleted_style: HighlightStyle = HighlightStyle.OUTLINE
    modified_style: HighlightStyle = HighlightStyle.DASHED
    unchanged_style: HighlightStyle = HighlightStyle.OUTLINE
    
    # 线宽配置
    line_width: float = 2.0
    highlight_opacity: float = 0.7
    
    # 文本标注配置
    show_labels: bool = True
    label_font_size: float = 8.0
    label_offset: float = 5.0
    
    # 图例配置
    show_legend: bool = True
    legend_position: str = "top-right"  # top-left, top-right, bottom-left, bottom-right


class PDFHighlighter:
    """PDF高亮标注器"""
    
    def __init__(self, config: Optional[HighlightConfig] = None):
        self.config = config or HighlightConfig()
        
        # 差异类型到颜色的映射
        self.color_map = {
            DifferenceType.ADDED: self.config.added_color,
            DifferenceType.DELETED: self.config.deleted_color,
            DifferenceType.MODIFIED: self.config.modified_color,
            DifferenceType.UNCHANGED: self.config.unchanged_color
        }
        
        # 差异类型到样式的映射
        self.style_map = {
            DifferenceType.ADDED: self.config.added_style,
            DifferenceType.DELETED: self.config.deleted_style,
            DifferenceType.MODIFIED: self.config.modified_style,
            DifferenceType.UNCHANGED: self.config.unchanged_style
        }
    
    def highlight_differences(self, comparison_result: ComparisonResult, 
                            output_path: str, 
                            highlight_unchanged: bool = False) -> bool:
        """生成高亮标注的PDF文件"""
        
        try:
            # 1. 打开原始PDF文件
            if not os.path.exists(comparison_result.file_a_path):
                raise FileNotFoundError(f"文件不存在: {comparison_result.file_a_path}")
            
            doc = fitz.open(comparison_result.file_a_path)
            
            # 2. 处理每一页
            for page_num in range(len(doc)):
                page = doc[page_num]
                self._highlight_page(page, comparison_result.differences, 
                                   highlight_unchanged, page_num)
            
            # 3. 添加图例
            if self.config.show_legend:
                self._add_legend(doc[0])  # 在第一页添加图例
            
            # 4. 保存结果
            doc.save(output_path)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"PDF高亮标注失败: {e}")
            return False
    
    def _highlight_page(self, page, differences: List[DifferenceDetail], 
                       highlight_unchanged: bool, page_num: int):
        """高亮单页的差异"""
        
        # 过滤当前页的差异
        page_differences = self._filter_page_differences(differences, page_num)
        
        for diff in page_differences:
            # 跳过未变化的图元（除非明确要求高亮）
            if diff.diff_type == DifferenceType.UNCHANGED and not highlight_unchanged:
                continue
            
            # 获取高亮配置
            color = self.color_map[diff.diff_type]
            style = self.style_map[diff.diff_type]
            
            # 高亮图元
            if diff.element_a:  # 原图元存在
                self._highlight_element(page, diff.element_a, color, style, 
                                      f"{diff.diff_type.value}_a")
            
            if diff.element_b and diff.element_b != diff.element_a:  # 新图元存在且不同
                self._highlight_element(page, diff.element_b, color, style, 
                                      f"{diff.diff_type.value}_b")
    
    def _filter_page_differences(self, differences: List[DifferenceDetail], 
                                page_num: int) -> List[DifferenceDetail]:
        """过滤当前页的差异"""
        
        page_differences = []
        
        for diff in differences:
            # 检查图元是否属于当前页
            if self._is_element_on_page(diff.element_a, page_num) or \
               self._is_element_on_page(diff.element_b, page_num):
                page_differences.append(diff)
        
        return page_differences
    
    def _is_element_on_page(self, element: Optional[Element], page_num: int) -> bool:
        """检查图元是否属于指定页面"""
        
        if element is None:
            return False
        
        # 检查图元的layer属性
        if hasattr(element, 'layer'):
            layer = element.layer
            if f"page_{page_num}" in layer or f"text_page_{page_num}" in layer:
                return True
        
        # 默认假设所有图元都在第0页
        return page_num == 0
    
    def _highlight_element(self, page, element: Element, color: Tuple[float, float, float], 
                          style: HighlightStyle, label: str):
        """高亮单个图元"""
        
        if isinstance(element, Line):
            self._highlight_line(page, element, color, style, label)
        elif isinstance(element, Circle):
            self._highlight_circle(page, element, color, style, label)
        elif isinstance(element, Arc):
            self._highlight_arc(page, element, color, style, label)
        elif isinstance(element, Text):
            self._highlight_text(page, element, color, style, label)
    
    def _highlight_line(self, page, line: Line, color: Tuple[float, float, float], 
                       style: HighlightStyle, label: str):
        """高亮线段"""
        
        # 转换坐标（从毫米到PDF点）
        start_point = self._mm_to_points(line.start)
        end_point = self._mm_to_points(line.end)
        
        # 创建高亮路径
        path = page.new_shape()
        
        if style == HighlightStyle.SOLID:
            # 实心填充
            path.draw_line(start_point, end_point)
            path.finish(width=self.config.line_width, color=color, fill=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.OUTLINE:
            # 轮廓线
            path.draw_line(start_point, end_point)
            path.finish(width=self.config.line_width, color=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.DASHED:
            # 虚线
            path.draw_line(start_point, end_point)
            path.finish(width=self.config.line_width, color=color, 
                       dash=[5, 5], opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.THICK:
            # 粗线
            path.draw_line(start_point, end_point)
            path.finish(width=self.config.line_width * 2, color=color, 
                       opacity=self.config.highlight_opacity)
        
        path.commit()
        
        # 添加标签
        if self.config.show_labels:
            self._add_label(page, line.midpoint(), label, color)
    
    def _highlight_circle(self, page, circle: Circle, color: Tuple[float, float, float], 
                         style: HighlightStyle, label: str):
        """高亮圆形"""
        
        # 转换坐标
        center = self._mm_to_points(circle.center)
        radius = self._mm_to_points(Point(circle.radius, 0)).x
        
        # 创建高亮路径
        path = page.new_shape()
        
        if style == HighlightStyle.SOLID:
            # 实心填充
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, fill=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.OUTLINE:
            # 轮廓线
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.DASHED:
            # 虚线
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, 
                       dash=[5, 5], opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.THICK:
            # 粗线
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width * 2, color=color, 
                       opacity=self.config.highlight_opacity)
        
        path.commit()
        
        # 添加标签
        if self.config.show_labels:
            self._add_label(page, circle.center, label, color)
    
    def _highlight_arc(self, page, arc: Arc, color: Tuple[float, float, float], 
                      style: HighlightStyle, label: str):
        """高亮弧形"""
        
        # 转换坐标
        center = self._mm_to_points(arc.center)
        radius = self._mm_to_points(Point(arc.radius, 0)).x
        
        # 创建高亮路径
        path = page.new_shape()
        
        # 计算弧的起点和终点
        start_angle = arc.start_angle
        end_angle = arc.end_angle
        
        # 简化为圆形（PyMuPDF的弧形绘制比较复杂）
        if style == HighlightStyle.SOLID:
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, fill=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.OUTLINE:
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, 
                       opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.DASHED:
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width, color=color, 
                       dash=[5, 5], opacity=self.config.highlight_opacity)
        elif style == HighlightStyle.THICK:
            path.draw_circle(center, radius)
            path.finish(width=self.config.line_width * 2, color=color, 
                       opacity=self.config.highlight_opacity)
        
        path.commit()
        
        # 添加标签
        if self.config.show_labels:
            self._add_label(page, arc.center, label, color)
    
    def _highlight_text(self, page, text: Text, color: Tuple[float, float, float], 
                       style: HighlightStyle, label: str):
        """高亮文本"""
        
        # 转换坐标
        position = self._mm_to_points(text.position)
        
        # 估算文本边界框
        text_width = text.width_estimate()
        text_height = text.height
        
        # 转换为PDF点
        width_points = self._mm_to_points(Point(text_width, 0)).x
        height_points = self._mm_to_points(Point(0, text_height)).y
        
        # 创建高亮矩形
        rect = fitz.Rect(position.x, position.y - height_points, 
                        position.x + width_points, position.y)
        
        if style == HighlightStyle.SOLID:
            # 实心填充
            page.draw_rect(rect, color=color, fill=color, 
                          width=self.config.line_width)
        elif style == HighlightStyle.OUTLINE:
            # 轮廓线
            page.draw_rect(rect, color=color, 
                          width=self.config.line_width)
        elif style == HighlightStyle.DASHED:
            # 虚线
            page.draw_rect(rect, color=color, 
                          width=self.config.line_width, 
                          dash=[5, 5])
        elif style == HighlightStyle.THICK:
            # 粗线
            page.draw_rect(rect, color=color, 
                          width=self.config.line_width * 2)
        
        # 添加标签
        if self.config.show_labels:
            self._add_label(page, text.position, label, color)
    
    def _add_label(self, page, position: Point, label: str, color: Tuple[float, float, float]):
        """添加文本标签"""
        
        # 转换坐标
        point = self._mm_to_points(position)
        
        # 调整标签位置（避免重叠）
        label_point = fitz.Point(point.x + self.config.label_offset, 
                                point.y - self.config.label_offset)
        
        # 插入文本
        page.insert_text(label_point, label, fontsize=self.config.label_font_size, 
                        color=color)
    
    def _add_legend(self, page):
        """添加图例"""
        
        # 获取页面尺寸
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height
        
        # 确定图例位置
        if self.config.legend_position == "top-right":
            legend_x = page_width - 150
            legend_y = 50
        elif self.config.legend_position == "top-left":
            legend_x = 50
            legend_y = 50
        elif self.config.legend_position == "bottom-right":
            legend_x = page_width - 150
            legend_y = page_height - 150
        elif self.config.legend_position == "bottom-left":
            legend_x = 50
            legend_y = page_height - 150
        else:
            legend_x = page_width - 150
            legend_y = 50
        
        # 图例项目
        legend_items = [
            ("新增", DifferenceType.ADDED),
            ("删除", DifferenceType.DELETED),
            ("修改", DifferenceType.MODIFIED),
            ("未变化", DifferenceType.UNCHANGED)
        ]
        
        # 绘制图例背景
        legend_rect = fitz.Rect(legend_x - 10, legend_y - 10, 
                               legend_x + 140, legend_y + len(legend_items) * 25 + 10)
        page.draw_rect(legend_rect, color=(0.9, 0.9, 0.9), fill=(0.9, 0.9, 0.9))
        
        # 绘制图例项目
        for i, (text, diff_type) in enumerate(legend_items):
            item_y = legend_y + i * 25
            
            # 绘制颜色块
            color = self.color_map[diff_type]
            color_rect = fitz.Rect(legend_x, item_y, legend_x + 15, item_y + 15)
            page.draw_rect(color_rect, color=color, fill=color)
            
            # 绘制文本
            text_point = fitz.Point(legend_x + 20, item_y + 12)
            page.insert_text(text_point, text, fontsize=10, color=(0, 0, 0))
    
    def _mm_to_points(self, point: Point) -> fitz.Point:
        """将毫米坐标转换为PDF点坐标"""
        
        # 1毫米 = 2.834645669点
        mm_to_points = 2.834645669
        
        return fitz.Point(point.x * mm_to_points, point.y * mm_to_points)
    
    def create_comparison_overlay(self, comparison_result: ComparisonResult, 
                                output_path: str) -> bool:
        """创建比对叠加图（并排显示两个PDF的差异）"""
        
        try:
            # 打开两个PDF文件
            doc_a = fitz.open(comparison_result.file_a_path)
            doc_b = fitz.open(comparison_result.file_b_path)
            
            # 创建新文档
            new_doc = fitz.open()
            
            # 处理每一页
            max_pages = max(len(doc_a), len(doc_b))
            
            for page_num in range(max_pages):
                # 创建新页面（两倍宽度）
                if page_num < len(doc_a):
                    page_a = doc_a[page_num]
                    page_width = page_a.rect.width
                    page_height = page_a.rect.height
                else:
                    page_width = 612  # 默认宽度
                    page_height = 792  # 默认高度
                
                new_page = new_doc.new_page(width=page_width * 2, height=page_height)
                
                # 复制页面A到左侧
                if page_num < len(doc_a):
                    page_a = doc_a[page_num]
                    new_page.show_pdf_page(fitz.Rect(0, 0, page_width, page_height), 
                                          doc_a, page_num)
                
                # 复制页面B到右侧
                if page_num < len(doc_b):
                    page_b = doc_b[page_num]
                    new_page.show_pdf_page(fitz.Rect(page_width, 0, page_width * 2, page_height), 
                                          doc_b, page_num)
                
                # 添加差异标注
                self._add_difference_annotations(new_page, comparison_result.differences, 
                                               page_num, page_width)
            
            # 保存结果
            new_doc.save(output_path)
            new_doc.close()
            doc_a.close()
            doc_b.close()
            
            return True
            
        except Exception as e:
            print(f"创建比对叠加图失败: {e}")
            return False
    
    def _add_difference_annotations(self, page, differences: List[DifferenceDetail], 
                                  page_num: int, page_width: float):
        """添加差异标注"""
        
        # 过滤当前页的差异
        page_differences = self._filter_page_differences(differences, page_num)
        
        for i, diff in enumerate(page_differences):
            # 确定标注位置（左侧或右侧）
            if diff.element_a and not diff.element_b:
                # 只在A中存在，标注在左侧
                x_offset = 0
                element = diff.element_a
            elif diff.element_b and not diff.element_a:
                # 只在B中存在，标注在右侧
                x_offset = page_width
                element = diff.element_b
            else:
                # 都存在，标注在左侧
                x_offset = 0
                element = diff.element_a or diff.element_b
            
            if element:
                # 获取元素中心点
                center = self._get_element_center(element)
                point = self._mm_to_points(center)
                
                # 调整坐标
                point.x += x_offset
                
                # 添加标注
                annotation_text = f"{diff.diff_type.value.upper()}\n{diff.description}"
                color = self.color_map[diff.diff_type]
                
                # 创建标注矩形
                rect = fitz.Rect(point.x - 20, point.y - 10, point.x + 20, point.y + 10)
                
                # 添加高亮
                page.add_highlight_annot(rect)
                
                # 添加文本标注
                page.add_text_annot(point, annotation_text)
    
    def _get_element_center(self, element: Element) -> Point:
        """获取图元中心点"""
        if isinstance(element, Line):
            return element.midpoint()
        elif isinstance(element, (Circle, Arc)):
            return element.center
        elif isinstance(element, Text):
            return element.position
        else:
            return Point(0, 0)
    
    def update_config(self, new_config: HighlightConfig):
        """更新高亮配置"""
        self.config = new_config
        
        # 更新映射
        self.color_map = {
            DifferenceType.ADDED: self.config.added_color,
            DifferenceType.DELETED: self.config.deleted_color,
            DifferenceType.MODIFIED: self.config.modified_color,
            DifferenceType.UNCHANGED: self.config.unchanged_color
        }
        
        self.style_map = {
            DifferenceType.ADDED: self.config.added_style,
            DifferenceType.DELETED: self.config.deleted_style,
            DifferenceType.MODIFIED: self.config.modified_style,
            DifferenceType.UNCHANGED: self.config.unchanged_style
        }
