# GitHub Research Pro 实现笔记

## 架构设计

```
GitHubResearchInput (Pydantic模型)
    ↓
GitHubResearchPro (核心类)
    ├── search()          → 执行GitHub API搜索
    ├── _analyze_repo()   → 分析单个仓库
    ├── _calc_score()     → 质量评分
    ├── _extract_readme() → README摘要
    ├── _extract_structure() → 目录结构
    ├── _extract_dependencies() → 依赖提取
    └── generate_report() → 报告生成
    ↓
search_and_learn_github() (便捷函数)
    ↓
TOOL_METADATA (Hermes Tool格式)
```

## 评分算法详解

### 权重分配

| 维度 | 权重 | 计算方式 | 理论满分 |
|------|------|----------|----------|
| Stars | 40% | min(stars/100, 40) | 5000+ stars |
| 活跃度 | 30% | 30天内=30, 90天内=20, 1年内=10 | <30天 |
| Forks | 20% | min(forks/50, 20) | 1000+ forks |
| Issue响应 | 10% | open_issues<50=10, <200=5 | <50 issues |

### 评分示例

| 项目 | Stars | 更新 | Forks | Issues | 得分 |
|------|-------|------|-------|--------|------|
| 优秀 | 5000 | 7天前 | 800 | 30 | 40+30+16+10=96 |
| 良好 | 1000 | 30天前 | 200 | 80 | 20+20+10+5=55 |
| 一般 | 200 | 60天前 | 50 | 150 | 10+10+5+0=25 |

## 关键实现细节

### 1. README摘要提取

```python
def _extract_readme(self, repo, max_chars=1500):
    readme = repo.get_readme()
    content = base64.b64decode(readme.content).decode('utf-8')
    
    # 提取关键部分
    summary = []
    for line in content.split('\n'):
        if line.startswith('# ') or line.startswith('## '):
            summary.append(line)
        elif line.startswith('- ') and len(summary) < 20:
            summary.append(line)
    
    return '\n'.join(summary)[:max_chars]
```

**策略：** 提取标题和列表项，忽略代码块和详细说明

### 2. 目录结构提取

```python
def _extract_structure(self, repo, max_depth=2):
    contents = repo.get_contents("")
    for item in contents:
        if item.type == "dir":
            # 只展开一层子目录
            sub_contents = repo.get_contents(item.path)
```

**限制：** 最多30个条目，防止大型仓库导致超时

### 3. 依赖文件识别

支持格式：
- Python: `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`
- Node.js: `package.json`

## 降级处理

当 PyGithub 不可用时：

```python
try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
```

在 `__init__` 中检查：
```python
if not GITHUB_AVAILABLE:
    raise ImportError("PyGithub未安装")
```

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 无Token | 返回配置错误提示 |
| API超时 | 抛出RuntimeError |
| 仓库无README | 返回"提取失败"标记 |
| 速率限制 | 依赖PyGithub自动重试 |

## 性能优化

1. **分页控制**：`per_page=10` 减少单次请求数据量
2. **并发限制**：通过 `asyncio.Semaphore` 控制（如需要异步版本）
3. **缓存建议**：搜索结果可缓存1小时，避免重复请求

## 扩展方向

1. **异步版本**：使用 `aiohttp` + GitHub REST API 直接请求
2. **本地缓存**：将搜索结果存入 SQLite，支持离线查询
3. **多源聚合**：同时搜索 GitHub + GitLab + Gitee
4. **代码相似度**：使用 AST 分析对比项目代码结构相似度
