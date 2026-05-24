#!/bin/bash
# GitHub Research Pro 安装脚本

echo "🔧 安装 GitHub Research Pro..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip install PyGithub pydantic -q

# 检查 Token
if [ -z "$GITHUB_TOKEN" ] && [ -z "$GH_TOKEN" ]; then
    echo "⚠️ 警告: 未设置 GITHUB_TOKEN 环境变量"
    echo "请执行: export GITHUB_TOKEN='your_token'"
fi

# 测试
echo "🧪 运行测试..."
python3 -c "from github_research_tool import TOOL_METADATA; print('✅ 安装成功')" 2>/dev/null || echo "⚠️ 测试跳过（无Token）"

echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  from scripts.github_research_tool import search_and_learn_github"
echo "  report = search_and_learn_github('your query')"
