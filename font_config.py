# -*- coding: utf-8 -*-
"""
字体配置模块
自动检测和设置最佳的中文字体
"""

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

def detect_chinese_fonts():
    """
    检测系统中可用的中文字体
    """
    print("🔍 检测系统中的中文字体...")
    
    # 常见的中文字体名称
    chinese_font_names = [
        'Microsoft YaHei',
        'Microsoft JhengHei', 
        'SimHei',
        'SimSun',
        'KaiTi',
        'FangSong',
        'STKaiti',
        'STSong',
        'STFangsong',
        'STHeiti',
        'PingFang SC',
        'Hiragino Sans GB',
        'Source Han Sans CN',
        'Noto Sans CJK SC',
        'WenQuanYi Micro Hei'
    ]
    
    available_fonts = []
    
    # 获取系统字体列表
    system_fonts = [f.name for f in fm.fontManager.ttflist]
    
    # 检查哪些中文字体可用
    for font_name in chinese_font_names:
        if font_name in system_fonts:
            available_fonts.append(font_name)
            print(f"  ✅ 找到字体: {font_name}")
    
    # 如果没找到常见字体，搜索包含中文关键词的字体
    if not available_fonts:
        print("  🔍 搜索其他可能的中文字体...")
        for font in system_fonts:
            if any(keyword in font.lower() for keyword in ['chinese', 'cjk', 'han', 'simhei', 'simsun', 'kaiti', 'fangsong']):
                available_fonts.append(font)
                print(f"  ✅ 找到字体: {font}")
    
    return available_fonts

def configure_chinese_font():
    """
    配置中文字体
    """
    print("⚙️  配置中文字体...")
    
    # 检测可用字体
    available_fonts = detect_chinese_fonts()
    
    if available_fonts:
        # 设置字体优先级，首选最常用的字体
        font_priority = available_fonts + ['DejaVu Sans', 'Arial Unicode MS']
        matplotlib.rcParams['font.sans-serif'] = font_priority
        matplotlib.rcParams['axes.unicode_minus'] = False
        matplotlib.rcParams['font.size'] = 10
        
        print(f"✅ 字体配置完成，使用优先级: {font_priority[:3]}...")
        
        # 验证字体设置
        test_font = matplotlib.rcParams['font.sans-serif'][0]
        print(f"🎯 当前主字体: {test_font}")
        
        return True
    else:
        print("❌ 未找到合适的中文字体")
        
        # 尝试直接指定字体文件路径（Windows系统）
        if platform.system() == "Windows":
            windows_fonts = [
                "C:/Windows/Fonts/msyh.ttc",     # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",   # 黑体
                "C:/Windows/Fonts/simsun.ttc",   # 宋体
                "C:/Windows/Fonts/kaiti.ttf",    # 楷体
            ]
            
            for font_path in windows_fonts:
                if os.path.exists(font_path):
                    try:
                        prop = fm.FontProperties(fname=font_path)
                        matplotlib.rcParams['font.sans-serif'] = [prop.get_name()] + ['DejaVu Sans']
                        matplotlib.rcParams['axes.unicode_minus'] = False
                        print(f"✅ 使用字体文件: {font_path}")
                        return True
                    except Exception as e:
                        print(f"❌ 加载字体文件失败: {e}")
        
        # 如果都失败了，使用基本配置
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False
        print("⚠️  使用默认字体，中文可能显示为方块")
        return False

def create_font_test():
    """
    创建字体测试图表
    """
    print("🧪 创建字体测试图表...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 测试数据
    months = ['1月', '2月', '3月', '4月', '5月', '6月']
    values = [100, 120, 90, 110, 130, 95]
    
    # 创建图表
    bars = ax.bar(months, values, color='lightblue', alpha=0.8)
    
    # 设置标题和标签
    ax.set_title('中文字体测试 - 生产计划图表', fontsize=16, fontweight='bold')
    ax.set_xlabel('月份', fontsize=12)
    ax.set_ylabel('生产量（件）', fontsize=12)
    
    # 添加数值标签
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height}件', ha='center', va='bottom', fontsize=10)
    
    # 添加网格
    ax.grid(True, alpha=0.3)
    
    # 添加说明文字
    ax.text(0.02, 0.98, '如果您能看到这些中文字符，说明字体配置成功！\n如果显示为方块□，则需要安装中文字体。', 
            transform=ax.transAxes, va='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    plt.tight_layout()
    
    # 保存测试图表
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/chinese_font_test.png', dpi=300, bbox_inches='tight')
    print("📁 字体测试图表已保存到: results/chinese_font_test.png")
    
    plt.show()

# 主函数
if __name__ == "__main__":
    print("🚀 开始字体配置...")
    success = configure_chinese_font()
    
    if success:
        create_font_test()
        print("✅ 字体测试完成")
    else:
        print("❌ 字体配置可能存在问题，请检查系统是否安装了中文字体") 