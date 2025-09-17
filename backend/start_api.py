#!/usr/bin/env python3
"""
API服务启动脚本
"""

import sys
import os
import uvicorn
from pathlib import Path

# 添加项目路径
sys.path.append('app')

def start_api_server():
    """启动API服务器"""
    
    print("🚀 启动PDF比对API服务...")
    
    # 检查必要文件
    if not os.path.exists('test_drawing.pdf'):
        print("⚠ 警告: 找不到test_drawing.pdf测试文件")
        print("  请确保有PDF文件用于测试")
    
    # 创建输出目录
    output_dirs = [
        "outputs",
        "outputs/uploads", 
        "outputs/comparisons",
        "outputs/highlights",
        "outputs/renders",
        "outputs/reports"
    ]
    
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构准备完成")
    
    # 启动服务器
    try:
        uvicorn.run(
            "app.services.pdf_comparison.api.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 API服务已停止")
    except Exception as e:
        print(f"✗ API服务启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_api_server()
