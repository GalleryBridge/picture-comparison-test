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
        self.timeout = 600  # 10分钟超时
    
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
你是一个专业的工程图纸分析专家。请仔细、系统地分析这张工程图纸图像，识别并提取**所有**的尺寸标注信息。

【分析要求】
请按以下步骤进行全面扫描：
1. **整体扫描**：从左到右、从上到下系统地扫描整个图像
2. **细节检查**：仔细查看每个角落、边缘和内部区域
3. **多次核查**：确保没有遗漏任何尺寸标注

【需要识别的尺寸类型】
- **线性尺寸**：长度、宽度、高度、直径、半径等
- **角度尺寸**：各种角度标注（°）
- **螺纹尺寸**：螺纹规格和螺距
- **孔径尺寸**：各种孔的直径和深度
- **倒角尺寸**：倒角和圆角尺寸
- **位置尺寸**：定位尺寸和坐标尺寸
- **其他标注**：包括任何带有数字和单位的标注

【识别特征】
寻找以下特征的数字：
- 带有尺寸线和箭头的数字
- 标有单位符号的数字（mm、cm、inch、°等）
- 带有公差的数字（±、+/-、上下偏差）
- 尺寸框内的数字
- 标注线引出的数字

请按照以下JSON格式返回结果：
{
    "dimensions": [
        {
            "value": "纯数字值（不含单位）",
            "unit": "单位(mm/cm/inch/°等)",
            "tolerance": "公差标注(如±0.1、+0.2/-0.1，无则为null)",
            "dimension_type": "尺寸类型(linear/angular/diameter/radius/thread/hole/chamfer/position)",
            "prefix": "前缀符号(如Φ、R、M等，无则为null)", 
            "position": {"x": x坐标像素值, "y": y坐标像素值},
            "confidence": 置信度(0.0-1.0),
            "description": "尺寸描述(如'主视图长度'、'孔径'等)"
        }
    ],
    "summary": {
        "total_dimensions": 识别到的总尺寸数量,
        "dimension_types": ["识别到的尺寸类型列表"],
        "units_found": ["发现的所有单位"],
        "has_tolerances": 是否包含公差信息,
        "scan_coverage": "扫描覆盖度评估(如'完整'、'部分')"
    },
    "analysis_notes": "分析说明和可能遗漏的区域"
}

【重要要求】
1. **全面性**：不要遗漏任何可能的尺寸，宁可多识别也不要少识别
2. **准确性**：确保每个尺寸值和位置都准确
3. **完整性**：包含所有相关信息（单位、公差、前缀等）
4. **系统性**：按照逻辑顺序进行扫描和识别
5. **置信度**：诚实评估每个识别结果的可信度

【输出示例】
```json
{
    "dimensions": [
        {
            "value": "100",
            "unit": "mm", 
            "tolerance": "±0.1",
            "dimension_type": "linear",
            "prefix": null,
            "position": {"x": 150, "y": 200},
            "confidence": 0.95,
            "description": "主视图长度尺寸"
        },
        {
            "value": "25",
            "unit": "mm",
            "tolerance": null,
            "dimension_type": "diameter", 
            "prefix": "Φ",
            "position": {"x": 300, "y": 180},
            "confidence": 0.90,
            "description": "圆孔直径"
        },
        {
            "value": "45",
            "unit": "°",
            "tolerance": null,
            "dimension_type": "angular",
            "prefix": null, 
            "position": {"x": 250, "y": 120},
            "confidence": 0.85,
            "description": "倒角角度"
        }
    ],
    "summary": {
        "total_dimensions": 3,
        "dimension_types": ["linear", "diameter", "angular"],
        "units_found": ["mm", "°"],
        "has_tolerances": true,
        "scan_coverage": "完整"
    },
    "analysis_notes": "图纸清晰，所有尺寸标注均已识别"
}
```

【特别注意】
- **小尺寸标注**：注意角落和细节处的小尺寸
- **重叠区域**：仔细辨认重叠或密集标注区域的每个尺寸
- **低对比度**：识别淡色、灰色或低对比度的标注
- **各种字体**：包括手写、印刷、不同大小的字体
- **边界尺寸**：图像边缘的尺寸标注
- **内部尺寸**：零件内部的孔径、槽宽等尺寸
- **宁多勿少**：如果不确定某数字是否为尺寸，优先包含

【扫描策略】
1. 先进行整体快速扫描，识别主要尺寸
2. 然后分区域仔细检查，确保不遗漏
3. 最后进行验证，核实每个尺寸的准确性

请严格按照JSON格式输出，确保语法正确，并尽最大努力识别**所有**尺寸标注！
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
