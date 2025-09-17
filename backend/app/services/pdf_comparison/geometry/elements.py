"""
几何图元定义模块

定义PDF图纸中的基本几何元素：点、线、圆、弧、文本等。
每个图元都包含位置信息、属性信息和基本几何计算方法。
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Union
import numpy as np
import math


@dataclass
class Point:
    """二维点"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        """计算到另一个点的距离"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def midpoint_to(self, other: 'Point') -> 'Point':
        """计算到另一个点的中点"""
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)
    
    def translate(self, dx: float, dy: float) -> 'Point':
        """平移点"""
        return Point(self.x + dx, self.y + dy)
    
    def rotate(self, angle: float, center: Optional['Point'] = None) -> 'Point':
        """绕指定中心旋转点（角度为弧度）"""
        if center is None:
            center = Point(0, 0)
        
        # 平移到原点
        x = self.x - center.x
        y = self.y - center.y
        
        # 旋转
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # 平移回去
        return Point(new_x + center.x, new_y + center.y)
    
    def __str__(self) -> str:
        return f"Point({self.x:.3f}, {self.y:.3f})"


@dataclass
class Line:
    """直线段"""
    start: Point
    end: Point
    layer: str = ""
    color: str = "black"
    line_type: str = "solid"
    thickness: float = 1.0
    
    def length(self) -> float:
        """计算线段长度"""
        return self.start.distance_to(self.end)
    
    def angle(self) -> float:
        """计算线段角度（弧度，相对于X轴正方向）"""
        return math.atan2(self.end.y - self.start.y, self.end.x - self.start.x)
    
    def midpoint(self) -> Point:
        """计算线段中点"""
        return self.start.midpoint_to(self.end)
    
    def direction_vector(self) -> Tuple[float, float]:
        """计算方向向量（单位向量）"""
        length = self.length()
        if length == 0:
            return (0, 0)
        return ((self.end.x - self.start.x) / length, 
                (self.end.y - self.start.y) / length)
    
    def is_parallel_to(self, other: 'Line', tolerance: float = 1e-6) -> bool:
        """判断是否与另一条线段平行"""
        angle_diff = abs(self.angle() - other.angle())
        # 考虑角度的周期性
        angle_diff = min(angle_diff, 2 * math.pi - angle_diff)
        return angle_diff < tolerance or abs(angle_diff - math.pi) < tolerance
    
    def distance_to_point(self, point: Point) -> float:
        """计算点到线段的最短距离"""
        # 向量计算
        A = self.start
        B = self.end
        P = point
        
        # 线段向量
        AB = (B.x - A.x, B.y - A.y)
        # 点到起点向量
        AP = (P.x - A.x, P.y - A.y)
        
        # 投影长度
        AB_squared = AB[0]**2 + AB[1]**2
        if AB_squared == 0:
            return A.distance_to(P)
        
        t = (AP[0] * AB[0] + AP[1] * AB[1]) / AB_squared
        
        # 限制在线段范围内
        t = max(0, min(1, t))
        
        # 投影点
        projection = Point(A.x + t * AB[0], A.y + t * AB[1])
        return P.distance_to(projection)
    
    def translate(self, dx: float, dy: float) -> 'Line':
        """平移线段"""
        return Line(
            start=self.start.translate(dx, dy),
            end=self.end.translate(dx, dy),
            layer=self.layer,
            color=self.color,
            line_type=self.line_type,
            thickness=self.thickness
        )
    
    def __str__(self) -> str:
        return f"Line({self.start} -> {self.end}, length={self.length():.3f})"


@dataclass
class Circle:
    """圆"""
    center: Point
    radius: float
    layer: str = ""
    color: str = "black"
    fill: bool = False
    
    def area(self) -> float:
        """计算圆的面积"""
        return math.pi * self.radius ** 2
    
    def circumference(self) -> float:
        """计算圆的周长"""
        return 2 * math.pi * self.radius
    
    def contains_point(self, point: Point) -> bool:
        """判断点是否在圆内"""
        return self.center.distance_to(point) <= self.radius
    
    def distance_to_point(self, point: Point) -> float:
        """计算点到圆边的最短距离"""
        center_distance = self.center.distance_to(point)
        return abs(center_distance - self.radius)
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """获取边界框 (xmin, ymin, xmax, ymax)"""
        return (
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.center.x + self.radius,
            self.center.y + self.radius
        )
    
    def translate(self, dx: float, dy: float) -> 'Circle':
        """平移圆"""
        return Circle(
            center=self.center.translate(dx, dy),
            radius=self.radius,
            layer=self.layer,
            color=self.color,
            fill=self.fill
        )
    
    def __str__(self) -> str:
        return f"Circle(center={self.center}, radius={self.radius:.3f})"


