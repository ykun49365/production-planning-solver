# 🏭 生产计划优化问题多求解器系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-完成-brightgreen.svg)](README.md)

基于多种优化模型和求解器的生产计划优化问题求解系统，支持MILP、LP、QP、NLP四种优化模型，提供完整的性能比较和可视化分析功能。

## 📋 项目概述

本项目实现了一个完整的生产计划优化求解系统，针对工厂生产计划与库存管理问题，提供了四种不同的数学优化模型：

- **MILP模型**：混合整数线性规划，考虑开机/停机决策
- **LP模型**：线性规划，连续生产无固定成本
- **QP模型**：二次规划，平滑生产计划优化
- **NLP模型**：非线性规划，考虑规模经济效应

## 🎯 核心功能

### ✨ 四种优化模型
- **MILP（混合整数线性规划）**：包含0-1开机决策变量，真实反映固定开机成本
- **LP（线性规划）**：纯连续变量，快速求解最低成本方案
- **QP（二次规划）**：二次目标函数，实现生产计划平滑化
- **NLP（非线性规划）**：非线性成本函数，考虑生产规模效应

### 🔍 多求解器支持
- **PuLP + CBC**：开源线性/整数规划求解器
- **CVXPY + CLARABEL**：现代凸优化求解器
- **SciPy + SLSQP**：序列二次规划非线性求解器
- **备选求解器**：GUROBI、OSQP、SCS等专业求解器

### 📊 完整的分析功能
- **性能比较**：四种模型的求解时间、成本、质量对比
- **可视化分析**：生产计划图表、成本分解、性能仪表板
- **详细报告**：CSV数据导出、文本分析报告
- **可扩展性分析**：不同问题规模的性能测试

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/MacOS

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

程序将自动：
1. 生成生产计划优化问题实例
2. 使用四种求解器求解
3. 生成性能比较报告
4. 创建可视化图表
5. 保存结果到 `results/` 目录

## 📁 项目结构

```
solver/
├── main.py                    # 主程序入口
├── config.py                  # 配置文件
├── data_generator.py          # 数据生成器
├── solver_milp.py            # MILP求解器
├── solver_lp.py              # LP求解器  
├── solver_qp.py              # QP求解器
├── solver_nlp.py             # NLP求解器
├── performance_analyzer.py    # 性能分析器
├── visualizer.py             # 可视化工具
├── font_config.py            # 字体配置模块
├── requirements.txt          # 依赖包列表
├── README.md                 # 项目说明
├── results/                  # 输出结果目录
│   ├── *.png                # 图表文件
│   ├── *.csv                # 数据文件
│   └── *.txt                # 分析报告
└── 生产计划优化问题及多求解器性能比较研究.md  # 技术文档
```

## 🔧 技术架构

### 数学模型

**问题描述**：工厂需要在T个时期内制定生产计划，最小化总成本（生产成本+库存成本+开机成本），满足需求约束和产能限制。

**决策变量**：
- `x_t`：第t期生产量
- `s_t`：第t期期末库存量  
- `y_t`：第t期是否开机（0-1变量，仅MILP模型）

**目标函数**：
```
minimize: Σ(c_prod * x_t + c_hold * s_t + c_setup * y_t)
```

**约束条件**：
- 库存平衡：`s_{t-1} + x_t = d_t + s_t`
- 产能限制：`x_t ≤ M * y_t`（MILP）或 `x_t ≤ M`（LP/QP/NLP）
- 非负约束：`x_t, s_t ≥ 0`

### 求解器技术栈

| 模型类型 | 主要库 | 核心求解器 | 特点 |
|---------|--------|------------|------|
| MILP | PuLP | CBC/Gurobi | 处理整数变量 |
| LP | PuLP | CBC | 线性规划专用 |
| QP | CVXPY | CLARABEL/OSQP | 二次凸优化 |
| NLP | SciPy | SLSQP/COBYLA | 非线性优化 |

## 📈 使用示例

### 基本使用
```python
from data_generator import DataGenerator
from solver_milp import solve_milp_problem

# 生成问题数据
generator = DataGenerator()
problem_data = generator.generate_problem_instance()

# 求解MILP问题
solver = solve_milp_problem(problem_data)
solver.print_solution()
```

### 性能比较
```python
from performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
# 添加多个求解结果
analyzer.add_result("MILP", "测试问题", milp_result)
analyzer.add_result("LP", "测试问题", lp_result)

# 生成比较报告
analyzer.generate_comparison_report()
analyzer.plot_performance_charts()
```

### 参数配置
编辑 `config.py` 文件自定义问题参数：
```python
TIME_PERIODS = 12           # 规划周期
DEMANDS = [100, 120, ...]   # 需求数据
PRODUCTION_COST = 10.0      # 生产成本
HOLDING_COST = 2.0          # 库存成本  
SETUP_COST = 500.0          # 开机成本
MAX_CAPACITY = 200          # 最大产能
```

## 📊 输出结果

### 图表文件
- `*_production_plan.png`：各求解器生产计划图
- `solver_comparison.png`：求解器对比图
- `performance_comparison.png`：性能比较图
- `comprehensive_dashboard.png`：综合分析仪表板

### 数据文件
- `solver_comparison_results.csv`：详细结果数据
- `performance_report.txt`：性能分析报告

### 控制台输出
```
🏆 求解器性能总结：
1. LP        : 求解时间 0.014秒, 总成本 14250元
2. NLP       : 求解时间 0.013秒, 总成本 14436元  
3. QP        : 求解时间 0.015秒, 总成本 14505元
4. MILP      : 求解时间 0.077秒, 总成本 19460元

💡 推荐建议：
• 最快求解器：LP
• 适用场景：对于12期生产计划问题
• 性能特点：LP在当前问题规模下表现最佳
```

## 🎨 特色功能

### 智能字体配置
- 自动检测系统中文字体
- 图表使用英文标题避免字体问题
- 程序输出保持中文界面

### 多种可视化
- 生产计划对比图
- 库存水平变化图  
- 成本分解饼图
- 性能比较分析图

### 灵活的配置系统
- 支持自定义需求模式
- 可调整成本参数
- 多种求解器选项

## 🔍 技术亮点

1. **模块化设计**：每个求解器独立封装，易于扩展
2. **统一接口**：所有求解器提供一致的调用接口
3. **错误处理**：完善的异常处理和用户提示
4. **性能优化**：多求解器并行比较
5. **结果验证**：自动验证解的可行性
6. **中英文混合界面**：程序输出中文，图表英文

## 📚 相关文档

- [生产计划优化问题及多求解器性能比较研究.md](生产计划优化问题及多求解器性能比较研究.md) - 详细的技术文档和问题建模

## 📧 联系方式

如有问题或建议，欢迎提交Issue或Pull Request。

---

**项目状态**：✅ 完成开发和测试，可直接使用

**最后更新**：2025年5月

**版本**：v1.0.0 