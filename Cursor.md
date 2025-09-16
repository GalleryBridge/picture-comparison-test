# 传统算法图纸比对实现方案

## 🎯 目标
使用传统算法实现工业级精度的PDF/DWG图纸比对，完全基于图元级/几何级比对，不依赖视觉大模型。

## 📋 整体流程

```
输入图纸（DWG/PDF）
      ↓
文件解析（DWG→图元 / PDF→矢量对象）
      ↓
坐标/图元标准化（对齐、单位转换）
      ↓
图元匹配 & 差异检测（新增/删除/修改）
      ↓
差异输出（JSON/高亮图/报告）
```

## 🏗️ 技术架构

### 核心模块设计

```
backend/app/services/
├── traditional_comparison/
│   ├── __init__.py
│   ├── parsers/                    # 文件解析器
│   │   ├── __init__.py
│   │   ├── dwg_parser.py          # DWG文件解析
│   │   ├── pdf_parser.py          # PDF矢量解析
│   │   └── base_parser.py         # 解析器基类
│   ├── geometry/                   # 几何处理
│   │   ├── __init__.py
│   │   ├── elements.py            # 图元定义
│   │   ├── normalizer.py          # 坐标标准化
│   │   └── spatial_index.py       # 空间索引
│   ├── matching/                   # 匹配算法
│   │   ├── __init__.py
│   │   ├── element_matcher.py     # 图元匹配
│   │   ├── diff_detector.py       # 差异检测
│   │   └── tolerance.py           # 容差控制
│   ├── visualization/              # 可视化输出
│   │   ├── __init__.py
│   │   ├── diff_renderer.py       # 差异渲染
│   │   └── report_generator.py    # 报告生成
│   └── comparison_engine.py        # 主引擎
```

## 🛠️ 技术栈

| 模块 | 技术/工具 | 说明 |
|------|-----------|------|
| DWG解析 | `ezdxf` + `ODA SDK`(可选) | DWG/DXF图元提取 |
| PDF解析 | `PyMuPDF` + `pdfplumber` | PDF矢量图元提取 |
| 空间索引 | `rtree` + `shapely` | R-Tree空间索引，几何计算 |
| 几何运算 | `numpy` + `scipy` | 矢量运算，仿射变换 |
| 差异检测 | 自研算法 | 基于容差的几何匹配 |
| 可视化 | `matplotlib` + `cairo` | 差异高亮图生成 |
| 输出格式 | `pandas` + `openpyxl` | 结构化报告输出 |

## 📐 核心算法实现

### 1. 图元定义 (geometry/elements.py)

```python
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Line:
    start: Point
    end: Point
    layer: str = ""
    color: str = ""
    line_type: str = ""
    
    def length(self) -> float:
        return self.start.distance_to(self.end)
    
    def angle(self) -> float:
        return np.arctan2(self.end.y - self.start.y, self.end.x - self.start.x)

@dataclass
class Circle:
    center: Point
    radius: float
    layer: str = ""
    color: str = ""
    
    def area(self) -> float:
        return np.pi * self.radius ** 2

@dataclass
class Arc:
    center: Point
    radius: float
    start_angle: float
    end_angle: float
    layer: str = ""
    color: str = ""

@dataclass
class Text:
    position: Point
    content: str
    height: float
    rotation: float = 0.0
    layer: str = ""

# 图元联合类型
Element = Line | Circle | Arc | Text
```

### 2. DWG解析器 (parsers/dwg_parser.py)

```python
import ezdxf
from typing import List, Dict, Any
from .base_parser import BaseParser
from ..geometry.elements import Line, Circle, Arc, Text, Point

class DWGParser(BaseParser):
    """DWG/DXF文件解析器"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
        
    def parse_file(self, file_path: str) -> List[Element]:
        """解析DWG/DXF文件，提取图元"""
        try:
            doc = ezdxf.readfile(file_path)
            elements = []
            
            # 遍历所有图层
            for entity in doc.modelspace():
                element = self._convert_entity(entity)
                if element:
                    elements.append(element)
                    
            return elements
            
        except Exception as e:
            raise ValueError(f"DWG解析失败: {e}")
    
    def _convert_entity(self, entity) -> Optional[Element]:
        """转换ezdxf实体为内部图元格式"""
        entity_type = entity.dxftype()
        
        if entity_type == 'LINE':
            return Line(
                start=Point(entity.dxf.start.x, entity.dxf.start.y),
                end=Point(entity.dxf.end.x, entity.dxf.end.y),
                layer=entity.dxf.layer,
                color=str(entity.dxf.color)
            )
            
        elif entity_type == 'CIRCLE':
            return Circle(
                center=Point(entity.dxf.center.x, entity.dxf.center.y),
                radius=entity.dxf.radius,
                layer=entity.dxf.layer,
                color=str(entity.dxf.color)
            )
            
        elif entity_type == 'ARC':
            return Arc(
                center=Point(entity.dxf.center.x, entity.dxf.center.y),
                radius=entity.dxf.radius,
                start_angle=entity.dxf.start_angle,
                end_angle=entity.dxf.end_angle,
                layer=entity.dxf.layer,
                color=str(entity.dxf.color)
            )
            
        elif entity_type == 'TEXT':
            return Text(
                position=Point(entity.dxf.insert.x, entity.dxf.insert.y),
                content=entity.dxf.text,
                height=entity.dxf.height,
                rotation=entity.dxf.rotation,
                layer=entity.dxf.layer
            )
            
        return None
```

