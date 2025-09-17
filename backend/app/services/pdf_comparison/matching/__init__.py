"""
匹配算法模块

包含图元匹配、相似度计算、差异检测和容差控制等功能。
"""

from .tolerance import ToleranceConfig, ToleranceManager
from .element_matcher import ElementMatcher, MatchResult, MatchingStatistics
from .similarity_calculator import SimilarityCalculator, SimilarityMethod, SimilarityResult, SimilarityWeights
from .diff_detector import DiffDetector, DifferenceType, ModificationType, DifferenceDetail, DifferenceStatistics

__all__ = [
    "ToleranceConfig", "ToleranceManager",
    "ElementMatcher", "MatchResult", "MatchingStatistics",
    "SimilarityCalculator", "SimilarityMethod", "SimilarityResult", "SimilarityWeights",
    "DiffDetector", "DifferenceType", "ModificationType", "DifferenceDetail", "DifferenceStatistics"
]
