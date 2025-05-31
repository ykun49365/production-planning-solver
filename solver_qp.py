# -*- coding: utf-8 -*-
"""
QP（二次规划）求解器
在LP模型基础上增加生产平滑性的二次惩罚项，避免生产量大幅波动
"""

import cvxpy as cp
import time
import numpy as np
from config import VERBOSE_SOLVER, TIME_LIMIT, SMOOTHNESS_WEIGHT

class QPSolver:
    """
    二次规划求解器
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
        self.smoothness_weight = problem_data.get('smoothness_weight', SMOOTHNESS_WEIGHT)
        
        # 求解结果
        self.x = None  # 生产量变量
        self.s = None  # 库存量变量
        self.problem = None
        self.solve_time = None
        self.status = None
        self.objective_value = None
        self.solution = None
        
    def build_model(self):
        """
        构建QP数学模型
        """
        print("🔧 正在构建QP模型...")
        
        try:
            # 决策变量
            print("  📊 创建决策变量...")
            
            # x[t]: 第t期的生产量（连续变量）
            self.x = cp.Variable(self.T, nonneg=True, name="生产量")
            
            # s[t]: 第t期期末的库存量（连续变量）
            self.s = cp.Variable(self.T, nonneg=True, name="库存量")
            
            print(f"  ✅ 创建了{self.T * 2}个决策变量")
            
            # 目标函数：最小化总成本 + 生产平滑性惩罚
            print("  🎯 设置目标函数...")
            
            # 线性成本：生产成本 + 库存成本
            production_cost = cp.sum(cp.multiply(self.production_costs, self.x))
            holding_cost = cp.sum(cp.multiply(self.holding_costs, self.s))
            
            # 二次惩罚项：生产量变化的平滑性
            if self.T > 1:
                # 计算相邻期间生产量差的平方和
                production_changes = self.x[1:] - self.x[:-1]
                smoothness_penalty = self.smoothness_weight * cp.sum_squares(production_changes)
            else:
                smoothness_penalty = 0
            
            total_cost = production_cost + holding_cost + smoothness_penalty
            
            print(f"  ✅ 目标函数设置完成（生产成本 + 库存成本 + 平滑性惩罚，权重={self.smoothness_weight}）")
            
            # 约束条件
            print("  ⚖️  添加约束条件...")
            
            constraints = []
            
            # 1. 库存平衡约束
            for t in range(self.T):
                if t == 0:
                    # 第一期：初始库存 + 生产量 = 需求 + 期末库存
                    constraints.append(
                        self.initial_inventory + self.x[t] == self.demands[t] + self.s[t]
                    )
                else:
                    # 其他期：上期期末库存 + 生产量 = 需求 + 期末库存
                    constraints.append(
                        self.s[t-1] + self.x[t] == self.demands[t] + self.s[t]
                    )
            
            # 2. 产能约束
            for t in range(self.T):
                constraints.append(self.x[t] <= self.max_capacities[t])
            
            print(f"  ✅ 添加了{len(constraints)}个约束条件")
            
            # 创建优化问题
            self.problem = cp.Problem(cp.Minimize(total_cost), constraints)
            
            print("🎉 QP模型构建完成！")
            return True
            
        except Exception as e:
            print(f"❌ 构建QP模型时出错：{e}")
            return False
    
    def solve(self, solver_name='CLARABEL'):
        """
        求解QP模型
        
        参数:
            solver_name: 求解器名称（CLARABEL, OSQP, SCS等）
        """
        if not self.problem:
            print("❌ 模型尚未构建，请先调用build_model()")
            return False
        
        print(f"🚀 开始求解QP模型（使用{solver_name}求解器）...")
        
        try:
            # 记录求解开始时间
            start_time = time.time()
            
            # 求解模型
            if solver_name == 'CLARABEL':
                self.problem.solve(solver=cp.CLARABEL, verbose=VERBOSE_SOLVER)
            elif solver_name == 'OSQP':
                self.problem.solve(solver=cp.OSQP, verbose=VERBOSE_SOLVER)
            elif solver_name == 'SCS':
                self.problem.solve(solver=cp.SCS, verbose=VERBOSE_SOLVER)
            else:
                # 默认求解器
                self.problem.solve(verbose=VERBOSE_SOLVER)
            
            # 记录求解时间
            self.solve_time = time.time() - start_time
            
            # 检查求解状态
            self.status = self.problem.status
            
            if self.problem.status == cp.OPTIMAL:
                print(f"✅ 求解成功！状态：{self.status}")
                print(f"⏱️  求解时间：{self.solve_time:.3f}秒")
                
                # 提取求解结果
                self.objective_value = self.problem.value
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
                    'setup': 0,        # 固定开机成本（QP模型中为0）
                    'smoothness': 0,   # 平滑性惩罚成本
                    'total': self.objective_value
                }
            }
            
            # 提取生产量和库存量
            production_values = self.x.value
            inventory_values = self.s.value
            
            total_production_cost = 0
            total_holding_cost = 0
            
            for t in range(self.T):
                # 生产量
                prod_qty = production_values[t]
                solution['production'].append(prod_qty)
                total_production_cost += prod_qty * self.production_costs[t]
                
                # 库存量
                inv_qty = inventory_values[t]
                solution['inventory'].append(inv_qty)
                total_holding_cost += inv_qty * self.holding_costs[t]
            
            # 计算平滑性惩罚成本
            smoothness_cost = 0
            if self.T > 1:
                for t in range(1, self.T):
                    diff = production_values[t] - production_values[t-1]
                    smoothness_cost += self.smoothness_weight * diff * diff
            
            # 更新成本分解
            solution['costs']['production'] = total_production_cost
            solution['costs']['holding'] = total_holding_cost
            solution['costs']['setup'] = 0  # QP模型无开机成本
            solution['costs']['smoothness'] = smoothness_cost
            
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
        print("📊 QP模型求解结果")
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
        print(f"  平滑惩罚：{costs['smoothness']:.2f}元 ({costs['smoothness']/costs['total']*100:.1f}%)")
        print(f"  开机成本：{costs['setup']:.2f}元 (QP模型无开机成本)")
        
        # 详细计划表
        print(f"\n📋 详细生产计划：")
        print("月份\t需求\t生产\t库存\t生产变化\t月成本")
        print("-" * 60)
        
        total_monthly_costs = 0
        for t in range(self.T):
            demand = self.demands[t]
            production = self.solution['production'][t]
            inventory = self.solution['inventory'][t]
            
            # 计算生产变化
            if t == 0:
                production_change = 0
            else:
                production_change = production - self.solution['production'][t-1]
            
            # 计算月度成本
            monthly_cost = (production * self.production_costs[t] + 
                           inventory * self.holding_costs[t])
            total_monthly_costs += monthly_cost
            
            print(f"{t+1:2d}\t{demand:4.0f}\t{production:6.1f}\t{inventory:6.1f}\t{production_change:8.1f}\t{monthly_cost:6.0f}")
        
        print("-" * 60)
        print(f"总计\t{sum(self.demands):4.0f}\t{sum(self.solution['production']):6.1f}\t"
              f"{self.solution['inventory'][-1]:6.1f}\t    -    \t{total_monthly_costs:6.0f}")
        
        # 统计信息
        print(f"\n📈 统计信息：")
        total_demand = sum(self.demands)
        total_production = sum(self.solution['production'])
        max_inventory = max(self.solution['inventory'])
        avg_inventory = np.mean(self.solution['inventory'])
        
        # 计算生产变化的标准差（衡量平滑性）
        production_changes = [self.solution['production'][t] - self.solution['production'][t-1] 
                             for t in range(1, self.T)]
        production_volatility = np.std(production_changes) if production_changes else 0
        
        print(f"  总需求量：{total_demand:.0f}件")
        print(f"  总生产量：{total_production:.1f}件")
        print(f"  最大库存：{max_inventory:.1f}件")
        print(f"  平均库存：{avg_inventory:.1f}件")
        print(f"  期末库存：{self.solution['inventory'][-1]:.1f}件")
        print(f"  生产波动性：{production_volatility:.1f}件（标准差）")
        print(f"  💡 QP模型特点：通过二次惩罚项实现生产平滑化")
        
        print("="*80)
    
    def get_result_summary(self):
        """
        返回结果摘要（供性能比较使用）
        """
        if not self.solution:
            return None
        
        return {
            'solver_name': 'QP',
            'status': self.status,
            'solve_time': self.solve_time,
            'objective_value': self.objective_value,
            'total_production': sum(self.solution['production']),
            'total_inventory': sum(self.solution['inventory']),
            'production_volatility': np.std([self.solution['production'][t] - self.solution['production'][t-1] 
                                           for t in range(1, self.T)]),
            'cost_breakdown': self.solution['costs']
        }


def solve_qp_problem(problem_data, solver_name='CLARABEL'):
    """
    便捷函数：求解QP问题
    
    参数:
        problem_data: 问题数据
        solver_name: 求解器名称
    
    返回:
        求解器实例
    """
    solver = QPSolver(problem_data)
    
    if solver.build_model():
        if solver.solve(solver_name):
            return solver
    
    return None


# 测试代码
if __name__ == "__main__":
    from data_generator import DataGenerator
    
    print("🧪 测试QP求解器...")
    
    try:
        # 生成测试数据
        generator = DataGenerator()
        problem_data = generator.generate_problem_instance()
        
        if problem_data:
            print("✅ 测试数据生成成功")
            
            # 求解问题
            solver = solve_qp_problem(problem_data)
            
            if solver:
                solver.print_solution()
                
                # 测试结果摘要
                summary = solver.get_result_summary()
                print(f"\n📄 结果摘要：{summary}")
                print("✅ QP求解器测试成功")
            else:
                print("❌ QP求解失败")
        else:
            print("❌ 无法生成测试数据")
            
    except Exception as e:
        print(f"❌ QP求解器测试出错：{e}")
        import traceback
        traceback.print_exc() 