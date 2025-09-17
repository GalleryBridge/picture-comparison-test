"""
相似度计算器模块

提供精确的相似度计算算法，支持多种相似度度量方法。
包含几何相似度、属性相似度、上下文相似度等计算功能。
"""

import math
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from geometry.elements import Element, Point, Line, Circle, Arc, Text
from matching.tolerance import ToleranceConfig


class SimilarityMethod(Enum):
    """相似度计算方法"""
    EUCLIDEAN = "euclidean"          # 欧几里得距离
    MANHATTAN = "manhattan"          # 曼哈顿距离
    COSINE = "cosine"               # 余弦相似度
    JACCARD = "jaccard"             # 雅卡尔相似度
    HAUSDORFF = "hausdorff"         # 豪斯多夫距离
    WEIGHTED_COMBINED = "weighted"   # 加权组合


@dataclass
class SimilarityResult:
    """相似度计算结果"""
    overall_similarity: float
    geometric_similarity: float
    attribute_similarity: float
    contextual_similarity: float
    method_used: SimilarityMethod
    detailed_scores: Dict[str, float]
    confidence: float


@dataclass
class SimilarityWeights:
    """相似度权重配置"""
    position: float = 0.3
    shape: float = 0.4
    size: float = 0.2
    orientation: float = 0.1
    
    def normalize(self):
        """归一化权重"""
        total = self.position + self.shape + self.size + self.orientation
        if total > 0:
            self.position /= total
            self.shape /= total
            self.size /= total
            self.orientation /= total


