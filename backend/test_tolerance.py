#!/usr/bin/env python3
"""
容差配置系统测试脚本
"""

import sys
sys.path.append('app')

from services.pdf_comparison.matching.tolerance import ToleranceConfig, ToleranceManager

def test_tolerance_config():
    """测试容差配置功能"""
    
    print("=== 容差配置系统测试 ===")
    
    # 1. 测试预设配置
    print("\n=== 预设配置测试 ===")
    
    configs = {
        '超高精度': ToleranceConfig.ultra_precise(),
        '高精度': ToleranceConfig.high_precision(),
        '标准': ToleranceConfig.standard(),
        '宽松': ToleranceConfig.relaxed()
    }
    
    for name, config in configs.items():
        print(f"{name}配置:")
        print(f"  {config.get_description()}")
        print(f"  搜索半径: {config.max_search_radius}mm")
        print(f"  文本容差: {config.text_position}mm")
    
    # 2. 测试自定义配置
    print("\n=== 自定义配置测试 ===")
    
    try:
        custom_config = ToleranceConfig.custom(
            position=0.2,
            length_ratio=0.02,
            similarity_threshold=0.9
        )
        print(f"自定义配置: {custom_config}")
        
        # 测试字典转换
        config_dict = custom_config.to_dict()
        print(f"转换为字典: 包含 {len(config_dict)} 个参数")
        
        # 从字典重建
        rebuilt_config = ToleranceConfig.from_dict(config_dict)
        print(f"从字典重建: {rebuilt_config}")
        
    except Exception as e:
        print(f"自定义配置测试失败: {e}")
    
    # 3. 测试参数验证
    print("\n=== 参数验证测试 ===")
    
    # 测试无效参数
    invalid_configs = [
        {'position': -1},  # 负数位置容差
        {'length_ratio': 1.5},  # 超出范围的长度比例
        {'similarity_threshold': 1.5},  # 超出范围的相似度
    ]
    
    for i, invalid_params in enumerate(invalid_configs):
        try:
            ToleranceConfig.custom(**invalid_params)
            print(f"验证测试 {i+1}: 失败 - 应该抛出异常")
        except ValueError as e:
            print(f"验证测试 {i+1}: 通过 - {e}")
    
    # 4. 测试配置兼容性
    print("\n=== 配置兼容性测试 ===")
    
    high_precision = ToleranceConfig.high_precision()
    standard = ToleranceConfig.standard()
    relaxed = ToleranceConfig.relaxed()
    
    compatibility_tests = [
        (high_precision, standard, "高精度 vs 标准"),
        (standard, relaxed, "标准 vs 宽松"),
        (high_precision, relaxed, "高精度 vs 宽松")
    ]
    
    for config1, config2, desc in compatibility_tests:
        compatible = config1.is_compatible_with(config2)
        print(f"{desc}: {'兼容' if compatible else '不兼容'}")
    
    # 5. 测试配置缩放
    print("\n=== 配置缩放测试 ===")
    
    base_config = ToleranceConfig.standard()
    print(f"基础配置: {base_config}")
    
    scale_factors = [0.5, 2.0, 10.0]
    for factor in scale_factors:
        scaled_config = base_config.scale(factor)
        print(f"缩放 {factor}x: {scaled_config}")
    
    # 6. 测试容差管理器
    print("\n=== 容差管理器测试 ===")
    
    manager = ToleranceManager()
    
    # 获取预设配置
    standard_preset = manager.get_preset('standard')
    print(f"标准预设: {standard_preset}")
    
    # 添加自定义配置
    custom_name = "我的配置"
    custom_config = ToleranceConfig.custom(position=0.15, similarity_threshold=0.88)
    manager.add_custom_config(custom_name, custom_config)
    
    retrieved_custom = manager.get_custom_config(custom_name)
    print(f"自定义配置: {retrieved_custom}")
    
    # 列出所有配置
    all_configs = manager.list_all_configs()
    print(f"总配置数: {len(all_configs)}")
    
    # 7. 测试配置推荐
    print("\n=== 配置推荐测试 ===")
    
    drawing_types = ['mechanical', 'architectural', 'electrical', 'precision']
    precision_levels = ['high', 'standard', 'low']
    
    for drawing_type in drawing_types:
        print(f"{drawing_type.upper()} 图纸推荐:")
        for precision_level in precision_levels:
            recommended = manager.recommend_config(drawing_type, precision_level)
            print(f"  {precision_level}: {recommended.get_description()}")
    
    # 8. 测试实际应用场景
    print("\n=== 实际应用场景测试 ===")
    
    scenarios = [
        {
            'name': '精密机械零件图',
            'config': ToleranceConfig.ultra_precise(),
            'description': '需要微米级精度'
        },
        {
            'name': '建筑平面图',
            'config': ToleranceConfig.relaxed(),
            'description': '允许较大误差'
        },
        {
            'name': '电路板布局图',
            'config': ToleranceConfig.high_precision(),
            'description': '需要高精度但不是微米级'
        }
    ]
    
    for scenario in scenarios:
        config = scenario['config']
        print(f"{scenario['name']} ({scenario['description']}):")
        print(f"  配置: {config}")
        print(f"  最大搜索范围: {config.max_search_radius}mm")
        print(f"  角度容差: {config.angle * 180 / 3.14159:.1f}°")
    
    print("\n✅ 容差配置系统测试完成!")
    return True

if __name__ == "__main__":
    test_tolerance_config()
