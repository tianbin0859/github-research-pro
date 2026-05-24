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
version: "1.0.0"
author: "tianbin"
---

# 🔍 GitHub Research Pro

编程前自动搜索并学习GitHub相似开源项目的硬核技能。

## ⚡ 编程前置工作流准则

当你收到任何编写新功能、新模块或独立项目的任务时，**禁止立即开始写代码**。必须严格执行以下步骤：

1. **定义问题**：明确用户要写的东西属于什么领域
2. **同行评审（关键）**：调用 `github_research_pro` 工具，搜索至少3个GitHub上最优秀、最相似的开源项目
3. **消化学习**：仔细阅读这些开源项目的项目结构、依赖选择和设计模式
4. **制定方案**：向用户汇报从开源项目中学到了什么，然后再给出代码实现

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

# 配置Token
export GITHUB_TOKEN="your_github_token"
```

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

详见关联技能的参考文档：
- `github-research-before-coding/references/pygithub-setup-guide.md` — PyGithub安装与Token配置
- `github-research-before-coding/references/github-auth-workarounds.md` — GitHub认证问题与替代方案

## 📁 参考文档

- `references/tool-implementation-notes.md` — 评分算法、实现细节、扩展方向
- `../github-research-before-coding/references/pygithub-setup-guide.md` — PyGithub安装与Token配置

## 🔗 相关资源

- [PyGithub文档](https://pygithub.readthedocs.io/)
- [GitHub Search API](https://docs.github.com/en/rest/search)
- 关联技能: `github-research-before-coding` (手动预研流程 + 故障排查指南)
