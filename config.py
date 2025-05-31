# -*- coding: utf-8 -*-
"""
生产计划优化问题配置文件
包含所有重要的参数设置，用户可以通过修改这些参数来调整问题规模和成本
"""

# ====================
# 基本问题参数
# ====================

# 规划时间周期数（月份数）
TIME_PERIODS = 12

# 每月需求量（单位：件）
# 可以手动设置每月需求，或者使用自动生成
MONTHLY_DEMANDS = [
    100, 120, 90, 110, 130, 95,   # 前6个月
    140, 125, 105, 115, 135, 160  # 后6个月
]

# 如果想自动生成需求，设置为True
AUTO_GENERATE_DEMANDS = False
DEMAND_MIN = 80   # 最小需求量
DEMAND_MAX = 160  # 最大需求量

# ====================
# 成本参数
# ====================

# 单位生产成本（元/件）
PRODUCTION_COST = 10.0

# 单位库存持有成本（元/件/月）
HOLDING_COST = 2.0

# 固定开机成本（元/次）- 每月如果生产就要支付
SETUP_COST = 500.0

# ====================
# 生产约束
# ====================

# 最大产能（件/月）
MAX_CAPACITY = 200

# 初始库存量（件）
INITIAL_INVENTORY = 0

# ====================
# 二次规划模型参数
# ====================

# 生产平滑性权重参数（用于QP模型）
# 数值越大，生产量变化越平滑
SMOOTHNESS_WEIGHT = 0.1

# ====================
# 非线性规划模型参数
# ====================

# 非线性生产成本系数（用于NLP模型）
# 生产成本 = PRODUCTION_COST * x + NL_COST_COEFF * x^1.2
NL_COST_COEFFICIENT = 0.05

# ====================
# 求解器设置
# ====================

# 要测试的求解器列表
# 可选：'PULP_CBC', 'CVXPY', 'GUROBI'
SOLVERS_TO_TEST = ['PULP_CBC', 'CVXPY']

# 求解时间限制（秒）
TIME_LIMIT = 300

# 是否显示求解器详细输出
VERBOSE_SOLVER = False

# ====================
# 输出设置
# ====================

# 是否生成图表
GENERATE_PLOTS = True

# 是否保存结果到文件
SAVE_RESULTS = True

# 结果输出目录
OUTPUT_DIR = "results"

# ====================
# 验证参数有效性
# ====================

def validate_config():
    """
    验证配置参数的有效性
    """
    errors = []
    
    # 检查时间周期
    if TIME_PERIODS <= 0:
        errors.append("时间周期数必须大于0")
    
    # 检查需求量设置
    if not AUTO_GENERATE_DEMANDS:
        if len(MONTHLY_DEMANDS) != TIME_PERIODS:
            errors.append(f"手动设置的需求量数量({len(MONTHLY_DEMANDS)})必须等于时间周期数({TIME_PERIODS})")
        if any(d <= 0 for d in MONTHLY_DEMANDS):
            errors.append("所有需求量必须大于0")
    else:
        if DEMAND_MIN <= 0 or DEMAND_MAX <= 0:
            errors.append("自动生成需求的最小值和最大值必须大于0")
        if DEMAND_MIN >= DEMAND_MAX:
            errors.append("需求最小值必须小于最大值")
    
    # 检查成本参数
    if PRODUCTION_COST <= 0:
        errors.append("生产成本必须大于0")
    if HOLDING_COST < 0:
        errors.append("库存成本不能为负数")
    if SETUP_COST < 0:
        errors.append("开机成本不能为负数")
    
    # 检查生产约束
    if MAX_CAPACITY <= 0:
        errors.append("最大产能必须大于0")
    if INITIAL_INVENTORY < 0:
        errors.append("初始库存不能为负数")
    
    # 检查其他参数
    if SMOOTHNESS_WEIGHT < 0:
        errors.append("平滑性权重不能为负数")
    if NL_COST_COEFFICIENT < 0:
        errors.append("非线性成本系数不能为负数")
    
    return errors

# 在导入时自动验证配置
if __name__ == "__main__":
    # 只有直接运行这个文件时才进行验证
    validation_errors = validate_config()
    if validation_errors:
        print("配置文件存在以下错误：")
        for error in validation_errors:
            print(f"- {error}")
    else:
        print("配置文件验证通过！")
        print(f"规划周期：{TIME_PERIODS}个月")
        print(f"需求模式：{'自动生成' if AUTO_GENERATE_DEMANDS else '手动设置'}")
        print(f"生产成本：{PRODUCTION_COST}元/件")
        print(f"库存成本：{HOLDING_COST}元/件/月")
        print(f"开机成本：{SETUP_COST}元/次")
        print(f"最大产能：{MAX_CAPACITY}件/月") 