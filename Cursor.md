# PDF图纸传统算法比对实现方案

## 🎯 目标
使用传统算法实现工业级精度的PDF图纸比对，完全基于图元级/几何级比对，不依赖视觉大模型。专注于PDF矢量图纸的精确解析和比对。

## 📋 整体流程

```
输入图纸（PDF）
      ↓
文件解析（PDF → 矢量对象）
      ↓
坐标/图元标准化（对齐、单位转换）
      ↓
图元匹配 & 差异检测（新增/删除/修改）
      ↓
差异输出（JSON / 高亮图 / 报告）
```

## 🏗️ 技术架构

### 核心模块设计

```
backend/app/services/
├── pdf_comparison/
│   ├── __init__.py
│   ├── parser/                     # PDF解析器
│   │   ├── __init__.py
│   │   ├── pdf_parser.py          # PDF矢量解析
│   │   ├── vector_extractor.py    # 矢量图元提取
│   │   └── text_extractor.py      # 文本元素提取
│   ├── geometry/                   # 几何处理
│   │   ├── __init__.py
│   │   ├── elements.py            # 图元定义
│   │   ├── normalizer.py          # 坐标标准化
│   │   ├── spatial_index.py       # 空间索引
│   │   └── coordinate_system.py   # 坐标系统处理
│   ├── matching/                   # 匹配算法
│   │   ├── __init__.py
│   │   ├── element_matcher.py     # 图元匹配
│   │   ├── similarity_calculator.py # 相似度计算
│   │   ├── diff_detector.py       # 差异检测
│   │   └── tolerance.py           # 容差控制
│   ├── visualization/              # 可视化输出
│   │   ├── __init__.py
│   │   ├── diff_renderer.py       # 差异渲染
│   │   ├── pdf_highlighter.py     # PDF高亮标注
│   │   └── report_generator.py    # 报告生成
│   └── comparison_engine.py        # 主比对引擎
```

## 🛠️ 技术栈

| 模块 | 技术/工具 | 说明 |
|------|-----------|------|
| PDF解析 | `PyMuPDF` + `pdfplumber` + `PDFium` | PDF矢量图元和文本提取 |
| 矢量提取 | `PyMuPDF.get_drawings()` | PDF绘图指令解析 |
| 空间索引 | `rtree` + `shapely` | R-Tree空间索引，几何计算 |
| 几何运算 | `numpy` + `scipy` | 矢量运算，仿射变换 |
| 坐标处理 | `numpy` + 自研算法 | 坐标系标准化和变换 |
| 差异检测 | 自研算法 | 基于容差的几何匹配 |
| PDF标注 | `PyMuPDF` + `reportlab` | PDF差异高亮和标注 |
| 可视化 | `matplotlib` + `PIL` | 差异图像生成 |
| 输出格式 | `pandas` + `openpyxl` + `jinja2` | 结构化报告输出 |

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

### 2. PDF解析器 (parser/pdf_parser.py)

