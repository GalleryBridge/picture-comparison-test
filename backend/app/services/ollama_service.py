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
        self.timeout = 900  # 15分钟超时
    
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
        获取优化的尺寸识别提示词 - 支持表格和标注识别
        """
        return """你是专业的工程图纸分析专家。请识别图像中的所有尺寸标注信息，包括表格中的公差项目。

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
    "table_items": [
        {
            "item_name": "项目名称",
            "description": "项目描述",
            "tolerance_value": "公差数值",
            "unit": "单位",
            "row_number": 1,
            "confidence": 0.9
        }
    ],
    "summary": {
        "total_dimensions": 0,
        "total_table_items": 0,
        "dimension_types": [],
        "units_found": [],
        "has_tolerances": false,
        "has_table": false,
        "scan_coverage": "完整"
    },
    "analysis_notes": "分析说明"
}
```

识别要求：

A. 图纸标注识别：
1. 扫描整个图像，识别所有数字+单位的组合（mm、cm、°、inch等）
2. 注意公差标注（±符号）
3. 识别前缀符号（Φ、R、C、M等）
4. 包括线性、角度、直径、半径、倒角等所有类型

B. 表格信息识别：
1. 识别表格结构，特别是检查清单类表格
2. 提取左侧描述列的所有文本项目，如：
   - 总长公差、总厚度公差、总长度公差
   - base宽度公差、base长度公差、base厚度公差
   - 角度公差类项目（FA角度、block角度、prism角度等）
   - 位置公差项目（出光位置、焦点距离等）
   - 其他工程参数（光口焦距、REC外径等）
3. 关联右侧对应的数值和公差
4. 按行序号记录每个项目

C. 特别注意：
- 中文工程术语的准确识别
- 表格中的公差符号（±0.05、±0.03等）
- 项目描述的完整性
- 不要遗漏任何表格行

dimension_type选项：linear, angular, diameter, radius, thread, hole, chamfer, position, roughness, tolerance_spec

请只输出JSON，不要其他内容！"""
    
    def _get_enhanced_prompt(self) -> str:
        """
        获取增强版提示词 - 专门用于表格检查清单分析
        """
        return """你是专业的工程检查清单分析专家。请仔细识别图像中的表格内容，特别是左侧的描述项目。

重点识别以下类型的表格项目：

**公差类项目（重点）：**
- 总长公差、总厚度公差、总长度公差
- base宽度公差、base长度公差、base厚度公差  
- 角度公差（FA角度、block角度、prism角度、出光角度等）
- 位置公差（出光位置、焦点距base底板、焦点距base侧壁等）
- 贴装公差（治具保证贴装、非治具保证贴装、贴装角度等）

**尺寸类项目：**
- 外径、厚度、长度相关项目
- REC外径公差、REC尾翼厚度公差
- FA尾胶长度、REC尾胶长度
- 光口焦距、铣边角度

**通用公差：**
- 其余未定义尺寸公差、其余未定义角度公差

严格按照以下JSON格式输出：
```json
{
    "dimensions": [],
    "table_items": [
        {
            "item_name": "总长公差",
            "description": "产品总体长度的公差要求",
            "tolerance_value": "±0.05",
            "unit": "mm",
            "row_number": 1,
            "confidence": 0.9
        }
    ],
    "summary": {
        "total_dimensions": 0,
        "total_table_items": 25,
        "has_tolerances": true,
        "has_table": true,
        "scan_coverage": "表格完整扫描"
    },
    "analysis_notes": "检查清单表格分析完成"
}
```

要求：
1. 仔细扫描表格每一行的描述文字
2. 准确提取中文工程术语
3. 关联对应的数值公差（±0.05、±0.03等）
4. 按行号顺序记录
5. 不要遗漏任何表格行项目

请只输出JSON，不要其他内容！"""
    
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
    
    def parse_dimensions_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        从AI响应中解析尺寸信息和表格信息 - 增强版
        """
        try:
            import re
            all_dimensions = []
            all_table_items = []
            
            print(f"🔍 开始解析AI响应，长度: {len(response_text)}")
            
            # 方法1: 提取markdown格式的JSON代码块
            json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL | re.IGNORECASE)
            print(f"📄 找到 {len(json_blocks)} 个JSON代码块")
            
            for i, block in enumerate(json_blocks):
                try:
                    print(f"🔄 解析第 {i+1} 个JSON代码块...")
                    data = json.loads(block)
                    dimensions = data.get("dimensions", [])
                    table_items = data.get("table_items", [])
                    print(f"✅ 成功解析出 {len(dimensions)} 个尺寸标注, {len(table_items)} 个表格项目")
                    all_dimensions.extend(dimensions)
                    all_table_items.extend(table_items)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {str(e)}")
                    continue
            
            # 方法2: 尝试直接解析纯JSON（去除markdown标记）
            if not all_dimensions and not all_table_items:
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
                        table_items = data.get("table_items", [])
                        print(f"✅ 直接JSON解析成功，找到 {len(dimensions)} 个尺寸标注, {len(table_items)} 个表格项目")
                        all_dimensions.extend(dimensions)
                        all_table_items.extend(table_items)
                    except json.JSONDecodeError as e:
                        print(f"❌ 直接JSON解析失败: {str(e)}")
            
            # 方法3: 增强的正则表达式回退解析（仅用于尺寸）
            if not all_dimensions:
                print("🔄 使用增强正则表达式解析尺寸...")
                all_dimensions = self._extract_dimensions_with_enhanced_regex(response_text)
                print(f"📊 正则表达式解析找到 {len(all_dimensions)} 个尺寸")
            
            print(f"🎉 总共解析出 {len(all_dimensions)} 个尺寸标注, {len(all_table_items)} 个表格项目")
            
            return {
                "dimensions": all_dimensions,
                "table_items": all_table_items,
                "total_items": len(all_dimensions) + len(all_table_items)
            }
            
        except Exception as e:
            print(f"❌ 解析信息失败: {str(e)}")
            return {
                "dimensions": [],
                "table_items": [],
                "total_items": 0
            }
    
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
