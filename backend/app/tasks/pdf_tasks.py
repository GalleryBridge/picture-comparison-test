"""
PDF处理相关的函数
"""

from app.services.pdf_service import PDFService
from app.services.ollama_service import OllamaService
from app.core.config import settings
import os
import json
from typing import Dict, Any


def process_pdf_task(file_id: str, pdf_path: str) -> Dict[str, Any]:
    """
    处理PDF文件的主任务
    """
    try:
        print(f"🚀 开始处理PDF文件: {pdf_path}")
        print(f"📄 文件ID: {file_id}")
        
        # 创建服务实例
        pdf_service = PDFService()
        
        # 获取PDF信息
        pdf_info = pdf_service.get_pdf_info(pdf_path)
        page_count = pdf_info["page_count"]
        print(f"📊 PDF包含 {page_count} 页")
        

        
        # 创建输出目录
        output_dir = os.path.join(settings.UPLOAD_DIR, "images", file_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # 转换PDF为图像
        print(f"🔄 开始转换PDF为图像...")
        image_paths = pdf_service.convert_pdf_to_images(pdf_path, output_dir)
        print(f"✅ 图像转换完成，生成 {len(image_paths)} 张图像")
        

        
        # 直接调用AI分析，不使用Celery
        print(f"🚀 开始直接调用AI分析...")
        
        try:
            # 创建Ollama服务实例
            ollama_service = OllamaService()
            
            # 检查模型可用性
            print(f"🔍 检查Ollama模型: {ollama_service.model}")
            import httpx
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{ollama_service.base_url}/api/show",
                    json={"name": ollama_service.model}
                )
                if response.status_code != 200:
                    raise Exception(f"Ollama模型不可用: {response.status_code}")
                print(f"✅ 模型 {ollama_service.model} 可用")
            
            # 开始分析图像
            print(f"🚀 开始分析 {len(image_paths)} 张图像...")
            results = []
            
            for i, image_path in enumerate(image_paths):
                print(f"📄 分析第 {i+1}/{len(image_paths)} 页: {image_path}")
                
                # 图像增强处理
                print(f"🖼️ 开始图像增强处理...")
                enhanced_image_path = pdf_service.enhance_for_engineering_drawing(image_path)
                print(f"✅ 图像增强完成: {enhanced_image_path}")
                
                # 编码增强后的图像
                image_base64 = ollama_service.encode_image_to_base64(enhanced_image_path)
                print(f"📸 增强图像编码完成，大小: {len(image_base64)} 字符")
                
                # 构建请求数据
                request_data = {
                    "model": ollama_service.model,
                    "prompt": ollama_service._get_default_prompt(),
                    "images": [image_base64],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                }
                
                print(f"🤖 发送请求到Ollama: {ollama_service.base_url}")
                
                # 发送请求到Ollama
                with httpx.Client(timeout=ollama_service.timeout) as client:
                    response = client.post(
                        f"{ollama_service.base_url}/api/generate",
                        json=request_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"Ollama API请求失败: {response.status_code}")
                    
                    result = response.json()
                    print(f"✅ 第 {i+1} 页分析成功，响应长度: {len(result.get('response', ''))}")
                    
                    # 解析尺寸和表格信息
                    parsed_data = ollama_service.parse_dimensions_from_response(
                        result.get("response", "")
                    )
                    
                    results.append({
                        "success": True,
                        "response": result.get("response", ""),
                        "model": result.get("model", ""),
                        "parsed_dimensions": parsed_data.get("dimensions", []),
                        "parsed_table_items": parsed_data.get("table_items", []),
                        "page_number": i + 1,
                        "image_path": image_path
                    })
            
            # 整理最终结果
            total_dimensions = sum(len(r.get("parsed_dimensions", [])) for r in results)
            total_table_items = sum(len(r.get("parsed_table_items", [])) for r in results)
            print(f"✅ AI分析完成，共找到 {total_dimensions} 个尺寸标注, {total_table_items} 个表格项目")
            
            print(f"🎉 AI分析完成！")
            

            
            # 返回完整结果
            result = {
                "file_id": file_id,
                "pdf_info": pdf_info,
                "image_paths": image_paths,
                "ai_analysis": {
                    "total_pages": len(image_paths),
                    "total_dimensions": total_dimensions,
                    "total_table_items": total_table_items,
                    "page_results": results,
                    "summary": {
                        "pages_analyzed": len(image_paths),
                        "successful_pages": sum(1 for r in results if r.get("success")),
                        "total_dimensions_found": total_dimensions,
                        "total_table_items_found": total_table_items,
                        "total_items_found": total_dimensions + total_table_items
                    }
                },
                "status": "completed",
                "message": "PDF处理和AI分析全部完成"
            }
            
            # 输出完整的JSON结果到控制台
            print("=" * 80)
            print("📊 完整分析结果JSON:")
            print("=" * 80)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ AI分析失败: {e}")
            # 如果AI分析失败，返回部分结果
            result = {
                "file_id": file_id,
                "pdf_info": pdf_info,
                "image_paths": image_paths,
                "ai_analysis": {
                    "error": str(e),
                    "status": "failed"
                },
                "status": "ai_analysis_failed",
                "message": f"PDF处理完成，但AI分析失败: {str(e)}"
            }
            
            # 即使失败也输出JSON结果
            print("=" * 80)
            print("📊 分析结果JSON (部分失败):")
            print("=" * 80)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("=" * 80)
        
        return result
        
    except Exception as e:
        # 清理临时文件
        try:
            if 'image_paths' in locals():
                pdf_service.cleanup_temp_files(image_paths)
        except:
            pass
        
        print(f"❌ PDF处理失败: {e}")
        raise



