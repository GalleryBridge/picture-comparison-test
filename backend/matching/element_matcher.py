"""
图元匹配器模块

基于几何特征的图元匹配算法，支持不同类型图元的精确匹配。
使用空间索引优化匹配性能，支持容差配置。
"""

from typing import List, Dict, Tuple, Optional, Set
import math
import numpy as np
from dataclasses import dataclass

from geometry.elements import Element, Point, Line, Circle, Arc, Text
from geometry.spatial_index import SpatialIndex
from matching.tolerance import ToleranceConfig


@dataclass
class MatchResult:
    """匹配结果"""
    element_a: Element
    element_b: Element
    similarity: float
    match_type: str  # 'exact', 'similar', 'partial'
    confidence: float
    geometric_distance: float
    feature_differences: Dict[str, float]


@dataclass
class MatchingStatistics:
    """匹配统计信息"""
    total_elements_a: int
    total_elements_b: int
    matched_pairs: int
    unmatched_a: int
    unmatched_b: int
    exact_matches: int
    similar_matches: int
    partial_matches: int
    average_similarity: float
    processing_time: float


class ElementMatcher:
    """图元匹配器 - 核心匹配算法"""
    
    def __init__(self, tolerance_config: ToleranceConfig):
        self.tolerance = tolerance_config
        self.spatial_index_a = SpatialIndex()
        self.spatial_index_b = SpatialIndex()
        
        # 匹配结果缓存
        self._match_cache: Dict[Tuple[int, int], MatchResult] = {}
        
        # 特征权重配置
        self.feature_weights = {
            'position': 0.3,
            'geometry': 0.4,
            'attributes': 0.2,
            'context': 0.1
        }
    
    def match_elements(self, elements_a: List[Element], elements_b: List[Element]) -> Tuple[List[MatchResult], MatchingStatistics]:
        """匹配两组图元"""
        import time
        start_time = time.time()
        
        # 清空并重建空间索引
        self._build_spatial_indexes(elements_a, elements_b)
        
        # 执行匹配
        matches = []
        matched_b_ids = set()
        
        for i, element_a in enumerate(elements_a):
            best_match = self._find_best_match(element_a, elements_b, matched_b_ids)
            
            if best_match and best_match.similarity >= self.tolerance.similarity_threshold:
                matches.append(best_match)
                # 找到element_b在elements_b中的索引
                for j, element_b in enumerate(elements_b):
                    if element_b is best_match.element_b:
                        matched_b_ids.add(j)
                        break
        
        # 计算统计信息
        processing_time = time.time() - start_time
        stats = self._calculate_statistics(elements_a, elements_b, matches, processing_time)
        
        return matches, stats
    
    def _build_spatial_indexes(self, elements_a: List[Element], elements_b: List[Element]):
        """构建空间索引"""
        self.spatial_index_a.clear()
        self.spatial_index_b.clear()
        
        self.spatial_index_a.insert_batch(elements_a)
        self.spatial_index_b.insert_batch(elements_b)
    
    def _find_best_match(self, element_a: Element, elements_b: List[Element], 
                        matched_b_ids: Set[int]) -> Optional[MatchResult]:
        """为单个图元找到最佳匹配"""
        
        # 1. 使用空间索引找到候选匹配
        candidates = self._get_candidates(element_a, elements_b, matched_b_ids)
        
        if not candidates:
            return None
        
        # 2. 计算每个候选的相似度
        best_match = None
        best_similarity = 0.0
        
        for candidate_idx, candidate_element in candidates:
            if candidate_idx in matched_b_ids:
                continue
            
            similarity = self._calculate_similarity(element_a, candidate_element)
            
            if similarity > best_similarity and similarity >= self.tolerance.similarity_threshold:
                best_similarity = similarity
                
                # 创建匹配结果
                match_result = MatchResult(
                    element_a=element_a,
                    element_b=candidate_element,
                    similarity=similarity,
                    match_type=self._determine_match_type(similarity),
                    confidence=self._calculate_confidence(element_a, candidate_element, similarity),
                    geometric_distance=self._calculate_geometric_distance(element_a, candidate_element),
                    feature_differences=self._calculate_feature_differences(element_a, candidate_element)
                )
                
                best_match = match_result
        
        return best_match
    
    def _get_candidates(self, element_a: Element, elements_b: List[Element], 
                       matched_b_ids: Set[int]) -> List[Tuple[int, Element]]:
        """获取候选匹配图元"""
        
        # 1. 基于空间位置的候选
        nearby_candidates = self.spatial_index_b.query_nearby(
            element_a, self.tolerance.max_search_radius
        )
        
        # 2. 基于类型的过滤
        type_filtered = []
        for elem_id, elem in nearby_candidates:
            if type(elem) == type(element_a):  # 同类型匹配
                # 找到在elements_b中的索引
                for i, element_b in enumerate(elements_b):
                    if element_b is elem and i not in matched_b_ids:
                        type_filtered.append((i, elem))
                        break
        
        # 3. 限制候选数量
        if len(type_filtered) > self.tolerance.max_candidates_per_element:
            # 按距离排序，取最近的候选
            element_center = self._get_element_center(element_a)
            type_filtered.sort(key=lambda x: self._get_element_center(x[1]).distance_to(element_center))
            type_filtered = type_filtered[:self.tolerance.max_candidates_per_element]
        
        return type_filtered
    
    def _calculate_similarity(self, element_a: Element, element_b: Element) -> float:
        """计算两个图元的相似度"""
        
        if type(element_a) != type(element_b):
            return 0.0
        
        # 根据图元类型计算相似度
        if isinstance(element_a, Line):
            return self._calculate_line_similarity(element_a, element_b)
        elif isinstance(element_a, Circle):
            return self._calculate_circle_similarity(element_a, element_b)
        elif isinstance(element_a, Arc):
            return self._calculate_arc_similarity(element_a, element_b)
        elif isinstance(element_a, Text):
            return self._calculate_text_similarity(element_a, element_b)
        else:
            return 0.0
    
    def _calculate_line_similarity(self, line_a: Line, line_b: Line) -> float:
        """计算线段相似度"""
        
        # 1. 位置相似度
        pos_sim = self._calculate_position_similarity(
            self._get_element_center(line_a),
            self._get_element_center(line_b)
        )
        
        # 2. 长度相似度
        length_a = line_a.length()
        length_b = line_b.length()
        length_sim = self._calculate_length_similarity(length_a, length_b)
        
        # 3. 角度相似度
        angle_a = line_a.angle()
        angle_b = line_b.angle()
        angle_sim = self._calculate_angle_similarity(angle_a, angle_b)
        
        # 4. 端点相似度
        endpoint_sim = self._calculate_endpoint_similarity(line_a, line_b)
        
        # 加权平均
        similarity = (
            pos_sim * 0.25 +
            length_sim * 0.25 +
            angle_sim * 0.25 +
            endpoint_sim * 0.25
        )
        
        return similarity
    
    def _calculate_circle_similarity(self, circle_a: Circle, circle_b: Circle) -> float:
        """计算圆形相似度"""
        
        # 1. 中心位置相似度
        pos_sim = self._calculate_position_similarity(circle_a.center, circle_b.center)
        
        # 2. 半径相似度
        radius_diff = abs(circle_a.radius - circle_b.radius)
        radius_sim = max(0.0, 1.0 - radius_diff / self.tolerance.radius_tolerance)
        
        # 加权平均
        similarity = pos_sim * 0.5 + radius_sim * 0.5
        
        return similarity
    
    def _calculate_arc_similarity(self, arc_a: Arc, arc_b: Arc) -> float:
        """计算弧形相似度"""
        
        # 1. 中心位置相似度
        pos_sim = self._calculate_position_similarity(arc_a.center, arc_b.center)
        
        # 2. 半径相似度
        radius_diff = abs(arc_a.radius - arc_b.radius)
        radius_sim = max(0.0, 1.0 - radius_diff / self.tolerance.radius_tolerance)
        
        # 3. 角度范围相似度
        angle_sim = self._calculate_arc_angle_similarity(arc_a, arc_b)
        
        # 加权平均
        similarity = pos_sim * 0.4 + radius_sim * 0.3 + angle_sim * 0.3
        
        return similarity
    
    def _calculate_text_similarity(self, text_a: Text, text_b: Text) -> float:
        """计算文本相似度"""
        
        # 1. 位置相似度
        pos_sim = self._calculate_position_similarity(text_a.position, text_b.position)
        
        # 2. 内容相似度
        content_sim = self._calculate_text_content_similarity(text_a.content, text_b.content)
        
        # 3. 字体大小相似度
        height_diff = abs(text_a.height - text_b.height)
        height_sim = max(0.0, 1.0 - height_diff / (text_a.height * 0.2))  # 20%容差
        
        # 加权平均
        similarity = pos_sim * 0.3 + content_sim * 0.5 + height_sim * 0.2
        
        return similarity
    
    def _calculate_position_similarity(self, pos_a: Point, pos_b: Point) -> float:
        """计算位置相似度"""
        distance = pos_a.distance_to(pos_b)
        return max(0.0, 1.0 - distance / self.tolerance.position)
    
    def _calculate_length_similarity(self, length_a: float, length_b: float) -> float:
        """计算长度相似度"""
        if length_a == 0 and length_b == 0:
            return 1.0
        
        max_length = max(length_a, length_b)
        if max_length == 0:
            return 1.0
        
        length_diff_ratio = abs(length_a - length_b) / max_length
        return max(0.0, 1.0 - length_diff_ratio / self.tolerance.length_ratio)
    
    def _calculate_angle_similarity(self, angle_a: float, angle_b: float) -> float:
        """计算角度相似度"""
        # 处理角度周期性
        angle_diff = abs(angle_a - angle_b)
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        
        return max(0.0, 1.0 - angle_diff / self.tolerance.angle)
    
    def _calculate_endpoint_similarity(self, line_a: Line, line_b: Line) -> float:
        """计算线段端点相似度"""
        
        # 方案1: 起点对起点，终点对终点
        sim1 = (
            self._calculate_position_similarity(line_a.start, line_b.start) +
            self._calculate_position_similarity(line_a.end, line_b.end)
        ) / 2
        
        # 方案2: 起点对终点，终点对起点（考虑方向相反的情况）
        sim2 = (
            self._calculate_position_similarity(line_a.start, line_b.end) +
            self._calculate_position_similarity(line_a.end, line_b.start)
        ) / 2
        
        return max(sim1, sim2)
    
    def _calculate_arc_angle_similarity(self, arc_a: Arc, arc_b: Arc) -> float:
        """计算弧角度范围相似度"""
        
        # 计算弧长相似度
        arc_length_a = arc_a.arc_length()
        arc_length_b = arc_b.arc_length()
        length_sim = self._calculate_length_similarity(arc_length_a, arc_length_b)
        
        # 计算起始角度和结束角度相似度
        start_angle_sim = self._calculate_angle_similarity(arc_a.start_angle, arc_b.start_angle)
        end_angle_sim = self._calculate_angle_similarity(arc_a.end_angle, arc_b.end_angle)
        
        return (length_sim + start_angle_sim + end_angle_sim) / 3
    
    def _calculate_text_content_similarity(self, content_a: str, content_b: str) -> float:
        """计算文本内容相似度"""
        
        if content_a == content_b:
            return 1.0
        
        if not content_a or not content_b:
            return 0.0
        
        # 简单的字符串相似度计算（可以使用更复杂的算法如编辑距离）
        content_a = content_a.strip().lower()
        content_b = content_b.strip().lower()
        
        if content_a == content_b:
            return 1.0
        
        # 计算字符重叠度
        set_a = set(content_a)
        set_b = set(content_b)
        
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _determine_match_type(self, similarity: float) -> str:
        """确定匹配类型"""
        if similarity >= 0.95:
            return 'exact'
        elif similarity >= 0.8:
            return 'similar'
        elif similarity >= self.tolerance.similarity_threshold:
            return 'partial'
        else:
            return 'no_match'
    
    def _calculate_confidence(self, element_a: Element, element_b: Element, similarity: float) -> float:
        """计算匹配置信度"""
        
        # 基础置信度就是相似度
        base_confidence = similarity
        
        # 根据图元复杂度调整置信度
        complexity_factor = self._calculate_element_complexity(element_a)
        
        # 复杂度越高，置信度越高（因为匹配更困难）
        confidence = base_confidence * (1.0 + complexity_factor * 0.1)
        
        return min(1.0, confidence)
    
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
    
    def _calculate_geometric_distance(self, element_a: Element, element_b: Element) -> float:
        """计算几何距离"""
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        return center_a.distance_to(center_b)
    
    def _calculate_feature_differences(self, element_a: Element, element_b: Element) -> Dict[str, float]:
        """计算特征差异"""
        differences = {}
        
        # 位置差异
        center_a = self._get_element_center(element_a)
        center_b = self._get_element_center(element_b)
        differences['position'] = center_a.distance_to(center_b)
        
        # 根据类型计算特定差异
        if isinstance(element_a, Line) and isinstance(element_b, Line):
            differences['length'] = abs(element_a.length() - element_b.length())
            differences['angle'] = abs(element_a.angle() - element_b.angle())
        
        elif isinstance(element_a, Circle) and isinstance(element_b, Circle):
            differences['radius'] = abs(element_a.radius - element_b.radius)
        
        elif isinstance(element_a, Arc) and isinstance(element_b, Arc):
            differences['radius'] = abs(element_a.radius - element_b.radius)
            differences['arc_length'] = abs(element_a.arc_length() - element_b.arc_length())
        
        elif isinstance(element_a, Text) and isinstance(element_b, Text):
            differences['height'] = abs(element_a.height - element_b.height)
            differences['content_length'] = abs(len(element_a.content) - len(element_b.content))
        
        return differences
    
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
                            matches: List[MatchResult], processing_time: float) -> MatchingStatistics:
        """计算匹配统计信息"""
        
        matched_a_count = len(matches)
        # 使用id()来标识唯一的element_b对象
        matched_b_ids = set(id(match.element_b) for match in matches)
        matched_b_count = len(matched_b_ids)
        
        # 按匹配类型统计
        exact_matches = sum(1 for match in matches if match.match_type == 'exact')
        similar_matches = sum(1 for match in matches if match.match_type == 'similar')
        partial_matches = sum(1 for match in matches if match.match_type == 'partial')
        
        # 平均相似度
        avg_similarity = sum(match.similarity for match in matches) / len(matches) if matches else 0.0
        
        return MatchingStatistics(
            total_elements_a=len(elements_a),
            total_elements_b=len(elements_b),
            matched_pairs=len(matches),
            unmatched_a=len(elements_a) - matched_a_count,
            unmatched_b=len(elements_b) - matched_b_count,
            exact_matches=exact_matches,
            similar_matches=similar_matches,
            partial_matches=partial_matches,
            average_similarity=avg_similarity,
            processing_time=processing_time
        )
    
    def get_unmatched_elements(self, elements_a: List[Element], elements_b: List[Element], 
                              matches: List[MatchResult]) -> Tuple[List[Element], List[Element]]:
        """获取未匹配的图元"""
        
        # 使用id()来标识已匹配的图元
        matched_a_ids = set(id(match.element_a) for match in matches)
        matched_b_ids = set(id(match.element_b) for match in matches)
        
        unmatched_a = [elem for elem in elements_a if id(elem) not in matched_a_ids]
        unmatched_b = [elem for elem in elements_b if id(elem) not in matched_b_ids]
        
        return unmatched_a, unmatched_b
