#!/bin/sh
# 正式运行前清理缓存，避免之前的运行影响下次。
# 用法: ./clean_cache.sh  或  sh clean_cache.sh

set -e
cd "$(dirname "$0")"

echo "清理项目缓存..."

# 1. Python 字节码缓存（仅项目代码，排除 .venv）
find . -name "__pycache__" -type d -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true

# 2. ADK 本地存储（adk web 的 artifact / session 持久化目录）
if [ -d ".adk" ]; then
  rm -rf .adk
  echo "  已删除 .adk"
fi

# 3. Identity 工具写入的 profile 输出（避免被下次运行误读）
if [ -f "my_agent/tests/my_tests.test.json" ]; then
  rm -f my_agent/tests/my_tests.test.json
  echo "  已删除 my_agent/tests/my_tests.test.json"
fi

echo "缓存清理完成。可运行 adk web 或 python main.py。"
