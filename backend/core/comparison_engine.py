"""
PDF图纸比对引擎

整合所有模块的核心比对系统，提供完整的PDF图纸比对功能。
支持多种比对模式、精度配置和输出格式。
"""

import os
import time
import json
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.pdf_parser import PDFParser
from geometry.normalizer import CoordinateNormalizer
from geometry.elements import Element
from matching.tolerance import ToleranceConfig, ToleranceManager
from matching.element_matcher import ElementMatcher, MatchResult, MatchingStatistics
from matching.similarity_calculator import SimilarityCalculator, SimilarityMethod
from matching.diff_detector import DiffDetector, DifferenceDetail, DifferenceStatistics, DifferenceType


class ComparisonMode(Enum):
    """比对模式"""
    STRICT = "strict"           # 严格模式 - 高精度
    STANDARD = "standard"       # 标准模式 - 平衡精度和性能
    RELAXED = "relaxed"         # 宽松模式 - 容错性强
    CUSTOM = "custom"           # 自定义模式


class OutputFormat(Enum):
    """输出格式"""
    JSON = "json"               # JSON格式
    DICT = "dict"               # Python字典
    SUMMARY = "summary"         # 摘要报告
    DETAILED = "detailed"       # 详细报告


@dataclass
class ComparisonConfig:
    """比对配置"""
    mode: ComparisonMode = ComparisonMode.STANDARD
    tolerance_config: Optional[ToleranceConfig] = None
    similarity_method: SimilarityMethod = SimilarityMethod.WEIGHTED_COMBINED
    enable_caching: bool = True
    max_processing_time: float = 300.0  # 最大处理时间（秒）
    output_format: OutputFormat = OutputFormat.DICT
    
    # 高级选项
    enable_preprocessing: bool = True
    enable_postprocessing: bool = True
    parallel_processing: bool = False
    debug_mode: bool = False