### 3. PDF解析器 (parsers/pdf_parser.py)

```python
import fitz  # PyMuPDF
from typing import List, Dict, Any
from .base_parser import BaseParser
from ..geometry.elements import Line, Circle, Text, Point

class PDFParser(BaseParser):
    """PDF矢量图元解析器"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
        
    def parse_file(self, file_path: str) -> List[Element]:
        """解析PDF文件，提取矢量图元"""
        try:
            doc = fitz.open(file_path)
            elements = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_elements = self._parse_page(page)
                elements.extend(page_elements)
                
            doc.close()
            return elements
            
        except Exception as e:
            raise ValueError(f"PDF解析失败: {e}")
    
    def _parse_page(self, page) -> List[Element]:
        """解析单页PDF，提取图元"""
        elements = []
        
        # 获取绘图指令
        drawings = page.get_drawings()
        
        for drawing in drawings:
            for item in drawing["items"]:
                element = self._convert_path_item(item)
                if element:
                    elements.append(element)
        
        # 获取文本
        text_dict = page.get_text("dict")
        text_elements = self._extract_text_elements(text_dict)
        elements.extend(text_elements)
        
        return elements
    
    def _convert_path_item(self, item) -> Optional[Element]:
        """转换PDF路径项为图元"""
        if item[0] == "l":  # 直线
            x1, y1, x2, y2 = item[1:]
            return Line(
                start=Point(x1, y1),
                end=Point(x2, y2),
                layer="default"
            )
            
        elif item[0] == "c":  # 三次贝塞尔曲线
            # 简化处理：如果是圆弧，转换为Arc
            # 复杂曲线可能需要分段处理
            pass
            
        return None
    
    def _extract_text_elements(self, text_dict) -> List[Text]:
        """提取文本元素"""
        elements = []
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        elements.append(Text(
                            position=Point(span["bbox"][0], span["bbox"][1]),
                            content=span["text"],
                            height=span["size"]
                        ))
                        
        return elements
```

### 4. 空间索引 (geometry/spatial_index.py)

```python
from rtree import index
from typing import List, Tuple, Dict
from .elements import Element, Point, Line, Circle, Arc

class SpatialIndex:
    """R-Tree空间索引，用于快速查找邻近图元"""
    
    def __init__(self):
        self.idx = index.Index()
        self.elements: Dict[int, Element] = {}
        self.next_id = 0
    
    def insert(self, element: Element) -> int:
        """插入图元到空间索引"""
        bbox = self._get_bbox(element)
        element_id = self.next_id
        self.next_id += 1
        
        self.idx.insert(element_id, bbox)
        self.elements[element_id] = element
        
        return element_id
    
    def query_nearby(self, element: Element, tolerance: float = 1.0) -> List[Tuple[int, Element]]:
        """查找指定图元附近的其他图元"""
        bbox = self._get_bbox(element)
        # 扩展边界框
        expanded_bbox = (
            bbox[0] - tolerance, bbox[1] - tolerance,
            bbox[2] + tolerance, bbox[3] + tolerance
        )
        
        nearby_ids = list(self.idx.intersection(expanded_bbox))
        return [(id, self.elements[id]) for id in nearby_ids]
    
    def _get_bbox(self, element: Element) -> Tuple[float, float, float, float]:
        """获取图元的边界框 (xmin, ymin, xmax, ymax)"""
        if isinstance(element, Line):
            return (
                min(element.start.x, element.end.x),
                min(element.start.y, element.end.y),
                max(element.start.x, element.end.x),
                max(element.start.y, element.end.y)
            )
        elif isinstance(element, Circle):
            return (
                element.center.x - element.radius,
                element.center.y - element.radius,
                element.center.x + element.radius,
                element.center.y + element.radius
            )
        elif isinstance(element, Arc):
            # 简化处理：使用圆的边界框
            return (
                element.center.x - element.radius,
                element.center.y - element.radius,
                element.center.x + element.radius,
                element.center.y + element.radius
            )
        else:
            # 默认点边界框
            return (element.position.x, element.position.y, 
                   element.position.x, element.position.y)
```

