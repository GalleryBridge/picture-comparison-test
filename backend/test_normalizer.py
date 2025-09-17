#!/usr/bin/env python3
"""
坐标标准化器测试脚本
"""

import sys
sys.path.append('app')

from services.pdf_comparison.parser.pdf_parser import PDFParser
from services.pdf_comparison.geometry.normalizer import CoordinateNormalizer

def test_normalizer():
    """测试坐标标准化器功能"""
    
    # 1. 解析PDF获取原始图元
    print("=== 解析PDF文件 ===")
    parser = PDFParser()
    result = parser.parse_file('test_drawing.pdf')
    
    original_elements = result['elements']
    page_info = result['page_info'][0] if result['page_info'] else None
    
    print(f"原始图元数: {len(original_elements)}")
    
    # 显示原始图元的坐标范围
    print("\n=== 原始图元坐标范围 ===")
    for i, element in enumerate(original_elements[:3]):
        print(f"  {i+1}. {element}")
    
    # 2. 创建标准化器并处理
    print("\n=== 开始坐标标准化 ===")
    normalizer = CoordinateNormalizer()
    
    # 显示转换信息
    conversion_info = normalizer.get_conversion_info()
    print("转换信息:")
    for key, value in conversion_info.items():
        print(f"  {key}: {value}")
    
    # 执行标准化
    normalized_elements = normalizer.normalize(original_elements, page_info)
    
    print(f"\n标准化后图元数: {len(normalized_elements)}")
    
    # 显示标准化后的图元
    print("\n=== 标准化后图元 ===")
    for i, element in enumerate(normalized_elements[:3]):
        print(f"  {i+1}. {element}")
    
    # 3. 计算边界框
    print("\n=== 边界框对比 ===")
    
    # 原始边界框（手动计算）
    original_bounds = normalizer.get_elements_bounds(original_elements)
    print(f"原始边界框: ({original_bounds[0]:.2f}, {original_bounds[1]:.2f}, {original_bounds[2]:.2f}, {original_bounds[3]:.2f}) 点")
    
    # 标准化后边界框
    normalized_bounds = normalizer.get_elements_bounds(normalized_elements)
    print(f"标准化边界框: ({normalized_bounds[0]:.2f}, {normalized_bounds[1]:.2f}, {normalized_bounds[2]:.2f}, {normalized_bounds[3]:.2f}) mm")
    
    # 4. 验证坐标转换
    print("\n=== 坐标转换验证 ===")
    
    # 检查是否所有坐标都是非负的（对齐后应该从0开始）
    min_coords = []
    for element in normalized_elements:
        if hasattr(element, 'start'):  # Line
            min_coords.extend([element.start.x, element.start.y, element.end.x, element.end.y])
        elif hasattr(element, 'center'):  # Circle, Arc
            min_coords.extend([element.center.x - element.radius, element.center.y - element.radius])
        elif hasattr(element, 'position'):  # Text
            min_coords.extend([element.position.x, element.position.y])
    
    actual_min = min(min_coords) if min_coords else 0
    print(f"最小坐标值: {actual_min:.6f} mm (应该接近0)")
    
    # 5. 单位转换验证
    print("\n=== 单位转换验证 ===")
    if original_elements and normalized_elements:
        # 比较第一个线段的长度
        for orig, norm in zip(original_elements, normalized_elements):
            if hasattr(orig, 'length') and hasattr(norm, 'length'):
                orig_length = orig.length()
                norm_length = norm.length()
                expected_length = orig_length * normalizer.point_to_mm
                
                print(f"线段长度对比:")
                print(f"  原始: {orig_length:.2f} 点")
                print(f"  标准化: {norm_length:.2f} mm")
                print(f"  预期: {expected_length:.2f} mm")
                print(f"  误差: {abs(norm_length - expected_length):.6f} mm")
                break
    
    print("\n✅ 坐标标准化测试完成!")
    return True

if __name__ == "__main__":
    test_normalizer()
