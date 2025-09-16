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
        获取优化的尺寸识别提示词 - 确保JSON输出一致性
        """
        return """你是专业的工程图纸分析专家。请识别图像中的所有尺寸标注信息。

重要：请严格按照以下JSON格式输出，不要包含任何其他文字或解释！

```json
{
    "dimensions": [
        {
            "value": "数字值",
            "unit": "单位",
            "tolerance": "公差或null",
            "dimension_type": "类型",
            "prefix": "前缀或null",
            "position": {"x": 0, "y": 0},
            "confidence": 0.9,
            "description": "描述"
        }
    ],
    "summary": {
        "total_dimensions": 0,
        "dimension_types": [],
        "units_found": [],
        "has_tolerances": false,
        "scan_coverage": "完整"
    },
    "analysis_notes": "分析说明"
}
```

识别要求：
1. 扫描整个图像，从左到右、从上到下
2. 识别所有数字+单位的组合（mm、cm、°、inch等）
3. 注意公差标注（±符号）
4. 识别前缀符号（Φ、R、C、M等）
5. 包括线性、角度、直径、半径、倒角等所有类型
6. 不要遗漏角落、边缘、重叠区域的小尺寸
7. 对不确定的标注也要包含，标注低置信度

dimension_type选项：linear, angular, diameter, radius, thread, hole, chamfer, position, roughness

请只输出JSON，不要其他内容！"""
    
    def _get_enhanced_prompt(self) -> str:
        """
        获取增强版提示词 - 用于复杂图纸的二次分析
        """
        return """你是工程图纸分析专家。这是一张复杂的工程图纸，请进行深度分析。

请特别注意以下区域的尺寸标注：
- 图像边缘和角落的小标注
- 线条交叉处的隐藏尺寸  
- 淡色或低对比度的标注
- 重叠或密集标注区域
- 内部细节和特殊符号

输出格式（只输出JSON）：
```json
{
    "dimensions": [
        {
            "value": "数字",
            "unit": "单位",
            "tolerance": "公差",
            "dimension_type": "类型",
            "prefix": "前缀",
            "position": {"x": 0, "y": 0},
            "confidence": 0.8,
            "description": "详细描述"
        }
    ],
    "summary": {
        "total_dimensions": 0,
        "scan_coverage": "深度扫描"
    }
}
```