class SimilarityCalculator:
    """相似度计算器 - 提供多种相似度计算方法"""
    
    def __init__(self, tolerance_config: ToleranceConfig, method: SimilarityMethod = SimilarityMethod.WEIGHTED_COMBINED):
        self.tolerance = tolerance_config
        self.method = method
        self.weights = SimilarityWeights()
        self.weights.normalize()
        
        # 缓存计算结果
        self._similarity_cache: Dict[Tuple[int, int], SimilarityResult] = {}
    
    def calculate_similarity(self, element_a: Element, element_b: Element, 
                           use_cache: bool = True) -> SimilarityResult:
        """计算两个图元的相似度"""
        
        # 检查缓存
        cache_key = (id(element_a), id(element_b))
        if use_cache and cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        # 类型检查
        if type(element_a) != type(element_b):
            result = SimilarityResult(
                overall_similarity=0.0,
                geometric_similarity=0.0,
                attribute_similarity=0.0,
                contextual_similarity=0.0,
                method_used=self.method,
                detailed_scores={},
                confidence=1.0
            )
            if use_cache:
                self._similarity_cache[cache_key] = result
            return result
        
        # 根据方法计算相似度
        if self.method == SimilarityMethod.WEIGHTED_COMBINED:
            result = self._calculate_weighted_similarity(element_a, element_b)
        elif self.method == SimilarityMethod.EUCLIDEAN:
            result = self._calculate_euclidean_similarity(element_a, element_b)
        elif self.method == SimilarityMethod.MANHATTAN:
            result = self._calculate_manhattan_similarity(element_a, element_b)
        elif self.method == SimilarityMethod.COSINE:
            result = self._calculate_cosine_similarity(element_a, element_b)
        elif self.method == SimilarityMethod.JACCARD:
            result = self._calculate_jaccard_similarity(element_a, element_b)
        elif self.method == SimilarityMethod.HAUSDORFF:
            result = self._calculate_hausdorff_similarity(element_a, element_b)
        else:
            result = self._calculate_weighted_similarity(element_a, element_b)
        
        # 缓存结果
        if use_cache:
            self._similarity_cache[cache_key] = result
        
        return result
    
    def _calculate_weighted_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """计算加权组合相似度"""
        
        # 1. 几何相似度
        geometric_sim = self._calculate_geometric_similarity(element_a, element_b)
        
        # 2. 属性相似度
        attribute_sim = self._calculate_attribute_similarity(element_a, element_b)
        
        # 3. 上下文相似度（暂时简化）
        contextual_sim = 1.0  # 可以后续扩展
        
        # 4. 详细分数
        detailed_scores = self._calculate_detailed_scores(element_a, element_b)
        
        # 5. 加权计算总相似度
        overall_sim = (
            geometric_sim * 0.6 +
            attribute_sim * 0.3 +
            contextual_sim * 0.1
        )
        
        # 6. 计算置信度
        confidence = self._calculate_confidence(element_a, element_b, detailed_scores)
        
        return SimilarityResult(
            overall_similarity=overall_sim,
            geometric_similarity=geometric_sim,
            attribute_similarity=attribute_sim,
            contextual_similarity=contextual_sim,
            method_used=SimilarityMethod.WEIGHTED_COMBINED,
            detailed_scores=detailed_scores,
            confidence=confidence
        )
    
    def _calculate_geometric_similarity(self, element_a: Element, element_b: Element) -> float:
        """计算几何相似度"""
        
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            return self._calculate_line_geometric_similarity(element_a, element_b)
        elif isinstance(element_a, Circle) and isinstance(element_b, Circle):
            return self._calculate_circle_geometric_similarity(element_a, element_b)
        elif isinstance(element_a, Arc) and isinstance(element_b, Arc):
            return self._calculate_arc_geometric_similarity(element_a, element_b)
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            return self._calculate_text_geometric_similarity(element_a, element_b)
        else:
            return 0.0
    
    def _calculate_line_geometric_similarity(self, line_a: Line, line_b: Line) -> float:
        """计算线段几何相似度"""
        
        # 1. 位置相似度
        center_a = line_a.midpoint()
        center_b = line_b.midpoint()
        position_sim = self._position_similarity(center_a, center_b)
        
        # 2. 长度相似度
        length_sim = self._length_similarity(line_a.length(), line_b.length())
        
        # 3. 角度相似度
        angle_sim = self._angle_similarity(line_a.angle(), line_b.angle())
        
        # 4. 端点相似度
        endpoint_sim = self._endpoint_similarity(line_a, line_b)
        
        # 加权组合
        return (
            position_sim * self.weights.position +
            length_sim * self.weights.size +
            angle_sim * self.weights.orientation +
            endpoint_sim * self.weights.shape
        )
    
    def _calculate_circle_geometric_similarity(self, circle_a: Circle, circle_b: Circle) -> float:
        """计算圆形几何相似度"""
        
        # 1. 中心位置相似度
        position_sim = self._position_similarity(circle_a.center, circle_b.center)
        
        # 2. 半径相似度
        radius_sim = self._radius_similarity(circle_a.radius, circle_b.radius)
        
        # 圆形的形状和方向相似度都是1.0（圆形没有方向性）
        return (
            position_sim * self.weights.position +
            radius_sim * self.weights.size +
            1.0 * self.weights.shape +
            1.0 * self.weights.orientation
        )
    
    def _calculate_arc_geometric_similarity(self, arc_a: Arc, arc_b: Arc) -> float:
        """计算弧形几何相似度"""
        
        # 1. 中心位置相似度
        position_sim = self._position_similarity(arc_a.center, arc_b.center)
        
        # 2. 半径相似度
        radius_sim = self._radius_similarity(arc_a.radius, arc_b.radius)
        
        # 3. 弧长相似度
        arc_length_sim = self._length_similarity(arc_a.arc_length(), arc_b.arc_length())
        
        # 4. 角度范围相似度
        angle_range_sim = self._arc_angle_similarity(arc_a, arc_b)
        
        return (
            position_sim * self.weights.position +
            radius_sim * self.weights.size +
            arc_length_sim * self.weights.shape +
            angle_range_sim * self.weights.orientation
        )
    
    def _calculate_text_geometric_similarity(self, text_a: Text, text_b: Text) -> float:
        """计算文本几何相似度"""
        
        # 1. 位置相似度
        position_sim = self._position_similarity(text_a.position, text_b.position)
        
        # 2. 字体大小相似度
        size_sim = self._length_similarity(text_a.height, text_b.height)
        
        # 3. 内容相似度（作为形状相似度）
        content_sim = self._text_content_similarity(text_a.content, text_b.content)
        
        # 4. 旋转角度相似度
        rotation_sim = self._angle_similarity(text_a.rotation, text_b.rotation)
        
        return (
            position_sim * self.weights.position +
            size_sim * self.weights.size +
            content_sim * self.weights.shape +
            rotation_sim * self.weights.orientation
        )
    
    def _calculate_attribute_similarity(self, element_a: Element, element_b: Element) -> float:
        """计算属性相似度"""
        
        similarities = []
        
        # 图层相似度
        if hasattr(element_a, 'layer') and hasattr(element_b, 'layer'):
            layer_sim = 1.0 if element_a.layer == element_b.layer else 0.5
            similarities.append(layer_sim)
        
        # 颜色相似度
        if hasattr(element_a, 'color') and hasattr(element_b, 'color'):
            color_sim = 1.0 if element_a.color == element_b.color else 0.3
            similarities.append(color_sim)
        
        # 线型相似度（对于线段）
        if hasattr(element_a, 'line_type') and hasattr(element_b, 'line_type'):
            line_type_sim = 1.0 if element_a.line_type == element_b.line_type else 0.7
            similarities.append(line_type_sim)
        
        # 字体相似度（对于文本）
        if hasattr(element_a, 'font') and hasattr(element_b, 'font'):
            font_sim = 1.0 if element_a.font == element_b.font else 0.8
            similarities.append(font_sim)
        
        return sum(similarities) / len(similarities) if similarities else 1.0
    
    def _calculate_detailed_scores(self, element_a: Element, element_b: Element) -> Dict[str, float]:
        """计算详细分数"""
        
        scores = {}
        
        # 通用分数
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        scores['position'] = self._position_similarity(center_a, center_b)
        
        # 类型特定分数
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            scores['length'] = self._length_similarity(element_a.length(), element_b.length())
            scores['angle'] = self._angle_similarity(element_a.angle(), element_b.angle())
            scores['endpoint'] = self._endpoint_similarity(element_a, element_b)
        
        elif isinstance(element_a, Circle) and isinstance(element_b, Circle):
            scores['radius'] = self._radius_similarity(element_a.radius, element_b.radius)
            scores['area'] = self._area_similarity(element_a.area(), element_b.area())
        
        elif isinstance(element_a, Arc) and isinstance(element_b, Arc):
            scores['radius'] = self._radius_similarity(element_a.radius, element_b.radius)
            scores['arc_length'] = self._length_similarity(element_a.arc_length(), element_b.arc_length())
            scores['angle_range'] = self._arc_angle_similarity(element_a, element_b)
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            scores['content'] = self._text_content_similarity(element_a.content, element_b.content)
            scores['height'] = self._length_similarity(element_a.height, element_b.height)
            scores['rotation'] = self._angle_similarity(element_a.rotation, element_b.rotation)
        
        return scores
    
    def _position_similarity(self, pos_a: Point, pos_b: Point) -> float:
        """位置相似度"""
        distance = pos_a.distance_to(pos_b)
        return max(0.0, 1.0 - distance / self.tolerance.position)
    
    def _length_similarity(self, length_a: float, length_b: float) -> float:
        """长度相似度"""
        if length_a == 0 and length_b == 0:
            return 1.0
        
        max_length = max(length_a, length_b)
        if max_length == 0:
            return 1.0
        
        ratio_diff = abs(length_a - length_b) / max_length
        return max(0.0, 1.0 - ratio_diff / self.tolerance.length_ratio)
    
    def _angle_similarity(self, angle_a: float, angle_b: float) -> float:
        """角度相似度"""
        # 处理角度周期性
        angle_diff = abs(angle_a - angle_b)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        return max(0.0, 1.0 - angle_diff / self.tolerance.angle)
    
    def _radius_similarity(self, radius_a: float, radius_b: float) -> float:
        """半径相似度"""
        radius_diff = abs(radius_a - radius_b)
        return max(0.0, 1.0 - radius_diff / self.tolerance.radius_tolerance)
    
    def _area_similarity(self, area_a: float, area_b: float) -> float:
        """面积相似度"""
        if area_a == 0 and area_b == 0:
            return 1.0
        
        max_area = max(area_a, area_b)
        if max_area == 0:
            return 1.0
        
        ratio_diff = abs(area_a - area_b) / max_area
        return max(0.0, 1.0 - ratio_diff / (self.tolerance.length_ratio * 2))  # 面积容差是长度容差的2倍
    
    def _endpoint_similarity(self, line_a: Line, line_b: Line) -> float:
        """端点相似度"""
        # 方案1: 起点对起点，终点对终点
        sim1 = (
            self._position_similarity(line_a.start, line_b.start) +
            self._position_similarity(line_a.end, line_b.end)
        ) / 2
        
        # 方案2: 起点对终点，终点对起点
        sim2 = (
            self._position_similarity(line_a.start, line_b.end) +
            self._position_similarity(line_a.end, line_b.start)
        ) / 2
        
        return max(sim1, sim2)
    
    def _arc_angle_similarity(self, arc_a: Arc, arc_b: Arc) -> float:
        """弧角度范围相似度"""
        start_sim = self._angle_similarity(arc_a.start_angle, arc_b.start_angle)
        end_sim = self._angle_similarity(arc_a.end_angle, arc_b.end_angle)
        return (start_sim + end_sim) / 2
    
    def _text_content_similarity(self, content_a: str, content_b: str) -> float:
        """文本内容相似度"""
        if content_a == content_b:
            return 1.0
        
        if not content_a or not content_b:
            return 0.0
        
        # 使用编辑距离计算相似度
        return self._levenshtein_similarity(content_a, content_b)
    
    def _levenshtein_similarity(self, s1: str, s2: str) -> float:
        """基于编辑距离的字符串相似度"""
        if len(s1) == 0:
            return 0.0 if len(s2) > 0 else 1.0
        if len(s2) == 0:
            return 0.0
        
        # 计算编辑距离
        distance = self._levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        return 1.0 - distance / max_len
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
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
    
    def _calculate_confidence(self, element_a: Element, element_b: Element, 
                            detailed_scores: Dict[str, float]) -> float:
        """计算置信度"""
        
        # 基于详细分数的方差计算置信度
        if not detailed_scores:
            return 0.5
        
        scores = list(detailed_scores.values())
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # 方差越小，置信度越高
        confidence = 1.0 - min(variance, 0.5) * 2
        
        # 根据图元复杂度调整
        complexity_factor = self._calculate_element_complexity(element_a)
        confidence *= (1.0 + complexity_factor * 0.1)
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_element_complexity(self, element: Element) -> float:
        """计算图元复杂度"""
        if isinstance(element, Line):
            return 1.0
        elif isinstance(element, Circle):
            return 1.2
        elif isinstance(element, Arc):
            return 1.5
        elif isinstance(element, Text):
            return 1.3 + len(element.content) * 0.01
        else:
            return 1.0
    
    # 其他相似度计算方法的实现
    def _calculate_euclidean_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """欧几里得距离相似度"""
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        distance = center_a.distance_to(center_b)
        
        similarity = max(0.0, 1.0 - distance / self.tolerance.max_search_radius)
        
        return SimilarityResult(
            overall_similarity=similarity,
            geometric_similarity=similarity,
            attribute_similarity=1.0,
            contextual_similarity=1.0,
            method_used=SimilarityMethod.EUCLIDEAN,
            detailed_scores={'distance': distance},
            confidence=0.8
        )
    
    def _calculate_manhattan_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """曼哈顿距离相似度"""
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        
        manhattan_distance = abs(center_a.x - center_b.x) + abs(center_a.y - center_b.y)
        similarity = max(0.0, 1.0 - manhattan_distance / (self.tolerance.max_search_radius * 2))
        
        return SimilarityResult(
            overall_similarity=similarity,
            geometric_similarity=similarity,
            attribute_similarity=1.0,
            contextual_similarity=1.0,
            method_used=SimilarityMethod.MANHATTAN,
            detailed_scores={'manhattan_distance': manhattan_distance},
            confidence=0.7
        )
    
    def _calculate_cosine_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """余弦相似度（简化实现）"""
        # 将图元特征向量化
        vector_a = self._element_to_vector(element_a)
        vector_b = self._element_to_vector(element_b)
        
        # 计算余弦相似度
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        
        if norm_a == 0 or norm_b == 0:
            similarity = 0.0
        else:
            similarity = dot_product / (norm_a * norm_b)
        
        return SimilarityResult(
            overall_similarity=similarity,
            geometric_similarity=similarity,
            attribute_similarity=1.0,
            contextual_similarity=1.0,
            method_used=SimilarityMethod.COSINE,
            detailed_scores={'cosine': similarity},
            confidence=0.9
        )
    
    def _calculate_jaccard_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """雅卡尔相似度（简化实现）"""
        # 基于属性集合的雅卡尔相似度
        attrs_a = self._get_element_attributes(element_a)
        attrs_b = self._get_element_attributes(element_b)
        
        intersection = len(attrs_a & attrs_b)
        union = len(attrs_a | attrs_b)
        
        similarity = intersection / union if union > 0 else 0.0
        
        return SimilarityResult(
            overall_similarity=similarity,
            geometric_similarity=0.5,
            attribute_similarity=similarity,
            contextual_similarity=1.0,
            method_used=SimilarityMethod.JACCARD,
            detailed_scores={'jaccard': similarity},
            confidence=0.6
        )
    
    def _calculate_hausdorff_similarity(self, element_a: Element, element_b: Element) -> SimilarityResult:
        """豪斯多夫距离相似度（简化实现）"""
        # 获取图元的关键点
        points_a = self._get_element_points(element_a)
        points_b = self._get_element_points(element_b)
        
        # 计算豪斯多夫距离
        hausdorff_dist = self._hausdorff_distance(points_a, points_b)
        similarity = max(0.0, 1.0 - hausdorff_dist / self.tolerance.max_search_radius)
        
        return SimilarityResult(
            overall_similarity=similarity,
            geometric_similarity=similarity,
            attribute_similarity=1.0,
            contextual_similarity=1.0,
            method_used=SimilarityMethod.HAUSDORFF,
            detailed_scores={'hausdorff_distance': hausdorff_dist},
            confidence=0.8
        )
    
    def _element_to_vector(self, element: Element) -> np.ndarray:
        """将图元转换为特征向量"""
        if isinstance(element, Line):
            return np.array([
                element.start.x, element.start.y,
                element.end.x, element.end.y,
                element.length(), element.angle()
            ])
        elif isinstance(element, Circle):
            return np.array([
                element.center.x, element.center.y,
                element.radius, element.area(), 0, 0
            ])
        elif isinstance(element, Arc):
            return np.array([
                element.center.x, element.center.y,
                element.radius, element.arc_length(),
                element.start_angle, element.end_angle
            ])
        elif isinstance(element, Text):
            return np.array([
                element.position.x, element.position.y,
                element.height, len(element.content),
                element.rotation, 0
            ])
        else:
            return np.zeros(6)
    
    def _get_element_attributes(self, element: Element) -> set:
        """获取图元属性集合"""
        attrs = {type(element).__name__}
        
        if hasattr(element, 'layer'):
            attrs.add(f"layer_{element.layer}")
        if hasattr(element, 'color'):
            attrs.add(f"color_{element.color}")
        if hasattr(element, 'line_type'):
            attrs.add(f"line_type_{element.line_type}")
        if hasattr(element, 'font'):
            attrs.add(f"font_{element.font}")
        
        return attrs
    
    def _get_element_points(self, element: Element) -> List[Point]:
        """获取图元的关键点"""
        if isinstance(element, Line):
            return [element.start, element.end]
        elif isinstance(element, (Circle, Arc)):
            # 圆形/弧形的关键点：中心点和边界点
            center = element.center
            radius = element.radius
            return [
                center,
                Point(center.x + radius, center.y),
                Point(center.x - radius, center.y),
                Point(center.x, center.y + radius),
                Point(center.x, center.y - radius)
            ]
        elif isinstance(element, Text):
            return [element.position]
        else:
            return []
    
    def _hausdorff_distance(self, points_a: List[Point], points_b: List[Point]) -> float:
        """计算豪斯多夫距离"""
        if not points_a or not points_b:
            return float('inf')
        
        # 计算从A到B的最大最小距离
        max_min_dist_a_to_b = 0
        for point_a in points_a:
            min_dist = min(point_a.distance_to(point_b) for point_b in points_b)
            max_min_dist_a_to_b = max(max_min_dist_a_to_b, min_dist)
        
        # 计算从B到A的最大最小距离
        max_min_dist_b_to_a = 0
        for point_b in points_b:
            min_dist = min(point_b.distance_to(point_a) for point_a in points_a)
            max_min_dist_b_to_a = max(max_min_dist_b_to_a, min_dist)
        
        return max(max_min_dist_a_to_b, max_min_dist_b_to_a)
    
    def clear_cache(self):
        """清空缓存"""
        self._similarity_cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        return {
            'cache_size': len(self._similarity_cache),
            'cache_hits': getattr(self, '_cache_hits', 0),
            'cache_misses': getattr(self, '_cache_misses', 0)
        }