### 5. 图元匹配器 (matching/element_matcher.py)

```python
from typing import List, Tuple, Optional, Dict
from ..geometry.elements import Element, Line, Circle, Arc, Text
from ..geometry.spatial_index import SpatialIndex
from .tolerance import ToleranceConfig

class ElementMatcher:
    """图元匹配器，基于几何相似度匹配图元"""
    
    def __init__(self, tolerance: ToleranceConfig):
        self.tolerance = tolerance
    
    def match_elements(self, elements_a: List[Element], 
                      elements_b: List[Element]) -> Dict[str, List]:
        """匹配两组图元，返回匹配结果"""
        
        # 构建空间索引
        index_b = SpatialIndex()
        for elem in elements_b:
            index_b.insert(elem)
        
        matched_pairs = []
        unmatched_a = []
        matched_b_ids = set()
        
        # 对A中每个图元寻找B中的匹配
        for elem_a in elements_a:
            nearby_elements = index_b.query_nearby(elem_a, self.tolerance.position)
            
            best_match = None
            best_similarity = 0.0
            
            for elem_id, elem_b in nearby_elements:
                if elem_id in matched_b_ids:
                    continue
                    
                similarity = self._calculate_similarity(elem_a, elem_b)
                if similarity > self.tolerance.similarity_threshold and similarity > best_similarity:
                    best_match = (elem_id, elem_b)
                    best_similarity = similarity
            
            if best_match:
                matched_pairs.append((elem_a, best_match[1]))
                matched_b_ids.add(best_match[0])
            else:
                unmatched_a.append(elem_a)
        
        # 找出B中未匹配的图元
        unmatched_b = [elem for i, elem in enumerate(elements_b) 
                      if i not in matched_b_ids]
        
        return {
            'matched': matched_pairs,
            'deleted': unmatched_a,  # A中有，B中没有
            'added': unmatched_b     # B中有，A中没有
        }
    
    def _calculate_similarity(self, elem_a: Element, elem_b: Element) -> float:
        """计算两个图元的相似度 [0.0, 1.0]"""
        
        # 类型不同，相似度为0
        if type(elem_a) != type(elem_b):
            return 0.0
        
        if isinstance(elem_a, Line) and isinstance(elem_b, Line):
            return self._line_similarity(elem_a, elem_b)
        elif isinstance(elem_a, Circle) and isinstance(elem_b, Circle):
            return self._circle_similarity(elem_a, elem_b)
        elif isinstance(elem_a, Arc) and isinstance(elem_b, Arc):
            return self._arc_similarity(elem_a, elem_b)
        elif isinstance(elem_a, Text) and isinstance(elem_b, Text):
            return self._text_similarity(elem_a, elem_b)
        
        return 0.0
    
    def _line_similarity(self, line_a: Line, line_b: Line) -> float:
        """计算直线相似度"""
        # 长度相似度
        len_a, len_b = line_a.length(), line_b.length()
        if len_a == 0 or len_b == 0:
            return 0.0
        
        len_sim = 1.0 - abs(len_a - len_b) / max(len_a, len_b)
        if len_sim < (1.0 - self.tolerance.length_ratio):
            return 0.0
        
        # 位置相似度（起点和终点距离）
        start_dist = line_a.start.distance_to(line_b.start)
        end_dist = line_a.end.distance_to(line_b.end)
        
        # 考虑线段方向可能相反
        start_dist_rev = line_a.start.distance_to(line_b.end)
        end_dist_rev = line_a.end.distance_to(line_b.start)
        
        pos_error = min(start_dist + end_dist, start_dist_rev + end_dist_rev)
        pos_sim = max(0.0, 1.0 - pos_error / self.tolerance.position)
        
        # 角度相似度
        angle_diff = abs(line_a.angle() - line_b.angle())
        angle_diff = min(angle_diff, 2*3.14159 - angle_diff)  # 考虑周期性
        angle_sim = max(0.0, 1.0 - angle_diff / self.tolerance.angle)
        
        # 综合相似度
        return (len_sim * 0.4 + pos_sim * 0.4 + angle_sim * 0.2)
    
    def _circle_similarity(self, circle_a: Circle, circle_b: Circle) -> float:
        """计算圆相似度"""
        # 半径相似度
        radius_diff = abs(circle_a.radius - circle_b.radius)
        radius_sim = max(0.0, 1.0 - radius_diff / self.tolerance.position)
        
        # 中心点距离
        center_dist = circle_a.center.distance_to(circle_b.center)
        center_sim = max(0.0, 1.0 - center_dist / self.tolerance.position)
        
        return (radius_sim * 0.5 + center_sim * 0.5)
```