```python
import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any, Optional, Tuple
from ..geometry.elements import Line, Circle, Arc, Text, Point, Element

class PDFParser:
    """PDF矢量图元解析器 - 专注于工程图纸解析"""
    
    def __init__(self, tolerance: float = 0.1):
        self.tolerance = tolerance
        self.supported_elements = ['line', 'circle', 'arc', 'text', 'polyline']
        
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """解析PDF文件，提取矢量图元和元数据"""
        try:
            # 使用PyMuPDF解析矢量图形
            fitz_doc = fitz.open(file_path)
            # 使用pdfplumber解析文本和表格
            plumber_doc = pdfplumber.open(file_path)
            
            result = {
                'elements': [],
                'metadata': self._extract_metadata(fitz_doc),
                'page_info': []
            }
            
            for page_num in range(len(fitz_doc)):
                fitz_page = fitz_doc[page_num]
                plumber_page = plumber_doc.pages[page_num]
                
                page_elements = self._parse_page(fitz_page, plumber_page, page_num)
                result['elements'].extend(page_elements)
                
                # 页面信息
                page_info = {
                    'page_num': page_num,
                    'bbox': fitz_page.rect,
                    'rotation': fitz_page.rotation,
                    'element_count': len(page_elements)
                }
                result['page_info'].append(page_info)
                
            fitz_doc.close()
            plumber_doc.close()
            
            return result
            
        except Exception as e:
            raise ValueError(f"PDF解析失败: {e}")
    
    def _parse_page(self, fitz_page, plumber_page, page_num: int) -> List[Element]:
        """解析单页PDF，提取所有图元"""
        elements = []
        
        # 1. 解析矢量图形 (使用PyMuPDF)
        vector_elements = self._extract_vector_elements(fitz_page, page_num)
        elements.extend(vector_elements)
        
        # 2. 解析文本元素 (使用pdfplumber，精度更高)
        text_elements = self._extract_text_elements(plumber_page, page_num)
        elements.extend(text_elements)
        
        # 3. 解析表格和标注 (如果存在)
        table_elements = self._extract_table_elements(plumber_page, page_num)
        elements.extend(table_elements)
        
        return elements
    
    def _extract_vector_elements(self, page, page_num: int) -> List[Element]:
        """提取矢量图元 (线条、圆、弧等)"""
        elements = []
        
        # 获取绘图指令
        drawings = page.get_drawings()
        
        for drawing in drawings:
            # 解析路径
            for path in drawing.get("items", []):
                element = self._convert_path_to_element(path, page_num)
                if element:
                    elements.append(element)
        
        return elements
    
    def _convert_path_to_element(self, path, page_num: int) -> Optional[Element]:
        """将PDF路径转换为几何图元"""
        if not path:
            return None
            
        path_type = path[0] if isinstance(path, (list, tuple)) else None
        
        try:
            if path_type == "l":  # 直线 (lineto)
                if len(path) >= 5:
                    x1, y1, x2, y2 = path[1:5]
                    return Line(
                        start=Point(float(x1), float(y1)),
                        end=Point(float(x2), float(y2)),
                        layer=f"page_{page_num}",
                        color="black"
                    )
                    
            elif path_type == "c":  # 三次贝塞尔曲线
                # 检测是否为圆弧
                if len(path) >= 7:
                    arc = self._bezier_to_arc(path[1:7])
                    if arc:
                        return arc
                        
            elif path_type == "re":  # 矩形
                if len(path) >= 5:
                    x, y, w, h = path[1:5]
                    # 将矩形转换为4条线段
                    return self._rectangle_to_lines(x, y, w, h, page_num)
                    
        except (ValueError, IndexError) as e:
            print(f"路径转换错误: {e}")
            
        return None
    
    def _bezier_to_arc(self, bezier_points: List[float]) -> Optional[Arc]:
        """将贝塞尔曲线转换为圆弧 (如果可能)"""
        try:
            # 简化实现：检测圆形贝塞尔曲线
            x1, y1, x2, y2, x3, y3 = bezier_points
            
            # 计算中心点和半径 (简化算法)
            center_x = (x1 + x3) / 2
            center_y = (y1 + y3) / 2
            radius = ((x1 - center_x)**2 + (y1 - center_y)**2)**0.5
            
            # 计算角度
            import math
            start_angle = math.atan2(y1 - center_y, x1 - center_x)
            end_angle = math.atan2(y3 - center_y, x3 - center_x)
            
            return Arc(
                center=Point(center_x, center_y),
                radius=radius,
                start_angle=start_angle,
                end_angle=end_angle,
                layer="default",
                color="black"
            )
            
        except Exception:
            return None
    
    def _extract_text_elements(self, page, page_num: int) -> List[Text]:
        """提取文本元素 (使用pdfplumber获得更好的精度)"""
        elements = []
        
        try:
            # 获取所有文本字符
            chars = page.chars
            
            for char in chars:
                if char.get('text', '').strip():
                    elements.append(Text(
                        position=Point(float(char['x0']), float(char['y0'])),
                        content=char['text'],
                        height=float(char.get('size', 12)),
                        rotation=0.0,
                        layer=f"text_page_{page_num}",
                        font=char.get('fontname', 'unknown')
                    ))
                    
        except Exception as e:
            print(f"文本提取错误: {e}")
            
        return elements
    
    def _extract_table_elements(self, page, page_num: int) -> List[Element]:
        """提取表格元素"""
        elements = []
        
        try:
            tables = page.find_tables()
            
            for table in tables:
                # 将表格边框转换为线段
                bbox = table.bbox
                if bbox:
                    x0, y0, x1, y1 = bbox
                    # 表格外框
                    elements.extend([
                        Line(Point(x0, y0), Point(x1, y0), f"table_page_{page_num}"),  # 上边
                        Line(Point(x1, y0), Point(x1, y1), f"table_page_{page_num}"),  # 右边
                        Line(Point(x1, y1), Point(x0, y1), f"table_page_{page_num}"),  # 下边
                        Line(Point(x0, y1), Point(x0, y0), f"table_page_{page_num}")   # 左边
                    ])
                    
        except Exception as e:
            print(f"表格提取错误: {e}")
            
        return elements
    
    def _extract_metadata(self, doc) -> Dict[str, Any]:
        """提取PDF元数据"""
        metadata = doc.metadata
        return {
            'title': metadata.get('title', ''),
            'author': metadata.get('author', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': doc.page_count,
            'is_pdf': doc.is_pdf,
            'needs_pass': doc.needs_pass
        }
```

