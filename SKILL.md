---
name: github-research-pro
description: |
  Use when: 1) 用户要求编写新功能/新模块/新项目 2) 用户说"参考开源项目" 3) 技术选型不确定 4) 需要学习业界最佳实践
  编程前必须调用此工具搜索GitHub相似开源项目，学习架构设计和实现思路。
triggers:
  - 写代码前
  - 新功能开发
  - 技术选型
  - 参考开源
  - 学习架构
  - 项目重构
  - 最佳实践
  - 设计模式
  - 依赖选择
  - 目录结构
tags:
  - github
  - research
  - architecture
  - best-practices
  - code-quality
related_skills:
  - github-research-before-coding
  - code-review
  - test-patterns
  - clean-code-review
category: software-development
version: "1.1.0"
author: "tianbin"
---

# 🔍 GitHub Research Pro

编程前自动搜索并学习GitHub相似开源项目的硬核技能。

## ⚡ 编程前置工作流准则

当你收到任何编写新功能、新模块或独立项目的任务时，**禁止立即开始写代码**。必须严格执行以下步骤：

1. **定义问题**：明确用户要写的东西属于什么领域
2. **同行评审（关键）**：调用 `github_research_pro` 工具，搜索至少3个GitHub上最优秀、最相似的开源项目
3. **消化学习**：仔细阅读这些开源项目的项目结构、依赖选择和设计模式
4. **综合分析**：基于预研结果撰写技术实现文档，包含方案对比、选型理由、实现checklist
5. **用户确认**：向用户汇报技术文档，经同意后再开始编码
6. **编码执行**：用户说"好"/"开始"/"确认"或选择方案后，再启动编程

**用户明确说"直接写"/"不用搜"/"我知道怎么做"时，可跳过预研步骤。**

## 🧬 自进化系统 (L1-L4)

技能内置自进化机制，每次搜索自动记录数据并优化搜索策略：

### 进化层级

| 层级 | 功能 | 触发条件 |
|------|------|----------|
| **L1 数据收集** | 记录每次搜索的查询/结果/时长/质量/错误 | 每次搜索自动执行 |
| **L2 效果分析** | 统计平均质量/时长/错误率/高频关键词 | 每次搜索后自动分析 |
| **L3 规则优化** | 根据历史数据动态调整搜索参数 | 积累数据后自动优化 |
| **L4 版本迭代** | 每10次会话触发深度进化分析 | 达到阈值自动触发 |

### 自适应规则

系统根据历史表现自动调整：

- **错误率 > 30%** → 减少并发(max_results=2)、增加冷却时间
- **平均质量 < 5** → 提高星级门槛(min_stars=100)
- **平均时长 > 60s** → 减少分析数量

### 数据存储

```
.evolution/
├── sessions.jsonl   # 原始会话数据
├── stats.json       # 统计分析结果
└── rules.json       # 优化后的规则
```

### 查看进化状态

```python
from scripts.github_research_tool import tracker

# 查看统计
stats = tracker.analyze()
print(f"总会话: {stats['total_sessions']}")
print(f"平均质量: {stats['avg_quality']}")

# 查看当前规则
rules = tracker.get_rules()
print(f"min_stars: {rules['min_stars_default']}")
```

## 🛠️ 工具使用

### 基本调用

```python
from scripts.github_research_tool import search_and_learn_github

# 搜索相似项目
report = search_and_learn_github(
    query="FastAPI rate limiter",
    language="python",
    min_stars=50,
    max_results=3
)
print(report)
```

### 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| query | str | 必填 | 搜索关键词 |
| language | str | "python" | 编程语言过滤 |
| min_stars | int | 50 | 最小star数 |
| max_results | int | 3 | 分析项目数量 |

### 环境配置

```bash
# 安装依赖
pip install PyGithub pydantic

# 配置Token（方式1：环境变量）
export GITHUB_TOKEN="your_github_token"

# 配置Token（方式2：GitHub CLI - 推荐）
gh auth login
# Token会自动从 gh auth token 获取
```

### Token传递技巧（execute_code环境）

当使用 `execute_code` 工具时，环境变量不会自动传递，需要显式设置：

```python
import os
import subprocess

# 从GitHub CLI获取token并设置
token = subprocess.run(['gh', 'auth', 'token'], 
                       capture_output=True, text=True).stdout.strip()
os.environ['GITHUB_TOKEN'] = token

# 然后再导入github_research_tool
from github_research_tool import search_and_learn_github
```

**常见错误**：先import模块再设置环境变量会导致401错误，因为模块在导入时已读取环境变量。

## 📊 输出报告结构

工具会生成包含以下内容的预研报告：

1. **项目基本信息**：Stars/Forks/语言/更新时间
2. **README核心摘要**：特性、安装、使用方式
3. **目录结构**：学习大厂开源项目的文件组织规范
4. **依赖文件**：参考经过验证的第三方库选择
5. **技术方案建议**：推荐参考哪个项目及原因

## 🎯 质量评分算法

工具内置评分系统（0-100分）：

| 维度 | 权重 | 计算方式 |
|------|------|----------|
| Stars | 40% | min(stars/100, 40) |
| 活跃度 | 30% | 30天内更新=30分 |
| Forks | 20% | min(forks/50, 20) |
| Issue响应 | 10% | open_issues<50=10分 |

## 🚀 进阶功能

### 技术栈自动识别

工具会自动提取项目的依赖文件：
- Python: `requirements.txt`, `pyproject.toml`, `setup.py`
- Node.js: `package.json`

### 目录结构学习

自动分析目标仓库的目录组织方式，输出规范的树形结构供参考。

## ⚠️ 注意事项

1. **必须配置 GITHUB_TOKEN**，否则无法调用API
2. **PyGithub 安装问题**：某些终端环境导入会超时，推荐使用 `execute_code` 工具测试
3. 搜索关键词应尽量具体，如 `"FastAPI JWT authentication"` 而非 `"web framework"`
4. 报告中的README摘要会被截断，建议访问原仓库查看完整内容
5. 评分仅供参考，最终选择应结合项目实际需求

## 🔧 故障排查

### 自进化系统

- **数据未记录**：检查 `.evolution/` 目录权限
- **规则未生效**：调用 `tracker.get_rules()` 查看当前规则
- **进化未触发**：默认阈值10次会话，可通过 `tracker.should_evolve(3)` 降低

### API与认证

详见关联技能的参考文档：
- `github-research-before-coding/references/pygithub-setup-guide.md` — PyGithub安装与Token配置
- `github-research-before-coding/references/github-auth-workarounds.md` — GitHub认证问题与替代方案

## 📁 参考文档

- `references/tool-implementation-notes.md` — 评分算法、实现细节、扩展方向
- `references/self-evolution-guide.md` — 自进化系统使用指南与API参考
- `references/tech-spec-template.md` — 技术实现文档标准模板（预研后必须撰写）
- `../github-research-before-coding/references/pygithub-setup-guide.md` — PyGithub安装与Token配置

## 🔗 相关资源

- [PyGithub文档](https://pygithub.readthedocs.io/)
- [GitHub Search API](https://docs.github.com/en/rest/search)
- 关联技能: `github-research-before-coding` (手动预研流程 + 故障排查指南)
