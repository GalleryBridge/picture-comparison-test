#!/usr/bin/env python3
"""
PDF解析器测试脚本
"""

import sys
sys.path.append('app')

from services.pdf_comparison.parser.pdf_parser import PDFParser

def test_pdf_parser():
    """测试PDF解析器功能"""
    
    # 创建解析器
    parser = PDFParser()
    
    # 验证PDF文件
    print("=== PDF验证结果 ===")
    validation = parser.validate_pdf('test_drawing.pdf')
    for key, value in validation.items():
        print(f"  {key}: {value}")
    
    if not validation['is_valid']:
        print("PDF文件无效，停止测试")
        return
    
    print("\n=== 开始解析PDF ===")
    try:
        result = parser.parse_file('test_drawing.pdf')
        
        print("\n=== 解析结果 ===")
        print(f"  总图元数: {len(result['elements'])}")
        print(f"  页面数: {len(result['page_info'])}")
        
        # 显示前几个图元
        print("\n=== 前5个图元 ===")
        for i, element in enumerate(result['elements'][:5]):
            print(f"  {i+1}. {element}")
        
        # 按类型统计图元
        print("\n=== 图元类型统计 ===")
        type_counts = {}
        for element in result['elements']:
            elem_type = type(element).__name__
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        for elem_type, count in type_counts.items():
            print(f"  {elem_type}: {count}个")
            
        # 显示元数据
        print("\n=== 元数据 ===")
        metadata = result['metadata']
        for key in ['page_count', 'creator', 'producer', 'title']:
            if key in metadata and metadata[key]:
                print(f"  {key}: {metadata[key]}")
        
        # 显示页面信息
        print("\n=== 页面信息 ===")
        for page_info in result['page_info']:
            print(f"  页面 {page_info['page_num']}: {page_info['element_count']}个图元")
            print(f"    边界框: {page_info['bbox']}")
            
        print("\n✅ PDF解析测试成功!")
        return True
        
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_pdf_parser()
