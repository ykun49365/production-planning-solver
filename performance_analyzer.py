# -*- coding: utf-8 -*-
"""
性能分析器模块
用于比较不同求解器的性能，生成分析报告
"""

import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import numpy as np
import matplotlib

# 使用字体配置模块
try:
    from font_config import configure_chinese_font
    configure_chinese_font()
except ImportError:
    # 如果没有字体配置模块，使用默认设置
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'KaiTi', 'FangSong', 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False

class PerformanceAnalyzer:
    """
    性能分析器类
    """
    
    def __init__(self):
        """初始化性能分析器"""
        self.results = []
        self.comparison_data = None
        
    def add_result(self, solver_name, problem_name, result_summary):
        """
        添加求解结果
        
        参数:
            solver_name: 求解器名称
            problem_name: 问题名称
            result_summary: 结果摘要字典
        """
        if result_summary:
            result_data = {
                'solver_name': solver_name,
                'problem_name': problem_name,
                'timestamp': datetime.now(),
                **result_summary
            }
            self.results.append(result_data)
            print(f"✅ 添加求解结果：{solver_name} - {problem_name}")
        else:
            print(f"❌ 无效的求解结果：{solver_name} - {problem_name}")
    
    def compare_solvers(self, problem_data, solver_functions):
        """
        比较多个求解器的性能
        
        参数:
            problem_data: 问题数据
            solver_functions: 求解器函数字典 {'solver_name': function}
        """
        print("🔄 开始求解器性能比较...")
        print("="*60)
        
        problem_name = f"{problem_data['time_periods']}期问题"
        
        for solver_name, solver_func in solver_functions.items():
            try:
                print(f"\n🚀 测试求解器：{solver_name}")
                print("-" * 40)
                
                # 记录开始时间
                start_time = time.time()
                
                # 调用求解器
                solver = solver_func(problem_data)
                
                # 记录总时间
                total_time = time.time() - start_time
                
                if solver:
                    # 获取结果摘要
                    summary = solver.get_result_summary()
                    if summary:
                        summary['total_time'] = total_time
                        self.add_result(solver_name, problem_name, summary)
                        print(f"✅ {solver_name} 求解成功，用时 {total_time:.3f}秒")
                    else:
                        print(f"❌ {solver_name} 无法获取结果摘要")
                else:
                    print(f"❌ {solver_name} 求解失败")
                    
            except Exception as e:
                print(f"❌ {solver_name} 运行出错：{e}")
        
        print("="*60)
        print("✅ 求解器性能比较完成")
    
    def generate_comparison_report(self):
        """
        生成比较报告
        """
        if not self.results:
            print("❌ 没有可用的求解结果")
            return None
        
        print("\n📊 生成性能比较报告...")
        
        # 转换为DataFrame
        df = pd.DataFrame(self.results)
        
        print("\n" + "="*80)
        print("📈 求解器性能比较报告")
        print("="*80)
        
        # 基本统计
        print("🏆 求解器基本信息：")
        for solver in df['solver_name'].unique():
            solver_data = df[df['solver_name'] == solver]
            success_rate = len(solver_data[solver_data['status'] == 'Optimal']) / len(solver_data) * 100
            avg_time = solver_data['solve_time'].mean()
            print(f"  {solver:15s}: 成功率 {success_rate:5.1f}%, 平均求解时间 {avg_time:.3f}秒")
        
        # 按问题分组比较
        print(f"\n📊 详细比较结果：")
        comparison_table = df.pivot_table(
            index='problem_name', 
            columns='solver_name', 
            values=['solve_time', 'objective_value'],
            aggfunc='mean'
        )
        
        print(comparison_table)
        
        # 找出最快的求解器
        print(f"\n🥇 性能排名：")
        
        # 按求解时间排名
        time_ranking = df.groupby('solver_name')['solve_time'].mean().sort_values()
        print(f"求解速度排名（平均时间）：")
        for i, (solver, time_val) in enumerate(time_ranking.items(), 1):
            print(f"  {i}. {solver}: {time_val:.3f}秒")
        
        # 按目标值排名（如果适用）
        if 'objective_value' in df.columns and df['objective_value'].notna().any():
            obj_ranking = df.groupby('solver_name')['objective_value'].mean().sort_values()
            print(f"\n最优解质量排名（平均目标值）：")
            for i, (solver, obj_val) in enumerate(obj_ranking.items(), 1):
                print(f"  {i}. {solver}: {obj_val:.2f}")
        
        # 保存比较数据
        self.comparison_data = df
        
        print("="*80)
        
        return df
    
    def plot_performance_charts(self, save_plots=True, output_dir="results"):
        """
        绘制性能比较图表
        
        参数:
            save_plots: 是否保存图表
            output_dir: 输出目录
        """
        if self.comparison_data is None or self.comparison_data.empty:
            print("❌ 没有比较数据，请先运行generate_comparison_report()")
            return
        
        print("📊 生成性能比较图表...")
        
        # 创建输出目录
        if save_plots:
            os.makedirs(output_dir, exist_ok=True)
        
        df = self.comparison_data
        
        # 设置图表样式
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Solver Performance Comparison Analysis', fontsize=16, fontweight='bold')
        
        # 1. 求解时间比较
        ax1 = axes[0, 0]
        solver_times = df.groupby('solver_name')['solve_time'].mean()
        bars1 = ax1.bar(solver_times.index, solver_times.values, 
                       color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'][:len(solver_times)])
        ax1.set_title('Average Solve Time Comparison')
        ax1.set_ylabel('Time (seconds)')
        ax1.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom')
        
        # 2. 目标值比较（如果有的话）
        ax2 = axes[0, 1]
        if 'objective_value' in df.columns and df['objective_value'].notna().any():
            solver_objs = df.groupby('solver_name')['objective_value'].mean()
            bars2 = ax2.bar(solver_objs.index, solver_objs.values,
                          color=['#9b59b6', '#34495e', '#16a085', '#e67e22'][:len(solver_objs)])
            ax2.set_title('Average Objective Value Comparison')
            ax2.set_ylabel('Objective Value')
            ax2.tick_params(axis='x', rotation=45)
            
            # 添加数值标签
            for bar in bars2:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.0f}', ha='center', va='bottom')
        else:
            ax2.text(0.5, 0.5, 'No Objective Value Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Objective Value Comparison')
        
        # 3. 求解时间分布箱型图
        ax3 = axes[1, 0]
        solve_times_list = [df[df['solver_name'] == solver]['solve_time'].values 
                           for solver in df['solver_name'].unique()]
        box_plot = ax3.boxplot(solve_times_list, labels=df['solver_name'].unique(), patch_artist=True)
        
        # 设置箱型图颜色
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax3.set_title('Solve Time Distribution')
        ax3.set_ylabel('Time (seconds)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. 成功率比较
        ax4 = axes[1, 1]
        success_rates = []
        solver_names = df['solver_name'].unique()
        
        for solver in solver_names:
            solver_data = df[df['solver_name'] == solver]
            success_rate = len(solver_data[solver_data['status'] == 'Optimal']) / len(solver_data) * 100
            success_rates.append(success_rate)
        
        bars4 = ax4.bar(solver_names, success_rates, 
                       color=['#27ae60', '#c0392b', '#8e44ad', '#d35400'][:len(solver_names)])
        ax4.set_title('Success Rate Comparison')
        ax4.set_ylabel('Success Rate (%)')
        ax4.set_ylim(0, 105)
        ax4.tick_params(axis='x', rotation=45)
        
        # 添加数值标签
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_plots:
            filepath = os.path.join(output_dir, 'performance_comparison.png')
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            print(f"📁 图表已保存到：{filepath}")
        
        plt.show()
    
    def save_detailed_report(self, output_dir="results"):
        """
        保存详细的分析报告到文件
        """
        if not self.results:
            print("❌ 没有可用的求解结果")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存CSV文件
        df = pd.DataFrame(self.results)
        csv_path = os.path.join(output_dir, 'solver_comparison_results.csv')
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"📁 详细结果已保存到：{csv_path}")
        
        # 生成文本报告
        report_path = os.path.join(output_dir, 'performance_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("生产计划优化问题求解器性能比较报告\n")
            f.write("="*80 + "\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 基本统计
            f.write("1. 求解器基本信息\n")
            f.write("-" * 40 + "\n")
            
            for solver in df['solver_name'].unique():
                solver_data = df[df['solver_name'] == solver]
                success_rate = len(solver_data[solver_data['status'] == 'Optimal']) / len(solver_data) * 100
                avg_time = solver_data['solve_time'].mean()
                f.write(f"{solver:15s}: 成功率 {success_rate:5.1f}%, 平均求解时间 {avg_time:.3f}秒\n")
            
            f.write("\n2. 性能排名\n")
            f.write("-" * 40 + "\n")
            
            # 按求解时间排名
            time_ranking = df.groupby('solver_name')['solve_time'].mean().sort_values()
            f.write("求解速度排名（平均时间）：\n")
            for i, (solver, time_val) in enumerate(time_ranking.items(), 1):
                f.write(f"  {i}. {solver}: {time_val:.3f}秒\n")
            
            # 结论和建议
            f.write("\n3. 结论和建议\n")
            f.write("-" * 40 + "\n")
            fastest_solver = time_ranking.index[0]
            f.write(f"• 最快的求解器：{fastest_solver} ({time_ranking.iloc[0]:.3f}秒)\n")
            f.write(f"• 建议：对于类似规模的生产计划问题，推荐使用{fastest_solver}求解器\n")
            f.write(f"• 数据规模：{df['problem_name'].iloc[0]}\n")
            f.write(f"• 测试求解器数量：{len(df['solver_name'].unique())}\n")
        
        print(f"📁 分析报告已保存到：{report_path}")
    
    def analyze_scalability(self, scenarios_results):
        """
        分析求解器的可扩展性
        
        参数:
            scenarios_results: 多场景测试结果 {scenario_name: results_list}
        """
        print("📈 分析求解器可扩展性...")
        
        scalability_data = []
        
        for scenario_name, results in scenarios_results.items():
            for result in results:
                if result:
                    scalability_data.append({
                        'scenario': scenario_name,
                        'solver': result['solver_name'],
                        'problem_size': result.get('time_periods', 0),
                        'solve_time': result.get('solve_time', 0),
                        'objective_value': result.get('objective_value', 0)
                    })
        
        if not scalability_data:
            print("❌ 没有可扩展性分析数据")
            return
        
        df_scale = pd.DataFrame(scalability_data)
        
        # 绘制可扩展性图表
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        for solver in df_scale['solver'].unique():
            solver_data = df_scale[df_scale['solver'] == solver]
            plt.plot(solver_data['problem_size'], solver_data['solve_time'], 
                    'o-', label=solver, linewidth=2, markersize=8)
        plt.xlabel('Problem Size (Number of Periods)')
        plt.ylabel('Solve Time (seconds)')
        plt.title('Solve Time vs Problem Size')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 2)
        # 时间复杂度分析
        for solver in df_scale['solver'].unique():
            solver_data = df_scale[df_scale['solver'] == solver].sort_values('problem_size')
            if len(solver_data) > 1:
                # 计算时间增长率
                time_growth = np.diff(solver_data['solve_time']) / np.diff(solver_data['problem_size'])
                plt.plot(solver_data['problem_size'].iloc[1:], time_growth, 
                        's-', label=f'{solver} Growth Rate', alpha=0.7)
        plt.xlabel('Problem Size (Number of Periods)')
        plt.ylabel('Time Growth Rate (sec/period)')
        plt.title('Time Growth Rate Analysis')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("✅ 可扩展性分析完成")


# 测试代码
if __name__ == "__main__":
    # 创建测试数据
    analyzer = PerformanceAnalyzer()
    
    # 模拟一些测试结果
    test_results = [
        {'solver_name': 'MILP', 'status': 'Optimal', 'solve_time': 0.5, 'objective_value': 15000},
        {'solver_name': 'LP', 'status': 'Optimal', 'solve_time': 0.2, 'objective_value': 14500},
    ]
    
    for i, result in enumerate(test_results):
        analyzer.add_result(result['solver_name'], f"测试问题{i+1}", result)
    
    # 生成报告
    df = analyzer.generate_comparison_report()
    if df is not None:
        analyzer.plot_performance_charts(save_plots=False)
        print("🧪 性能分析器测试完成") 