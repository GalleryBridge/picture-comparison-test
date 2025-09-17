"""
空间索引模块

使用R-Tree实现高效的空间索引，用于快速查找邻近图元。
支持大量图元的快速匹配和范围查询。
"""

from rtree import index
from typing import List, Tuple, Dict, Optional, Set
from .elements import Element, Point, Line, Circle, Arc, Text


class SpatialIndex:
    """R-Tree空间索引，用于快速查找邻近图元"""
    
    def __init__(self):
        # 创建R-Tree索引
        self.idx = index.Index()
        # 存储图元对象
        self.elements: Dict[int, Element] = {}
        # ID计数器
        self.next_id = 0
        # 类型索引（可选的优化）
        self.type_index: Dict[str, Set[int]] = {}
        
    def insert(self, element: Element) -> int:
        """插入图元到空间索引"""
        bbox = self._get_bbox(element)
        element_id = self.next_id
        self.next_id += 1
        
        # 插入到R-Tree
        self.idx.insert(element_id, bbox)
        
        # 存储图元
        self.elements[element_id] = element
        
        # 更新类型索引
        element_type = type(element).__name__
        if element_type not in self.type_index:
            self.type_index[element_type] = set()
        self.type_index[element_type].add(element_id)
        
        return element_id
    
    def insert_batch(self, elements: List[Element]) -> List[int]:
        """批量插入图元"""
        ids = []
        for element in elements:
            element_id = self.insert(element)
            ids.append(element_id)
        return ids
    
    def query_nearby(self, element: Element, tolerance: float = 1.0) -> List[Tuple[int, Element]]:
        """查找指定图元附近的其他图元"""
        bbox = self._get_bbox(element)
        # 扩展边界框
        expanded_bbox = (
            bbox[0] - tolerance, bbox[1] - tolerance,
            bbox[2] + tolerance, bbox[3] + tolerance
        )
        
        nearby_ids = list(self.idx.intersection(expanded_bbox))
        return [(id, self.elements[id]) for id in nearby_ids if id in self.elements]
    
    def query_point(self, point: Point, tolerance: float = 1.0) -> List[Tuple[int, Element]]:
        """查找指定点附近的图元"""
        bbox = (
            point.x - tolerance, point.y - tolerance,
            point.x + tolerance, point.y + tolerance
        )
        
        nearby_ids = list(self.idx.intersection(bbox))
        return [(id, self.elements[id]) for id in nearby_ids if id in self.elements]
    
    def query_bbox(self, bbox: Tuple[float, float, float, float]) -> List[Tuple[int, Element]]:
        """查找指定边界框内的图元"""
        nearby_ids = list(self.idx.intersection(bbox))
        return [(id, self.elements[id]) for id in nearby_ids if id in self.elements]
    
    def query_by_type(self, element_type: type, tolerance: float = 1.0, 
                     center_point: Optional[Point] = None) -> List[Tuple[int, Element]]:
        """按类型查找图元"""
        type_name = element_type.__name__
        
        if type_name not in self.type_index:
            return []
        
        type_ids = self.type_index[type_name]
        
        if center_point is None:
            # 返回所有该类型的图元
            return [(id, self.elements[id]) for id in type_ids if id in self.elements]
        else:
            # 返回指定点附近的该类型图元
            nearby_results = self.query_point(center_point, tolerance)
            return [(id, elem) for id, elem in nearby_results 
                   if isinstance(elem, element_type)]
    
    def remove(self, element_id: int) -> bool:
        """从索引中移除图元"""
        if element_id not in self.elements:
            return False
        
        element = self.elements[element_id]
        bbox = self._get_bbox(element)
        
        # 从R-Tree中移除
        self.idx.delete(element_id, bbox)
        
        # 从存储中移除
        del self.elements[element_id]
        
        # 从类型索引中移除
        element_type = type(element).__name__
        if element_type in self.type_index:
            self.type_index[element_type].discard(element_id)
        
        return True
    
    def update(self, element_id: int, new_element: Element) -> bool:
        """更新图元"""
        if element_id not in self.elements:
            return False
        
        # 移除旧的
        old_element = self.elements[element_id]
        old_bbox = self._get_bbox(old_element)
        self.idx.delete(element_id, old_bbox)
        
        # 插入新的
        new_bbox = self._get_bbox(new_element)
        self.idx.insert(element_id, new_bbox)
        
        # 更新存储
        self.elements[element_id] = new_element
        
        # 更新类型索引（如果类型改变）
        old_type = type(old_element).__name__
        new_type = type(new_element).__name__
        
        if old_type != new_type:
            if old_type in self.type_index:
                self.type_index[old_type].discard(element_id)
            if new_type not in self.type_index:
                self.type_index[new_type] = set()
            self.type_index[new_type].add(element_id)
        
        return True
    
    def clear(self):
        """清空索引"""
        # 重新创建索引
        self.idx = index.Index()
        self.elements.clear()
        self.type_index.clear()
        self.next_id = 0
    
    def get_statistics(self) -> Dict[str, any]:
        """获取索引统计信息"""
        stats = {
            'total_elements': len(self.elements),
            'next_id': self.next_id,
            'type_counts': {}
        }
        
        for element_type, ids in self.type_index.items():
            stats['type_counts'][element_type] = len(ids)
        
        return stats
    
    def _get_bbox(self, element: Element) -> Tuple[float, float, float, float]:
        """获取图元的边界框 (xmin, ymin, xmax, ymax)"""
        if isinstance(element, Line):
            return (
                min(element.start.x, element.end.x),
                min(element.start.y, element.end.y),
                max(element.start.x, element.end.x),
                max(element.start.y, element.end.y)
            )
        elif isinstance(element, Circle):
            return (
                element.center.x - element.radius,
                element.center.y - element.radius,
                element.center.x + element.radius,
                element.center.y + element.radius
            )
        elif isinstance(element, Arc):
            # 简化处理：使用圆的边界框
            # 更精确的实现需要考虑弧的实际范围
            return (
                element.center.x - element.radius,
                element.center.y - element.radius,
                element.center.x + element.radius,
                element.center.y + element.radius
            )
        elif isinstance(element, Text):
            # 估算文本边界框
            width = element.width_estimate()
            return (
                element.position.x,
                element.position.y,
                element.position.x + width,
                element.position.y + element.height
            )
        else:
            # 默认点边界框
            if hasattr(element, 'position'):
                pos = element.position
                return (pos.x, pos.y, pos.x, pos.y)
            else:
                return (0, 0, 0, 0)
    
    def find_closest(self, target_element: Element, candidates: List[Element], 
                    max_distance: float = float('inf')) -> Optional[Tuple[Element, float]]:
        """在候选图元中找到最接近目标图元的一个"""
        if not candidates:
            return None
        
        target_center = self._get_element_center(target_element)
        closest_element = None
        closest_distance = max_distance
        
        for candidate in candidates:
            candidate_center = self._get_element_center(candidate)
            distance = target_center.distance_to(candidate_center)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_element = candidate
        
        return (closest_element, closest_distance) if closest_element else None
    
    def _get_element_center(self, element: Element) -> Point:
        """获取图元的中心点"""
        if isinstance(element, Line):
            return element.midpoint()
        elif isinstance(element, (Circle, Arc)):
            return element.center
        elif isinstance(element, Text):
            return element.center_point()
        else:
            # 默认处理
            if hasattr(element, 'position'):
                return element.position
            else:
                return Point(0, 0)
    
    def optimize(self):
        """优化索引结构（重建索引）"""
        # 保存所有图元
        elements_backup = list(self.elements.values())
        
        # 清空并重建
        self.clear()
        
        # 重新插入所有图元
        for element in elements_backup:
            self.insert(element)
    
    def get_density_map(self, grid_size: int = 10) -> Dict[Tuple[int, int], int]:
        """获取图元密度分布图"""
        if not self.elements:
            return {}
        
        # 计算整体边界框
        all_bboxes = [self._get_bbox(elem) for elem in self.elements.values()]
        min_x = min(bbox[0] for bbox in all_bboxes)
        min_y = min(bbox[1] for bbox in all_bboxes)
        max_x = max(bbox[2] for bbox in all_bboxes)
        max_y = max(bbox[3] for bbox in all_bboxes)
        
        # 计算网格大小
        width = max_x - min_x
        height = max_y - min_y
        cell_width = width / grid_size
        cell_height = height / grid_size
        
        # 统计每个网格的图元数量
        density_map = {}
        
        for element in self.elements.values():
            center = self._get_element_center(element)
            
            # 计算网格坐标
            grid_x = int((center.x - min_x) / cell_width)
            grid_y = int((center.y - min_y) / cell_height)
            
            # 边界处理
            grid_x = min(grid_x, grid_size - 1)
            grid_y = min(grid_y, grid_size - 1)
            
            grid_key = (grid_x, grid_y)
            density_map[grid_key] = density_map.get(grid_key, 0) + 1
        
        return density_map