### 6. 容差配置 (matching/tolerance.py)

```python
from dataclasses import dataclass

@dataclass
class ToleranceConfig:
    """容差配置，控制匹配精度"""
    
    # 位置容差 (毫米)
    position: float = 0.1
    
    # 长度比例容差 (0.01 = 1%)
    length_ratio: float = 0.01
    
    # 角度容差 (弧度)
    angle: float = 0.017  # 约1度
    
    # 相似度阈值
    similarity_threshold: float = 0.8
    
    # 文本匹配容差
    text_position: float = 1.0  # 文本位置容差更大
    
    @classmethod
    def high_precision(cls) -> 'ToleranceConfig':
        """高精度配置"""
        return cls(
            position=0.05,
            length_ratio=0.005,
            angle=0.009,  # 0.5度
            similarity_threshold=0.9
        )
    
    @classmethod
    def standard(cls) -> 'ToleranceConfig':
        """标准精度配置"""
        return cls()
    
    @classmethod
    def relaxed(cls) -> 'ToleranceConfig':
        """宽松配置"""
        return cls(
            position=0.5,
            length_ratio=0.05,
            angle=0.087,  # 5度
            similarity_threshold=0.7
        )
```

### 7. 主比对引擎 (comparison_engine.py)

```python
from typing import List, Dict, Any, Tuple
from .parsers.dwg_parser import DWGParser
from .parsers.pdf_parser import PDFParser
from .geometry.normalizer import CoordinateNormalizer
from .matching.element_matcher import ElementMatcher
from .matching.tolerance import ToleranceConfig
from .visualization.diff_renderer import DiffRenderer

class TraditionalComparisonEngine:
    """传统算法图纸比对引擎"""
    
    def __init__(self, tolerance: ToleranceConfig = None):
        self.tolerance = tolerance or ToleranceConfig.standard()
        self.dwg_parser = DWGParser(self.tolerance.position)
        self.pdf_parser = PDFParser(self.tolerance.position)
        self.normalizer = CoordinateNormalizer()
        self.matcher = ElementMatcher(self.tolerance)
        self.renderer = DiffRenderer()
    
    def compare_files(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """比对两个图纸文件"""
        
        # 1. 解析文件
        elements_a = self._parse_file(file_a)
        elements_b = self._parse_file(file_b)
        
        print(f"解析完成: 文件A {len(elements_a)}个图元, 文件B {len(elements_b)}个图元")
        
        # 2. 坐标标准化
        elements_a = self.normalizer.normalize(elements_a)
        elements_b = self.normalizer.normalize(elements_b)
        
        # 3. 图元匹配
        match_result = self.matcher.match_elements(elements_a, elements_b)
        
        # 4. 生成比对结果
        comparison_result = {
            'summary': {
                'total_a': len(elements_a),
                'total_b': len(elements_b),
                'matched': len(match_result['matched']),
                'added': len(match_result['added']),
                'deleted': len(match_result['deleted']),
                'similarity': self._calculate_overall_similarity(match_result)
            },
            'details': {
                'matched_pairs': match_result['matched'],
                'added_elements': match_result['added'],
                'deleted_elements': match_result['deleted']
            },
            'tolerance_used': self.tolerance
        }
        
        return comparison_result
    
    def _parse_file(self, file_path: str) -> List:
        """根据文件类型选择解析器"""
        file_ext = file_path.lower().split('.')[-1]
        
        if file_ext in ['dwg', 'dxf']:
            return self.dwg_parser.parse_file(file_path)
        elif file_ext == 'pdf':
            return self.pdf_parser.parse_file(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def _calculate_overall_similarity(self, match_result: Dict) -> float:
        """计算整体相似度"""
        total_elements = (len(match_result['matched']) + 
                         len(match_result['added']) + 
                         len(match_result['deleted']))
        
        if total_elements == 0:
            return 1.0
            
        return len(match_result['matched']) / total_elements
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install ezdxf PyMuPDF pdfplumber rtree shapely numpy scipy matplotlib pandas openpyxl
```

