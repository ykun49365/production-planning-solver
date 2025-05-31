# -*- coding: utf-8 -*-
"""
NLP（非线性规划）求解器
包含非线性的生产成本函数，考虑生产效率随产量的非线性变化
"""

import numpy as np
import time
from scipy.optimize import minimize
from config import VERBOSE_SOLVER, TIME_LIMIT, NL_COST_COEFFICIENT

class NLPSolver:
    """
    非线性规划求解器
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
        self.nl_cost_coeff = problem_data.get('nl_cost_coefficient', NL_COST_COEFFICIENT)
        
        # 求解结果
        self.solve_time = None
        self.status = None
        self.objective_value = None
        self.solution = None
        self.optimization_result = None
        
    def _objective_function(self, x):
        """
        目标函数：非线性总成本
        
        参数:
            x: 决策变量向量 [生产量1, 生产量2, ..., 生产量T, 库存量1, 库存量2, ..., 库存量T]
        """
        try:
            # 分离决策变量
            production = x[:self.T]
            inventory = x[self.T:]
            
            total_cost = 0
            
            # 非线性生产成本：基础成本 + 非线性增量成本
            for t in range(self.T):
                if production[t] > 0:
                    # 非线性成本函数：cost = linear_cost * x + nl_coeff * x^1.2
                    linear_cost = self.production_costs[t] * production[t]
                    nonlinear_cost = self.nl_cost_coeff * (production[t] ** 1.2)
                    total_cost += linear_cost + nonlinear_cost
            
            # 线性库存成本
            for t in range(self.T):
                total_cost += self.holding_costs[t] * inventory[t]
            
            return total_cost
            
        except Exception as e:
            print(f"❌ 目标函数计算出错：{e}")
            return 1e10  # 返回大值表示不可行
    
    def _constraint_functions(self, x):
        """
        约束函数
        
        参数:
            x: 决策变量向量
            
        返回:
            约束违反量列表（<=0表示满足约束）
        """
        try:
            production = x[:self.T]
            inventory = x[self.T:]
            
            constraints = []
            
            # 1. 库存平衡约束
            for t in range(self.T):
                if t == 0:
                    # 第一期：初始库存 + 生产量 - 需求 - 期末库存 = 0
                    balance = self.initial_inventory + production[t] - self.demands[t] - inventory[t]
                else:
                    # 其他期：上期期末库存 + 生产量 - 需求 - 期末库存 = 0
                    balance = inventory[t-1] + production[t] - self.demands[t] - inventory[t]
                
                # 转换为不等式约束：|balance| <= 0，即 balance^2 <= 0
                constraints.append(balance * balance)
            
            # 2. 产能约束：生产量 <= 最大产能
            for t in range(self.T):
                constraints.append(production[t] - self.max_capacities[t])
            
            # 3. 非负约束：生产量 >= 0, 库存量 >= 0
            for t in range(self.T):
                constraints.append(-production[t])  # production[t] >= 0
                constraints.append(-inventory[t])   # inventory[t] >= 0
            
            return np.array(constraints)
            
        except Exception as e:
            print(f"❌ 约束函数计算出错：{e}")
            return np.array([1e10] * (4 * self.T))  # 返回大值表示约束违反
    
    def solve(self, method='SLSQP'):
        """
        求解NLP模型
        
        参数:
            method: 优化方法（SLSQP, COBYLA等）
        """
        print(f"🚀 开始求解NLP模型（使用{method}方法）...")
        
        try:
            # 初始解：简单的平均分配策略
            print("  🎯 设置初始解...")
            total_demand = sum(self.demands)
            avg_production = total_demand / self.T
            
            # 初始生产量：平均值
            initial_production = [min(avg_production, self.max_capacities[t]) for t in range(self.T)]
            
            # 初始库存量：简单计算
            initial_inventory = []
            current_inv = self.initial_inventory
            for t in range(self.T):
                current_inv = current_inv + initial_production[t] - self.demands[t]
                initial_inventory.append(max(0, current_inv))
            
            # 组合初始解
            x0 = np.array(initial_production + initial_inventory)
            
            print(f"  ✅ 初始解设置完成，变量数量：{len(x0)}")
            
            # 设置变量边界
            bounds = []
            # 生产量边界：[0, 最大产能]
            for t in range(self.T):
                bounds.append((0, self.max_capacities[t]))
            # 库存量边界：[0, 无穷大]
            for t in range(self.T):
                bounds.append((0, None))
            
            # 约束条件
            constraints = {
                'type': 'eq',
                'fun': lambda x: self._equality_constraints(x)
            }
            
            # 记录求解开始时间
            start_time = time.time()
            
            # 求解优化问题
            print("  🔄 开始优化计算...")
            result = minimize(
                fun=self._objective_function,
                x0=x0,
                method=method,
                bounds=bounds,
                constraints=constraints,
                options={
                    'disp': VERBOSE_SOLVER,
                    'maxiter': 1000,
                    'ftol': 1e-6
                }
            )
            
            # 记录求解时间
            self.solve_time = time.time() - start_time
            self.optimization_result = result
            
            # 检查求解状态
            if result.success:
                self.status = "Optimal"
                print(f"✅ 求解成功！状态：{self.status}")
                print(f"⏱️  求解时间：{self.solve_time:.3f}秒")
                
                # 提取求解结果
                self.objective_value = result.fun
                print(f"💰 最优总成本：{self.objective_value:.2f}元")
                
                # 提取决策变量的值
                self.solution = self._extract_solution(result.x)
                return True
                
            else:
                self.status = "Failed"
                print(f"❌ 求解失败！状态：{self.status}")
                print(f"失败原因：{result.message}")
                return False
                
        except Exception as e:
            print(f"❌ 求解过程中出错：{e}")
            return False
    
    def _equality_constraints(self, x):
        """
        等式约束：库存平衡约束
        """
        production = x[:self.T]
        inventory = x[self.T:]
        
        constraints = []
        
        for t in range(self.T):
            if t == 0:
                balance = self.initial_inventory + production[t] - self.demands[t] - inventory[t]
            else:
                balance = inventory[t-1] + production[t] - self.demands[t] - inventory[t]
            constraints.append(balance)
        
        return np.array(constraints)
    
    def _extract_solution(self, x):
        """
        提取求解结果
        """
        try:
            production = x[:self.T]
            inventory = x[self.T:]
            
            solution = {
                'production': list(production),
                'inventory': list(inventory),
                'costs': {
                    'production': 0,
                    'nonlinear': 0,
                    'holding': 0,
                    'setup': 0,  # NLP模型无开机成本
                    'total': self.objective_value
                }
            }
            
            # 计算成本分解
            total_linear_cost = 0
            total_nonlinear_cost = 0
            total_holding_cost = 0
            
            for t in range(self.T):
                # 线性生产成本
                linear_cost = self.production_costs[t] * production[t]
                total_linear_cost += linear_cost
                
                # 非线性生产成本
                if production[t] > 0:
                    nonlinear_cost = self.nl_cost_coeff * (production[t] ** 1.2)
                    total_nonlinear_cost += nonlinear_cost
                
                # 库存成本
                holding_cost = self.holding_costs[t] * inventory[t]
                total_holding_cost += holding_cost
            
            solution['costs']['production'] = total_linear_cost
            solution['costs']['nonlinear'] = total_nonlinear_cost
            solution['costs']['holding'] = total_holding_cost
            
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
        print("📊 NLP模型求解结果")
        print("="*80)
        
        # 基本信息
        print(f"🎯 求解状态：{self.status}")
        print(f"⏱️  求解时间：{self.solve_time:.3f}秒")
        print(f"💰 最优总成本：{self.objective_value:.2f}元")
        
        if self.optimization_result:
            print(f"🔢 迭代次数：{self.optimization_result.get('nit', '未知')}")
            print(f"📈 函数评估次数：{self.optimization_result.get('nfev', '未知')}")
        
        # 成本分解
        costs = self.solution['costs']
        print(f"\n💸 成本分解：")
        print(f"  线性生产成本：{costs['production']:.2f}元 ({costs['production']/costs['total']*100:.1f}%)")
        print(f"  非线性成本：{costs['nonlinear']:.2f}元 ({costs['nonlinear']/costs['total']*100:.1f}%)")
        print(f"  库存成本：{costs['holding']:.2f}元 ({costs['holding']/costs['total']*100:.1f}%)")
        print(f"  开机成本：{costs['setup']:.2f}元 (NLP模型无开机成本)")
        
        # 详细计划表
        print(f"\n📋 详细生产计划：")
        print("月份\t需求\t生产\t库存\t线性成本\t非线性成本\t月成本")
        print("-" * 70)
        
        total_monthly_costs = 0
        for t in range(self.T):
            demand = self.demands[t]
            production = self.solution['production'][t]
            inventory = self.solution['inventory'][t]
            
            # 计算月度成本
            linear_cost = self.production_costs[t] * production
            nonlinear_cost = self.nl_cost_coeff * (production ** 1.2) if production > 0 else 0
            holding_cost = self.holding_costs[t] * inventory
            monthly_cost = linear_cost + nonlinear_cost + holding_cost
            total_monthly_costs += monthly_cost
            
            print(f"{t+1:2d}\t{demand:4.0f}\t{production:6.1f}\t{inventory:6.1f}\t{linear_cost:8.0f}\t{nonlinear_cost:10.1f}\t{monthly_cost:6.0f}")
        
        print("-" * 70)
        print(f"总计\t{sum(self.demands):4.0f}\t{sum(self.solution['production']):6.1f}\t"
              f"{self.solution['inventory'][-1]:6.1f}\t{costs['production']:8.0f}\t{costs['nonlinear']:10.1f}\t{total_monthly_costs:6.0f}")
        
        # 统计信息
        print(f"\n📈 统计信息：")
        total_demand = sum(self.demands)
        total_production = sum(self.solution['production'])
        max_inventory = max(self.solution['inventory'])
        avg_inventory = np.mean(self.solution['inventory'])
        max_production = max(self.solution['production'])
        
        print(f"  总需求量：{total_demand:.0f}件")
        print(f"  总生产量：{total_production:.1f}件")
        print(f"  最大生产量：{max_production:.1f}件/月")
        print(f"  最大库存：{max_inventory:.1f}件")
        print(f"  平均库存：{avg_inventory:.1f}件")
        print(f"  期末库存：{self.solution['inventory'][-1]:.1f}件")
        print(f"  非线性成本占比：{costs['nonlinear']/costs['total']*100:.1f}%")
        print(f"  💡 NLP模型特点：考虑生产规模效应的非线性成本")
        
        print("="*80)
    
    def get_result_summary(self):
        """
        返回结果摘要（供性能比较使用）
        """
        if not self.solution:
            return None
        
        return {
            'solver_name': 'NLP',
            'status': self.status,
            'solve_time': self.solve_time,
            'objective_value': self.objective_value,
            'total_production': sum(self.solution['production']),
            'total_inventory': sum(self.solution['inventory']),
            'max_production': max(self.solution['production']),
            'nonlinear_cost_ratio': self.solution['costs']['nonlinear'] / self.objective_value,
            'cost_breakdown': self.solution['costs']
        }


def solve_nlp_problem(problem_data, method='SLSQP'):
    """
    便捷函数：求解NLP问题
    
    参数:
        problem_data: 问题数据
        method: 优化方法
    
    返回:
        求解器实例
    """
    solver = NLPSolver(problem_data)
    
    if solver.solve(method):
        return solver
    
    return None


# 测试代码
if __name__ == "__main__":
    from data_generator import DataGenerator
    
    print("🧪 测试NLP求解器...")
    
    try:
        # 生成测试数据
        generator = DataGenerator()
        problem_data = generator.generate_problem_instance()
        
        if problem_data:
            print("✅ 测试数据生成成功")
            
            # 求解问题
            solver = solve_nlp_problem(problem_data)
            
            if solver:
                solver.print_solution()
                
                # 测试结果摘要
                summary = solver.get_result_summary()
                print(f"\n📄 结果摘要：{summary}")
                print("✅ NLP求解器测试成功")
            else:
                print("❌ NLP求解失败")
        else:
            print("❌ 无法生成测试数据")
            
    except Exception as e:
        print(f"❌ NLP求解器测试出错：{e}")
        import traceback
        traceback.print_exc() 