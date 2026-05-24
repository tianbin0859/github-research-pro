#!/usr/bin/env python3
"""
GitHub Research Pro - 编程前自动预研工具
基于 PyGithub + Pydantic 的硬核技能实现
"""

import os
import json
import base64
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# 自进化数据存储路径
EVO_DATA_DIR = os.path.expanduser("~/.hermes/skills/software-development/github-research-pro/.evolution")
os.makedirs(EVO_DATA_DIR, exist_ok=True)

try:
    from github import Github
    from github.Repository import Repository
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    Github = None
    Repository = None


# GitHub Token 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


class EvolutionTracker:
    """自进化追踪器 - L1数据收集→L2分析→L3优化→L4迭代"""
    
    def __init__(self):
        self.data_file = os.path.join(EVO_DATA_DIR, "sessions.jsonl")
        self.stats_file = os.path.join(EVO_DATA_DIR, "stats.json")
        self.rules_file = os.path.join(EVO_DATA_DIR, "rules.json")
        self._ensure_files()
    
    def _ensure_files(self):
        """确保文件存在"""
        for f in [self.data_file, self.stats_file, self.rules_file]:
            if not os.path.exists(f):
                with open(f, 'w') as fh:
                    if f.endswith('.json'):
                        json.dump({}, fh)
    
    def record_session(self, query: str, results_count: int, duration: float, 
                      quality_score: int, errors: List[str], findings: List[str]):
        """L1: 记录单次搜索数据"""
        session = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": results_count,
            "duration_sec": duration,
            "quality_score": quality_score,  # 1-10
            "errors": errors,
            "findings": findings,
            "version": "1.0.0"
        }
        with open(self.data_file, 'a') as f:
            f.write(json.dumps(session, ensure_ascii=False) + '\n')
    
    def analyze(self) -> dict:
        """L2: 分析历史数据"""
        if not os.path.exists(self.data_file):
            return {}
        
        sessions = []
        with open(self.data_file, 'r') as f:
            for line in f:
                if line.strip():
                    sessions.append(json.loads(line))
        
        if not sessions:
            return {}
        
        total = len(sessions)
        avg_quality = sum(s['quality_score'] for s in sessions) / total
        avg_duration = sum(s['duration_sec'] for s in sessions) / total
        error_rate = sum(1 for s in sessions if s['errors']) / total
        
        # 识别高频错误
        error_types = {}
        for s in sessions:
            for e in s['errors']:
                error_types[e] = error_types.get(e, 0) + 1
        
        # 识别高频关键词
        keywords = {}
        for s in sessions:
            kw = s['query'].split()[0]
            keywords[kw] = keywords.get(kw, 0) + 1
        
        stats = {
            "total_sessions": total,
            "avg_quality": round(avg_quality, 2),
            "avg_duration_sec": round(avg_duration, 2),
            "error_rate": round(error_rate, 2),
            "top_errors": sorted(error_types.items(), key=lambda x: -x[1])[:5],
            "top_keywords": sorted(keywords.items(), key=lambda x: -x[1])[:5],
            "last_analyzed": datetime.now().isoformat()
        }
        
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        return stats
    
    def optimize_rules(self) -> dict:
        """L3: 基于分析优化搜索规则"""
        stats = self.analyze()
        if not stats:
            return {}
        
        rules = {
            "min_stars_default": 50,
            "max_results_default": 3,
            "quality_threshold": 7,
            "error_cooldown_sec": 60,
            "last_updated": datetime.now().isoformat()
        }
        
        # 根据错误率调整
        if stats.get('error_rate', 0) > 0.3:
            rules["error_cooldown_sec"] = 120
            rules["max_results_default"] = 2
        
        # 根据质量调整
        if stats.get('avg_quality', 5) < 5:
            rules["min_stars_default"] = 100
        
        # 根据时长调整
        if stats.get('avg_duration_sec', 30) > 60:
            rules["max_results_default"] = 2
        
        with open(self.rules_file, 'w') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        
        return rules
    
    def get_rules(self) -> dict:
        """获取当前优化后的规则"""
        if os.path.exists(self.rules_file):
            with open(self.rules_file, 'r') as f:
                return json.load(f)
        return self.optimize_rules()
    
    def should_evolve(self, session_threshold: int = 10) -> bool:
        """判断是否触发进化"""
        stats = self.analyze()
        return stats.get('total_sessions', 0) >= session_threshold


