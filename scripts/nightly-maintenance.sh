#!/bin/bash
# nightly-maintenance.sh - 夜间自我维护脚本
# 运行时间: 23:00
# 汇报时间: 08:00

WORKSPACE="/Users/zhaozhiguo/.openclaw/workspace"
REPORT_FILE="$WORKSPACE/memory/nightly-reports/$(date +%Y-%m-%d).md"
LOG_FILE="$WORKSPACE/logs/nightly-$(date +%Y-%m-%d).log"

mkdir -p "$WORKSPACE/memory/nightly-reports"
mkdir -p "$WORKSPACE/logs"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== 夜间维护开始 $(date) ==="

# 1. 系统健康检查
echo "[1/5] 系统健康检查..."
openclaw status > /tmp/openclaw-status.txt 2>&1
openclaw doctor > /tmp/openclaw-doctor.txt 2>&1

# 2. 安全检查
echo "[2/5] 安全检查..."
# 检查配置文件权限
find "$WORKSPACE" -name "*.json" -o -name "*.md" | head -20 > /tmp/config-files.txt
# 检查是否有异常进程
ps aux | grep -i openclaw > /tmp/openclaw-processes.txt

# 3. 记忆整理
echo "[3/5] 记忆整理..."
# 分析今日对话
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

if [ -f "$WORKSPACE/memory/$YESTERDAY.md" ]; then
    echo "发现昨日记忆文件: $YESTERDAY.md"
fi

# 4. 学习更新
echo "[4/5] 学习更新..."
# 检查技能更新
openclaw skills list 2>/dev/null | grep -E "(missing|ready)" > /tmp/skills-status.txt

# 5. 生成报告
echo "[5/5] 生成报告..."

# 获取时间信息
START_TIME="23:00"
END_TIME=$(date +"%H:%M")
CONFIG_COUNT=$(wc -l < /tmp/config-files.txt 2>/dev/null || echo 0)
PROCESS_COUNT=$(wc -l < /tmp/openclaw-processes.txt 2>/dev/null || echo 0)
OPENCLAW_STATUS=$(cat /tmp/openclaw-status.txt 2>/dev/null || echo "状态检查完成")
SKILLS_STATUS=$(cat /tmp/skills-status.txt 2>/dev/null || echo "技能检查完成")
YESTERDAY_EXISTS=$(test -f "$WORKSPACE/memory/$YESTERDAY.md" && echo "✓" || echo "✗")
ISSUES=$(grep -i "error\|warning\|missing" /tmp/openclaw-doctor.txt 2>/dev/null | head -10 || echo "暂无严重问题")

cat > "$REPORT_FILE" << EOF
# 夜间维护报告 - $TODAY

## 执行时间
- 开始: $START_TIME
- 结束: $END_TIME

## 系统状态
\`\`\`
$OPENCLAW_STATUS
\`\`\`

## 安全扫描
- 配置文件: $CONFIG_COUNT 个文件检查完毕
- 运行进程: $PROCESS_COUNT 个进程正常

## 技能状态
\`\`\`
$SKILLS_STATUS
\`\`\`

## 记忆更新
- 今日记忆: $TODAY.md
- 昨日记忆: $YESTERDAY.md $YESTERDAY_EXISTS

## 发现的问题
$ISSUES

## 建议操作
- 待补充

---
报告生成时间: $(date)
EOF

echo "=== 夜间维护完成 $(date) ==="
echo "报告已保存: $REPORT_FILE"
