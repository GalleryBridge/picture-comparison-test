#!/usr/bin/env python3
"""
主比对引擎测试脚本
"""

import sys
import os
import time
import tempfile
sys.path.append('app')

from services.pdf_comparison.comparison_engine import (
    PDFComparisonEngine, ComparisonConfig, ComparisonMode, OutputFormat
)
from services.pdf_comparison.matching.tolerance import ToleranceConfig
from services.pdf_comparison.matching.similarity_calculator import SimilarityMethod

def test_comparison_engine():
    """测试主比对引擎功能"""
    
    print("=== PDF比对引擎测试 ===")
    
    # 1. 基础配置测试
    print("\n=== 基础配置测试 ===")
    
    configs = [
        ("严格模式", ComparisonConfig(mode=ComparisonMode.STRICT, debug_mode=True)),
        ("标准模式", ComparisonConfig(mode=ComparisonMode.STANDARD, debug_mode=True)),
        ("宽松模式", ComparisonConfig(mode=ComparisonMode.RELAXED, debug_mode=True))
    ]
    
    for config_name, config in configs:
        print(f"\n--- {config_name} ---")
        
        engine = PDFComparisonEngine(config)
        
        # 测试同一文件比对（应该完全相同）
        if os.path.exists('test_drawing.pdf'):
            result = engine.compare_files('test_drawing.pdf', 'test_drawing.pdf')
            
            print(f"比对结果:")
            print(f"  状态: {'成功' if result.success else '失败'}")
            print(f"  处理时间: {result.processing_time:.4f}秒")
            print(f"  图元数量: A={result.elements_a_count}, B={result.elements_b_count}")
            print(f"  匹配对数: {result.matching_statistics.matched_pairs}")
            print(f"  平均相似度: {result.matching_statistics.average_similarity:.3f}")
            print(f"  总差异: {result.difference_statistics.total_differences}")
            print(f"  变化率: {result.difference_statistics.change_rate:.1%}")
            
            if result.error_message:
                print(f"  错误: {result.error_message}")
        else:
            print("  跳过测试 - 找不到test_drawing.pdf文件")
    
    # 2. 不同相似度方法测试
    print("\n=== 不同相似度方法测试 ===")
    
    similarity_methods = [
        SimilarityMethod.WEIGHTED_COMBINED,
        SimilarityMethod.EUCLIDEAN,
        SimilarityMethod.COSINE
    ]
    
    if os.path.exists('test_drawing.pdf'):
        for method in similarity_methods:
            config = ComparisonConfig(
                mode=ComparisonMode.STANDARD,
                similarity_method=method,
                debug_mode=False
            )
            
            engine = PDFComparisonEngine(config)
            result = engine.compare_files('test_drawing.pdf', 'test_drawing.pdf')
            
            print(f"{method.value}: 相似度={result.matching_statistics.average_similarity:.3f}, "
                  f"时间={result.processing_time:.4f}秒")
    
    # 3. 输出格式测试
    print("\n=== 输出格式测试 ===")
    
    if os.path.exists('test_drawing.pdf'):
        engine = PDFComparisonEngine(ComparisonConfig(debug_mode=False))
        result = engine.compare_files('test_drawing.pdf', 'test_drawing.pdf')
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # 测试不同输出格式
            formats = [
                (OutputFormat.JSON, "result.json"),
                (OutputFormat.SUMMARY, "result_summary.txt"),
                (OutputFormat.DETAILED, "result_detailed.txt")
            ]
            
            for format_type, filename in formats:
                output_path = os.path.join(temp_dir, filename)
                success = engine.export_result(result, output_path, format_type)
                
                if success and os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"  {format_type.value}: 导出成功, 文件大小={file_size}字节")
                    
                    # 显示部分内容
                    with open(output_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"    预览: {preview}")
                else:
                    print(f"  {format_type.value}: 导出失败")
    
    # 4. 缓存性能测试
    print("\n=== 缓存性能测试 ===")
    
    if os.path.exists('test_drawing.pdf'):
        # 启用缓存的引擎
        config_with_cache = ComparisonConfig(enable_caching=True, debug_mode=False)
        engine_cached = PDFComparisonEngine(config_with_cache)
        
        # 禁用缓存的引擎
        config_no_cache = ComparisonConfig(enable_caching=False, debug_mode=False)
        engine_no_cache = PDFComparisonEngine(config_no_cache)
        
        # 测试多次比对
        test_count = 3
        
        # 无缓存测试
        start_time = time.time()
        for i in range(test_count):
            engine_no_cache.compare_files('test_drawing.pdf', 'test_drawing.pdf')
        no_cache_time = time.time() - start_time
        
        # 有缓存测试
        start_time = time.time()
        for i in range(test_count):
            engine_cached.compare_files('test_drawing.pdf', 'test_drawing.pdf')
        cache_time = time.time() - start_time
        
        print(f"缓存性能对比 ({test_count}次比对):")
        print(f"  无缓存: {no_cache_time:.4f}秒")
        print(f"  有缓存: {cache_time:.4f}秒")
        print(f"  加速比: {no_cache_time / cache_time:.1f}x" if cache_time > 0 else "  加速比: ∞")
        
        # 显示缓存统计
        stats = engine_cached.get_statistics()
        print(f"  缓存统计: {stats}")
    
    # 5. 自定义容差配置测试
    print("\n=== 自定义容差配置测试 ===")
    
    if os.path.exists('test_drawing.pdf'):
        # 创建自定义容差配置
        custom_tolerance = ToleranceConfig.custom(
            position=0.05,
            similarity_threshold=0.9,
            max_search_radius=2.0
        )
        
        custom_config = ComparisonConfig(
            mode=ComparisonMode.CUSTOM,
            tolerance_config=custom_tolerance,
            debug_mode=False
        )
        
        engine = PDFComparisonEngine(custom_config)
        result = engine.compare_files('test_drawing.pdf', 'test_drawing.pdf')
        
        print(f"自定义配置结果:")
        print(f"  容差配置: {custom_tolerance}")
        print(f"  匹配对数: {result.matching_statistics.matched_pairs}")
        print(f"  平均相似度: {result.matching_statistics.average_similarity:.3f}")
    
    # 6. 错误处理测试
    print("\n=== 错误处理测试 ===")
    
    engine = PDFComparisonEngine(ComparisonConfig(debug_mode=False))
    
    # 测试不存在的文件
    result = engine.compare_files('nonexistent1.pdf', 'nonexistent2.pdf')
    
    print(f"不存在文件测试:")
    print(f"  状态: {'成功' if result.success else '失败'}")
    print(f"  错误信息: {result.error_message}")
    
    # 7. 引擎统计信息
    print("\n=== 引擎统计信息 ===")
    
    stats = engine.get_statistics()
    print(f"引擎统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 8. 批量比对测试（如果有多个文件）
    print("\n=== 批量比对测试 ===")
    
    # 创建一些测试文件对
    test_pairs = []
    if os.path.exists('test_drawing.pdf'):
        # 同一文件的多次比对
        test_pairs = [
            ('test_drawing.pdf', 'test_drawing.pdf'),
            ('test_drawing.pdf', 'test_drawing.pdf')
        ]
    
    if test_pairs:
        engine = PDFComparisonEngine(ComparisonConfig(debug_mode=False))
        
        start_time = time.time()
        batch_results = engine.batch_compare(test_pairs)
        batch_time = time.time() - start_time
        
        print(f"批量比对结果:")
        print(f"  文件对数: {len(test_pairs)}")
        print(f"  总时间: {batch_time:.4f}秒")
        print(f"  平均时间: {batch_time/len(test_pairs):.4f}秒/对")
        print(f"  成功率: {sum(1 for r in batch_results if r.success) / len(batch_results):.1%}")
    else:
        print("  跳过批量测试 - 没有足够的测试文件")
    
    # 9. 配置更新测试
    print("\n=== 配置更新测试 ===")
    
    engine = PDFComparisonEngine(ComparisonConfig(mode=ComparisonMode.STANDARD))
    print(f"初始模式: {engine.config.mode.value}")
    
    # 更新配置
    new_config = ComparisonConfig(mode=ComparisonMode.STRICT)
    engine.update_config(new_config)
    print(f"更新后模式: {engine.config.mode.value}")
    
    # 10. 内存清理测试
    print("\n=== 内存清理测试 ===")
    
    engine = PDFComparisonEngine(ComparisonConfig(enable_caching=True))
    
    # 执行一些比对以填充缓存
    if os.path.exists('test_drawing.pdf'):
        for i in range(3):
            engine.compare_files('test_drawing.pdf', 'test_drawing.pdf')
    
    stats_before = engine.get_statistics()
    print(f"清理前缓存大小: {stats_before['cache_size']}")
    
    # 清理缓存
    engine.clear_cache()
    
    stats_after = engine.get_statistics()
    print(f"清理后缓存大小: {stats_after['cache_size']}")
    
    print("\n✅ PDF比对引擎测试完成!")
    return True

if __name__ == "__main__":
    test_comparison_engine()