@dataclass
class ComparisonResult:
    """比对结果"""
    # 基本信息
    file_a_path: str
    file_b_path: str
    comparison_id: str
    timestamp: str
    processing_time: float
    
    # 解析结果
    elements_a_count: int
    elements_b_count: int
    
    # 匹配结果
    matching_statistics: MatchingStatistics
    
    # 差异结果
    differences: List[DifferenceDetail]
    difference_statistics: DifferenceStatistics
    
    # 配置信息
    config: ComparisonConfig
    
    # 状态信息
    success: bool
    error_message: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class PDFComparisonEngine:
    """PDF图纸比对引擎 - 核心比对系统"""
    
    def __init__(self, config: Optional[ComparisonConfig] = None):
        self.config = config or ComparisonConfig()
        
        # 初始化组件
        self._initialize_components()
        
        # 缓存
        self._parsing_cache: Dict[str, Any] = {}
        self._comparison_cache: Dict[str, ComparisonResult] = {}
        
        # 统计信息
        self.total_comparisons = 0
        self.successful_comparisons = 0
        self.failed_comparisons = 0
    
    def _initialize_components(self):
        """初始化所有组件"""
        
        # 获取容差配置
        if self.config.tolerance_config:
            tolerance_config = self.config.tolerance_config
        else:
            tolerance_manager = ToleranceManager()
            if self.config.mode == ComparisonMode.STRICT:
                tolerance_config = tolerance_manager.get_preset('high_precision')
            elif self.config.mode == ComparisonMode.STANDARD:
                tolerance_config = tolerance_manager.get_preset('standard')
            elif self.config.mode == ComparisonMode.RELAXED:
                tolerance_config = tolerance_manager.get_preset('relaxed')
            else:  # CUSTOM
                tolerance_config = tolerance_manager.get_preset('standard')
        
        # 初始化组件
        self.pdf_parser = PDFParser()
        self.coordinate_normalizer = CoordinateNormalizer()
        self.element_matcher = ElementMatcher(tolerance_config)
        self.similarity_calculator = SimilarityCalculator(tolerance_config, self.config.similarity_method)
        self.diff_detector = DiffDetector(tolerance_config)
        
        # 保存配置
        self.tolerance_config = tolerance_config
    
    def compare_files(self, file_a_path: str, file_b_path: str, 
                     comparison_id: Optional[str] = None) -> ComparisonResult:
        """比对两个PDF文件"""
        
        start_time = time.time()
        
        # 生成比对ID
        if comparison_id is None:
            comparison_id = f"comp_{int(time.time())}_{hash((file_a_path, file_b_path)) % 10000}"
        
        # 检查缓存
        cache_key = f"{file_a_path}|{file_b_path}|{hash(str(self.config))}"
        if self.config.enable_caching and cache_key in self._comparison_cache:
            cached_result = self._comparison_cache[cache_key]
            if self.config.debug_mode:
                print(f"使用缓存结果: {comparison_id}")
            return cached_result
        
        try:
            # 1. 解析PDF文件
            if self.config.debug_mode:
                print(f"开始解析PDF文件: {file_a_path}, {file_b_path}")
            
            elements_a, metadata_a = self._parse_pdf_file(file_a_path)
            elements_b, metadata_b = self._parse_pdf_file(file_b_path)
            
            if self.config.debug_mode:
                print(f"解析完成: A={len(elements_a)}个图元, B={len(elements_b)}个图元")
            
            # 2. 预处理
            if self.config.enable_preprocessing:
                elements_a = self._preprocess_elements(elements_a, metadata_a)
                elements_b = self._preprocess_elements(elements_b, metadata_b)
            
            # 3. 执行比对
            if self.config.debug_mode:
                print("开始图元匹配...")
            
            matches, matching_stats = self.element_matcher.match_elements(elements_a, elements_b)
            
            if self.config.debug_mode:
                print(f"匹配完成: {matching_stats.matched_pairs}对匹配")
                print("开始差异检测...")
            
            differences, diff_stats = self.diff_detector.detect_differences(elements_a, elements_b)
            
            if self.config.debug_mode:
                print(f"差异检测完成: {diff_stats.total_differences}个差异")
            
            # 4. 后处理
            if self.config.enable_postprocessing:
                differences = self._postprocess_differences(differences)
            
            # 5. 创建结果
            processing_time = time.time() - start_time
            
            result = ComparisonResult(
                file_a_path=file_a_path,
                file_b_path=file_b_path,
                comparison_id=comparison_id,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                processing_time=processing_time,
                elements_a_count=len(elements_a),
                elements_b_count=len(elements_b),
                matching_statistics=matching_stats,
                differences=differences,
                difference_statistics=diff_stats,
                config=self.config,
                success=True
            )
            
            # 6. 缓存结果
            if self.config.enable_caching:
                self._comparison_cache[cache_key] = result
            
            # 7. 更新统计
            self.total_comparisons += 1
            self.successful_comparisons += 1
            
            if self.config.debug_mode:
                print(f"比对完成: {processing_time:.4f}秒")
            
            return result
            
        except Exception as e:
            # 处理错误
            processing_time = time.time() - start_time
            
            error_result = ComparisonResult(
                file_a_path=file_a_path,
                file_b_path=file_b_path,
                comparison_id=comparison_id,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                processing_time=processing_time,
                elements_a_count=0,
                elements_b_count=0,
                matching_statistics=MatchingStatistics(0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0),
                differences=[],
                difference_statistics=DifferenceStatistics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0, {}),
                config=self.config,
                success=False,
                error_message=str(e)
            )
            
            self.total_comparisons += 1
            self.failed_comparisons += 1
            
            if self.config.debug_mode:
                print(f"比对失败: {e}")
            
            return error_result
    
    def _parse_pdf_file(self, file_path: str) -> Tuple[List[Element], Dict[str, Any]]:
        """解析PDF文件"""
        
        # 检查解析缓存
        if self.config.enable_caching and file_path in self._parsing_cache:
            cached_data = self._parsing_cache[file_path]
            return cached_data['elements'], cached_data['metadata']
        
        # 解析文件
        result = self.pdf_parser.parse_file(file_path)
        elements = result['elements']
        metadata = result.get('metadata', {})
        page_info = result.get('page_info', [])
        
        # 坐标标准化
        if elements and page_info:
            elements = self.coordinate_normalizer.normalize(elements, page_info[0])
        
        # 缓存结果
        if self.config.enable_caching:
            self._parsing_cache[file_path] = {
                'elements': elements,
                'metadata': metadata,
                'page_info': page_info
            }
        
        return elements, metadata
    
    def _preprocess_elements(self, elements: List[Element], metadata: Dict[str, Any]) -> List[Element]:
        """预处理图元"""
        
        # 这里可以添加各种预处理逻辑
        # 例如：过滤、排序、去重等
        
        processed_elements = []
        
        for element in elements:
            # 基本过滤：去除过小的图元
            if hasattr(element, 'length') and callable(element.length):
                if element.length() < 0.01:  # 小于0.01mm的线段
                    continue
            
            if hasattr(element, 'radius'):
                if element.radius < 0.01:  # 小于0.01mm半径的圆
                    continue
            
            if hasattr(element, 'height'):
                if element.height < 0.1:  # 小于0.1mm的文字
                    continue
            
            processed_elements.append(element)
        
        return processed_elements
    
    def _postprocess_differences(self, differences: List[DifferenceDetail]) -> List[DifferenceDetail]:
        """后处理差异"""
        
        # 这里可以添加各种后处理逻辑
        # 例如：合并相似差异、过滤噪声等
        
        processed_differences = []
        
        for diff in differences:
            # 过滤置信度过低的差异
            if diff.confidence < 0.3:
                continue
            
            processed_differences.append(diff)
        
        return processed_differences
    
    def batch_compare(self, file_pairs: List[Tuple[str, str]], 
                     output_dir: Optional[str] = None) -> List[ComparisonResult]:
        """批量比对"""
        
        results = []
        
        for i, (file_a, file_b) in enumerate(file_pairs):
            comparison_id = f"batch_{int(time.time())}_{i}"
            
            if self.config.debug_mode:
                print(f"批量比对 {i+1}/{len(file_pairs)}: {file_a} vs {file_b}")
            
            result = self.compare_files(file_a, file_b, comparison_id)
            results.append(result)
            
            # 保存单个结果
            if output_dir:
                self._save_result(result, output_dir)
        
        return results
    
    def compare_directories(self, dir_a: str, dir_b: str, 
                           pattern: str = "*.pdf") -> List[ComparisonResult]:
        """比对两个目录中的PDF文件"""
        
        from pathlib import Path
        import fnmatch
        
        dir_a_path = Path(dir_a)
        dir_b_path = Path(dir_b)
        
        # 获取文件列表
        files_a = [f for f in dir_a_path.rglob(pattern) if f.is_file()]
        files_b = [f for f in dir_b_path.rglob(pattern) if f.is_file()]
        
        # 按文件名匹配
        file_pairs = []
        for file_a in files_a:
            relative_path = file_a.relative_to(dir_a_path)
            file_b = dir_b_path / relative_path
            
            if file_b.exists():
                file_pairs.append((str(file_a), str(file_b)))
        
        if self.config.debug_mode:
            print(f"找到 {len(file_pairs)} 对匹配文件")
        
        return self.batch_compare(file_pairs)
    
    def export_result(self, result: ComparisonResult, 
                     output_path: str, format: OutputFormat = None) -> bool:
        """导出比对结果"""
        
        if format is None:
            format = self.config.output_format
        
        try:
            if format == OutputFormat.JSON:
                self._export_json(result, output_path)
            elif format == OutputFormat.DICT:
                self._export_dict(result, output_path)
            elif format == OutputFormat.SUMMARY:
                self._export_summary(result, output_path)
            elif format == OutputFormat.DETAILED:
                self._export_detailed(result, output_path)
            
            return True
            
        except Exception as e:
            if self.config.debug_mode:
                print(f"导出失败: {e}")
            return False
    
    def _export_json(self, result: ComparisonResult, output_path: str):
        """导出JSON格式"""
        
        # 转换为可序列化的字典
        data = self._result_to_dict(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_dict(self, result: ComparisonResult, output_path: str):
        """导出Python字典格式"""
        
        data = self._result_to_dict(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(repr(data))
    
    def _export_summary(self, result: ComparisonResult, output_path: str):
        """导出摘要报告"""
        
        report = self._generate_summary_report(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _export_detailed(self, result: ComparisonResult, output_path: str):
        """导出详细报告"""
        
        report = self._generate_detailed_report(result)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def _result_to_dict(self, result: ComparisonResult) -> Dict[str, Any]:
        """将结果转换为字典"""
        
        data = asdict(result)
        
        # 处理不可序列化的对象
        data['matching_statistics'] = asdict(result.matching_statistics)
        data['difference_statistics'] = asdict(result.difference_statistics)
        data['config'] = asdict(result.config)
        
        # 处理差异列表
        data['differences'] = []
        for diff in result.differences:
            diff_dict = asdict(diff)
            # 简化图元表示
            if diff.element_a:
                diff_dict['element_a'] = str(diff.element_a)
            if diff.element_b:
                diff_dict['element_b'] = str(diff.element_b)
            data['differences'].append(diff_dict)
        
        return data
    
    def _generate_summary_report(self, result: ComparisonResult) -> str:
        """生成摘要报告"""
        
        lines = [
            "=== PDF图纸比对摘要报告 ===",
            f"比对ID: {result.comparison_id}",
            f"时间: {result.timestamp}",
            f"处理时间: {result.processing_time:.4f}秒",
            f"",
            f"文件信息:",
            f"  文件A: {result.file_a_path} ({result.elements_a_count}个图元)",
            f"  文件B: {result.file_b_path} ({result.elements_b_count}个图元)",
            f"",
            f"比对结果:",
            f"  状态: {'成功' if result.success else '失败'}",
            f"  匹配对数: {result.matching_statistics.matched_pairs}",
            f"  平均相似度: {result.matching_statistics.average_similarity:.3f}",
            f"",
            f"差异统计:",
            f"  总差异: {result.difference_statistics.total_differences}个",
            f"  新增: {result.difference_statistics.added_count}个",
            f"  删除: {result.difference_statistics.deleted_count}个",
            f"  修改: {result.difference_statistics.modified_count}个",
            f"  变化率: {result.difference_statistics.change_rate:.1%}",
            f"",
            f"配置信息:",
            f"  比对模式: {result.config.mode.value}",
            f"  相似度方法: {result.config.similarity_method.value}",
            f"  容差配置: {self.tolerance_config.get_description()}"
        ]
        
        if result.error_message:
            lines.extend([
                f"",
                f"错误信息:",
                f"  {result.error_message}"
            ])
        
        if result.warnings:
            lines.extend([
                f"",
                f"警告信息:"
            ])
            for warning in result.warnings:
                lines.append(f"  - {warning}")
        
        return "\n".join(lines)
    
    def _generate_detailed_report(self, result: ComparisonResult) -> str:
        """生成详细报告"""
        
        summary = self._generate_summary_report(result)
        
        # 添加详细差异信息
        detailed_lines = [
            summary,
            "",
            "=== 详细差异信息 ===",
            ""
        ]
        
        # 按类型分组显示差异
        diff_by_type = {}
        for diff in result.differences:
            diff_type = diff.diff_type.value
            if diff_type not in diff_by_type:
                diff_by_type[diff_type] = []
            diff_by_type[diff_type].append(diff)
        
        for diff_type, diffs in diff_by_type.items():
            detailed_lines.append(f"--- {diff_type.upper()}差异 ({len(diffs)}个) ---")
            
            for i, diff in enumerate(diffs):
                detailed_lines.append(f"{i+1}. {diff.description}")
                detailed_lines.append(f"   相似度: {diff.similarity:.3f}, 置信度: {diff.confidence:.3f}")
                
                if diff.modification_types:
                    mod_types = [mt.value for mt in diff.modification_types]
                    detailed_lines.append(f"   修改类型: {', '.join(mod_types)}")
                
                if diff.geometric_changes:
                    detailed_lines.append(f"   几何变化: {diff.geometric_changes}")
                
                if diff.attribute_changes:
                    detailed_lines.append(f"   属性变化: {diff.attribute_changes}")
                
                detailed_lines.append("")
        
        return "\n".join(detailed_lines)
    
    def _save_result(self, result: ComparisonResult, output_dir: str):
        """保存单个结果"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 保存JSON格式
        json_file = output_path / f"{result.comparison_id}.json"
        self._export_json(result, str(json_file))
        
        # 保存摘要报告
        summary_file = output_path / f"{result.comparison_id}_summary.txt"
        self._export_summary(result, str(summary_file))
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取引擎统计信息"""
        
        return {
            'total_comparisons': self.total_comparisons,
            'successful_comparisons': self.successful_comparisons,
            'failed_comparisons': self.failed_comparisons,
            'success_rate': self.successful_comparisons / max(self.total_comparisons, 1),
            'cache_size': len(self._comparison_cache),
            'parsing_cache_size': len(self._parsing_cache)
        }
    
    def clear_cache(self):
        """清空缓存"""
        self._parsing_cache.clear()
        self._comparison_cache.clear()
        
        # 清空组件缓存
        if hasattr(self.similarity_calculator, 'clear_cache'):
            self.similarity_calculator.clear_cache()
    
    def update_config(self, new_config: ComparisonConfig):
        """更新配置"""
        self.config = new_config
        self._initialize_components()
        
        # 清空缓存（因为配置改变了）
        self.clear_cache()