### 2. 基本使用

```python
from app.services.traditional_comparison.comparison_engine import TraditionalComparisonEngine
from app.services.traditional_comparison.matching.tolerance import ToleranceConfig

# 创建比对引擎
engine = TraditionalComparisonEngine(
    tolerance=ToleranceConfig.high_precision()
)

# 比对两个文件
result = engine.compare_files("drawing_v1.dwg", "drawing_v2.dwg")

print(f"相似度: {result['summary']['similarity']:.2%}")
print(f"新增: {result['summary']['added']}个图元")
print(f"删除: {result['summary']['deleted']}个图元")
```

### 3. API集成

在 `backend/app/api/endpoints/` 中添加传统比对接口：

```python
# traditional_comparison.py
from fastapi import APIRouter, UploadFile, File
from ...services.traditional_comparison.comparison_engine import TraditionalComparisonEngine

router = APIRouter()

@router.post("/traditional-compare")
async def traditional_compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...)
):
    engine = TraditionalComparisonEngine()
    
    # 保存上传文件
    file_a_path = save_upload_file(file_a)
    file_b_path = save_upload_file(file_b)
    
    # 执行比对
    result = engine.compare_files(file_a_path, file_b_path)
    
    return result
```

## ⚙️ 配置参数

### 精度级别选择

```python
# 高精度 (工业级)
ToleranceConfig.high_precision()   # 0.05mm位置精度

# 标准精度
ToleranceConfig.standard()         # 0.1mm位置精度  

# 宽松精度
ToleranceConfig.relaxed()          # 0.5mm位置精度
```

### 自定义容差

```python
custom_tolerance = ToleranceConfig(
    position=0.02,          # 位置容差 2mm
    length_ratio=0.001,     # 长度容差 0.1%
    angle=0.005,            # 角度容差 0.3度
    similarity_threshold=0.95  # 相似度阈值 95%
)
```

## 📊 性能优化

### 1. 空间索引优化
- 使用R-Tree加速邻近查找
- 大图纸(>10万图元)必须启用

### 2. 分层处理
- 按CAD图层分别比对
- 并行处理多个图层

### 3. 内存管理
- 大文件分块处理
- 及时释放解析对象

## 🎨 差异可视化

### 输出格式
- **JSON**: 结构化差异数据
- **高亮图片**: PNG/SVG格式
- **Excel报告**: 详细差异表格
- **CAD文件**: 标注差异的DWG文件

### 颜色编码
- 🔴 **红色**: 删除的图元
- 🟢 **绿色**: 新增的图元  
- 🔵 **蓝色**: 修改的图元
- ⚫ **黑色**: 未变化的图元

## 🧪 测试验证

### 精度测试
```python
def test_precision():
    """测试不同精度下的比对结果"""
    test_cases = [
        ("identical.dwg", "identical.dwg", 1.0),
        ("v1.dwg", "v1_0.1mm_shift.dwg", 0.99),
        ("v1.dwg", "v2_major_change.dwg", 0.3)
    ]
    
    for file_a, file_b, expected_sim in test_cases:
        result = engine.compare_files(file_a, file_b)
        actual_sim = result['summary']['similarity']
        assert abs(actual_sim - expected_sim) < 0.05
```

## 🔧 扩展功能

### 1. 支持更多图元类型
- Polyline (多段线)
- Spline (样条曲线)  
- Block (块参照)
- Dimension (标注)

### 2. 高级匹配算法
- 图形配准 (Image Registration)
- 拓扑匹配 (Topology Matching)
- 语义匹配 (Semantic Matching)

### 3. 并行处理
- 多进程图元解析
- GPU加速几何运算

---

## 📝 实施计划

### 阶段1: 核心功能 (1-2周)
- [ ] 基础图元定义
- [ ] DWG/PDF解析器
- [ ] 简单匹配算法
- [ ] 基本差异检测

### 阶段2: 精度优化 (1周)  
- [ ] 空间索引集成
- [ ] 容差配置系统
- [ ] 坐标标准化
- [ ] 相似度算法优化

### 阶段3: 可视化输出 (1周)
- [ ] 差异高亮渲染
- [ ] 报告生成
- [ ] API接口集成
- [ ] 前端展示组件

### 阶段4: 测试验证 (1周)
- [ ] 单元测试
- [ ] 精度测试
- [ ] 性能测试  
- [ ] 实际图纸验证

**总工期**: 4-5周，可达到工业级精度要求。
