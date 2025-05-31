# -*- coding: utf-8 -*-
"""
生产计划优化问题主程序
整合所有求解器和分析工具，提供完整的优化解决方案
"""

# 首先配置字体
try:
    from font_config import configure_chinese_font
    configure_chinese_font()
    print("✅ 中文字体配置完成")
except ImportError:
    print("⚠️  使用默认字体配置")

import os
import time
from datetime import datetime

# 导入自定义模块
from data_generator import DataGenerator
from solver_milp import solve_milp_problem
from solver_lp import solve_lp_problem

# 尝试导入可选的求解器
try:
    from solver_qp import solve_qp_problem
    QP_AVAILABLE = True
except ImportError:
    print("⚠️  QP求解器不可用：缺少cvxpy依赖")
    QP_AVAILABLE = False

try:
    from solver_nlp import solve_nlp_problem
    NLP_AVAILABLE = True
except ImportError:
    print("⚠️  NLP求解器不可用：缺少scipy依赖")
    NLP_AVAILABLE = False

from performance_analyzer import PerformanceAnalyzer
from visualizer import ProductionPlanVisualizer
from config import *

def print_welcome():
    """打印欢迎信息"""
    print("="*80)
    print(" " * 20 + "🏭 生产计划优化问题求解器 🏭")
    print("="*80)
    print("📋 功能特点：")
    print("  • 支持多种优化模型：MILP、LP、QP、NLP")
    print("  • 多求解器性能比较：PuLP、CVXPY、Gurobi等")
    print("  • 可视化分析：生产计划图表、性能对比图")
    print("  • 详细报告：求解结果、性能分析、成本分解")
    print("="*80)
    print(f"⏰ 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

def create_output_directory():
    """创建输出目录"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"📁 输出目录已创建：{OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"❌ 创建输出目录失败：{e}")
        return False

def solve_single_problem():
    """求解单个问题实例"""
    print("\n" + "="*60)
    print("🎯 第一部分：单问题求解和详细分析")
    print("="*60)
    
    # 生成问题数据
    generator = DataGenerator()
    problem_data = generator.generate_problem_instance()
    
    if not problem_data:
        print("❌ 无法生成问题数据")
        return None
    
    # 显示问题摘要
    generator.print_problem_summary(problem_data)
    
    # 定义可用的求解器
    available_solvers = {
        'MILP': solve_milp_problem,
        'LP': solve_lp_problem,
    }
    
    if QP_AVAILABLE:
        available_solvers['QP'] = solve_qp_problem
    
    if NLP_AVAILABLE:
        available_solvers['NLP'] = solve_nlp_problem
    
    # 存储求解结果
    solver_results = {}
    
    # 逐个测试求解器
    for solver_name, solver_func in available_solvers.items():
        print(f"\n{'-'*50}")
        print(f"🚀 正在测试 {solver_name} 求解器...")
        print(f"{'-'*50}")
        
        try:
            start_time = time.time()
            solver = solver_func(problem_data)
            solve_time = time.time() - start_time
            
            if solver:
                print(f"✅ {solver_name} 求解成功！")
                solver.print_solution()
                
                # 保存结果
                solver_results[solver_name] = {
                    'solver': solver,
                    'problem_data': problem_data,
                    'solution': solver.solution,
                    'solve_time': solve_time
                }
                
                # 生成可视化图表
                if GENERATE_PLOTS:
                    visualizer = ProductionPlanVisualizer()
                    visualizer.plot_production_plan(
                        problem_data, 
                        solver.solution, 
                        solver_name,
                        save_plot=SAVE_RESULTS,
                        output_dir=OUTPUT_DIR
                    )
            else:
                print(f"❌ {solver_name} 求解失败")
                
        except Exception as e:
            print(f"❌ {solver_name} 运行出错：{e}")
    
    return solver_results

def compare_solver_performance(solver_results):
    """比较求解器性能"""
    if not solver_results:
        print("❌ 没有可用的求解结果进行比较")
        return
    
    print("\n" + "="*60)
    print("📊 第二部分：求解器性能比较分析")
    print("="*60)
    
    # 创建性能分析器
    analyzer = PerformanceAnalyzer()
    
    # 添加求解结果
    for solver_name, result in solver_results.items():
        summary = result['solver'].get_result_summary()
        if summary:
            summary['total_time'] = result['solve_time']
            analyzer.add_result(solver_name, "主要测试问题", summary)
    
    # 生成比较报告
    comparison_df = analyzer.generate_comparison_report()
    
    if comparison_df is not None and GENERATE_PLOTS:
        # 生成性能比较图表
        analyzer.plot_performance_charts(
            save_plots=SAVE_RESULTS,
            output_dir=OUTPUT_DIR
        )
        
        # 生成求解器结果对比图
        visualizer = ProductionPlanVisualizer()
        visualizer.plot_solver_comparison(
            solver_results,
            save_plot=SAVE_RESULTS,
            output_dir=OUTPUT_DIR
        )
        
        # 创建综合仪表板
        visualizer.create_summary_dashboard(
            solver_results,
            save_plot=SAVE_RESULTS,
            output_dir=OUTPUT_DIR
        )
    
    # 保存详细报告
    if SAVE_RESULTS:
        analyzer.save_detailed_report(OUTPUT_DIR)

def run_scalability_analysis():
    """运行可扩展性分析"""
    print("\n" + "="*60)
    print("📈 第三部分：求解器可扩展性分析")
    print("="*60)
    
    try:
        generator = DataGenerator()
        scenarios = generator.create_test_scenarios(3)
        
        if not scenarios:
            print("❌ 无法创建测试场景")
            return
        
        analyzer = PerformanceAnalyzer()
        
        # 对每个场景运行所有求解器
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n🎯 场景 {i}: {scenario['name']}")
            print("-" * 40)
            
            # 可用求解器
            solver_functions = {
                'MILP': solve_milp_problem,
                'LP': solve_lp_problem,
            }
            
            if QP_AVAILABLE:
                solver_functions['QP'] = solve_qp_problem
            
            if NLP_AVAILABLE:
                solver_functions['NLP'] = solve_nlp_problem
            
            # 测试每个求解器
            analyzer.compare_solvers(scenario, solver_functions)
        
        # 生成可扩展性分析
        scenarios_results = {}
        for result in analyzer.results:
            scenario_name = result['problem_name']
            if scenario_name not in scenarios_results:
                scenarios_results[scenario_name] = []
            scenarios_results[scenario_name].append(result)
        
        analyzer.analyze_scalability(scenarios_results)
        
    except Exception as e:
        print(f"❌ 可扩展性分析出错：{e}")

def print_summary_and_recommendations(solver_results):
    """打印总结和建议"""
    print("\n" + "="*80)
    print("📋 第四部分：总结与建议")
    print("="*80)
    
    if not solver_results:
        print("❌ 没有可用的求解结果")
        return
    
    print("🏆 求解器性能总结：")
    print("-" * 50)
    
    # 按求解时间排序
    sorted_results = sorted(solver_results.items(), 
                           key=lambda x: x[1]['solve_time'])
    
    for i, (solver_name, result) in enumerate(sorted_results, 1):
        solve_time = result['solve_time']
        total_cost = result['solution']['costs']['total']
        print(f"{i}. {solver_name:10s}: 求解时间 {solve_time:.3f}秒, 总成本 {total_cost:.0f}元")
    
    # 从结果中获取问题规模信息
    first_result = next(iter(solver_results.values()))
    time_periods = first_result['problem_data']['time_periods']
    
    # 推荐最佳求解器
    fastest_solver = sorted_results[0][0]
    print(f"\n💡 推荐建议：")
    print(f"• 最快求解器：{fastest_solver}")
    print(f"• 适用场景：对于{time_periods}期生产计划问题")
    print(f"• 性能特点：{fastest_solver}在当前问题规模下表现最佳")
    
    # 模型选择建议
    print(f"\n🎯 模型选择建议：")
    if 'MILP' in solver_results and 'LP' in solver_results:
        milp_cost = solver_results['MILP']['solution']['costs']['total']
        lp_cost = solver_results['LP']['solution']['costs']['total']
        cost_difference = milp_cost - lp_cost
        
        print(f"• MILP vs LP 成本差异：{cost_difference:.0f}元")
        if cost_difference > 0:
            print(f"• LP模型成本更低，因为没有固定开机成本")
            print(f"• 如果实际存在开机成本，应选择MILP模型")
        else:
            print(f"• MILP模型在当前参数下更优")
    
    print(f"\n📊 输出文件：")
    if SAVE_RESULTS:
        print(f"• 详细报告：{OUTPUT_DIR}/performance_report.txt")
        print(f"• 数据文件：{OUTPUT_DIR}/solver_comparison_results.csv")
        if GENERATE_PLOTS:
            print(f"• 图表文件：{OUTPUT_DIR}/ 目录下的PNG文件")
    
    print("="*80)

def main():
    """主函数"""
    # 打印欢迎信息
    print_welcome()
    
    # 验证配置
    validation_errors = validate_config()
    if validation_errors:
        print("❌ 配置文件存在错误：")
        for error in validation_errors:
            print(f"  - {error}")
        print("请修改config.py文件后重新运行")
        return
    
    # 创建输出目录
    if SAVE_RESULTS:
        if not create_output_directory():
            return
    
    try:
        # 第一部分：求解单个问题
        solver_results = solve_single_problem()
        
        # 第二部分：性能比较
        if solver_results:
            compare_solver_performance(solver_results)
        
        # 第三部分：可扩展性分析（可选）
        print(f"\n❓ 是否运行可扩展性分析？（测试不同问题规模）")
        response = input("输入 'y' 或 'yes' 继续，其他键跳过：").lower().strip()
        if response in ['y', 'yes', '是', 'Y']:
            run_scalability_analysis()
        else:
            print("⏭️  跳过可扩展性分析")
        
        # 第四部分：总结和建议
        if solver_results:
            print_summary_and_recommendations(solver_results)
        
        print(f"\n🎉 程序运行完成！")
        if SAVE_RESULTS:
            print(f"📁 所有结果已保存到：{OUTPUT_DIR} 目录")
        
    except KeyboardInterrupt:
        print("\n⏹️  程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序运行出错：{e}")
        print("请检查配置文件和依赖包是否正确安装")

if __name__ == "__main__":
    main() 