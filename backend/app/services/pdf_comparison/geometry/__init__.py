"""
几何处理模块

包含图元定义、坐标标准化、空间索引等几何相关功能。
"""

from .elements import Point, Line, Circle, Arc, Text, Element
from .normalizer import CoordinateNormalizer
from .spatial_index import SpatialIndex

__all__ = [
    "Point", "Line", "Circle", "Arc", "Text", "Element",
    "CoordinateNormalizer", "SpatialIndex"
]
