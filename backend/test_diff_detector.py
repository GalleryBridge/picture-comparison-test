#!/usr/bin/env python3
"""
差异检测器测试脚本
"""

import sys
sys.path.append('app')

from services.pdf_comparison.geometry.elements import Point, Line, Circle, Arc, Text
from services.pdf_comparison.matching.tolerance import ToleranceConfig
from services.pdf_comparison.matching.diff_detector import DiffDetector, DifferenceType, ModificationType

def create_test_scenarios():
    """创建测试场景"""
    
    scenarios = []
    
    # 场景1: 完全相同的图纸
    elements_a1 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Text(Point(10, 10), "测试文本", 2.0, 0, "text_layer")
    ]
    elements_b1 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Text(Point(10, 10), "测试文本", 2.0, 0, "text_layer")
    ]
    scenarios.append(("完全相同图纸", elements_a1, elements_b1))
    
    # 场景2: 有新增图元
    elements_a2 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red")
    ]
    elements_b2 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Text(Point(10, 10), "新增文本", 2.0, 0, "text_layer"),  # 新增
        Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue")        # 新增
    ]
    scenarios.append(("有新增图元", elements_a2, elements_b2))
    
    # 场景3: 有删除图元
    elements_a3 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Text(Point(10, 10), "要删除的文本", 2.0, 0, "text_layer"),  # 将被删除
        Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue")         # 将被删除
    ]
    elements_b3 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red")
    ]
    scenarios.append(("有删除图元", elements_a3, elements_b3))
    
    # 场景4: 有修改图元
    elements_a4 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red"),
        Arc(Point(15, 15), 5, 0, 1.57, "layer3", "blue"),
        Text(Point(20, 20), "原始文本", 2.0, 0, "text_layer")
    ]
    elements_b4 = [
        Line(Point(0.2, 0.1), Point(10.3, 0.05), "layer1", "black"),  # 位置和尺寸修改
        Circle(Point(5.1, 4.9), 3.5, "layer2", "green"),              # 位置、尺寸、颜色修改
        Arc(Point(15, 15), 5, 0.2, 1.8, "layer3", "blue"),           # 角度修改
        Text(Point(20.5, 19.8), "修改后文本", 2.2, 0.1, "text_layer")  # 位置、内容、尺寸、旋转修改
    ]
    scenarios.append(("有修改图元", elements_a4, elements_b4))
    
    # 场景5: 复杂混合场景
    elements_a5 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),      # 保持不变
        Line(Point(0, 5), Point(10, 5), "layer1", "black"),     # 将被删除
        Circle(Point(5, 5), 3, "layer2", "red"),                # 将被修改
        Text(Point(10, 10), "原文本", 2.0, 0, "text_layer")      # 将被修改
    ]
    elements_b5 = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),     # 保持不变
        Circle(Point(5.2, 4.8), 3.3, "layer2", "blue"),        # 修改（位置、尺寸、颜色）
        Text(Point(10.5, 9.8), "新文本", 2.1, 0, "text_layer"), # 修改（位置、内容、尺寸）
        Arc(Point(20, 20), 4, 0, 3.14, "layer3", "green"),     # 新增
        Line(Point(15, 15), Point(25, 25), "layer4", "yellow")  # 新增
    ]
    scenarios.append(("复杂混合场景", elements_a5, elements_b5))
    
    return scenarios

