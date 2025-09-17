#!/usr/bin/env python3
"""
相似度计算器测试脚本
"""

import sys
import time
sys.path.append('app')

from services.pdf_comparison.geometry.elements import Point, Line, Circle, Arc, Text
from services.pdf_comparison.matching.tolerance import ToleranceConfig
from services.pdf_comparison.matching.similarity_calculator import (
    SimilarityCalculator, SimilarityMethod, SimilarityWeights
)

def create_test_pairs():
    """创建测试图元对"""
    
    test_pairs = []
    
    # 1. 完全相同的线段
    line1 = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    line2 = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    test_pairs.append(("完全相同线段", line1, line2, 1.0))
    
    # 2. 轻微差异的线段
    line3 = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    line4 = Line(Point(0.05, 0.02), Point(10.03, 0.01), "layer1", "black")
    test_pairs.append(("轻微差异线段", line3, line4, 0.9))
    
    # 3. 方向相反的线段
    line5 = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    line6 = Line(Point(10, 0), Point(0, 0), "layer1", "black")
    test_pairs.append(("方向相反线段", line5, line6, 0.95))
    
    # 4. 完全相同的圆
    circle1 = Circle(Point(5, 5), 3, "layer2", "red")
    circle2 = Circle(Point(5, 5), 3, "layer2", "red")
    test_pairs.append(("完全相同圆形", circle1, circle2, 1.0))
    
    # 5. 轻微差异的圆
    circle3 = Circle(Point(5, 5), 3, "layer2", "red")
    circle4 = Circle(Point(5.02, 4.98), 3.01, "layer2", "red")
    test_pairs.append(("轻微差异圆形", circle3, circle4, 0.9))
    
    # 6. 完全相同的弧
    arc1 = Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue")
    arc2 = Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue")
    test_pairs.append(("完全相同弧形", arc1, arc2, 1.0))
    
    # 7. 轻微差异的弧
    arc3 = Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue")
    arc4 = Arc(Point(15.01, 14.99), 5.02, 0.01, 1.56, "layer3", "blue")
    test_pairs.append(("轻微差异弧形", arc3, arc4, 0.85))
    
    # 8. 完全相同的文本
    text1 = Text(Point(20, 20), "测试文本", 2.0, 0, "text_layer")
    text2 = Text(Point(20, 20), "测试文本", 2.0, 0, "text_layer")
    test_pairs.append(("完全相同文本", text1, text2, 1.0))
    
    # 9. 轻微差异的文本
    text3 = Text(Point(20, 20), "测试文本", 2.0, 0, "text_layer")
    text4 = Text(Point(20.05, 19.98), "测试文本", 2.01, 0, "text_layer")
    test_pairs.append(("轻微差异文本", text3, text4, 0.9))
    
    # 10. 内容不同的文本
    text5 = Text(Point(20, 20), "测试文本", 2.0, 0, "text_layer")
    text6 = Text(Point(20, 20), "测试内容", 2.0, 0, "text_layer")
    test_pairs.append(("内容不同文本", text5, text6, 0.7))
    
    # 11. 不同类型的图元
    line7 = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    circle5 = Circle(Point(5, 0), 5, "layer1", "black")
    test_pairs.append(("不同类型图元", line7, circle5, 0.0))
    
    return test_pairs

