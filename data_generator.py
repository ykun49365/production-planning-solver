# -*- coding: utf-8 -*-
"""
数据生成器模块
负责生成生产计划优化问题的测试数据
"""

import random
import numpy as np
from config import *

class DataGenerator:
    """
    生产计划优化问题的数据生成器
    """
    
    def __init__(self):
        """初始化数据生成器"""
        self.time_periods = TIME_PERIODS
        self.demands = None
        self.setup_costs = None
        self.production_costs = None
        self.holding_costs = None
        
    def generate_demands(self):
        """
        生成需求数据
        根据配置决定使用手动设置还是自动生成
        """
        try:
            if AUTO_GENERATE_DEMANDS:
                print(f"🎲 自动生成{self.time_periods}个月的需求数据...")
                # 使用随机数生成需求，但保证有一定的季节性模式
                base_demands = []
                for t in range(self.time_periods):
                    # 添加季节性变化：年中和年末需求较高
                    seasonal_factor = 1.0
                    if t % 12 in [5, 6, 10, 11]:  # 6月、7月、11月、12月
                        seasonal_factor = 1.2
                    elif t % 12 in [1, 2]:  # 2月、3月
                        seasonal_factor = 0.9
                    
                    base_demand = random.randint(DEMAND_MIN, DEMAND_MAX)
                    seasonal_demand = int(base_demand * seasonal_factor)
                    base_demands.append(seasonal_demand)
                
                self.demands = base_demands
                print(f"✅ 自动生成的需求：{self.demands}")
            else:
                print(f"📋 使用手动设置的需求数据...")
                if len(MONTHLY_DEMANDS) != self.time_periods:
                    raise ValueError(f"手动设置的需求数量({len(MONTHLY_DEMANDS)})与时间周期数({self.time_periods})不匹配")
                self.demands = MONTHLY_DEMANDS.copy()
                print(f"✅ 手动设置的需求：{self.demands}")
            
            return self.demands
            
        except Exception as e:
            print(f"❌ 生成需求数据时出错：{e}")
            # 使用默认需求
            self.demands = [100] * self.time_periods
            print(f"🔧 使用默认需求：{self.demands}")
            return self.demands
    
    def generate_cost_parameters(self):
        """
        生成成本参数
        """
        try:
            print("💰 设置成本参数...")
            
            # 生产成本（每个时期可能不同，但这里使用统一值）
            self.production_costs = [PRODUCTION_COST] * self.time_periods
            
            # 库存持有成本
            self.holding_costs = [HOLDING_COST] * self.time_periods
            
            # 固定开机成本
            self.setup_costs = [SETUP_COST] * self.time_periods
            
            print(f"✅ 生产成本: {PRODUCTION_COST}元/件")
            print(f"✅ 库存成本: {HOLDING_COST}元/件/月")
            print(f"✅ 开机成本: {SETUP_COST}元/次")
            
            return {
                'production_costs': self.production_costs,
                'holding_costs': self.holding_costs,
                'setup_costs': self.setup_costs
            }
            
        except Exception as e:
            print(f"❌ 生成成本参数时出错：{e}")
            return None
    
    def generate_capacity_constraints(self):
        """
        生成产能约束
        """
        try:
            print("🏭 设置产能约束...")
            
            # 每月最大产能（可以设为不同值，这里使用统一值）
            max_capacities = [MAX_CAPACITY] * self.time_periods
            
            print(f"✅ 最大产能: {MAX_CAPACITY}件/月")
            
            return max_capacities
            
        except Exception as e:
            print(f"❌ 生成产能约束时出错：{e}")
            return [200] * self.time_periods  # 默认值
    
    def generate_problem_instance(self):
        """
        生成完整的问题实例
        返回包含所有必要数据的字典
        """
        print("="*50)
        print("🚀 正在生成生产计划优化问题实例...")
        print("="*50)
        
        try:
            # 验证配置
            validation_errors = validate_config()
            if validation_errors:
                print("❌ 配置验证失败：")
                for error in validation_errors:
                    print(f"  - {error}")
                raise ValueError("配置文件存在错误")
            
            problem_data = {
                'time_periods': self.time_periods,
                'demands': self.generate_demands(),
                'initial_inventory': INITIAL_INVENTORY,
                'max_capacities': self.generate_capacity_constraints(),
                **self.generate_cost_parameters()
            }
            
            # 添加其他参数
            problem_data.update({
                'smoothness_weight': SMOOTHNESS_WEIGHT,
                'nl_cost_coefficient': NL_COST_COEFFICIENT
            })
            
            print("="*50)
            print("✅ 问题实例生成完成！")
            print("="*50)
            print(f"📊 问题规模：{self.time_periods}个时期")
            print(f"📈 总需求量：{sum(self.demands)}件")
            print(f"📉 平均需求：{sum(self.demands)/len(self.demands):.1f}件/月")
            print(f"🏭 产能利用率：{sum(self.demands)/(self.time_periods*MAX_CAPACITY)*100:.1f}%")
            
            return problem_data
            
        except Exception as e:
            print(f"❌ 生成问题实例时出错：{e}")
            return None
    
    def create_test_scenarios(self, num_scenarios=3):
        """
        创建多个测试场景，用于性能比较
        """
        global TIME_PERIODS  # 将global声明移到函数开头
        
        print(f"🎯 创建{num_scenarios}个测试场景...")
        
        scenarios = []
        original_time_periods = TIME_PERIODS
        
        try:
            # 场景1：小规模问题（6个月）
            TIME_PERIODS = 6
            self.time_periods = 6
            scenario1 = self.generate_problem_instance()
            scenario1['name'] = "小规模问题(6个月)"
            scenarios.append(scenario1)
            
            # 场景2：中等规模问题（12个月）
            TIME_PERIODS = 12
            self.time_periods = 12
            scenario2 = self.generate_problem_instance()
            scenario2['name'] = "中等规模问题(12个月)"
            scenarios.append(scenario2)
            
            # 场景3：大规模问题（24个月）
            if num_scenarios >= 3:
                TIME_PERIODS = 24
                self.time_periods = 24
                scenario3 = self.generate_problem_instance()
                scenario3['name'] = "大规模问题(24个月)"
                scenarios.append(scenario3)
            
        except Exception as e:
            print(f"❌ 创建测试场景时出错：{e}")
        finally:
            # 恢复原始设置
            TIME_PERIODS = original_time_periods
            self.time_periods = original_time_periods
        
        print(f"✅ 成功创建{len(scenarios)}个测试场景")
        return scenarios
    
    def print_problem_summary(self, problem_data):
        """
        打印问题摘要信息
        """
        if not problem_data:
            print("❌ 无效的问题数据")
            return
        
        print("\n" + "="*60)
        print("📋 生产计划优化问题摘要")
        print("="*60)
        
        print(f"⏰ 规划周期：{problem_data['time_periods']}个月")
        print(f"📦 初始库存：{problem_data['initial_inventory']}件")
        print(f"🏭 月产能：{problem_data['max_capacities'][0]}件")
        
        print("\n📊 需求分析：")
        demands = problem_data['demands']
        print(f"  总需求：{sum(demands)}件")
        print(f"  平均需求：{np.mean(demands):.1f}件/月")
        print(f"  需求范围：{min(demands)} - {max(demands)}件")
        print(f"  需求变异系数：{np.std(demands)/np.mean(demands):.2f}")
        
        print("\n💰 成本结构：")
        print(f"  生产成本：{problem_data['production_costs'][0]}元/件")
        print(f"  库存成本：{problem_data['holding_costs'][0]}元/件/月") 
        print(f"  开机成本：{problem_data['setup_costs'][0]}元/次")
        
        # 简单的成本预估
        total_demand = sum(demands)
        min_production_cost = total_demand * problem_data['production_costs'][0]
        max_setup_cost = len(demands) * problem_data['setup_costs'][0]
        
        print(f"\n💡 成本预估：")
        print(f"  最低生产成本：{min_production_cost}元（满足所有需求）")
        print(f"  最高开机成本：{max_setup_cost}元（每月都开机）")
        print(f"  预估总成本范围：{min_production_cost + max_setup_cost//2} - {min_production_cost + max_setup_cost}元")
        
        print("="*60)


# 测试代码
if __name__ == "__main__":
    # 创建数据生成器并测试
    generator = DataGenerator()
    
    # 生成单个问题实例
    problem = generator.generate_problem_instance()
    if problem:
        generator.print_problem_summary(problem)
    
    # 测试多场景生成
    print("\n" + "="*50)
    print("测试多场景生成...")
    scenarios = generator.create_test_scenarios(3)
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n场景{i}: {scenario['name']}")
        print(f"  时期数：{scenario['time_periods']}")
        print(f"  总需求：{sum(scenario['demands'])}") 