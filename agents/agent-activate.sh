#!/bin/bash
# agent-activate.sh - AI员工激活脚本

WORKSPACE="/Users/zhaozhiguo/.openclaw/workspace"
AGENT_NAME=$1
TASK=$2

# 映射表
declare -A AGENT_MAP=(
    ["码神"]="tech-ai"
    ["爆点"]="ops-ai"
    ["雷达"]="market-ai"
    ["鹰眼"]="overseer-ai"
    ["成交"]="sales-ai"
    ["算盘"]="finance-ai"
    ["笔杆子"]="copy-ai"
    ["话筒"]="pr-ai"
    ["架构师"]="product-ai"
    ["小天使"]="hr-ai"
    ["先锋"]="legal-ai"
)

if [ -z "$AGENT_NAME" ] || [ -z "$TASK" ]; then
    echo "用法: ./agent-activate.sh <AI名称> <任务描述>"
    echo ""
    echo "可用AI:"
    for name in "${!AGENT_MAP[@]}"; do
        echo "  - $name"
    done
    exit 1
fi

FILE_NAME=${AGENT_MAP[$AGENT_NAME]}
if [ -z "$FILE_NAME" ]; then
    echo "未知AI: $AGENT_NAME"
    exit 1
fi

PROMPT_FILE="$WORKSPACE/agents/prompts/$FILE_NAME.md"
if [ ! -f "$PROMPT_FILE" ]; then
    echo "找不到AI配置文件: $PROMPT_FILE"
    exit 1
fi

# 读取prompt
echo "=== 激活 $AGENT_NAME ==="
echo ""
cat "$PROMPT_FILE"
echo ""
echo "=== 当前任务 ==="
echo "$TASK"
echo ""
echo "=== 开始执行 ==="