### 3. 坐标标准化器 (geometry/normalizer.py)

```python
import numpy as np
from typing import List, Dict, Any, Tuple
from .elements import Element, Point, Line, Circle, Arc, Text

class CoordinateNormalizer:
    """坐标系统标准化器 - 处理PDF坐标系差异"""
    
    def __init__(self):
        self.reference_dpi = 72  # PDF标准DPI
        self.target_unit = "mm"  # 目标单位：毫米
        
    def normalize(self, elements: List[Element], page_info: Dict = None) -> List[Element]:
        """标准化图元坐标系统"""
        if not elements:
            return elements
            
        # 1. 坐标系转换 (PDF坐标系 -> 标准坐标系)
        elements = self._convert_coordinate_system(elements, page_info)
        
        # 2. 单位标准化 (点 -> 毫米)
        elements = self._convert_units(elements)
        
        # 3. 坐标对齐 (以左下角为原点)
        elements = self._align_coordinates(elements)
        
        return elements
    
    def _convert_coordinate_system(self, elements: List[Element], page_info: Dict = None) -> List[Element]:
        """转换PDF坐标系 (左下角原点 -> 左上角原点)"""
        if not page_info or 'bbox' not in page_info:
            return elements
            
        page_height = page_info['bbox'][3] - page_info['bbox'][1]
        
        normalized_elements = []
        for element in elements:
            if isinstance(element, Line):
                normalized_elements.append(Line(
                    start=Point(element.start.x, page_height - element.start.y),
                    end=Point(element.end.x, page_height - element.end.y),
                    layer=element.layer,
                    color=element.color,
                    line_type=element.line_type
                ))
            elif isinstance(element, Circle):
                normalized_elements.append(Circle(
                    center=Point(element.center.x, page_height - element.center.y),
                    radius=element.radius,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Arc):
                normalized_elements.append(Arc(
                    center=Point(element.center.x, page_height - element.center.y),
                    radius=element.radius,
                    start_angle=element.start_angle,
                    end_angle=element.end_angle,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Text):
                normalized_elements.append(Text(
                    position=Point(element.position.x, page_height - element.position.y),
                    content=element.content,
                    height=element.height,
                    rotation=element.rotation,
                    layer=element.layer
                ))
            else:
                normalized_elements.append(element)
                
        return normalized_elements
    
    def _convert_units(self, elements: List[Element]) -> List[Element]:
        """单位转换：PDF点 -> 毫米"""
        # 1 PDF点 = 1/72 英寸 = 25.4/72 毫米 ≈ 0.3528 毫米
        point_to_mm = 25.4 / 72
        
        converted_elements = []
        for element in elements:
            if isinstance(element, Line):
                converted_elements.append(Line(
                    start=Point(element.start.x * point_to_mm, element.start.y * point_to_mm),
                    end=Point(element.end.x * point_to_mm, element.end.y * point_to_mm),
                    layer=element.layer,
                    color=element.color,
                    line_type=element.line_type
                ))
            elif isinstance(element, Circle):
                converted_elements.append(Circle(
                    center=Point(element.center.x * point_to_mm, element.center.y * point_to_mm),
                    radius=element.radius * point_to_mm,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Arc):
                converted_elements.append(Arc(
                    center=Point(element.center.x * point_to_mm, element.center.y * point_to_mm),
                    radius=element.radius * point_to_mm,
                    start_angle=element.start_angle,
                    end_angle=element.end_angle,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Text):
                converted_elements.append(Text(
                    position=Point(element.position.x * point_to_mm, element.position.y * point_to_mm),
                    content=element.content,
                    height=element.height * point_to_mm,
                    rotation=element.rotation,
                    layer=element.layer
                ))
            else:
                converted_elements.append(element)
                
        return converted_elements
    
    def _align_coordinates(self, elements: List[Element]) -> List[Element]:
        """坐标对齐 - 将最小坐标设为原点"""
        if not elements:
            return elements
            
        # 找到最小坐标
        min_x = min_y = float('inf')
        
        for element in elements:
            if isinstance(element, Line):
                min_x = min(min_x, element.start.x, element.end.x)
                min_y = min(min_y, element.start.y, element.end.y)
            elif isinstance(element, (Circle, Arc)):
                min_x = min(min_x, element.center.x - element.radius)
                min_y = min(min_y, element.center.y - element.radius)
            elif isinstance(element, Text):
                min_x = min(min_x, element.position.x)
                min_y = min(min_y, element.position.y)
        
        # 如果没有有效坐标，返回原始元素
        if min_x == float('inf') or min_y == float('inf'):
            return elements
            
        # 平移所有元素
        aligned_elements = []
        for element in elements:
            if isinstance(element, Line):
                aligned_elements.append(Line(
                    start=Point(element.start.x - min_x, element.start.y - min_y),
                    end=Point(element.end.x - min_x, element.end.y - min_y),
                    layer=element.layer,
                    color=element.color,
                    line_type=element.line_type
                ))
            elif isinstance(element, Circle):
                aligned_elements.append(Circle(
                    center=Point(element.center.x - min_x, element.center.y - min_y),
                    radius=element.radius,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Arc):
                aligned_elements.append(Arc(
                    center=Point(element.center.x - min_x, element.center.y - min_y),
                    radius=element.radius,
                    start_angle=element.start_angle,
                    end_angle=element.end_angle,
                    layer=element.layer,
                    color=element.color
                ))
            elif isinstance(element, Text):
                aligned_elements.append(Text(
                    position=Point(element.position.x - min_x, element.position.y - min_y),
                    content=element.content,
                    height=element.height,
                    rotation=element.rotation,
                    layer=element.layer
                ))
            else:
                aligned_elements.append(element)
                
        return aligned_elements
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

### 7. PDF比对引擎 (comparison_engine.py)

```python
from typing import List, Dict, Any, Tuple
from .parser.pdf_parser import PDFParser
from .geometry.normalizer import CoordinateNormalizer
from .matching.element_matcher import ElementMatcher
from .matching.tolerance import ToleranceConfig
from .visualization.diff_renderer import DiffRenderer
from .visualization.pdf_highlighter import PDFHighlighter