def test_diff_detector():
    """测试差异检测器功能"""
    
    print("=== 差异检测器测试 ===")
    
    # 创建测试场景
    scenarios = create_test_scenarios()
    
    # 测试不同容差配置
    tolerance_configs = {
        '高精度': ToleranceConfig.high_precision(),
        '标准': ToleranceConfig.standard(),
        '宽松': ToleranceConfig.relaxed()
    }
    
    print("\n=== 基础差异检测测试 ===")
    
    # 使用标准配置进行基础测试
    detector = DiffDetector(ToleranceConfig.standard())
    
    for scenario_name, elements_a, elements_b in scenarios:
        print(f"\n--- {scenario_name} ---")
        print(f"图元A: {len(elements_a)} 个")
        for i, elem in enumerate(elements_a):
            print(f"  A{i}: {elem}")
        
        print(f"图元B: {len(elements_b)} 个")
        for i, elem in enumerate(elements_b):
            print(f"  B{i}: {elem}")
        
        # 检测差异
        differences, statistics = detector.detect_differences(elements_a, elements_b)
        
        print(f"\n差异检测结果:")
        print(f"  总差异: {statistics.total_differences} 个")
        print(f"  新增: {statistics.added_count} 个")
        print(f"  删除: {statistics.deleted_count} 个")
        print(f"  修改: {statistics.modified_count} 个")
        print(f"  未变化: {statistics.unchanged_count} 个")
        print(f"  变化率: {statistics.change_rate:.1%}")
        print(f"  处理时间: {statistics.processing_time:.4f}秒")
        
        # 显示详细差异
        print(f"\n详细差异:")
        for i, diff in enumerate(differences):
            print(f"  差异{i+1}: {diff.diff_type.value} - {diff.description}")
            print(f"    相似度: {diff.similarity:.3f}, 置信度: {diff.confidence:.3f}")
            
            if diff.modification_types:
                print(f"    修改类型: {[mt.value for mt in diff.modification_types]}")
            
            if diff.geometric_changes:
                print(f"    几何变化: {diff.geometric_changes}")
            
            if diff.attribute_changes:
                print(f"    属性变化: {diff.attribute_changes}")
        
        # 生成摘要报告
        report = detector.generate_summary_report(differences, statistics)
        print(f"\n摘要报告:")
        print(report)
    
    print("\n=== 不同容差配置对比测试 ===")
    
    # 选择一个有修改的场景进行对比
    test_elements_a = [
        Line(Point(0, 0), Point(10, 0), "layer1", "black"),
        Circle(Point(5, 5), 3, "layer2", "red")
    ]
    test_elements_b = [
        Line(Point(0.08, 0.05), Point(10.12, 0.03), "layer1", "black"),  # 轻微位置差异
        Circle(Point(5.15, 4.92), 3.08, "layer2", "red")                 # 轻微位置和尺寸差异
    ]
    
    print(f"测试用例: 轻微差异图元")
    
    for config_name, config in tolerance_configs.items():
        detector = DiffDetector(config)
        differences, statistics = detector.detect_differences(test_elements_a, test_elements_b)
        
        print(f"\n{config_name}配置结果:")
        print(f"  配置: {config}")
        print(f"  检测到差异: {statistics.total_differences} 个")
        print(f"  修改图元: {statistics.modified_count} 个")
        print(f"  未变化图元: {statistics.unchanged_count} 个")
        print(f"  变化率: {statistics.change_rate:.1%}")
        
        # 显示修改类型统计
        if statistics.position_changes > 0:
            print(f"  位置变化: {statistics.position_changes} 个")
        if statistics.size_changes > 0:
            print(f"  尺寸变化: {statistics.size_changes} 个")
    
    print("\n=== 差异筛选测试 ===")
    
    # 使用复杂场景测试筛选功能
    complex_elements_a, complex_elements_b = scenarios[-1][1], scenarios[-1][2]
    detector = DiffDetector(ToleranceConfig.standard())
    differences, statistics = detector.detect_differences(complex_elements_a, complex_elements_b)
    
    print(f"复杂场景总差异: {len(differences)} 个")
    
    # 按类型筛选
    added_diffs = detector.get_differences_by_type(differences, DifferenceType.ADDED)
    deleted_diffs = detector.get_differences_by_type(differences, DifferenceType.DELETED)
    modified_diffs = detector.get_differences_by_type(differences, DifferenceType.MODIFIED)
    unchanged_diffs = detector.get_differences_by_type(differences, DifferenceType.UNCHANGED)
    
    print(f"按类型筛选:")
    print(f"  新增差异: {len(added_diffs)} 个")
    print(f"  删除差异: {len(deleted_diffs)} 个")
    print(f"  修改差异: {len(modified_diffs)} 个")
    print(f"  未变化: {len(unchanged_diffs)} 个")
    
    # 重要差异筛选
    significant_diffs = detector.get_significant_differences(differences, min_confidence=0.9)
    print(f"高置信度差异: {len(significant_diffs)} 个")
    
    print("\n=== 修改类型详细分析 ===")
    
    for diff in modified_diffs:
        print(f"\n修改图元: {type(diff.element_a).__name__}")
        print(f"  修改类型: {[mt.value for mt in diff.modification_types]}")
        print(f"  相似度: {diff.similarity:.3f}")
        
        if diff.geometric_changes:
            print(f"  几何变化:")
            for key, value in diff.geometric_changes.items():
                print(f"    {key}: {value:.4f}")
        
        if diff.attribute_changes:
            print(f"  属性变化:")
            for key, value in diff.attribute_changes.items():
                print(f"    {key}: {value}")
    
    print("\n=== 性能测试 ===")
    
    # 创建大量图元进行性能测试
    import time
    
    large_elements_a = []
    large_elements_b = []
    
    for i in range(50):
        x, y = i % 10, i // 10
        # 原图元
        large_elements_a.append(Line(Point(x, y), Point(x+1, y+1), f"layer_{i}"))
        
        # 修改后图元（轻微差异）
        if i % 5 == 0:  # 20%的图元有修改
            large_elements_b.append(Line(Point(x+0.1, y+0.05), Point(x+1.05, y+1.02), f"layer_{i}"))
        else:  # 80%的图元保持不变
            large_elements_b.append(Line(Point(x, y), Point(x+1, y+1), f"layer_{i}"))
    
    # 添加一些新增和删除
    large_elements_b.append(Circle(Point(50, 50), 5, "new_layer"))  # 新增
    large_elements_a.append(Text(Point(60, 60), "删除的文本", 2.0))   # 删除
    
    print(f"性能测试: {len(large_elements_a)} vs {len(large_elements_b)} 图元")
    
    detector = DiffDetector(ToleranceConfig.standard())
    
    start_time = time.time()
    differences, statistics = detector.detect_differences(large_elements_a, large_elements_b)
    end_time = time.time()
    
    print(f"性能结果:")
    print(f"  处理时间: {end_time - start_time:.4f}秒")
    print(f"  处理速度: {len(large_elements_a) / (end_time - start_time):.0f} 图元/秒")
    print(f"  检测到差异: {statistics.total_differences} 个")
    print(f"  新增: {statistics.added_count}, 删除: {statistics.deleted_count}, 修改: {statistics.modified_count}")
    print(f"  变化率: {statistics.change_rate:.1%}")
    
    print("\n✅ 差异检测器测试完成!")
    return True

if __name__ == "__main__":
    test_diff_detector()
