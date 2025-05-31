# -*- coding: utf-8 -*-
"""
可视化工具模块
用于生成生产计划优化结果的图表和可视化分析
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os
from datetime import datetime

# 使用字体配置模块
try:
    from font_config import configure_chinese_font
    configure_chinese_font()
except ImportError:
    # 如果没有字体配置模块，使用默认设置
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False

# 设置seaborn样式
sns.set_style("whitegrid")
try:
    plt.style.use('seaborn-v0_8')
except:
    plt.style.use('seaborn')

class ProductionPlanVisualizer:
    """
    生产计划可视化器
    """
    
    def __init__(self):
        """初始化可视化器"""
        self.color_palette = {
            'production': '#3498db',    # 蓝色
            'demand': '#e74c3c',        # 红色  
            'inventory': '#2ecc71',     # 绿色
            'setup': '#f39c12',         # 橙色
            'cost': '#9b59b6'           # 紫色
        }
        
    def plot_production_plan(self, problem_data, solution, solver_name="", save_plot=True, output_dir="results"):
        """
        绘制生产计划图表
        
        参数:
            problem_data: 问题数据
            solution: 求解结果
            solver_name: 求解器名称
            save_plot: 是否保存图表
            output_dir: 输出目录
        """
        if not solution:
            print("❌ 无有效的求解结果")
            return
        
        print(f"📊 生成{solver_name}求解结果可视化图表...")
        
        # 准备数据
        periods = list(range(1, problem_data['time_periods'] + 1))
        demands = problem_data['demands']
        production = solution['production']
        inventory = solution['inventory']
        
        # 创建图表
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle(f'{solver_name} Production Plan Optimization Results', fontsize=16, fontweight='bold')
        
        # 1. 生产量与需求对比
        ax1 = axes[0, 0]
        width = 0.35
        x = np.arange(len(periods))
        
        bars1 = ax1.bar(x - width/2, production, width, 
                       label='Production', color=self.color_palette['production'], alpha=0.8)
        bars2 = ax1.bar(x + width/2, demands, width,
                       label='Demand', color=self.color_palette['demand'], alpha=0.8)
        
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Quantity')
        ax1.set_title('Production vs Demand')
        ax1.set_xticks(x)
        ax1.set_xticklabels(periods)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}', ha='center', va='bottom', fontsize=8)
        
        # 2. 库存水平变化
        ax2 = axes[0, 1]
        ax2.plot(periods, inventory, 'o-', color=self.color_palette['inventory'], 
                linewidth=3, markersize=8, label='End Inventory')
        ax2.fill_between(periods, inventory, alpha=0.3, color=self.color_palette['inventory'])
        
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Inventory Level')
        ax2.set_title('Inventory Level Changes')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 添加数值标签
        for i, inv in enumerate(inventory):
            ax2.text(periods[i], inv + max(inventory)*0.02, f'{inv:.0f}', 
                    ha='center', va='bottom', fontsize=8)
        
        # 3. 开机状态（如果有的话）
        ax3 = axes[1, 0]
        if 'setup' in solution:
            setup_status = solution['setup']
            colors = [self.color_palette['setup'] if s else '#bdc3c7' for s in setup_status]
            bars3 = ax3.bar(periods, [1]*len(periods), color=colors, alpha=0.8)
            
            ax3.set_xlabel('Period')
            ax3.set_ylabel('Setup Status')
            ax3.set_title('Setup Status by Period')
            ax3.set_ylim(0, 1.2)
            ax3.set_yticks([0, 1])
            ax3.set_yticklabels(['Off', 'On'])
            
            # 添加开机月份标注
            setup_months = sum(setup_status)
            ax3.text(0.02, 0.98, f'Active Periods: {setup_months}/{len(periods)}', 
                    transform=ax3.transAxes, va='top', 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        else:
            ax3.text(0.5, 0.5, 'No Setup Decision in LP Model', ha='center', va='center', 
                    transform=ax3.transAxes, fontsize=14)
            ax3.set_title('Setup Status (N/A)')
        
        ax3.grid(True, alpha=0.3)
        
        # 4. 成本分解饼图
        ax4 = axes[1, 1]
        if 'costs' in solution:
            costs = solution['costs']
            cost_labels = []
            cost_values = []
            cost_colors = []
            
            if costs['production'] > 0:
                cost_labels.append(f"Production\n{costs['production']:.0f}")
                cost_values.append(costs['production'])
                cost_colors.append(self.color_palette['production'])
            
            if costs['holding'] > 0:
                cost_labels.append(f"Inventory\n{costs['holding']:.0f}") 
                cost_values.append(costs['holding'])
                cost_colors.append(self.color_palette['inventory'])
            
            if costs['setup'] > 0:
                cost_labels.append(f"Setup\n{costs['setup']:.0f}")
                cost_values.append(costs['setup'])
                cost_colors.append(self.color_palette['setup'])
            
            if cost_values:
                wedges, texts, autotexts = ax4.pie(cost_values, labels=cost_labels, colors=cost_colors,
                                                  autopct='%1.1f%%', startangle=90)
                
                # 美化饼图
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(10)
            
            ax4.set_title(f'Cost Breakdown\nTotal: {costs["total"]:.0f}')
        else:
            ax4.text(0.5, 0.5, 'No Cost Data', ha='center', va='center', 
                    transform=ax4.transAxes, fontsize=14)
            ax4.set_title('Cost Breakdown')
        
        plt.tight_layout()
        
        # 保存图表
        if save_plot:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{solver_name}_production_plan.png" if solver_name else "production_plan.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📁 图表已保存到：{filepath}")
        
        plt.show()
    
    def plot_solver_comparison(self, results_dict, save_plot=True, output_dir="results"):
        """
        绘制多求解器结果对比图
        
        参数:
            results_dict: 求解器结果字典 {solver_name: {'problem_data': data, 'solution': solution}}
            save_plot: 是否保存图表
            output_dir: 输出目录
        """
        if not results_dict:
            print("❌ 没有可比较的求解结果")
            return
        
        print("📊 生成求解器对比图表...")
        
        # 准备对比数据
        solver_names = list(results_dict.keys())
        total_costs = []
        solve_times = []
        production_totals = []
        inventory_totals = []
        
        for solver_name, result in results_dict.items():
            solution = result['solution']
            if solution and 'costs' in solution:
                total_costs.append(solution['costs']['total'])
                production_totals.append(sum(solution['production']))
                inventory_totals.append(sum(solution['inventory']))
            else:
                total_costs.append(0)
                production_totals.append(0)
                inventory_totals.append(0)
                
            # 获取求解时间（如果有的话）
            if 'solve_time' in result:
                solve_times.append(result['solve_time'])
            else:
                solve_times.append(0)
        
        # 创建对比图表
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Solver Results Comparison Analysis', fontsize=16, fontweight='bold')
        
        # 1. 总成本对比
        ax1 = axes[0, 0]
        bars1 = ax1.bar(solver_names, total_costs, 
                       color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'][:len(solver_names)])
        ax1.set_title('Total Cost Comparison')
        ax1.set_ylabel('Cost')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}', ha='center', va='bottom')
        
        # 2. 求解时间对比
        ax2 = axes[0, 1]
        bars2 = ax2.bar(solver_names, solve_times,
                       color=['#9b59b6', '#34495e', '#16a085', '#e67e22'][:len(solver_names)])
        ax2.set_title('Solve Time Comparison')
        ax2.set_ylabel('Time (seconds)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}', ha='center', va='bottom')
        
        # 3. 生产量对比
        ax3 = axes[1, 0]
        bars3 = ax3.bar(solver_names, production_totals,
                       color=['#27ae60', '#c0392b', '#8e44ad', '#d35400'][:len(solver_names)])
        ax3.set_title('Total Production Comparison')
        ax3.set_ylabel('Quantity')
        ax3.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars3:
            height = bar.get_height()
            if height > 0:
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}', ha='center', va='bottom')
        
        # 4. 库存量对比
        ax4 = axes[1, 1]
        bars4 = ax4.bar(solver_names, inventory_totals,
                       color=['#f1c40f', '#e67e22', '#1abc9c', '#95a5a6'][:len(solver_names)])
        ax4.set_title('Total Inventory Comparison')
        ax4.set_ylabel('Quantity')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        if save_plot:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, 'solver_comparison.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📁 对比图表已保存到：{filepath}")
        
        plt.show()
    
    def plot_detailed_timeline(self, problem_data, solution, solver_name="", save_plot=True, output_dir="results"):
        """
        绘制详细的时间线图表
        
        参数:
            problem_data: 问题数据
            solution: 求解结果  
            solver_name: 求解器名称
            save_plot: 是否保存图表
            output_dir: 输出目录
        """
        if not solution:
            print("❌ 无有效的求解结果")
            return
        
        print(f"📈 生成{solver_name}详细时间线图表...")
        
        # 准备数据
        periods = list(range(1, problem_data['time_periods'] + 1))
        demands = problem_data['demands']
        production = solution['production']
        inventory = solution['inventory']
        
        # 计算累计值
        cumulative_demand = np.cumsum(demands)
        cumulative_production = np.cumsum(production)
        
        # 创建时间线图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        fig.suptitle(f'{solver_name} 详细生产计划时间线', fontsize=16, fontweight='bold')
        
        # 1. 生产、需求和库存时间线
        ax1_twin = ax1.twinx()  # 创建双y轴
        
        # 左轴：数量
        line1 = ax1.plot(periods, production, 'o-', color=self.color_palette['production'], 
                        linewidth=3, markersize=8, label='Production')
        line2 = ax1.plot(periods, demands, 's-', color=self.color_palette['demand'], 
                        linewidth=3, markersize=8, label='Demand')
        
        # 右轴：库存
        line3 = ax1_twin.plot(periods, inventory, '^-', color=self.color_palette['inventory'], 
                             linewidth=3, markersize=8, label='End Inventory')
        
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Production/Demand (Quantity)')
        ax1_twin.set_ylabel('Inventory Level')
        ax1.set_title('Production, Demand, and Inventory Time Line')
        
        # 合并图例
        lines = line1 + line2 + line3
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
        
        ax1.grid(True, alpha=0.3)
        
        # 2. 累计生产与累计需求
        ax2.plot(periods, cumulative_production, 'o-', color=self.color_palette['production'], 
                linewidth=3, markersize=8, label='Cumulative Production')
        ax2.plot(periods, cumulative_demand, 's-', color=self.color_palette['demand'], 
                linewidth=3, markersize=8, label='Cumulative Demand')
        
        # 填充区域表示缺口或盈余
        ax2.fill_between(periods, cumulative_production, cumulative_demand, 
                        where=(np.array(cumulative_production) >= np.array(cumulative_demand)), 
                        color=self.color_palette['inventory'], alpha=0.3, label='Inventory Surplus')
        ax2.fill_between(periods, cumulative_production, cumulative_demand, 
                        where=(np.array(cumulative_production) < np.array(cumulative_demand)), 
                        color=self.color_palette['demand'], alpha=0.3, label='Supply Shortage')
        
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Cumulative Quantity')
        ax2.set_title('Cumulative Production vs Demand Comparison')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存图表
        if save_plot:
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{solver_name}_timeline.png" if solver_name else "timeline.png"
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📁 时间线图表已保存到：{filepath}")
        
        plt.show()
    
    def create_summary_dashboard(self, results_dict, save_plot=True, output_dir="results"):
        """
        创建综合仪表板
        
        参数:
            results_dict: 求解器结果字典
            save_plot: 是否保存图表
            output_dir: 输出目录
        """
        if not results_dict:
            print("❌ 没有可用的求解结果")
            return
        
        print("📊 生成综合分析仪表板...")
        
        # 创建大型仪表板
        fig = plt.figure(figsize=(20, 15))
        fig.suptitle('Production Planning Optimization Comprehensive Analysis Dashboard', fontsize=20, fontweight='bold')
        
        # 布局：3行4列的网格
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # 获取第一个结果作为基准
        first_result = next(iter(results_dict.values()))
        problem_data = first_result['problem_data']
        periods = list(range(1, problem_data['time_periods'] + 1))
        
        # 1. 生产计划对比 (1行2列)
        ax1 = fig.add_subplot(gs[0, :2])
        for solver_name, result in results_dict.items():
            if result['solution']:
                ax1.plot(periods, result['solution']['production'], 'o-', 
                        label=f'{solver_name} Production', linewidth=2, markersize=6)
        
        ax1.plot(periods, problem_data['demands'], 's--', color='red', 
                label='Demand', linewidth=2, markersize=6)
        ax1.set_title('Production Plan Comparison Across Solvers')
        ax1.set_xlabel('Period')
        ax1.set_ylabel('Quantity')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 库存水平对比 (1行2列)
        ax2 = fig.add_subplot(gs[0, 2:])
        for solver_name, result in results_dict.items():
            if result['solution']:
                ax2.plot(periods, result['solution']['inventory'], 'o-', 
                        label=f'{solver_name} Inventory', linewidth=2, markersize=6)
        
        ax2.set_title('Inventory Level Comparison Across Solvers')
        ax2.set_xlabel('Period')
        ax2.set_ylabel('Inventory Level')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3-6. 各求解器详细结果（每个占1个子图）
        solver_count = 0
        for solver_name, result in results_dict.items():
            if solver_count >= 4:  # 最多显示4个求解器
                break
            
            if result['solution']:
                ax = fig.add_subplot(gs[1 + solver_count//2, solver_count%2])
                
                # 绘制生产和需求的堆叠条形图
                width = 0.6
                ax.bar(periods, result['solution']['production'], width, 
                      label='Production', color=self.color_palette['production'], alpha=0.7)
                ax.bar(periods, problem_data['demands'], width, 
                      label='Demand', color=self.color_palette['demand'], alpha=0.5)
                
                ax.set_title(f'{solver_name} Production Plan')
                ax.set_xlabel('Period')
                ax.set_ylabel('Quantity')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # 添加成本信息
                if 'costs' in result['solution']:
                    total_cost = result['solution']['costs']['total']
                    ax.text(0.02, 0.98, f'Total Cost: {total_cost:.0f}', 
                           transform=ax.transAxes, va='top',
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7))
            
            solver_count += 1
        
        # 保存仪表板
        if save_plot:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, 'comprehensive_dashboard.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📁 综合仪表板已保存到：{filepath}")
        
        plt.show()


# 测试代码
if __name__ == "__main__":
    print("🧪 测试可视化工具...")
    
    # 创建模拟数据
    visualizer = ProductionPlanVisualizer()
    
    # 模拟问题数据
    problem_data = {
        'time_periods': 6,
        'demands': [100, 120, 90, 110, 130, 95]
    }
    
    # 模拟解决方案
    solution = {
        'production': [150, 80, 100, 120, 100, 110],
        'inventory': [50, 10, 20, 30, 0, 15],
        'setup': [1, 1, 1, 1, 1, 1],
        'costs': {
            'production': 6600,
            'holding': 250,
            'setup': 3000,
            'total': 9850
        }
    }
    
    # 测试基本绘图功能
    visualizer.plot_production_plan(problem_data, solution, "测试求解器", save_plot=False)
    
    print("✅ 可视化工具测试完成") 