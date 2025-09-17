#!/usr/bin/env python3
"""
图元匹配器测试脚本
"""

import sys
import time
sys.path.append('app')

from services.pdf_comparison.parser.pdf_parser import PDFParser
from services.pdf_comparison.geometry.normalizer import CoordinateNormalizer
from services.pdf_comparison.matching.tolerance import ToleranceConfig
from services.pdf_comparison.matching.element_matcher import ElementMatcher
from services.pdf_comparison.geometry.elements import Point, Line, Circle, Arc, Text

def create_test_elements():
    """创建测试图元"""
    
    # 创建一组基础图元
    elements_a = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Line(Point(0, 0), Point(0, 10), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue"),  # 90度弧
        Text(Point(20, 20), "测试文本", 2.0, 0, "text_layer")
    ]
    
    # 创建相似的图元组（有轻微差异）
    elements_b = [
        Line(Point(0.05, 0.02), Point(10.03, 0.01), "layer1", "black"),  # 轻微位置差异
        Line(Point(0.01, 0), Point(0.02, 9.98), "layer1", "black"),     # 轻微长度差异
        Circle(Point(5.02, 4.98), 3.01, "layer2", "red"),               # 轻微半径差异
        Arc(Point(15.01, 14.99), 5.02, 0.01, 1.56, "layer3", "blue"),  # 轻微角度差异
        Text(Point(20.05, 19.98), "测试文本", 2.01, 0, "text_layer"),    # 轻微位置差异
        # 额外的图元（在A中没有对应）
        Line(Point(30, 30), Point(40, 40), "layer4", "green")
    ]
    
    return elements_a, elements_b

