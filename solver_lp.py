# -*- coding: utf-8 -*-
"""
LP（线性规划）求解器
实现简化的生产计划优化问题，去除固定开机成本和0-1决策变量
"""

import pulp
import time
import numpy as np
from config import VERBOSE_SOLVER, TIME_LIMIT

class LPSolver:
    """
    线性规划求解器
    """
    
    def __init__(self, problem_data):
        """
        初始化求解器
        
        参数:
            problem_data: 问题数据字典，包含需求、成本、约束等信息
        """
        self.problem_data = problem_data
        self.T = problem_data['time_periods']
        self.demands = problem_data['demands']
        self.production_costs = problem_data['production_costs']
        self.holding_costs = problem_data['holding_costs']
        self.max_capacities = problem_data['max_capacities']
        self.initial_inventory = problem_data['initial_inventory']
        
        # 求解结果
        self.model = None
        self.solve_time = None
        self.status = None
        self.objective_value = None
        self.solution = None
        
    def build_model(self):
        """
        构建LP数学模型
        """
        print("🔧 正在构建LP模型...")
        
        try:
            # 创建PuLP问题实例
            self.model = pulp.LpProblem("生产计划优化_LP", pulp.LpMinimize)
            
            # 决策变量
            print("  📊 创建决策变量...")
            
            # x[t]: 第t期的生产量（连续变量）
            self.x = {}
            for t in range(self.T):
                self.x[t] = pulp.LpVariable(f"生产量_{t+1}月", 
                                           lowBound=0, 
                                           upBound=self.max_capacities[t],
                                           cat='Continuous')
            
            # s[t]: 第t期期末的库存量（连续变量）
            self.s = {}
            for t in range(self.T):
                self.s[t] = pulp.LpVariable(f"库存量_{t+1}月末", 
                                           lowBound=0, 
                                           cat='Continuous')
            
            print(f"  ✅ 创建了{len(self.x) + len(self.s)}个决策变量")
            
            # 目标函数：最小化总成本（无固定开机成本）
            print("  🎯 设置目标函数...")
            
            # 生产成本
            production_cost = pulp.lpSum([self.production_costs[t] * self.x[t] 
                                        for t in range(self.T)])
            
            # 库存持有成本
            holding_cost = pulp.lpSum([self.holding_costs[t] * self.s[t] 
                                     for t in range(self.T)])
            
            total_cost = production_cost + holding_cost
            self.model += total_cost, "总成本"
            
            print("  ✅ 目标函数设置完成（生产成本 + 库存成本）")
            
            # 约束条件
            print("  ⚖️  添加约束条件...")
            
            # 库存平衡约束：期初库存 + 生产量 = 需求 + 期末库存
            for t in range(self.T):
                if t == 0:
                    # 第一期：初始库存 + 生产量 = 需求 + 期末库存
                    self.model += (self.initial_inventory + self.x[t] == 
                                  self.demands[t] + self.s[t]), f"库存平衡_{t+1}月"
                else:
                    # 其他期：上期期末库存 + 生产量 = 需求 + 期末库存
                    self.model += (self.s[t-1] + self.x[t] == 
                                  self.demands[t] + self.s[t]), f"库存平衡_{t+1}月"
            
            print(f"  ✅ 添加了{self.T}个库存平衡约束")
            
            print("🎉 LP模型构建完成！")
            return True
            
        except Exception as e:
            print(f"❌ 构建LP模型时出错：{e}")
            return False
    
    def solve(self, solver_name='PULP_CBC_CMD'):
        """
        求解LP模型
        
        参数:
            solver_name: 求解器名称
        """
        if not self.model:
            print("❌ 模型尚未构建，请先调用build_model()")
            return False
        
        print(f"🚀 开始求解LP模型（使用{solver_name}求解器）...")
        
        try:
            # 选择求解器
            if solver_name == 'PULP_CBC_CMD':
                solver = pulp.PULP_CBC_CMD(msg=VERBOSE_SOLVER, timeLimit=TIME_LIMIT)
            elif solver_name == 'GUROBI':
                try:
                    solver = pulp.GUROBI(msg=VERBOSE_SOLVER, timeLimit=TIME_LIMIT)
                except:
                    print("⚠️  Gurobi求解器不可用，切换到CBC求解器")
                    solver = pulp.PULP_CBC_CMD(msg=VERBOSE_SOLVER, timeLimit=TIME_LIMIT)
            else:
                solver = pulp.PULP_CBC_CMD(msg=VERBOSE_SOLVER, timeLimit=TIME_LIMIT)
            
            # 记录求解开始时间
            start_time = time.time()
            
            # 求解模型
            self.model.solve(solver)
            
            # 记录求解时间
            self.solve_time = time.time() - start_time
            
            # 检查求解状态
            self.status = pulp.LpStatus[self.model.status]
            
            if self.model.status == pulp.LpStatusOptimal:
                print(f"✅ 求解成功！状态：{self.status}")
                print(f"⏱️  求解时间：{self.solve_time:.3f}秒")
                
                # 提取求解结果
                self.objective_value = pulp.value(self.model.objective)
                print(f"💰 最优总成本：{self.objective_value:.2f}元")
                
                # 提取决策变量的值
                self.solution = self._extract_solution()
                return True
                
            else:
                print(f"❌ 求解失败！状态：{self.status}")
                return False
                
        except Exception as e:
            print(f"❌ 求解过程中出错：{e}")
            return False
    
    def _extract_solution(self):
        """
        提取求解结果
        """
        try:
            solution = {
                'production': [],      # 每期生产量
                'inventory': [],       # 每期期末库存
                'costs': {
                    'production': 0,   # 总生产成本
                    'holding': 0,      # 总库存成本
                    'setup': 0,        # 固定开机成本（LP模型中为0）
                    'total': self.objective_value
                }
            }
            
            total_production_cost = 0
            total_holding_cost = 0
            
            for t in range(self.T):
                # 生产量
                prod_qty = pulp.value(self.x[t])
                solution['production'].append(prod_qty)
                total_production_cost += prod_qty * self.production_costs[t]
                
                # 库存量
                inv_qty = pulp.value(self.s[t])
                solution['inventory'].append(inv_qty)
                total_holding_cost += inv_qty * self.holding_costs[t]
            
            # 更新成本分解
            solution['costs']['production'] = total_production_cost
            solution['costs']['holding'] = total_holding_cost
            solution['costs']['setup'] = 0  # LP模型无开机成本
            
            return solution
            
        except Exception as e:
            print(f"❌ 提取解决方案时出错：{e}")
            return None
    
    def print_solution(self):
        """
        打印详细的求解结果
        """
        if not self.solution:
            print("❌ 无可用的求解结果")
            return
        
        print("\n" + "="*80)
        print("📊 LP模型求解结果")
        print("="*80)
        
        # 基本信息
        print(f"🎯 求解状态：{self.status}")
        print(f"⏱️  求解时间：{self.solve_time:.3f}秒")
        print(f"💰 最优总成本：{self.objective_value:.2f}元")
        
        # 成本分解
        costs = self.solution['costs']
        print(f"\n💸 成本分解：")
        print(f"  生产成本：{costs['production']:.2f}元 ({costs['production']/costs['total']*100:.1f}%)")
        print(f"  库存成本：{costs['holding']:.2f}元 ({costs['holding']/costs['total']*100:.1f}%)")
        print(f"  开机成本：{costs['setup']:.2f}元 (LP模型无开机成本)")
        
        # 详细计划表
        print(f"\n📋 详细生产计划：")
        print("月份\t需求\t生产\t库存\t月成本")
        print("-" * 50)
        
        total_monthly_costs = 0
        for t in range(self.T):
            demand = self.demands[t]
            production = self.solution['production'][t]
            inventory = self.solution['inventory'][t]
            
            # 计算月度成本
            monthly_cost = (production * self.production_costs[t] + 
                           inventory * self.holding_costs[t])
            total_monthly_costs += monthly_cost
            
            print(f"{t+1:2d}\t{demand:4.0f}\t{production:6.1f}\t{inventory:6.1f}\t{monthly_cost:6.0f}")
        
        print("-" * 50)
        print(f"总计\t{sum(self.demands):4.0f}\t{sum(self.solution['production']):6.1f}\t"
              f"{self.solution['inventory'][-1]:6.1f}\t{total_monthly_costs:6.0f}")
        
        # 统计信息
        print(f"\n📈 统计信息：")
        total_demand = sum(self.demands)
        total_production = sum(self.solution['production'])
        max_inventory = max(self.solution['inventory'])
        avg_inventory = np.mean(self.solution['inventory'])
        
        print(f"  总需求量：{total_demand:.0f}件")
        print(f"  总生产量：{total_production:.1f}件")
        print(f"  最大库存：{max_inventory:.1f}件")
        print(f"  平均库存：{avg_inventory:.1f}件")
        print(f"  期末库存：{self.solution['inventory'][-1]:.1f}件")
        
        # LP模型特点分析
        production_periods = sum(1 for p in self.solution['production'] if p > 0.01)
        print(f"  生产期数：{production_periods}个月（{production_periods/self.T*100:.1f}%）")
        print(f"  💡 LP模型特点：无固定开机成本，可以灵活安排生产")
        
        print("="*80)
    
    def get_result_summary(self):
        """
        返回结果摘要（供性能比较使用）
        """
        if not self.solution:
            return None
        
        return {
            'solver_name': 'LP',
            'status': self.status,
            'solve_time': self.solve_time,
            'objective_value': self.objective_value,
            'total_production': sum(self.solution['production']),
            'total_inventory': sum(self.solution['inventory']),
            'production_periods': sum(1 for p in self.solution['production'] if p > 0.01),
            'cost_breakdown': self.solution['costs']
        }


def solve_lp_problem(problem_data, solver_name='PULP_CBC_CMD'):
    """
    便捷函数：求解LP问题
    
    参数:
        problem_data: 问题数据
        solver_name: 求解器名称
    
    返回:
        求解器实例
    """
    solver = LPSolver(problem_data)
    
    if solver.build_model():
        if solver.solve(solver_name):
            return solver
    
    return None


# 测试代码
if __name__ == "__main__":
    from data_generator import DataGenerator
    
    print("🧪 测试LP求解器...")
    
    try:
        # 生成测试数据
        generator = DataGenerator()
        problem_data = generator.generate_problem_instance()
        
        if problem_data:
            print("✅ 测试数据生成成功")
            
            # 求解问题
            solver = solve_lp_problem(problem_data)
            
            if solver:
                solver.print_solution()
                
                # 测试结果摘要
                summary = solver.get_result_summary()
                print(f"\n📄 结果摘要：{summary}")
                print("✅ LP求解器测试成功")
            else:
                print("❌ LP求解失败")
        else:
            print("❌ 无法生成测试数据")
            
    except Exception as e:
        print(f"❌ LP求解器测试出错：{e}")
        import traceback
        traceback.print_exc()