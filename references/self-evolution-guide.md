# 自进化系统使用指南

GitHub Research Pro 的自进化系统通过 L1-L4 四级机制持续优化搜索策略。

## 快速开始

自进化系统**无需手动配置**，每次搜索自动记录数据并优化。

## L1: 数据收集

每次搜索自动记录以下数据到 `.evolution/sessions.jsonl`：

```json
{
  "timestamp": "2026-05-24T22:30:00",
  "query": "fastapi auth",
  "results_count": 3,
  "duration_sec": 25.5,
  "quality_score": 8,
  "errors": [],
  "findings": ["fastapi-users: 用户认证"]
}
```

**字段说明：**
- `quality_score`: 1-10分，基于结果数量和错误数计算
- `errors`: 错误列表，用于识别高频问题
- `findings`: 发现的项目摘要

## L2: 效果分析

调用 `tracker.analyze()` 获取统计报告：

```python
{
  "total_sessions": 15,
  "avg_quality": 7.5,
  "avg_duration_sec": 32.0,
  "error_rate": 0.15,
  "top_errors": [["API限流", 3], ["超时", 2]],
  "top_keywords": [["fastapi", 5], ["scraper", 4]]
}
```

## L3: 规则优化

系统根据分析结果自动调整搜索参数：

| 条件 | 调整 |
|------|------|
| 错误率 > 30% | max_results=2, cooldown=120s |
| 平均质量 < 5 | min_stars=100 |
| 平均时长 > 60s | max_results=2 |

**当前规则查看：**
```python
from scripts.github_research_tool import tracker
rules = tracker.get_rules()
```

## L4: 进化触发

默认每 **10次会话** 触发深度进化分析，自动优化规则。

**手动检查：**
```python
if tracker.should_evolve(5):  # 自定义阈值
    print("触发进化")
```

## 数据文件位置

```
~/.hermes/skills/software-development/github-research-pro/.evolution/
├── sessions.jsonl   # 追加写入，所有历史会话
├── stats.json       # 最新统计结果
└── rules.json       # 当前优化规则
```

## 重置进化数据

如需清空历史重新开始：

```bash
rm -f .evolution/sessions.jsonl .evolution/stats.json .evolution/rules.json
```

## API参考

### EvolutionTracker 类

```python
tracker = EvolutionTracker()

# 记录会话
tracker.record_session(query, results_count, duration, quality_score, errors, findings)

# 分析历史
stats = tracker.analyze()

# 优化规则
rules = tracker.optimize_rules()

# 获取当前规则
rules = tracker.get_rules()

# 检查进化
should_evolve = tracker.should_evolve(threshold=10)
```

## 实现细节

自进化系统集成在 `GitHubResearchPro.search()` 方法中：

1. 搜索前：应用当前优化规则调整参数
2. 搜索中：记录每个仓库的分析结果和错误
3. 搜索后：计算质量评分并持久化会话数据
4. 进化检查：达到阈值时触发分析和规则更新

**质量评分算法：**
```python
quality = min(10, max(1, len(results) * 3 + (5 if not errors else 0)))
```

## 故障排查

| 问题 | 解决 |
|------|------|
| 数据未记录 | 检查 `.evolution/` 目录写权限 |
| 规则未生效 | 确认 `tracker.get_rules()` 返回非空 |
| 进化未触发 | 检查会话数是否达到阈值 |
| stats.json为空 | 至少完成1次成功搜索后才会生成 |