def test_element_matcher():
    """测试图元匹配器功能"""
    
    print("=== 图元匹配器测试 ===")
    
    # 1. 创建测试数据
    print("\n=== 创建测试数据 ===")
    elements_a, elements_b = create_test_elements()
    
    print(f"图元组A: {len(elements_a)} 个图元")
    for i, elem in enumerate(elements_a):
        print(f"  A{i}: {elem}")
    
    print(f"图元组B: {len(elements_b)} 个图元")
    for i, elem in enumerate(elements_b):
        print(f"  B{i}: {elem}")
    
    # 2. 测试不同精度配置的匹配
    print("\n=== 不同精度配置测试 ===")
    
    tolerance_configs = {
        '高精度': ToleranceConfig.high_precision(),
        '标准': ToleranceConfig.standard(),
        '宽松': ToleranceConfig.relaxed()
    }
    
    for config_name, tolerance in tolerance_configs.items():
        print(f"\n--- {config_name}配置匹配 ---")
        print(f"配置: {tolerance}")
        
        matcher = ElementMatcher(tolerance)
        matches, stats = matcher.match_elements(elements_a, elements_b)
        
        print(f"匹配统计:")
        print(f"  总图元A: {stats.total_elements_a}")
        print(f"  总图元B: {stats.total_elements_b}")
        print(f"  匹配对数: {stats.matched_pairs}")
        print(f"  未匹配A: {stats.unmatched_a}")
        print(f"  未匹配B: {stats.unmatched_b}")
        print(f"  精确匹配: {stats.exact_matches}")
        print(f"  相似匹配: {stats.similar_matches}")
        print(f"  部分匹配: {stats.partial_matches}")
        print(f"  平均相似度: {stats.average_similarity:.3f}")
        print(f"  处理时间: {stats.processing_time:.4f}秒")
        
        # 显示匹配详情
        print(f"匹配详情:")
        for i, match in enumerate(matches):
            print(f"  匹配{i+1}: 相似度={match.similarity:.3f}, 类型={match.match_type}, "
                  f"置信度={match.confidence:.3f}, 距离={match.geometric_distance:.3f}mm")
            print(f"    A: {match.element_a}")
            print(f"    B: {match.element_b}")
            if match.feature_differences:
                print(f"    差异: {match.feature_differences}")
    
    # 3. 测试PDF文件匹配
    print("\n=== PDF文件匹配测试 ===")
    
    try:
        # 解析同一个PDF文件两次（模拟相同图纸的比较）
        parser = PDFParser()
        normalizer = CoordinateNormalizer()
        
        result_a = parser.parse_file('test_drawing.pdf')
        result_b = parser.parse_file('test_drawing.pdf')
        
        elements_a = normalizer.normalize(result_a['elements'], result_a['page_info'][0] if result_a['page_info'] else None)
        elements_b = normalizer.normalize(result_b['elements'], result_b['page_info'][0] if result_b['page_info'] else None)
        
        print(f"PDF图元A: {len(elements_a)} 个")
        print(f"PDF图元B: {len(elements_b)} 个")
        
        # 使用标准配置匹配
        tolerance = ToleranceConfig.standard()
        matcher = ElementMatcher(tolerance)
        matches, stats = matcher.match_elements(elements_a, elements_b)
        
        print(f"PDF匹配结果:")
        print(f"  匹配对数: {stats.matched_pairs}")
        print(f"  匹配率: {stats.matched_pairs / max(stats.total_elements_a, 1) * 100:.1f}%")
        print(f"  平均相似度: {stats.average_similarity:.3f}")
        
        # 显示前3个匹配
        for i, match in enumerate(matches[:3]):
            print(f"  PDF匹配{i+1}: 相似度={match.similarity:.3f}, 类型={match.match_type}")
    
    except Exception as e:
        print(f"PDF匹配测试失败: {e}")
    
    # 4. 性能测试
    print("\n=== 性能测试 ===")
    
    # 创建大量测试图元
    large_elements_a = []
    large_elements_b = []
    
    for i in range(100):
        x, y = i % 10, i // 10
        
        # 创建相似但有微小差异的图元
        large_elements_a.append(Line(Point(x, y), Point(x+1, y+1), f"layer_{i}"))
        large_elements_b.append(Line(Point(x+0.01, y+0.01), Point(x+1.01, y+1.01), f"layer_{i}"))
    
    print(f"性能测试: {len(large_elements_a)} vs {len(large_elements_b)} 图元")
    
    tolerance = ToleranceConfig.standard()
    matcher = ElementMatcher(tolerance)
    
    start_time = time.time()
    matches, stats = matcher.match_elements(large_elements_a, large_elements_b)
    end_time = time.time()
    
    print(f"性能结果:")
    print(f"  处理时间: {end_time - start_time:.4f}秒")
    print(f"  匹配速度: {len(large_elements_a) / (end_time - start_time):.0f} 图元/秒")
    print(f"  匹配率: {stats.matched_pairs / len(large_elements_a) * 100:.1f}%")
    print(f"  平均相似度: {stats.average_similarity:.3f}")
    
    # 5. 边界情况测试
    print("\n=== 边界情况测试 ===")
    
    # 空列表匹配
    empty_matches, empty_stats = matcher.match_elements([], [])
    print(f"空列表匹配: {empty_stats.matched_pairs} 对")
    
    # 单个图元匹配
    single_a = [Line(Point(0, 0), Point(1, 1))]
    single_b = [Line(Point(0.001, 0.001), Point(1.001, 1.001))]
    single_matches, single_stats = matcher.match_elements(single_a, single_b)
    print(f"单图元匹配: 相似度={single_matches[0].similarity:.3f}" if single_matches else "单图元匹配: 无匹配")
    
    # 不同类型图元
    mixed_a = [Line(Point(0, 0), Point(1, 1))]
    mixed_b = [Circle(Point(0.5, 0.5), 0.5)]
    mixed_matches, mixed_stats = matcher.match_elements(mixed_a, mixed_b)
    print(f"不同类型匹配: {mixed_stats.matched_pairs} 对")
    
    print("\n✅ 图元匹配器测试完成!")
    return True

if __name__ == "__main__":
    test_element_matcher()
