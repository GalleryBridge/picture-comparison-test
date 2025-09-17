#!/usr/bin/env python3
"""
调试PDF结构，查看绘图指令格式
"""

import fitz
import pdfplumber

def debug_pdf_structure(file_path):
    """调试PDF文件结构"""
    
    print("=== 使用PyMuPDF调试 ===")
    doc = fitz.open(file_path)
    page = doc[0]
    
    # 获取绘图指令
    drawings = page.get_drawings()
    print(f"绘图指令数量: {len(drawings)}")
    
    for i, drawing in enumerate(drawings):
        print(f"\n绘图 {i}:")
        print(f"  类型: {type(drawing)}")
        print(f"  键: {drawing.keys() if isinstance(drawing, dict) else 'N/A'}")
        
        if isinstance(drawing, dict):
            for key, value in drawing.items():
                if key == 'items':
                    print(f"  {key}: {len(value) if isinstance(value, list) else value}")
                    # 显示前几个项目
                    if isinstance(value, list):
                        for j, item in enumerate(value[:3]):
                            print(f"    项目 {j}: {item}")
                else:
                    print(f"  {key}: {value}")
    
    # 获取文本
    text_dict = page.get_text("dict")
    print(f"\n文本块数量: {len(text_dict.get('blocks', []))}")
    
    doc.close()
    
    print("\n=== 使用pdfplumber调试 ===")
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        
        # 获取所有对象
        print(f"字符数: {len(page.chars)}")
        print(f"线条数: {len(page.lines) if hasattr(page, 'lines') else 'N/A'}")
        print(f"矩形数: {len(page.rects) if hasattr(page, 'rects') else 'N/A'}")
        print(f"曲线数: {len(page.curves) if hasattr(page, 'curves') else 'N/A'}")
        
        # 显示线条信息
        if hasattr(page, 'lines') and page.lines:
            print("\n前3条线:")
            for i, line in enumerate(page.lines[:3]):
                print(f"  线 {i}: {line}")
        
        # 显示矩形信息
        if hasattr(page, 'rects') and page.rects:
            print("\n前3个矩形:")
            for i, rect in enumerate(page.rects[:3]):
                print(f"  矩形 {i}: {rect}")

if __name__ == "__main__":
    debug_pdf_structure('test_drawing.pdf')