def test_similarity_calculator():
    """测试相似度计算器功能"""
    
    print("=== 相似度计算器测试 ===")
    
    # 1. 创建测试数据
    test_pairs = create_test_pairs()
    
    # 2. 测试不同配置
    tolerance_configs = {
        '高精度': ToleranceConfig.high_precision(),
        '标准': ToleranceConfig.standard(),
        '宽松': ToleranceConfig.relaxed()
    }
    
    # 3. 测试不同相似度方法
    similarity_methods = [
        SimilarityMethod.WEIGHTED_COMBINED,
        SimilarityMethod.EUCLIDEAN,
        SimilarityMethod.MANHATTAN,
        SimilarityMethod.COSINE,
        SimilarityMethod.JACCARD,
        SimilarityMethod.HAUSDORFF
    ]
    
    print("\n=== 基础相似度测试 ===")
    
    # 使用标准配置和加权组合方法进行基础测试
    tolerance = ToleranceConfig.standard()
    calculator = SimilarityCalculator(tolerance, SimilarityMethod.WEIGHTED_COMBINED)
    
    for desc, elem_a, elem_b, expected in test_pairs:
        result = calculator.calculate_similarity(elem_a, elem_b)
        
        print(f"\n{desc}:")
        print(f"  预期相似度: {expected:.3f}")
        print(f"  实际相似度: {result.overall_similarity:.3f}")
        print(f"  几何相似度: {result.geometric_similarity:.3f}")
        print(f"  属性相似度: {result.attribute_similarity:.3f}")
        print(f"  置信度: {result.confidence:.3f}")
        print(f"  详细分数: {result.detailed_scores}")
        
        # 检查是否在合理范围内
        diff = abs(result.overall_similarity - expected)
        status = "✓" if diff <= 0.2 else "✗"
        print(f"  结果: {status} (差异: {diff:.3f})")
    
    print("\n=== 不同方法对比测试 ===")
    
    # 选择一个典型的测试用例
    test_line_a = Line(Point(0, 0), Point(10, 0), "layer1", "black")
    test_line_b = Line(Point(0.05, 0.02), Point(10.03, 0.01), "layer1", "black")
    
    print(f"测试用例: 轻微差异的线段")
    print(f"  线段A: {test_line_a}")
    print(f"  线段B: {test_line_b}")
    
    for method in similarity_methods:
        try:
            calculator = SimilarityCalculator(tolerance, method)
            result = calculator.calculate_similarity(test_line_a, test_line_b)
            
            print(f"\n{method.value.upper()}方法:")
            print(f"  总相似度: {result.overall_similarity:.3f}")
            print(f"  几何相似度: {result.geometric_similarity:.3f}")
            print(f"  置信度: {result.confidence:.3f}")
            
        except Exception as e:
            print(f"\n{method.value.upper()}方法: 错误 - {e}")
    
    print("\n=== 不同容差配置测试 ===")
    
    for config_name, config in tolerance_configs.items():
        calculator = SimilarityCalculator(config, SimilarityMethod.WEIGHTED_COMBINED)
        result = calculator.calculate_similarity(test_line_a, test_line_b)
        
        print(f"\n{config_name}配置:")
        print(f"  配置: {config}")
        print(f"  相似度: {result.overall_similarity:.3f}")
        print(f"  置信度: {result.confidence:.3f}")
    
    print("\n=== 性能测试 ===")
    
    # 创建大量测试图元
    test_elements_a = []
    test_elements_b = []
    
    for i in range(100):
        x, y = i % 10, i // 10
        test_elements_a.append(Line(Point(x, y), Point(x+1, y+1), f"layer_{i}"))
        test_elements_b.append(Line(Point(x+0.01, y+0.01), Point(x+1.01, y+1.01), f"layer_{i}"))
    
    calculator = SimilarityCalculator(ToleranceConfig.standard(), SimilarityMethod.WEIGHTED_COMBINED)
    
    # 测试计算速度
    start_time = time.time()
    
    similarities = []
    for elem_a, elem_b in zip(test_elements_a, test_elements_b):
        result = calculator.calculate_similarity(elem_a, elem_b)
        similarities.append(result.overall_similarity)
    
    end_time = time.time()
    
    print(f"性能测试结果:")
    print(f"  计算数量: {len(similarities)}")
    print(f"  总时间: {end_time - start_time:.4f}秒")
    print(f"  平均时间: {(end_time - start_time) / len(similarities) * 1000:.2f}毫秒/次")
    print(f"  计算速度: {len(similarities) / (end_time - start_time):.0f} 次/秒")
    print(f"  平均相似度: {sum(similarities) / len(similarities):.3f}")
    
    # 测试缓存性能
    print(f"\n=== 缓存性能测试 ===")
    
    calculator.clear_cache()
    
    # 第一次计算（无缓存）
    start_time = time.time()
    for elem_a, elem_b in zip(test_elements_a[:10], test_elements_b[:10]):
        calculator.calculate_similarity(elem_a, elem_b, use_cache=True)
    first_time = time.time() - start_time
    
    # 第二次计算（有缓存）
    start_time = time.time()
    for elem_a, elem_b in zip(test_elements_a[:10], test_elements_b[:10]):
        calculator.calculate_similarity(elem_a, elem_b, use_cache=True)
    second_time = time.time() - start_time
    
    cache_stats = calculator.get_cache_stats()
    
    print(f"缓存测试结果:")
    print(f"  首次计算时间: {first_time:.4f}秒")
    print(f"  缓存计算时间: {second_time:.4f}秒")
    print(f"  加速比: {first_time / second_time:.1f}x" if second_time > 0 else "  加速比: ∞")
    print(f"  缓存统计: {cache_stats}")
    
    print("\n=== 权重配置测试 ===")
    
    # 测试不同权重配置
    weight_configs = [
        ("位置优先", SimilarityWeights(position=0.6, shape=0.2, size=0.1, orientation=0.1)),
        ("形状优先", SimilarityWeights(position=0.1, shape=0.6, size=0.2, orientation=0.1)),
        ("大小优先", SimilarityWeights(position=0.1, shape=0.2, size=0.6, orientation=0.1)),
        ("方向优先", SimilarityWeights(position=0.1, shape=0.2, size=0.1, orientation=0.6))
    ]
    
    test_circle_a = Circle(Point(5, 5), 3, "layer1", "red")
    test_circle_b = Circle(Point(5.1, 4.9), 3.2, "layer1", "red")
    
    print(f"测试用例: 圆形差异")
    print(f"  圆形A: {test_circle_a}")
    print(f"  圆形B: {test_circle_b}")
    
    for weight_name, weights in weight_configs:
        calculator = SimilarityCalculator(ToleranceConfig.standard(), SimilarityMethod.WEIGHTED_COMBINED)
        calculator.weights = weights
        calculator.weights.normalize()
        
        result = calculator.calculate_similarity(test_circle_a, test_circle_b)
        
        print(f"\n{weight_name}权重:")
        print(f"  权重配置: pos={weights.position:.1f}, shape={weights.shape:.1f}, size={weights.size:.1f}, orient={weights.orientation:.1f}")
        print(f"  相似度: {result.overall_similarity:.3f}")
        print(f"  详细分数: {result.detailed_scores}")
    
    print("\n✅ 相似度计算器测试完成!")
    return True

if __name__ == "__main__":
    test_similarity_calculator()