class PDFComparisonEngine:
    """PDF图纸传统算法比对引擎"""
    
    def __init__(self, tolerance: ToleranceConfig = None):
        self.tolerance = tolerance or ToleranceConfig.standard()
        self.pdf_parser = PDFParser(self.tolerance.position)
        self.normalizer = CoordinateNormalizer()
        self.matcher = ElementMatcher(self.tolerance)
        self.renderer = DiffRenderer()
        self.highlighter = PDFHighlighter()
    
    def compare_pdf_files(self, file_a: str, file_b: str) -> Dict[str, Any]:
        """比对两个PDF图纸文件"""
        
        # 1. 解析PDF文件
        print("正在解析PDF文件...")
        result_a = self.pdf_parser.parse_file(file_a)
        result_b = self.pdf_parser.parse_file(file_b)
        
        elements_a = result_a['elements']
        elements_b = result_b['elements']
        
        print(f"解析完成: 文件A {len(elements_a)}个图元, 文件B {len(elements_b)}个图元")
        
        # 2. 坐标标准化
        print("正在标准化坐标系...")
        page_info_a = result_a['page_info'][0] if result_a['page_info'] else None
        page_info_b = result_b['page_info'][0] if result_b['page_info'] else None
        
        elements_a = self.normalizer.normalize(elements_a, page_info_a)
        elements_b = self.normalizer.normalize(elements_b, page_info_b)
        
        # 3. 图元匹配和差异检测
        print("正在进行图元匹配...")
        match_result = self.matcher.match_elements(elements_a, elements_b)
        
        # 4. 生成比对结果
        comparison_result = {
            'summary': {
                'file_a': file_a,
                'file_b': file_b,
                'total_a': len(elements_a),
                'total_b': len(elements_b),
                'matched': len(match_result['matched']),
                'added': len(match_result['added']),
                'deleted': len(match_result['deleted']),
                'similarity': self._calculate_overall_similarity(match_result),
                'comparison_time': self._get_current_time()
            },
            'details': {
                'matched_pairs': match_result['matched'],
                'added_elements': match_result['added'],
                'deleted_elements': match_result['deleted']
            },
            'metadata': {
                'file_a_info': result_a['metadata'],
                'file_b_info': result_b['metadata'],
                'tolerance_used': self.tolerance.__dict__,
                'page_info_a': result_a['page_info'],
                'page_info_b': result_b['page_info']
            }
        }
        
        return comparison_result
    
    def generate_diff_visualization(self, comparison_result: Dict[str, Any], 
                                  output_path: str = None) -> Dict[str, str]:
        """生成差异可视化文件"""
        
        # 1. 生成高亮PDF
        highlighted_pdf = self.highlighter.create_highlighted_pdf(
            comparison_result, output_path
        )
        
        # 2. 生成差异图像
        diff_image = self.renderer.render_diff_image(
            comparison_result, output_path
        )
        
        # 3. 生成报告
        report_files = self.renderer.generate_reports(
            comparison_result, output_path
        )
        
        return {
            'highlighted_pdf': highlighted_pdf,
            'diff_image': diff_image,
            'excel_report': report_files.get('excel'),
            'json_report': report_files.get('json'),
            'html_report': report_files.get('html')
        }
    
    def batch_compare(self, file_pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """批量比对PDF文件"""
        results = []
        
        for i, (file_a, file_b) in enumerate(file_pairs):
            print(f"正在处理第 {i+1}/{len(file_pairs)} 对文件...")
            try:
                result = self.compare_pdf_files(file_a, file_b)
                results.append(result)
            except Exception as e:
                print(f"比对失败 {file_a} vs {file_b}: {e}")
                results.append({
                    'error': str(e),
                    'file_a': file_a,
                    'file_b': file_b
                })
        
        return results
    
    def _calculate_overall_similarity(self, match_result: Dict) -> float:
        """计算整体相似度"""
        total_elements = (len(match_result['matched']) + 
                         len(match_result['added']) + 
                         len(match_result['deleted']))
        
        if total_elements == 0:
            return 1.0
            
        return len(match_result['matched']) / total_elements
    
    def _get_current_time(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_comparison_statistics(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """获取比对统计信息"""
        summary = comparison_result['summary']
        
        return {
            'element_statistics': {
                'total_elements_a': summary['total_a'],
                'total_elements_b': summary['total_b'],
                'matched_elements': summary['matched'],
                'added_elements': summary['added'],
                'deleted_elements': summary['deleted']
            },
            'similarity_metrics': {
                'overall_similarity': summary['similarity'],
                'match_rate': summary['matched'] / max(summary['total_a'], summary['total_b']) if max(summary['total_a'], summary['total_b']) > 0 else 0,
                'change_rate': (summary['added'] + summary['deleted']) / max(summary['total_a'], summary['total_b']) if max(summary['total_a'], summary['total_b']) > 0 else 0
            },
            'element_type_breakdown': self._analyze_element_types(comparison_result['details'])
        }
    
    def _analyze_element_types(self, details: Dict) -> Dict[str, int]:
        """分析图元类型分布"""
        type_counts = {'Line': 0, 'Circle': 0, 'Arc': 0, 'Text': 0, 'Other': 0}
        
        for element_list in [details['matched_pairs'], details['added_elements'], details['deleted_elements']]:
            for item in element_list:
                if isinstance(item, tuple):  # matched pairs
                    element = item[0]
                else:  # single elements
                    element = item
                    
                element_type = type(element).__name__
                if element_type in type_counts:
                    type_counts[element_type] += 1
                else:
                    type_counts['Other'] += 1
        
        return type_counts
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install PyMuPDF pdfplumber rtree shapely numpy scipy matplotlib pandas openpyxl reportlab jinja2
```

### 2. 基本使用

```python
from app.services.pdf_comparison.comparison_engine import PDFComparisonEngine
from app.services.pdf_comparison.matching.tolerance import ToleranceConfig

# 创建PDF比对引擎
engine = PDFComparisonEngine(
    tolerance=ToleranceConfig.high_precision()
)

# 比对两个PDF文件
result = engine.compare_pdf_files("drawing_v1.pdf", "drawing_v2.pdf")

print(f"相似度: {result['summary']['similarity']:.2%}")
print(f"新增: {result['summary']['added']}个图元")
print(f"删除: {result['summary']['deleted']}个图元")

# 生成可视化文件
visualization = engine.generate_diff_visualization(result, "./output/")
print(f"高亮PDF: {visualization['highlighted_pdf']}")
print(f"差异图像: {visualization['diff_image']}")
```

### 3. API集成

在 `backend/app/api/endpoints/` 中添加PDF比对接口：

```python
# pdf_comparison.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from ...services.pdf_comparison.comparison_engine import PDFComparisonEngine
from ...services.pdf_comparison.matching.tolerance import ToleranceConfig

router = APIRouter()

@router.post("/pdf-compare")
async def pdf_compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    precision: str = "standard"  # high_precision, standard, relaxed
):
    # 验证文件格式
    if not (file_a.filename.endswith('.pdf') and file_b.filename.endswith('.pdf')):
        raise HTTPException(status_code=400, detail="只支持PDF文件")
    
    # 选择精度配置
    tolerance_map = {
        "high_precision": ToleranceConfig.high_precision(),
        "standard": ToleranceConfig.standard(),
        "relaxed": ToleranceConfig.relaxed()
    }
    tolerance = tolerance_map.get(precision, ToleranceConfig.standard())
    
    engine = PDFComparisonEngine(tolerance=tolerance)
    
    # 保存上传文件
    file_a_path = save_upload_file(file_a)
    file_b_path = save_upload_file(file_b)
    
    try:
        # 执行比对
        result = engine.compare_pdf_files(file_a_path, file_b_path)
        
        # 生成可视化文件
        visualization = engine.generate_diff_visualization(result)
        
        return {
            "comparison_result": result,
            "visualization_files": visualization,
            "statistics": engine.get_comparison_statistics(result)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"比对失败: {str(e)}")

@router.post("/pdf-batch-compare")
async def pdf_batch_compare(
    files: List[UploadFile] = File(...),
    precision: str = "standard"
):
    """批量PDF比对"""
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="至少需要2个PDF文件")
    
    # 构建文件对
    file_pairs = []
    for i in range(0, len(files), 2):
        if i + 1 < len(files):
            file_a_path = save_upload_file(files[i])
            file_b_path = save_upload_file(files[i + 1])
            file_pairs.append((file_a_path, file_b_path))
    
    # 批量比对
    tolerance = ToleranceConfig.standard()
    engine = PDFComparisonEngine(tolerance=tolerance)
    results = engine.batch_compare(file_pairs)
    
    return {"batch_results": results}
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

### 阶段1: PDF解析与图元提取 (1-2周)
- [ ] PDF矢量图元解析器开发
- [ ] 基础图元定义 (Line, Circle, Arc, Text)
- [ ] 坐标系统标准化
- [ ] PDF元数据提取

### 阶段2: 图元匹配与差异检测 (1周)  
- [ ] 空间索引集成 (R-Tree)
- [ ] 容差配置系统
- [ ] 几何相似度算法
- [ ] 差异检测逻辑

### 阶段3: 可视化与输出 (1周)
- [ ] PDF高亮标注功能
- [ ] 差异图像渲染
- [ ] 多格式报告生成 (JSON/Excel/HTML)
- [ ] API接口开发

### 阶段4: 测试与优化 (1周)
- [ ] 单元测试覆盖
- [ ] 精度测试验证
- [ ] 性能优化 (大文件处理)
- [ ] 实际PDF图纸验证

### 阶段5: 前端集成 (可选，1周)
- [ ] Vue组件开发
- [ ] 比对结果展示
- [ ] 交互式差异查看
- [ ] 批量处理界面

**总工期**: 4-6周，专注PDF图纸比对，达到工业级精度要求。

## 🎯 PDF专项优化

### PDF特有挑战
1. **坐标系差异**: PDF使用左下角原点，需要转换
2. **单位转换**: PDF点 -> 毫米的精确转换
3. **矢量提取**: 复杂路径的图元识别
4. **文本处理**: 字符级精确定位
5. **多页处理**: 页面间坐标统一

### 解决方案
1. **双库结合**: PyMuPDF(矢量) + pdfplumber(文本)
2. **精确转换**: 25.4/72毫米/点的标准转换
3. **智能识别**: 贝塞尔曲线到圆弧的转换
4. **字符级别**: 单字符位置的精确提取
5. **页面标准化**: 统一坐标系和单位