@dataclass
class Arc:
    """圆弧"""
    center: Point
    radius: float
    start_angle: float  # 起始角度（弧度）
    end_angle: float    # 结束角度（弧度）
    layer: str = ""
    color: str = "black"
    
    def arc_length(self) -> float:
        """计算弧长"""
        angle_diff = self.end_angle - self.start_angle
        # 处理角度跨越问题
        if angle_diff < 0:
            angle_diff += 2 * math.pi
        return self.radius * angle_diff
    
    def start_point(self) -> Point:
        """获取弧的起点"""
        return Point(
            self.center.x + self.radius * math.cos(self.start_angle),
            self.center.y + self.radius * math.sin(self.start_angle)
        )
    
    def end_point(self) -> Point:
        """获取弧的终点"""
        return Point(
            self.center.x + self.radius * math.cos(self.end_angle),
            self.center.y + self.radius * math.sin(self.end_angle)
        )
    
    def midpoint(self) -> Point:
        """获取弧的中点"""
        mid_angle = (self.start_angle + self.end_angle) / 2
        return Point(
            self.center.x + self.radius * math.cos(mid_angle),
            self.center.y + self.radius * math.sin(mid_angle)
        )
    
    def angle_span(self) -> float:
        """获取弧的角度跨度"""
        span = self.end_angle - self.start_angle
        if span < 0:
            span += 2 * math.pi
        return span
    
    def contains_angle(self, angle: float) -> bool:
        """判断角度是否在弧的范围内"""
        # 标准化角度到 [0, 2π)
        angle = angle % (2 * math.pi)
        start = self.start_angle % (2 * math.pi)
        end = self.end_angle % (2 * math.pi)
        
        if start <= end:
            return start <= angle <= end
        else:  # 跨越0度
            return angle >= start or angle <= end
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """获取边界框"""
        # 简化实现：使用完整圆的边界框
        return (
            self.center.x - self.radius,
            self.center.y - self.radius,
            self.center.x + self.radius,
            self.center.y + self.radius
        )
    
    def translate(self, dx: float, dy: float) -> 'Arc':
        """平移弧"""
        return Arc(
            center=self.center.translate(dx, dy),
            radius=self.radius,
            start_angle=self.start_angle,
            end_angle=self.end_angle,
            layer=self.layer,
            color=self.color
        )
    
    def __str__(self) -> str:
        return f"Arc(center={self.center}, radius={self.radius:.3f}, " \
               f"angles={math.degrees(self.start_angle):.1f}°-{math.degrees(self.end_angle):.1f}°)"


@dataclass
class Text:
    """文本"""
    position: Point
    content: str
    height: float
    rotation: float = 0.0  # 旋转角度（弧度）
    layer: str = ""
    color: str = "black"
    font: str = "Arial"
    bold: bool = False
    italic: bool = False
    
    def width_estimate(self) -> float:
        """估算文本宽度（简化计算）"""
        # 简化估算：每个字符约为字高的0.6倍
        return len(self.content) * self.height * 0.6
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """获取文本边界框"""
        width = self.width_estimate()
        
        # 考虑旋转的简化处理
        if abs(self.rotation) < 1e-6:  # 无旋转
            return (
                self.position.x,
                self.position.y,
                self.position.x + width,
                self.position.y + self.height
            )
        else:
            # 旋转后的边界框（简化）
            half_width = width / 2
            half_height = self.height / 2
            return (
                self.position.x - half_width,
                self.position.y - half_height,
                self.position.x + half_width,
                self.position.y + half_height
            )
    
    def center_point(self) -> Point:
        """获取文本中心点"""
        width = self.width_estimate()
        return Point(
            self.position.x + width / 2,
            self.position.y + self.height / 2
        )
    
    def translate(self, dx: float, dy: float) -> 'Text':
        """平移文本"""
        return Text(
            position=self.position.translate(dx, dy),
            content=self.content,
            height=self.height,
            rotation=self.rotation,
            layer=self.layer,
            color=self.color,
            font=self.font,
            bold=self.bold,
            italic=self.italic
        )
    
    def __str__(self) -> str:
        return f"Text('{self.content}' at {self.position}, height={self.height:.3f})"


# 图元联合类型
Element = Union[Line, Circle, Arc, Text]


def get_element_type(element: Element) -> str:
    """获取图元类型名称"""
    return type(element).__name__


def get_element_bounds(element: Element) -> Tuple[float, float, float, float]:
    """获取图元边界框 (xmin, ymin, xmax, ymax)"""
    if isinstance(element, Line):
        return (
            min(element.start.x, element.end.x),
            min(element.start.y, element.end.y),
            max(element.start.x, element.end.x),
            max(element.start.y, element.end.y)
        )
    elif isinstance(element, (Circle, Arc)):
        return element.bounding_box()
    elif isinstance(element, Text):
        return element.bounding_box()
    else:
        raise ValueError(f"Unknown element type: {type(element)}")


def translate_element(element: Element, dx: float, dy: float) -> Element:
    """平移图元"""
    return element.translate(dx, dy)


def elements_bounding_box(elements: List[Element]) -> Tuple[float, float, float, float]:
    """计算多个图元的总边界框"""
    if not elements:
        return (0, 0, 0, 0)
    
    bounds = [get_element_bounds(elem) for elem in elements]
    
    min_x = min(bound[0] for bound in bounds)
    min_y = min(bound[1] for bound in bounds)
    max_x = max(bound[2] for bound in bounds)
    max_y = max(bound[3] for bound in bounds)
    
    return (min_x, min_y, max_x, max_y)


def filter_elements_by_type(elements: List[Element], element_type: type) -> List[Element]:
    """按类型过滤图元"""
    return [elem for elem in elements if isinstance(elem, element_type)]


def filter_elements_by_layer(elements: List[Element], layer: str) -> List[Element]:
    """按图层过滤图元"""
    return [elem for elem in elements if hasattr(elem, 'layer') and elem.layer == layer]
