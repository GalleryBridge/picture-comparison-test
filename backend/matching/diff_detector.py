"""
差异检测器模块

基于图元匹配结果检测图纸差异，识别新增、删除、修改的图元。
提供详细的差异分析和统计信息。
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum
import time

from geometry.elements import Element, Point, Line, Circle, Arc, Text
from matching.element_matcher import ElementMatcher, MatchResult, MatchingStatistics
from matching.tolerance import ToleranceConfig


class DifferenceType(Enum):
    """差异类型"""
    ADDED = "added"          # 新增图元
    DELETED = "deleted"      # 删除图元
    MODIFIED = "modified"    # 修改图元
    UNCHANGED = "unchanged"  # 未变化图元


class ModificationType(Enum):
    """修改类型"""
    POSITION = "position"        # 位置变化
    SIZE = "size"               # 尺寸变化
    SHAPE = "shape"             # 形状变化
    ATTRIBUTE = "attribute"     # 属性变化
    ORIENTATION = "orientation" # 方向变化


@dataclass
class DifferenceDetail:
    """差异详情"""
    element_a: Optional[Element]  # 原图元（删除时为None）
    element_b: Optional[Element]  # 新图元（新增时为None）
    diff_type: DifferenceType
    modification_types: List[ModificationType]
    similarity: float
    confidence: float
    geometric_changes: Dict[str, float]
    attribute_changes: Dict[str, any]
    description: str


@dataclass
class DifferenceStatistics:
    """差异统计信息"""
    total_elements_a: int
    total_elements_b: int
    
    # 差异数量
    added_count: int
    deleted_count: int
    modified_count: int
    unchanged_count: int
    
    # 修改类型统计
    position_changes: int
    size_changes: int
    shape_changes: int
    attribute_changes: int
    orientation_changes: int
    
    # 整体统计
    total_differences: int
    change_rate: float
    processing_time: float
    
    # 按图元类型统计
    type_statistics: Dict[str, Dict[str, int]]


class DiffDetector:
    """差异检测器 - 基于匹配结果检测图纸差异"""
    
    def __init__(self, tolerance_config: ToleranceConfig):
        self.tolerance = tolerance_config
        self.element_matcher = ElementMatcher(tolerance_config)
        
        # 差异阈值配置
        self.modification_thresholds = {
            'position': tolerance_config.position,
            'size': tolerance_config.length_ratio,
            'angle': tolerance_config.angle,
            'radius': tolerance_config.radius_tolerance
        }
    
    def detect_differences(self, elements_a: List[Element], elements_b: List[Element]) -> Tuple[List[DifferenceDetail], DifferenceStatistics]:
        """检测两组图元的差异"""
        start_time = time.time()
        
        # 1. 执行图元匹配
        matches, match_stats = self.element_matcher.match_elements(elements_a, elements_b)
        
        # 2. 分析差异
        differences = []
        
        # 2.1 处理匹配的图元（可能有修改）
        matched_a_ids = set()
        matched_b_ids = set()
        
        for match in matches:
            # 找到图元在列表中的索引
            a_idx = self._find_element_index(match.element_a, elements_a)
            b_idx = self._find_element_index(match.element_b, elements_b)
            
            if a_idx is not None and b_idx is not None:
                matched_a_ids.add(a_idx)
                matched_b_ids.add(b_idx)
                
                # 分析是否有修改
                diff_detail = self._analyze_modification(match)
                differences.append(diff_detail)
        
        # 2.2 处理未匹配的图元A（删除的图元）
        for i, element_a in enumerate(elements_a):
            if i not in matched_a_ids:
                diff_detail = DifferenceDetail(
                    element_a=element_a,
                    element_b=None,
                    diff_type=DifferenceType.DELETED,
                    modification_types=[],
                    similarity=0.0,
                    confidence=1.0,
                    geometric_changes={},
                    attribute_changes={},
                    description=f"删除的{type(element_a).__name__}"
                )
                differences.append(diff_detail)
        
        # 2.3 处理未匹配的图元B（新增的图元）
        for i, element_b in enumerate(elements_b):
            if i not in matched_b_ids:
                diff_detail = DifferenceDetail(
                    element_a=None,
                    element_b=element_b,
                    diff_type=DifferenceType.ADDED,
                    modification_types=[],
                    similarity=0.0,
                    confidence=1.0,
                    geometric_changes={},
                    attribute_changes={},
                    description=f"新增的{type(element_b).__name__}"
                )
                differences.append(diff_detail)
        
        # 3. 计算统计信息
        processing_time = time.time() - start_time
        statistics = self._calculate_statistics(elements_a, elements_b, differences, processing_time)
        
        return differences, statistics
    
    def _find_element_index(self, target_element: Element, element_list: List[Element]) -> Optional[int]:
        """在图元列表中找到目标图元的索引"""
        for i, element in enumerate(element_list):
            if element is target_element:
                return i
        return None
    
    def _analyze_modification(self, match: MatchResult) -> DifferenceDetail:
        """分析匹配图元的修改情况"""
        
        element_a = match.element_a
        element_b = match.element_b
        
        # 判断是否有修改
        if match.similarity >= 0.999:  # 几乎完全相同
            diff_type = DifferenceType.UNCHANGED
            modification_types = []
            description = f"未变化的{type(element_a).__name__}"
        else:
            diff_type = DifferenceType.MODIFIED
            modification_types = self._identify_modification_types(element_a, element_b)
            description = f"修改的{type(element_a).__name__}: {', '.join([mt.value for mt in modification_types])}"
        
        # 计算几何变化
        geometric_changes = self._calculate_geometric_changes(element_a, element_b)
        
        # 计算属性变化
        attribute_changes = self._calculate_attribute_changes(element_a, element_b)
        
        return DifferenceDetail(
            element_a=element_a,
            element_b=element_b,
            diff_type=diff_type,
            modification_types=modification_types,
            similarity=match.similarity,
            confidence=match.confidence,
            geometric_changes=geometric_changes,
            attribute_changes=attribute_changes,
            description=description
        )
    
    def _identify_modification_types(self, element_a: Element, element_b: Element) -> List[ModificationType]:
        """识别修改类型"""
        
        modification_types = []
        
        # 位置变化检测
        if self._has_position_change(element_a, element_b):
            modification_types.append(ModificationType.POSITION)
        
        # 尺寸变化检测
        if self._has_size_change(element_a, element_b):
            modification_types.append(ModificationType.SIZE)
        
        # 形状变化检测
        if self._has_shape_change(element_a, element_b):
            modification_types.append(ModificationType.SHAPE)
        
        # 属性变化检测
        if self._has_attribute_change(element_a, element_b):
            modification_types.append(ModificationType.ATTRIBUTE)
        
        # 方向变化检测
        if self._has_orientation_change(element_a, element_b):
            modification_types.append(ModificationType.ORIENTATION)
        
        return modification_types
    
    def _has_position_change(self, element_a: Element, element_b: Element) -> bool:
        """检测位置变化"""
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        
        distance = center_a.distance_to(center_b)
        return distance > self.modification_thresholds['position']
    
    def _has_size_change(self, element_a: Element, element_b: Element) -> bool:
        """检测尺寸变化"""
        
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            length_a = element_a.length()
            length_b = element_b.length()
            if length_a > 0:
                ratio_change = abs(length_a - length_b) / length_a
                return ratio_change > self.modification_thresholds['size']
        
        elif isinstance(element_a, (Circle, Arc)) and isinstance(element_b, (Circle, Arc)):
            radius_change = abs(element_a.radius - element_b.radius)
            return radius_change > self.modification_thresholds['radius']
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            height_change = abs(element_a.height - element_b.height)
            if element_a.height > 0:
                ratio_change = height_change / element_a.height
                return ratio_change > self.modification_thresholds['size']
        
        return False
    
    def _has_shape_change(self, element_a: Element, element_b: Element) -> bool:
        """检测形状变化"""
        
        if isinstance(element_a, Arc) and isinstance(element_b, Arc):
            # 弧形的角度范围变化
            angle_diff_start = abs(element_a.start_angle - element_b.start_angle)
            angle_diff_end = abs(element_a.end_angle - element_b.end_angle)
            
            return (angle_diff_start > self.modification_thresholds['angle'] or 
                   angle_diff_end > self.modification_thresholds['angle'])
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            # 文本内容变化
            return element_a.content != element_b.content
        
        return False
    
    def _has_attribute_change(self, element_a: Element, element_b: Element) -> bool:
        """检测属性变化"""
        
        # 检查图层变化
        if hasattr(element_a, 'layer') and hasattr(element_b, 'layer'):
            if element_a.layer != element_b.layer:
                return True
        
        # 检查颜色变化
        if hasattr(element_a, 'color') and hasattr(element_b, 'color'):
            if element_a.color != element_b.color:
                return True
        
        # 检查线型变化
        if hasattr(element_a, 'line_type') and hasattr(element_b, 'line_type'):
            if element_a.line_type != element_b.line_type:
                return True
        
        # 检查字体变化
        if hasattr(element_a, 'font') and hasattr(element_b, 'font'):
            if element_a.font != element_b.font:
                return True
        
        return False
    
    def _has_orientation_change(self, element_a: Element, element_b: Element) -> bool:
        """检测方向变化"""
        
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            angle_diff = abs(element_a.angle() - element_b.angle())
            # 处理角度周期性
            angle_diff = min(angle_diff, 2 * 3.14159 - angle_diff)
            return angle_diff > self.modification_thresholds['angle']
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            rotation_diff = abs(element_a.rotation - element_b.rotation)
            return rotation_diff > self.modification_thresholds['angle']
        
        return False
    
    def _calculate_geometric_changes(self, element_a: Element, element_b: Element) -> Dict[str, float]:
        """计算几何变化量"""
        
        changes = {}
        
        # 位置变化
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        changes['position_distance'] = center_a.distance_to(center_b)
        changes['position_x_change'] = element_b.position.x - element_a.position.x if hasattr(element_a, 'position') and hasattr(element_b, 'position') else center_b.x - center_a.x
        changes['position_y_change'] = element_b.position.y - element_a.position.y if hasattr(element_a, 'position') and hasattr(element_b, 'position') else center_b.y - center_a.y
        
        # 类型特定变化
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            changes['length_change'] = element_b.length() - element_a.length()
            changes['angle_change'] = element_b.angle() - element_a.angle()
        
        elif isinstance(element_a, (Circle, Arc)) and isinstance(element_b, (Circle, Arc)):
            changes['radius_change'] = element_b.radius - element_a.radius
            
            if isinstance(element_a, Arc):
                changes['arc_length_change'] = element_b.arc_length() - element_a.arc_length()
                changes['start_angle_change'] = element_b.start_angle - element_a.start_angle
                changes['end_angle_change'] = element_b.end_angle - element_a.end_angle
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            changes['height_change'] = element_b.height - element_a.height
            changes['rotation_change'] = element_b.rotation - element_a.rotation
            changes['content_length_change'] = len(element_b.content) - len(element_a.content)
        
        return changes
    
    def _calculate_attribute_changes(self, element_a: Element, element_b: Element) -> Dict[str, any]:
        """计算属性变化"""
        
        changes = {}
        
        # 图层变化
        if hasattr(element_a, 'layer') and hasattr(element_b, 'layer'):
            if element_a.layer != element_b.layer:
                changes['layer'] = {'from': element_a.layer, 'to': element_b.layer}
        
        # 颜色变化
        if hasattr(element_a, 'color') and hasattr(element_b, 'color'):
            if element_a.color != element_b.color:
                changes['color'] = {'from': element_a.color, 'to': element_b.color}
        
        # 线型变化
        if hasattr(element_a, 'line_type') and hasattr(element_b, 'line_type'):
            if element_a.line_type != element_b.line_type:
                changes['line_type'] = {'from': element_a.line_type, 'to': element_b.line_type}
        
        # 字体变化
        if hasattr(element_a, 'font') and hasattr(element_b, 'font'):
            if element_a.font != element_b.font:
                changes['font'] = {'from': element_a.font, 'to': element_b.font}
        
        # 文本内容变化
        if isinstance(element_a, Text) and isinstance(element_b, Text):
            if element_a.content != element_b.content:
                changes['content'] = {'from': element_a.content, 'to': element_b.content}
        
        return changes
    
    def _get_element_center(self, element: Element) -> Point:
        """获取图元中心点"""
        if isinstance(element, Line):
            return Point(
                (element.start.x + element.end.x) / 2,
                (element.start.y + element.end.y) / 2
            )
        elif isinstance(element, (Circle, Arc)):
            return element.center
        elif isinstance(element, Text):
            return element.position
        else:
            return Point(0, 0)
    
    def _calculate_statistics(self, elements_a: List[Element], elements_b: List[Element], 
                            differences: List[DifferenceDetail], processing_time: float) -> DifferenceStatistics:
        """计算差异统计信息"""
        
        # 基本统计
        added_count = sum(1 for diff in differences if diff.diff_type == DifferenceType.ADDED)
        deleted_count = sum(1 for diff in differences if diff.diff_type == DifferenceType.DELETED)
        modified_count = sum(1 for diff in differences if diff.diff_type == DifferenceType.MODIFIED)
        unchanged_count = sum(1 for diff in differences if diff.diff_type == DifferenceType.UNCHANGED)
        
        # 修改类型统计
        position_changes = sum(1 for diff in differences 
                             if ModificationType.POSITION in diff.modification_types)
        size_changes = sum(1 for diff in differences 
                          if ModificationType.SIZE in diff.modification_types)
        shape_changes = sum(1 for diff in differences 
                           if ModificationType.SHAPE in diff.modification_types)
        attribute_changes = sum(1 for diff in differences 
                               if ModificationType.ATTRIBUTE in diff.modification_types)
        orientation_changes = sum(1 for diff in differences 
                                 if ModificationType.ORIENTATION in diff.modification_types)
        
        # 整体统计
        total_differences = added_count + deleted_count + modified_count
        total_elements = max(len(elements_a), len(elements_b))
        change_rate = total_differences / total_elements if total_elements > 0 else 0.0
        
        # 按图元类型统计
        type_statistics = self._calculate_type_statistics(differences)
        
        return DifferenceStatistics(
            total_elements_a=len(elements_a),
            total_elements_b=len(elements_b),
            added_count=added_count,
            deleted_count=deleted_count,
            modified_count=modified_count,
            unchanged_count=unchanged_count,
            position_changes=position_changes,
            size_changes=size_changes,
            shape_changes=shape_changes,
            attribute_changes=attribute_changes,
            orientation_changes=orientation_changes,
            total_differences=total_differences,
            change_rate=change_rate,
            processing_time=processing_time,
            type_statistics=type_statistics
        )
    
    def _calculate_type_statistics(self, differences: List[DifferenceDetail]) -> Dict[str, Dict[str, int]]:
        """按图元类型计算统计信息"""
        
        type_stats = {}
        
        for diff in differences:
            # 确定图元类型
            element = diff.element_a or diff.element_b
            if element is None:
                continue
            
            element_type = type(element).__name__
            
            if element_type not in type_stats:
                type_stats[element_type] = {
                    'added': 0,
                    'deleted': 0,
                    'modified': 0,
                    'unchanged': 0
                }
            
            # 统计差异类型
            if diff.diff_type == DifferenceType.ADDED:
                type_stats[element_type]['added'] += 1
            elif diff.diff_type == DifferenceType.DELETED:
                type_stats[element_type]['deleted'] += 1
            elif diff.diff_type == DifferenceType.MODIFIED:
                type_stats[element_type]['modified'] += 1
            elif diff.diff_type == DifferenceType.UNCHANGED:
                type_stats[element_type]['unchanged'] += 1
        
        return type_stats
    
    def get_differences_by_type(self, differences: List[DifferenceDetail], 
                               diff_type: DifferenceType) -> List[DifferenceDetail]:
        """按差异类型筛选差异"""
        return [diff for diff in differences if diff.diff_type == diff_type]
    
    def get_significant_differences(self, differences: List[DifferenceDetail], 
                                  min_confidence: float = 0.8) -> List[DifferenceDetail]:
        """获取重要差异（高置信度）"""
        return [diff for diff in differences if diff.confidence >= min_confidence]
    
    def generate_summary_report(self, differences: List[DifferenceDetail], 
                               statistics: DifferenceStatistics) -> str:
        """生成差异摘要报告"""
        
        report_lines = [
            "=== 图纸差异分析报告 ===",
            f"处理时间: {statistics.processing_time:.4f}秒",
            f"",
            f"图元统计:",
            f"  原图纸: {statistics.total_elements_a} 个图元",
            f"  新图纸: {statistics.total_elements_b} 个图元",
            f"",
            f"差异统计:",
            f"  新增: {statistics.added_count} 个",
            f"  删除: {statistics.deleted_count} 个", 
            f"  修改: {statistics.modified_count} 个",
            f"  未变化: {statistics.unchanged_count} 个",
            f"  总差异: {statistics.total_differences} 个",
            f"  变化率: {statistics.change_rate:.1%}",
            f"",
            f"修改类型统计:",
            f"  位置变化: {statistics.position_changes} 个",
            f"  尺寸变化: {statistics.size_changes} 个",
            f"  形状变化: {statistics.shape_changes} 个",
            f"  属性变化: {statistics.attribute_changes} 个",
            f"  方向变化: {statistics.orientation_changes} 个",
            f""
        ]
        
        # 按图元类型统计
        if statistics.type_statistics:
            report_lines.append("按图元类型统计:")
            for element_type, stats in statistics.type_statistics.items():
                report_lines.append(f"  {element_type}:")
                report_lines.append(f"    新增: {stats['added']}, 删除: {stats['deleted']}, 修改: {stats['modified']}, 未变化: {stats['unchanged']}")
        
        return "\n".join(report_lines)
