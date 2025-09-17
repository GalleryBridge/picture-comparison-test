"""
差异图像渲染模块

基于比对结果生成差异可视化图像，支持多种输出格式。
提供直观的差异展示和统计分析图表。
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import numpy as np
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path

from geometry.elements import Element, Point, Line, Circle as GeoCircle, Arc, Text
from matching.diff_detector import DifferenceDetail, DifferenceType, DifferenceStatistics
from core.comparison_engine import ComparisonResult


class RenderFormat(Enum):
    """渲染格式"""
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    PDF = "pdf"


class ChartType(Enum):
    """图表类型"""
    SUMMARY = "summary"                    # 比对摘要
    HEATMAP = "heatmap"                   # 差异热力图
    DISTRIBUTION = "distribution"          # 图元分布
    SIMILARITY = "similarity"             # 相似度分析
    GEOMETRIC = "geometric"               # 几何可视化


@dataclass
class RenderConfig:
    """渲染配置"""
    # 图像配置
    figure_size: Tuple[int, int] = (12, 8)
    dpi: int = 300
    background_color: str = "white"
    
    # 颜色配置
    added_color: str = "#2E8B57"      # 海绿色
    deleted_color: str = "#DC143C"    # 深红色
    modified_color: str = "#4169E1"   # 皇家蓝
    unchanged_color: str = "#808080"  # 灰色
    
    # 字体配置
    title_font_size: int = 16
    label_font_size: int = 12
    legend_font_size: int = 10
    
    # 布局配置
    show_grid: bool = True
    show_legend: bool = True
    tight_layout: bool = True


class DiffRenderer:
    """差异图像渲染器"""
    
    def __init__(self, config: Optional[RenderConfig] = None):
        self.config = config or RenderConfig()
        
        # 设置matplotlib样式
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 差异类型到颜色的映射
        self.color_map = {
            DifferenceType.ADDED: self.config.added_color,
            DifferenceType.DELETED: self.config.deleted_color,
            DifferenceType.MODIFIED: self.config.modified_color,
            DifferenceType.UNCHANGED: self.config.unchanged_color
        }
    
    def render_comparison_summary(self, comparison_result: ComparisonResult, 
                                output_path: str, format: RenderFormat = RenderFormat.PNG) -> bool:
        """渲染比对摘要图表"""
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.config.figure_size)
            fig.suptitle('PDF图纸比对摘要报告', fontsize=self.config.title_font_size, fontweight='bold')
            
            # 1. 差异统计柱状图
            self._render_difference_bar_chart(ax1, comparison_result.difference_statistics)
            
            # 2. 差异类型饼图
            self._render_difference_pie_chart(ax2, comparison_result.difference_statistics)
            
            # 3. 图元类型统计
            self._render_element_type_chart(ax3, comparison_result.difference_statistics)
            
            # 4. 匹配统计
            self._render_matching_chart(ax4, comparison_result.matching_statistics)
            
            # 保存图像
            if self.config.tight_layout:
                plt.tight_layout()
            
            plt.savefig(output_path, format=format.value, dpi=self.config.dpi, 
                       bbox_inches='tight', facecolor=self.config.background_color)
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"渲染比对摘要失败: {e}")
            return False
    
    def render_difference_heatmap(self, comparison_result: ComparisonResult, 
                                output_path: str, format: RenderFormat = RenderFormat.PNG) -> bool:
        """渲染差异热力图"""
        
        try:
            fig, ax = plt.subplots(figsize=self.config.figure_size)
            
            # 创建热力图数据
            heatmap_data = self._create_heatmap_data(comparison_result)
            
            # 绘制热力图
            sns.heatmap(heatmap_data, annot=True, cmap='RdYlBu_r', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .8},
                       ax=ax)
            
            ax.set_title('差异分布热力图', fontsize=self.config.title_font_size, fontweight='bold')
            ax.set_xlabel('图元类型', fontsize=self.config.label_font_size)
            ax.set_ylabel('差异类型', fontsize=self.config.label_font_size)
            
            if self.config.tight_layout:
                plt.tight_layout()
            
            plt.savefig(output_path, format=format.value, dpi=self.config.dpi, 
                       bbox_inches='tight', facecolor=self.config.background_color)
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"渲染差异热力图失败: {e}")
            return False
    
    def render_element_distribution(self, comparison_result: ComparisonResult, 
                                  output_path: str, format: RenderFormat = RenderFormat.PNG) -> bool:
        """渲染图元分布图"""
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.config.figure_size)
            
            # 1. 图元数量对比
            self._render_element_count_comparison(ax1, comparison_result)
            
            # 2. 图元类型分布
            self._render_element_type_distribution(ax2, comparison_result)
            
            fig.suptitle('图元分布分析', fontsize=self.config.title_font_size, fontweight='bold')
            
            if self.config.tight_layout:
                plt.tight_layout()
            
            plt.savefig(output_path, format=format.value, dpi=self.config.dpi, 
                       bbox_inches='tight', facecolor=self.config.background_color)
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"渲染图元分布图失败: {e}")
            return False
    
    def render_similarity_analysis(self, comparison_result: ComparisonResult, 
                                 output_path: str, format: RenderFormat = RenderFormat.PNG) -> bool:
        """渲染相似度分析图"""
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.config.figure_size)
            
            # 1. 相似度分布直方图
            self._render_similarity_histogram(ax1, comparison_result)
            
            # 2. 相似度箱线图
            self._render_similarity_boxplot(ax2, comparison_result)
            
            fig.suptitle('相似度分析', fontsize=self.config.title_font_size, fontweight='bold')
            
            if self.config.tight_layout:
                plt.tight_layout()
            
            plt.savefig(output_path, format=format.value, dpi=self.config.dpi, 
                       bbox_inches='tight', facecolor=self.config.background_color)
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"渲染相似度分析图失败: {e}")
            return False
    
    def render_geometric_visualization(self, comparison_result: ComparisonResult, 
                                     output_path: str, format: RenderFormat = RenderFormat.PNG) -> bool:
        """渲染几何可视化图"""
        
        try:
            fig, ax = plt.subplots(figsize=self.config.figure_size)
            
            # 绘制所有图元
            self._render_elements_on_plot(ax, comparison_result)
            
            ax.set_title('几何图元可视化', fontsize=self.config.title_font_size, fontweight='bold')
            ax.set_xlabel('X坐标 (mm)', fontsize=self.config.label_font_size)
            ax.set_ylabel('Y坐标 (mm)', fontsize=self.config.label_font_size)
            ax.set_aspect('equal')
            
            if self.config.show_grid:
                ax.grid(True, alpha=0.3)
            
            if self.config.show_legend:
                ax.legend()
            
            if self.config.tight_layout:
                plt.tight_layout()
            
            plt.savefig(output_path, format=format.value, dpi=self.config.dpi, 
                       bbox_inches='tight', facecolor=self.config.background_color)
            plt.close()
            
            return True
            
        except Exception as e:
            print(f"渲染几何可视化图失败: {e}")
            return False
    
    def _render_difference_bar_chart(self, ax, diff_stats: DifferenceStatistics):
        """渲染差异统计柱状图"""
        
        categories = ['新增', '删除', '修改', '未变化']
        values = [diff_stats.added_count, diff_stats.deleted_count, 
                 diff_stats.modified_count, diff_stats.unchanged_count]
        colors = [self.color_map[DifferenceType.ADDED], 
                 self.color_map[DifferenceType.DELETED],
                 self.color_map[DifferenceType.MODIFIED], 
                 self.color_map[DifferenceType.UNCHANGED]]
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_title('差异统计', fontsize=self.config.label_font_size, fontweight='bold')
        ax.set_ylabel('数量', fontsize=self.config.label_font_size)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(value), ha='center', va='bottom', fontweight='bold')
    
    def _render_difference_pie_chart(self, ax, diff_stats: DifferenceStatistics):
        """渲染差异类型饼图"""
        
        labels = ['新增', '删除', '修改', '未变化']
        sizes = [diff_stats.added_count, diff_stats.deleted_count, 
                diff_stats.modified_count, diff_stats.unchanged_count]
        colors = [self.color_map[DifferenceType.ADDED], 
                 self.color_map[DifferenceType.DELETED],
                 self.color_map[DifferenceType.MODIFIED], 
                 self.color_map[DifferenceType.UNCHANGED]]
        
        # 过滤掉0值
        filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        
        if filtered_data:
            labels, sizes, colors = zip(*filtered_data)
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                             startangle=90, textprops={'fontsize': self.config.legend_font_size})
            ax.set_title('差异类型分布', fontsize=self.config.label_font_size, fontweight='bold')
        else:
            ax.text(0.5, 0.5, '无差异', ha='center', va='center', 
                   fontsize=self.config.label_font_size, transform=ax.transAxes)
            ax.set_title('差异类型分布', fontsize=self.config.label_font_size, fontweight='bold')
    
    def _render_element_type_chart(self, ax, diff_stats: DifferenceStatistics):
        """渲染图元类型统计图"""
        
        if not diff_stats.type_statistics:
            ax.text(0.5, 0.5, '无图元类型数据', ha='center', va='center', 
                   fontsize=self.config.label_font_size, transform=ax.transAxes)
            ax.set_title('图元类型统计', fontsize=self.config.label_font_size, fontweight='bold')
            return
        
        # 收集所有图元类型的数据
        element_types = list(diff_stats.type_statistics.keys())
        added_counts = [diff_stats.type_statistics[et].get('added', 0) for et in element_types]
        deleted_counts = [diff_stats.type_statistics[et].get('deleted', 0) for et in element_types]
        modified_counts = [diff_stats.type_statistics[et].get('modified', 0) for et in element_types]
        
        x = np.arange(len(element_types))
        width = 0.25
        
        ax.bar(x - width, added_counts, width, label='新增', color=self.color_map[DifferenceType.ADDED], alpha=0.7)
        ax.bar(x, deleted_counts, width, label='删除', color=self.color_map[DifferenceType.DELETED], alpha=0.7)
        ax.bar(x + width, modified_counts, width, label='修改', color=self.color_map[DifferenceType.MODIFIED], alpha=0.7)
        
        ax.set_title('图元类型统计', fontsize=self.config.label_font_size, fontweight='bold')
        ax.set_ylabel('数量', fontsize=self.config.label_font_size)
        ax.set_xticks(x)
        ax.set_xticklabels(element_types, rotation=45, ha='right')
        ax.legend()
    
    def _render_matching_chart(self, ax, matching_stats):
        """渲染匹配统计图"""
        
        categories = ['精确匹配', '相似匹配', '部分匹配', '未匹配']
        values = [matching_stats.exact_matches, matching_stats.similar_matches, 
                 matching_stats.partial_matches, 
                 matching_stats.unmatched_a + matching_stats.unmatched_b]
        
        colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF6347']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_title('匹配统计', fontsize=self.config.label_font_size, fontweight='bold')
        ax.set_ylabel('数量', fontsize=self.config.label_font_size)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(value), ha='center', va='bottom', fontweight='bold')
    
    def _create_heatmap_data(self, comparison_result: ComparisonResult) -> np.ndarray:
        """创建热力图数据"""
        
        # 获取所有图元类型
        element_types = set()
        for diff in comparison_result.differences:
            if diff.element_a:
                element_types.add(type(diff.element_a).__name__)
            if diff.element_b:
                element_types.add(type(diff.element_b).__name__)
        
        element_types = sorted(list(element_types))
        diff_types = ['新增', '删除', '修改', '未变化']
        
        # 创建数据矩阵
        data = np.zeros((len(diff_types), len(element_types)))
        
        for diff in comparison_result.differences:
            element_type = None
            if diff.element_a:
                element_type = type(diff.element_a).__name__
            elif diff.element_b:
                element_type = type(diff.element_b).__name__
            
            if element_type and element_type in element_types:
                diff_type_idx = ['added', 'deleted', 'modified', 'unchanged'].index(diff.diff_type.value)
                element_type_idx = element_types.index(element_type)
                data[diff_type_idx, element_type_idx] += 1
        
        return data
    
    def _render_element_count_comparison(self, ax, comparison_result: ComparisonResult):
        """渲染图元数量对比图"""
        
        categories = ['文件A', '文件B']
        values = [comparison_result.elements_a_count, comparison_result.elements_b_count]
        colors = ['#4169E1', '#32CD32']
        
        bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')
        ax.set_title('图元数量对比', fontsize=self.config.label_font_size, fontweight='bold')
        ax.set_ylabel('图元数量', fontsize=self.config.label_font_size)
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(value), ha='center', va='bottom', fontweight='bold')
    
    def _render_element_type_distribution(self, ax, comparison_result: ComparisonResult):
        """渲染图元类型分布图"""
        
        # 统计图元类型
        type_counts = {}
        for diff in comparison_result.differences:
            if diff.element_a:
                elem_type = type(diff.element_a).__name__
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
            if diff.element_b:
                elem_type = type(diff.element_b).__name__
                type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        if type_counts:
            types = list(type_counts.keys())
            counts = list(type_counts.values())
            
            ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
            ax.set_title('图元类型分布', fontsize=self.config.label_font_size, fontweight='bold')
        else:
            ax.text(0.5, 0.5, '无图元数据', ha='center', va='center', 
                   fontsize=self.config.label_font_size, transform=ax.transAxes)
            ax.set_title('图元类型分布', fontsize=self.config.label_font_size, fontweight='bold')
    
    def _render_similarity_histogram(self, ax, comparison_result: ComparisonResult):
        """渲染相似度分布直方图"""
        
        similarities = [diff.similarity for diff in comparison_result.differences if diff.similarity > 0]
        
        if similarities:
            ax.hist(similarities, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_title('相似度分布', fontsize=self.config.label_font_size, fontweight='bold')
            ax.set_xlabel('相似度', fontsize=self.config.label_font_size)
            ax.set_ylabel('频次', fontsize=self.config.label_font_size)
        else:
            ax.text(0.5, 0.5, '无相似度数据', ha='center', va='center', 
                   fontsize=self.config.label_font_size, transform=ax.transAxes)
            ax.set_title('相似度分布', fontsize=self.config.label_font_size, fontweight='bold')
    
    def _render_similarity_boxplot(self, ax, comparison_result: ComparisonResult):
        """渲染相似度箱线图"""
        
        similarities = [diff.similarity for diff in comparison_result.differences if diff.similarity > 0]
        
        if similarities:
            ax.boxplot(similarities, patch_artist=True, 
                      boxprops=dict(facecolor='lightblue', alpha=0.7))
            ax.set_title('相似度箱线图', fontsize=self.config.label_font_size, fontweight='bold')
            ax.set_ylabel('相似度', fontsize=self.config.label_font_size)
        else:
            ax.text(0.5, 0.5, '无相似度数据', ha='center', va='center', 
                   fontsize=self.config.label_font_size, transform=ax.transAxes)
            ax.set_title('相似度箱线图', fontsize=self.config.label_font_size, fontweight='bold')
    
    def _render_elements_on_plot(self, ax, comparison_result: ComparisonResult):
        """在图上渲染图元"""
        
        for diff in comparison_result.differences:
            color = self.color_map[diff.diff_type]
            alpha = 0.7 if diff.diff_type != DifferenceType.UNCHANGED else 0.3
            
            # 渲染原图元
            if diff.element_a:
                self._draw_element(ax, diff.element_a, color, alpha, 'A')
            
            # 渲染新图元
            if diff.element_b and diff.element_b != diff.element_a:
                self._draw_element(ax, diff.element_b, color, alpha, 'B')
    
    def _draw_element(self, ax, element: Element, color: str, alpha: float, label: str):
        """绘制单个图元"""
        
        if isinstance(element, Line):
            ax.plot([element.start.x, element.end.x], [element.start.y, element.end.y], 
                   color=color, alpha=alpha, linewidth=2, label=f'{label}: Line')
        
        elif isinstance(element, GeoCircle):
            circle = Circle((element.center.x, element.center.y), element.radius, 
                          color=color, alpha=alpha, fill=False, linewidth=2)
            ax.add_patch(circle)
        
        elif isinstance(element, Arc):
            # 简化为圆形
            circle = Circle((element.center.x, element.center.y), element.radius, 
                          color=color, alpha=alpha, fill=False, linewidth=2, linestyle='--')
            ax.add_patch(circle)
        
        elif isinstance(element, Text):
            ax.scatter(element.position.x, element.position.y, color=color, alpha=alpha, 
                      s=50, marker='s', label=f'{label}: Text')
    
    def update_config(self, new_config: RenderConfig):
        """更新渲染配置"""
        self.config = new_config
        
        # 更新颜色映射
        self.color_map = {
            DifferenceType.ADDED: self.config.added_color,
            DifferenceType.DELETED: self.config.deleted_color,
            DifferenceType.MODIFIED: self.config.modified_color,
            DifferenceType.UNCHANGED: self.config.unchanged_color
        }
