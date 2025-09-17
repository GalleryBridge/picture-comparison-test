"""
容差配置模块

定义不同精度级别的容差配置，控制图元匹配的精度。
支持高精度、标准、宽松三种预设配置，以及自定义配置。
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import math


@dataclass
class ToleranceConfig:
    """容差配置类，控制匹配精度"""
    
    # 位置容差 (毫米)
    position: float = 0.1
    
    # 长度比例容差 (0.01 = 1%)
    length_ratio: float = 0.01
    
    # 角度容差 (弧度)
    angle: float = 0.017  # 约1度
    
    # 相似度阈值 (0.0-1.0)
    similarity_threshold: float = 0.8
    
    # 文本匹配容差
    text_position: float = 1.0  # 文本位置容差更大
    text_content_similarity: float = 0.9  # 文本内容相似度
    
    # 圆形/弧形特殊容差
    radius_tolerance: float = 0.1  # 半径容差 (毫米)
    arc_angle_tolerance: float = 0.087  # 弧角度容差 (约5度)
    
    # 高级匹配参数
    enable_fuzzy_matching: bool = True  # 启用模糊匹配
    max_search_radius: float = 10.0  # 最大搜索半径 (毫米)
    
    # 性能参数
    max_candidates_per_element: int = 50  # 每个图元的最大候选匹配数
    enable_early_termination: bool = True  # 启用早期终止优化
    
    def __post_init__(self):
        """初始化后验证参数"""
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证参数有效性"""
        if self.position < 0:
            raise ValueError("位置容差必须为非负数")
        
        if not 0 <= self.length_ratio <= 1:
            raise ValueError("长度比例容差必须在0-1之间")
        
        if self.angle < 0:
            raise ValueError("角度容差必须为非负数")
        
        if not 0 <= self.similarity_threshold <= 1:
            raise ValueError("相似度阈值必须在0-1之间")
        
        if self.max_search_radius < self.position:
            raise ValueError("最大搜索半径应大于等于位置容差")
    
    @classmethod
    def high_precision(cls) -> 'ToleranceConfig':
        """高精度配置 - 适用于精密工程图纸"""
        return cls(
            position=0.05,  # 0.05mm位置精度
            length_ratio=0.005,  # 0.5%长度容差
            angle=0.009,  # 0.5度角度容差
            similarity_threshold=0.95,  # 95%相似度要求
            text_position=0.5,  # 文本位置容差
            text_content_similarity=0.95,
            radius_tolerance=0.05,
            arc_angle_tolerance=0.017,  # 1度
            max_search_radius=2.0,  # 2mm搜索半径
            max_candidates_per_element=20
        )
    
    @classmethod
    def standard(cls) -> 'ToleranceConfig':
        """标准精度配置 - 适用于一般工程图纸"""
        return cls(
            position=0.1,  # 0.1mm位置精度
            length_ratio=0.01,  # 1%长度容差
            angle=0.017,  # 1度角度容差
            similarity_threshold=0.85,  # 85%相似度要求
            text_position=1.0,
            text_content_similarity=0.9,
            radius_tolerance=0.1,
            arc_angle_tolerance=0.035,  # 2度
            max_search_radius=5.0,  # 5mm搜索半径
            max_candidates_per_element=30
        )
    
    @classmethod
    def relaxed(cls) -> 'ToleranceConfig':
        """宽松配置 - 适用于手绘图纸或低精度扫描件"""
        return cls(
            position=0.5,  # 0.5mm位置精度
            length_ratio=0.05,  # 5%长度容差
            angle=0.087,  # 5度角度容差
            similarity_threshold=0.7,  # 70%相似度要求
            text_position=2.0,
            text_content_similarity=0.8,
            radius_tolerance=0.5,
            arc_angle_tolerance=0.175,  # 10度
            max_search_radius=10.0,  # 10mm搜索半径
            max_candidates_per_element=50
        )
    
    @classmethod
    def ultra_precise(cls) -> 'ToleranceConfig':
        """超高精度配置 - 适用于微米级精密图纸"""
        return cls(
            position=0.01,  # 0.01mm位置精度
            length_ratio=0.001,  # 0.1%长度容差
            angle=0.0035,  # 0.2度角度容差
            similarity_threshold=0.98,  # 98%相似度要求
            text_position=0.1,
            text_content_similarity=0.98,
            radius_tolerance=0.01,
            arc_angle_tolerance=0.0087,  # 0.5度
            max_search_radius=0.5,  # 0.5mm搜索半径
            max_candidates_per_element=10
        )
    
    @classmethod
    def custom(cls, **kwargs) -> 'ToleranceConfig':
        """自定义配置"""
        # 从标准配置开始
        config = cls.standard()
        
        # 更新指定参数
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                raise ValueError(f"未知参数: {key}")
        
        # 重新验证
        config._validate_parameters()
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'position': self.position,
            'length_ratio': self.length_ratio,
            'angle': self.angle,
            'angle_degrees': math.degrees(self.angle),
            'similarity_threshold': self.similarity_threshold,
            'text_position': self.text_position,
            'text_content_similarity': self.text_content_similarity,
            'radius_tolerance': self.radius_tolerance,
            'arc_angle_tolerance': self.arc_angle_tolerance,
            'arc_angle_degrees': math.degrees(self.arc_angle_tolerance),
            'enable_fuzzy_matching': self.enable_fuzzy_matching,
            'max_search_radius': self.max_search_radius,
            'max_candidates_per_element': self.max_candidates_per_element,
            'enable_early_termination': self.enable_early_termination
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToleranceConfig':
        """从字典创建配置"""
        # 转换角度（如果提供的是度数）
        if 'angle_degrees' in data and 'angle' not in data:
            data['angle'] = math.radians(data['angle_degrees'])
        
        if 'arc_angle_degrees' in data and 'arc_angle_tolerance' not in data:
            data['arc_angle_tolerance'] = math.radians(data['arc_angle_degrees'])
        
        # 过滤掉不是构造函数参数的键
        valid_keys = {
            'position', 'length_ratio', 'angle', 'similarity_threshold',
            'text_position', 'text_content_similarity', 'radius_tolerance',
            'arc_angle_tolerance', 'enable_fuzzy_matching', 'max_search_radius',
            'max_candidates_per_element', 'enable_early_termination'
        }
        
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
    
    def get_description(self) -> str:
        """获取配置描述"""
        return (
            f"位置精度: {self.position}mm, "
            f"长度容差: {self.length_ratio*100:.1f}%, "
            f"角度容差: {math.degrees(self.angle):.1f}°, "
            f"相似度阈值: {self.similarity_threshold*100:.0f}%"
        )
    
    def is_compatible_with(self, other: 'ToleranceConfig') -> bool:
        """检查与另一个配置是否兼容"""
        # 简单的兼容性检查：主要参数差异不超过50%
        tolerance = 0.5
        
        checks = [
            abs(self.position - other.position) / max(self.position, other.position) <= tolerance,
            abs(self.length_ratio - other.length_ratio) / max(self.length_ratio, other.length_ratio) <= tolerance,
            abs(self.angle - other.angle) / max(self.angle, other.angle) <= tolerance,
            abs(self.similarity_threshold - other.similarity_threshold) <= 0.2
        ]
        
        return all(checks)
    
    def scale(self, factor: float) -> 'ToleranceConfig':
        """按比例缩放容差配置"""
        if factor <= 0:
            raise ValueError("缩放因子必须为正数")
        
        return ToleranceConfig(
            position=self.position * factor,
            length_ratio=self.length_ratio,  # 比例不变
            angle=self.angle,  # 角度不变
            similarity_threshold=max(0.1, min(1.0, self.similarity_threshold)),  # 保持在合理范围
            text_position=self.text_position * factor,
            text_content_similarity=self.text_content_similarity,
            radius_tolerance=self.radius_tolerance * factor,
            arc_angle_tolerance=self.arc_angle_tolerance,
            enable_fuzzy_matching=self.enable_fuzzy_matching,
            max_search_radius=self.max_search_radius * factor,
            max_candidates_per_element=self.max_candidates_per_element,
            enable_early_termination=self.enable_early_termination
        )
    
    def __str__(self) -> str:
        return f"ToleranceConfig({self.get_description()})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ToleranceManager:
    """容差配置管理器"""
    
    def __init__(self):
        self._presets = {
            'ultra_precise': ToleranceConfig.ultra_precise(),
            'high_precision': ToleranceConfig.high_precision(),
            'standard': ToleranceConfig.standard(),
            'relaxed': ToleranceConfig.relaxed()
        }
        self._custom_configs = {}
    
    def get_preset(self, name: str) -> ToleranceConfig:
        """获取预设配置"""
        if name not in self._presets:
            raise ValueError(f"未知预设: {name}. 可用预设: {list(self._presets.keys())}")
        return self._presets[name]
    
    def add_custom_config(self, name: str, config: ToleranceConfig):
        """添加自定义配置"""
        self._custom_configs[name] = config
    
    def get_custom_config(self, name: str) -> ToleranceConfig:
        """获取自定义配置"""
        if name not in self._custom_configs:
            raise ValueError(f"未知自定义配置: {name}")
        return self._custom_configs[name]
    
    def list_all_configs(self) -> Dict[str, ToleranceConfig]:
        """列出所有配置"""
        all_configs = {}
        all_configs.update(self._presets)
        all_configs.update(self._custom_configs)
        return all_configs
    
    def recommend_config(self, drawing_type: str, precision_level: str = 'standard') -> ToleranceConfig:
        """根据图纸类型推荐配置"""
        recommendations = {
            'mechanical': {
                'high': 'high_precision',
                'standard': 'standard',
                'low': 'relaxed'
            },
            'architectural': {
                'high': 'standard',
                'standard': 'relaxed',
                'low': 'relaxed'
            },
            'electrical': {
                'high': 'high_precision',
                'standard': 'standard',
                'low': 'standard'
            },
            'precision': {
                'high': 'ultra_precise',
                'standard': 'high_precision',
                'low': 'standard'
            }
        }
        
        if drawing_type not in recommendations:
            return self.get_preset('standard')
        
        preset_name = recommendations[drawing_type].get(precision_level, 'standard')
        return self.get_preset(preset_name)