# 全局追踪器实例
tracker = EvolutionTracker()


class GitHubResearchInput(BaseModel):
    """输入参数模型"""
    query: str = Field(description="搜索关键词，如 'FastAPI rate limiter'")
    language: str = Field(default="python", description="编程语言过滤")
    min_stars: int = Field(default=50, description="最小star数")
    max_results: int = Field(default=3, description="分析项目数量")
    extract_readme: bool = Field(default=True, description="是否提取README")
    extract_structure: bool = Field(default=True, description="是否提取目录结构")
    extract_deps: bool = Field(default=True, description="是否提取依赖文件")


class RepoAnalysis(BaseModel):
    """仓库分析结果"""
    full_name: str
    url: str
    stars: int
    forks: int
    description: str
    language: str
    last_updated: str
    topics: List[str]
    readme_summary: str = ""
    structure: List[str] = []
    dependencies: Dict[str, List[str]] = {}
    score: float = 0.0


class GitHubResearchPro:
    """GitHub 预研工具核心类"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        if not self.token:
            raise ValueError("未配置 GITHUB_TOKEN 环境变量")
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub未安装，请执行: pip install PyGithub")
        self.g = Github(self.token, per_page=10)
    
    def search(self, params: GitHubResearchInput) -> List[RepoAnalysis]:
        """执行搜索和分析（集成自进化）"""
        import time
        start_time = time.time()
        errors = []
        findings = []
        
        # 应用自进化规则
        rules = tracker.get_rules()
        if rules:
            params.min_stars = max(params.min_stars, rules.get('min_stars_default', 50))
            params.max_results = min(params.max_results, rules.get('max_results_default', 3))
            print(f"🧬 应用进化规则: min_stars={params.min_stars}, max_results={params.max_results}")
        
        # 构建搜索查询
        query = params.query
        if params.language:
            query += f" language:{params.language}"
        query += f" stars:>{params.min_stars}"
        
        print(f"🔍 搜索: {query}")
        
        try:
            repos = self.g.search_repositories(query=query, sort="stars", order="desc")
            results = []
            
            for i, repo in enumerate(repos):
                if i >= params.max_results:
                    break
                
                print(f"  📦 分析 [{i+1}/{params.max_results}]: {repo.full_name}")
                try:
                    analysis = self._analyze_repo(repo, params)
                    results.append(analysis)
                    findings.append(f"{repo.full_name}: {repo.description or '无描述'}")
                except Exception as e:
                    errors.append(f"分析失败 {repo.full_name}: {str(e)}")
                    print(f"  ⚠️ 分析失败: {e}")
            
            # 按综合评分排序
            results.sort(key=lambda x: x.score, reverse=True)
            
            # L1: 记录会话数据
            duration = time.time() - start_time
            quality = min(10, max(1, len(results) * 3 + (5 if not errors else 0)))
            tracker.record_session(
                query=params.query,
                results_count=len(results),
                duration=duration,
                quality_score=quality,
                errors=errors,
                findings=findings
            )
            
            # L4: 检查是否触发进化
            if tracker.should_evolve(10):
                print("🧬 触发自进化分析...")
                stats = tracker.analyze()
                new_rules = tracker.optimize_rules()
                print(f"📊 进化统计: 平均质量={stats.get('avg_quality')}, 错误率={stats.get('error_rate')}")
            
            return results
            
        except Exception as e:
            errors.append(str(e))
            tracker.record_session(
                query=params.query,
                results_count=0,
                duration=time.time() - start_time,
                quality_score=1,
                errors=errors,
                findings=[]
            )
            raise RuntimeError(f"GitHub API 错误: {e}")
    
    def _analyze_repo(self, repo: Repository, params: GitHubResearchInput) -> RepoAnalysis:
        """分析单个仓库"""
        analysis = RepoAnalysis(
            full_name=repo.full_name,
            url=repo.html_url,
            stars=repo.stargazers_count,
            forks=repo.forks_count,
            description=repo.description or "",
            language=repo.language or "Unknown",
            last_updated=repo.updated_at.isoformat() if repo.updated_at else "",
            topics=repo.get_topics()[:10]
        )
        
        # 计算综合评分
        analysis.score = self._calc_score(repo)
        
        # 提取README
        if params.extract_readme:
            analysis.readme_summary = self._extract_readme(repo)
        
        # 提取目录结构
        if params.extract_structure:
            analysis.structure = self._extract_structure(repo)
        
        # 提取依赖
        if params.extract_deps:
            analysis.dependencies = self._extract_dependencies(repo)
        
        return analysis
    
    def _calc_score(self, repo: Repository) -> float:
        """计算仓库质量评分"""
        score = 0.0
        
        # Star 分数 (0-40)
        score += min(repo.stargazers_count / 100, 40)
        
        # 活跃度分数 (0-30)
        days_since_update = (datetime.now() - repo.updated_at.replace(tzinfo=None)).days
        if days_since_update < 30:
            score += 30
        elif days_since_update < 90:
            score += 20
        elif days_since_update < 365:
            score += 10
        
        # Fork 分数 (0-20)
        score += min(repo.forks_count / 50, 20)
        
        # Issue 响应分数 (0-10)
        if repo.open_issues_count < 50:
            score += 10
        elif repo.open_issues_count < 200:
            score += 5
        
        return round(score, 1)
    
    def _extract_readme(self, repo: Repository, max_chars: int = 1500) -> str:
        """提取README摘要"""
        try:
            readme = repo.get_readme()
            content = base64.b64decode(readme.content).decode('utf-8')
            # 清理并截断
            lines = content.split('\n')
            # 提取关键部分：标题、特性、安装、使用
            summary = []
            for line in lines:
                line = line.strip()
                if line.startswith('# ') or line.startswith('## '):
                    summary.append(line)
                elif line.startswith('- ') and len(summary) < 20:
                    summary.append(line)
                elif len('\n'.join(summary)) > max_chars:
                    break
            
            result = '\n'.join(summary)
            if len(result) > max_chars:
                result = result[:max_chars] + "\n..."
            return result
            
        except Exception as e:
            return f"*(README提取失败: {e})*"
    
    def _extract_structure(self, repo: Repository, max_depth: int = 2) -> List[str]:
        """提取目录结构"""
        try:
            contents = repo.get_contents("")
            structure = []
            
            for item in contents:
                if item.type == "dir":
                    structure.append(f"📁 {item.path}/")
                    # 只展开一层子目录
                    try:
                        sub_contents = repo.get_contents(item.path)
                        for sub in sub_contents[:5]:  # 限制数量
                            if sub.type == "dir":
                                structure.append(f"   📁 {sub.path}/")
                            else:
                                structure.append(f"   📄 {sub.path}")
                    except:
                        pass
                else:
                    structure.append(f"📄 {item.path}")
            
            return structure[:30]  # 限制总数
            
        except Exception as e:
            return [f"*(结构提取失败: {e})*"]
    
    def _extract_dependencies(self, repo: Repository) -> Dict[str, List[str]]:
        """提取依赖文件"""
        deps = {}
        
        # Python 依赖
        for filename in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
            try:
                content = repo.get_contents(filename)
                text = base64.b64decode(content.content).decode('utf-8')
                lines = [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('#')]
                deps[filename] = lines[:20]  # 限制数量
            except:
                pass
        
        # Node 依赖
        for filename in ["package.json"]:
            try:
                content = repo.get_contents(filename)
                text = base64.b64decode(content.content).decode('utf-8')
                data = json.loads(text)
                deps_list = []
                if 'dependencies' in data:
                    deps_list.extend([f"{k}@{v}" for k, v in list(data['dependencies'].items())[:15]])
                if 'devDependencies' in data:
                    deps_list.extend([f"{k}@{v}" for k, v in list(data['devDependencies'].items())[:5]])
                deps[filename] = deps_list
            except:
                pass
        
        return deps
    
    def generate_report(self, results: List[RepoAnalysis], query: str) -> str:
        """生成预研报告"""
        report = []
        report.append(f"# 🔍 GitHub 预研报告: {query}")
        report.append(f"\n> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"> 共分析 {len(results)} 个高星项目\n")
        
        for i, repo in enumerate(results, 1):
            report.append(f"## {i}. {repo.full_name} (评分: {repo.score})")
            report.append(f"- ⭐ Stars: {repo.stars} | 🍴 Forks: {repo.forks}")
            report.append(f"- 🏷️ 语言: {repo.language} | 更新: {repo.last_updated[:10]}")
            report.append(f"- 🔗 {repo.url}")
            if repo.topics:
                report.append(f"- 🏷️ Topics: {', '.join(repo.topics[:5])}")
            report.append(f"\n**描述**: {repo.description}\n")
            
            if repo.readme_summary:
                report.append("**README 核心**:")
                report.append("```markdown")
                report.append(repo.readme_summary)
                report.append("```\n")
            
            if repo.structure:
                report.append("**目录结构**:")
                report.append("```")
                for item in repo.structure[:15]:
                    report.append(item)
                report.append("```\n")
            
            if repo.dependencies:
                report.append("**依赖文件**:")
                for filename, items in repo.dependencies.items():
                    report.append(f"- `{filename}`: {', '.join(items[:5])}...")
                report.append("")
        
        # 添加建议
        report.append("---\n")
        report.append("## 💡 技术方案建议\n")
        
        if results:
            best = results[0]
            report.append(f"### 推荐参考: {best.full_name}")
            report.append(f"- 采用其目录结构组织方式")
            if best.dependencies:
                deps_file = list(best.dependencies.keys())[0]
                report.append(f"- 参考其 `{deps_file}` 的依赖选择")
            report.append(f"- 学习其 README 文档结构\n")
        
        report.append("### 实现 checklist")
        report.append("- [ ] 复用推荐项目的架构设计")
        report.append("- [ ] 引入经过验证的依赖库")
        report.append("- [ ] 遵循开源项目的代码规范")
        report.append("- [ ] 添加完整的文档和示例")
        
        return "\n".join(report)


def search_and_learn_github(
    query: str,
    language: str = "python",
    min_stars: int = 50,
    max_results: int = 3
) -> str:
    """
    在 GitHub 上搜索相似项目并生成技术方案建议。
    编程前必须调用此工具！
    """
    try:
        tool = GitHubResearchPro()
        params = GitHubResearchInput(
            query=query,
            language=language,
            min_stars=min_stars,
            max_results=max_results
        )
        
        results = tool.search(params)
        if not results:
            return "⚠️ 未找到符合条件的开源项目，建议调整关键词后重试。"
        
        return tool.generate_report(results, query)
        
    except ValueError as e:
        return f"❌ 配置错误: {e}\n请设置 GITHUB_TOKEN 环境变量。"
    except Exception as e:
        return f"❌ 执行错误: {e}"


# Hermes Tool 元数据
TOOL_METADATA = {
    "name": "github_research_pro",
    "description": "编程前必须调用：搜索GitHub相似开源项目，学习架构设计和实现思路。",
    "input_schema": GitHubResearchInput.schema(),
    "func": search_and_learn_github
}


if __name__ == "__main__":
    # 测试 + 自进化演示
    print("🧪 测试 GitHub Research Pro (含自进化)")
    
    # 显示当前进化状态
    stats = tracker.analyze()
    if stats:
        print(f"📊 历史会话: {stats.get('total_sessions', 0)}次")
        print(f"📊 平均质量: {stats.get('avg_quality', 'N/A')}")
        print(f"📊 错误率: {stats.get('error_rate', 'N/A')}")
    
    rules = tracker.get_rules()
    if rules:
        print(f"🧬 当前规则: min_stars={rules.get('min_stars_default')}, max_results={rules.get('max_results_default')}")
    
    if not GITHUB_TOKEN:
        print("⚠️ 未设置 GITHUB_TOKEN，跳过测试")
        exit(0)
    
    result = search_and_learn_github(
        query="python web scraping framework",
        language="python",
        min_stars=100,
        max_results=2
    )
    print(result)
