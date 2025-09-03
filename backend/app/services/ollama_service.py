"""
Ollama AI模型服务
"""

import httpx
import base64
import json
from typing import Dict, Any, List, Optional
from app.core.config import settings


class OllamaService:
    """Ollama AI模型服务类"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = 300  # 5分钟超时
    
    async def check_model_availability(self) -> bool:
        """
        检查模型是否可用
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # 使用 POST 方法检查模型是否可用
                response = await client.post(
                    f"{self.base_url}/api/show",
                    json={"name": self.model}
                )
                if response.status_code == 200:
                    return True
                
                # 如果 show 失败，回退到 tags 方法
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return any(model.get("name", "").startswith(self.model.split(":")[0]) 
                             for model in models)
                return False
        except Exception:
            return False
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将图像编码为base64字符串
        """
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            raise Exception(f"图像编码失败: {str(e)}")
    
    async def analyze_image(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        分析图像并提取尺寸信息
        """
        try:
            # 编码图像
            image_base64 = self.encode_image_to_base64(image_path)
            
            # 默认提示词
            if prompt is None:
                prompt = self._get_default_prompt()
            
            # 构建请求数据
            request_data = {
                "model": self.model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 降低随机性，提高准确性
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            # 发送请求
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API请求失败: {response.status_code}")
                
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": result.get("model", ""),
                    "total_duration": result.get("total_duration", 0),
                    "load_duration": result.get("load_duration", 0),
                    "prompt_eval_count": result.get("prompt_eval_count", 0),
                    "eval_count": result.get("eval_count", 0)
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
    
    def _get_default_prompt(self) -> str:
        """
        获取默认的尺寸识别提示词
        """
        return """
请仔细分析这张工程图纸图像，识别并提取所有的尺寸标注信息。

请按照以下格式返回JSON结果：
{
    "dimensions": [
        {
            "value": "数值",
            "unit": "单位(mm/cm/inch等)",
            "tolerance": "公差(如±0.1，如果没有则为null)",
            "position": {"x": x坐标, "y": y坐标},
            "confidence": 置信度(0-1之间的小数)
        }
    ],
    "summary": {
        "total_dimensions": 总尺寸数量,
        "units_found": ["发现的单位列表"],
        "has_tolerances": 是否包含公差信息
    }
}

注意事项：
1. 只识别明确的尺寸标注，不要包含其他数字
2. 尺寸值应该是纯数字，不包含单位
3. 位置坐标是相对于图像的像素位置
4. 置信度反映识别的确定程度
5. 如果无法识别任何尺寸，返回空的dimensions数组

请确保返回的是有效的JSON格式。
"""
    
    async def batch_analyze_images(self, image_paths: List[str], prompt: str = None) -> List[Dict[str, Any]]:
        """
        批量分析多个图像
        """
        results = []
        for i, image_path in enumerate(image_paths):
            try:
                result = await self.analyze_image(image_path, prompt)
                result["page_number"] = i + 1
                result["image_path"] = image_path
                results.append(result)
            except Exception as e:
                results.append({
                    "success": False,
                    "error": str(e),
                    "page_number": i + 1,
                    "image_path": image_path
                })
        
        return results
    
    def parse_dimensions_from_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        从AI响应中解析尺寸信息
        """
        try:
            # 尝试解析JSON响应
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                return data.get("dimensions", [])
            
            # 如果不是JSON格式，尝试使用正则表达式提取
            import re
            dimensions = []
            
            # 匹配常见的尺寸格式：数字+单位+可选公差
            pattern = r'(\d+\.?\d*)\s*(mm|cm|inch|in|″|′)\s*([±]\s*\d+\.?\d*)?'
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            
            for match in matches:
                value, unit, tolerance = match
                dimensions.append({
                    "value": value,
                    "unit": unit.lower(),
                    "tolerance": tolerance.strip() if tolerance else None,
                    "position": {"x": 0, "y": 0},  # 默认位置
                    "confidence": 0.7  # 默认置信度
                })
            
            return dimensions
            
        except Exception as e:
            print(f"解析尺寸信息失败: {str(e)}")
            return []