要求：宁可多识别也不要遗漏，包含所有可能的尺寸标注！"""
    
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
        从AI响应中解析尺寸信息 - 增强版
        """
        try:
            import re
            all_dimensions = []
            
            print(f"🔍 开始解析AI响应，长度: {len(response_text)}")
            
            # 方法1: 提取markdown格式的JSON代码块
            json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)
            print(f"📄 找到 {len(json_blocks)} 个JSON代码块")
            
            for i, block in enumerate(json_blocks):
                try:
                    print(f"🔄 解析第 {i+1} 个JSON代码块...")
                    data = json.loads(block)
                    dimensions = data.get("dimensions", [])
                    print(f"✅ 成功解析出 {len(dimensions)} 个尺寸")
                    all_dimensions.extend(dimensions)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {str(e)}")
                    continue
            
            # 方法2: 尝试直接解析纯JSON（去除markdown标记）
            if not all_dimensions:
                print("🔄 尝试直接JSON解析...")
                # 清理响应文本
                cleaned_text = response_text.strip()
                # 移除可能的markdown标记
                cleaned_text = re.sub(r'^```json\s*', '', cleaned_text, flags=re.MULTILINE)
                cleaned_text = re.sub(r'\s*```$', '', cleaned_text, flags=re.MULTILINE)
                
                if cleaned_text.startswith('{'):
                    try:
                        data = json.loads(cleaned_text)
                        dimensions = data.get("dimensions", [])
                        print(f"✅ 直接JSON解析成功，找到 {len(dimensions)} 个尺寸")
                        all_dimensions.extend(dimensions)
                    except json.JSONDecodeError as e:
                        print(f"❌ 直接JSON解析失败: {str(e)}")
            
            # 方法3: 增强的正则表达式回退解析
            if not all_dimensions:
                print("🔄 使用增强正则表达式解析...")
                all_dimensions = self._extract_dimensions_with_enhanced_regex(response_text)
                print(f"📊 正则表达式解析找到 {len(all_dimensions)} 个尺寸")
            
            print(f"🎉 总共解析出 {len(all_dimensions)} 个尺寸标注")
            return all_dimensions
            
        except Exception as e:
            print(f"❌ 解析尺寸信息失败: {str(e)}")
            return []
    
    def _extract_dimensions_with_enhanced_regex(self, text: str) -> List[Dict[str, Any]]:
        """
        增强的正则表达式尺寸提取
        """
        import re
        dimensions = []
        
        # 多种尺寸格式的正则表达式
        patterns = [
            # 基本格式: 数字 + 单位 + 可选公差
            (r'(\d+\.?\d*)\s*(mm|cm|inch|in|″|′|°|um)\s*([±]\s*\d+\.?\d*)?', 'basic'),
            
            # 直径格式: Φ + 数字 + 单位
            (r'[ΦΦφ]\s*(\d+\.?\d*)\s*(mm|cm|inch|in)?', 'diameter'),
            
            # 半径格式: R + 数字 + 单位  
            (r'R\s*(\d+\.?\d*)\s*(mm|cm|inch|in)?', 'radius'),
            
            # 倒角格式: C + 数字 + 单位
            (r'C\s*(\d+\.?\d*)\s*(mm|cm|inch|in)?', 'chamfer'),
            
            # 公差格式: 数字 ± 数字 单位
            (r'(\d+\.?\d*)\s*[±]\s*(\d+\.?\d*)\s*(mm|cm|inch|in|°)', 'tolerance'),
            
            # MAX/MIN格式: 数字 MAX/MIN
            (r'(\d+\.?\d*)\s*(MAX|MIN|max|min)', 'limit'),
            
            # 表面粗糙度: Ra + 数字 + 单位
            (r'Ra\s*(\d+\.?\d*)\s*(um|μm|mm)?', 'roughness'),
        ]
        
        for pattern, dim_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                if dim_type == 'basic':
                    value, unit, tolerance = match
                    dimensions.append({
                        "value": value,
                        "unit": unit.lower() if unit else "mm",
                        "tolerance": tolerance.strip() if tolerance else None,
                        "dimension_type": "linear",
                        "prefix": None,
                        "position": {"x": 0, "y": 0},
                        "confidence": 0.7,
                        "description": f"正则提取-{dim_type}"
                    })
                    
                elif dim_type == 'diameter':
                    value, unit = match
                    dimensions.append({
                        "value": value,
                        "unit": unit.lower() if unit else "mm",
                        "tolerance": None,
                        "dimension_type": "diameter", 
                        "prefix": "Φ",
                        "position": {"x": 0, "y": 0},
                        "confidence": 0.8,
                        "description": f"正则提取-直径"
                    })
                    
                elif dim_type == 'radius':
                    value, unit = match
                    dimensions.append({
                        "value": value,
                        "unit": unit.lower() if unit else "mm",
                        "tolerance": None,
                        "dimension_type": "radius",
                        "prefix": "R", 
                        "position": {"x": 0, "y": 0},
                        "confidence": 0.8,
                        "description": f"正则提取-半径"
                    })
                    
                elif dim_type == 'tolerance':
                    value, tolerance_val, unit = match
                    dimensions.append({
                        "value": value,
                        "unit": unit.lower(),
                        "tolerance": f"±{tolerance_val}",
                        "dimension_type": "linear",
                        "prefix": None,
                        "position": {"x": 0, "y": 0},
                        "confidence": 0.9,
                        "description": f"正则提取-公差"
                    })
                    
                elif dim_type == 'limit':
                    value, limit_type = match
                    dimensions.append({
                        "value": value,
                        "unit": "mm",
                        "tolerance": limit_type.upper(),
                        "dimension_type": "linear",
                        "prefix": None,
                        "position": {"x": 0, "y": 0},
                        "confidence": 0.8,
                        "description": f"正则提取-{limit_type.lower()}值"
                    })
        
        # 去重处理
        unique_dimensions = []
        seen = set()
        for dim in dimensions:
            key = f"{dim['value']}-{dim['unit']}-{dim.get('tolerance', '')}"
            if key not in seen:
                seen.add(key)
                unique_dimensions.append(dim)
        
        return unique_dimensions
