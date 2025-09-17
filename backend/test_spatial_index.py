#!/usr/bin/env python3
"""
空间索引测试脚本
"""

import sys
import time
sys.path.append('app')

from services.pdf_comparison.parser.pdf_parser import PDFParser
from services.pdf_comparison.geometry.normalizer import CoordinateNormalizer
from services.pdf_comparison.geometry.spatial_index import SpatialIndex
from services.pdf_comparison.geometry.elements import Point, Line, Circle

def test_spatial_index():
    """测试空间索引功能"""
    
    print("=== 空间索引测试 ===")
    
    # 1. 创建空间索引
    spatial_idx = SpatialIndex()
    
    # 2. 从PDF解析图元并插入索引
    print("\n=== 从PDF加载图元 ===")
    parser = PDFParser()
    normalizer = CoordinateNormalizer()
    
    result = parser.parse_file('test_drawing.pdf')
    elements = result['elements']
    page_info = result['page_info'][0] if result['page_info'] else None
    
    # 标准化坐标
    normalized_elements = normalizer.normalize(elements, page_info)
    
    print(f"加载了 {len(normalized_elements)} 个图元")
    
    # 3. 批量插入到空间索引
    print("\n=== 插入到空间索引 ===")
    start_time = time.time()
    element_ids = spatial_idx.insert_batch(normalized_elements)
    insert_time = time.time() - start_time
    
    print(f"插入 {len(element_ids)} 个图元，耗时: {insert_time:.4f} 秒")
    
    # 4. 获取统计信息
    print("\n=== 索引统计信息 ===")
    stats = spatial_idx.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 5. 测试邻近查询
    print("\n=== 邻近查询测试 ===")
    if normalized_elements:
        test_element = normalized_elements[0]
        print(f"测试图元: {test_element}")
        
        # 查找邻近图元
        tolerance = 10.0  # 10mm容差
        start_time = time.time()
        nearby = spatial_idx.query_nearby(test_element, tolerance)
        query_time = time.time() - start_time
        
        print(f"在 {tolerance}mm 范围内找到 {len(nearby)} 个图元，耗时: {query_time:.4f} 秒")
        
        # 显示前3个邻近图元
        for i, (elem_id, elem) in enumerate(nearby[:3]):
            print(f"  {i+1}. ID={elem_id}: {elem}")
    
    # 6. 测试点查询
    print("\n=== 点查询测试 ===")
    test_point = Point(50, 50)  # 测试点
    tolerance = 20.0
    
    start_time = time.time()
    nearby_point = spatial_idx.query_point(test_point, tolerance)
    query_time = time.time() - start_time
    
    print(f"点 {test_point} 附近 {tolerance}mm 范围内找到 {len(nearby_point)} 个图元")
    print(f"查询耗时: {query_time:.4f} 秒")
    
    # 7. 测试类型查询
    print("\n=== 类型查询测试 ===")
    line_elements = spatial_idx.query_by_type(Line)
    circle_elements = spatial_idx.query_by_type(Circle)
    
    print(f"Line 类型图元: {len(line_elements)} 个")
    print(f"Circle 类型图元: {len(circle_elements)} 个")
    
    # 8. 测试边界框查询
    print("\n=== 边界框查询测试 ===")
    bbox = (0, 0, 100, 100)  # 100x100mm 区域
    bbox_elements = spatial_idx.query_bbox(bbox)
    print(f"边界框 {bbox} 内找到 {len(bbox_elements)} 个图元")
    
    # 9. 测试最近邻查找
    print("\n=== 最近邻查找测试 ===")
    if len(normalized_elements) >= 2:
        target = normalized_elements[0]
        candidates = normalized_elements[1:]
        
        closest_result = spatial_idx.find_closest(target, candidates)
        if closest_result:
            closest_elem, distance = closest_result
            print(f"最近邻图元: {closest_elem}")
            print(f"距离: {distance:.2f} mm")
    
    # 10. 测试密度分布
    print("\n=== 密度分布测试 ===")
    density_map = spatial_idx.get_density_map(grid_size=5)
    print("密度分布图 (5x5网格):")
    for (x, y), count in sorted(density_map.items()):
        print(f"  网格({x},{y}): {count} 个图元")
    
    # 11. 性能测试 - 创建更多图元
    print("\n=== 性能测试 ===")
    
    # 创建大量测试图元
    test_elements = []
    for i in range(1000):
        x = i % 100
        y = i // 100
        test_line = Line(Point(x, y), Point(x+1, y+1), f"test_layer_{i}")
        test_elements.append(test_line)
    
    # 创建新的索引进行性能测试
    perf_idx = SpatialIndex()
    
    # 测试批量插入性能
    start_time = time.time()
    perf_idx.insert_batch(test_elements)
    insert_time = time.time() - start_time
    
    print(f"插入 {len(test_elements)} 个测试图元，耗时: {insert_time:.4f} 秒")
    print(f"平均插入速度: {len(test_elements)/insert_time:.0f} 图元/秒")
    
    # 测试查询性能
    query_count = 100
    total_query_time = 0
    
    for i in range(query_count):
        test_point = Point(i % 50, i // 50)
        start_time = time.time()
        results = perf_idx.query_point(test_point, 5.0)
        total_query_time += time.time() - start_time
    
    avg_query_time = total_query_time / query_count
    print(f"平均查询时间: {avg_query_time*1000:.2f} 毫秒")
    print(f"查询速度: {1/avg_query_time:.0f} 查询/秒")
    
    print("\n✅ 空间索引测试完成!")
    return True

if __name__ == "__main__":
    test_spatial_index()
