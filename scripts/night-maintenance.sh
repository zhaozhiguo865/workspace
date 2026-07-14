#!/bin/bash
# 夜间维护脚本 - 增强版
# 运行时间: 23:00

WORKSPACE="/Users/zhaozhiguo/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)
YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)

# 创建今日记忆文件
TODAY_FILE="$MEMORY_DIR/$DATE.md"
if [ ! -f "$TODAY_FILE" ]; then
    cat > "$TODAY_FILE" << EOF
---

## $DATE

_等待记录..._

---
EOF
    echo "[$(date)] 创建今日记忆文件: $TODAY_FILE" >> "$WORKSPACE/logs/maintenance.log"
fi

# 学习进度追踪
LEARNING_TRACKER="$MEMORY_DIR/learning-progress.json"
if [ ! -f "$LEARNING_TRACKER" ]; then
    cat > "$LEARNING_TRACKER" << 'EOF'
{
  "russian": {
    "total_vocabulary": 3153,
    "last_review": "",
    "review_streak": 0,
    "next_review": "",
    "weak_points": [],
    "mastered": []
  },
  "last_updated": ""
}
EOF
fi

# 更新学习进度
python3 << 'PYTHON_EOF'
import json
import os
from datetime import datetime, timedelta

WORKSPACE = "/Users/zhaozhiguo/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"

tracker_path = f"{MEMORY_DIR}/learning-progress.json"

with open(tracker_path, 'r') as f:
    data = json.load(f)

today = datetime.now().strftime("%Y-%m-%d")
data["russian"]["last_review"] = today
data["russian"]["review_streak"] += 1

# 基于遗忘曲线设置下次复习时间 (1, 3, 7, 14, 30 天)
streak = data["russian"]["review_streak"]
intervals = [1, 3, 7, 14, 30]
if streak < len(intervals):
    next_days = intervals[streak]
else:
    next_days = 30

next_review = (datetime.now() + timedelta(days=next_days)).strftime("%Y-%m-%d")
data["russian"]["next_review"] = next_review
data["last_updated"] = today

with open(tracker_path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"学习进度已更新，下次复习: {next_review}")
PYTHON_EOF

# 生成明日学习任务
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "tomorrow" +%Y-%m-%d)
TOMORROW_FILE="$MEMORY_DIR/$TOMORROW.md"

if [ ! -f "$TOMORROW_FILE" ]; then
    # 从学习进度获取复习内容
    REVIEW_CONTENT=$(python3 << 'PYTHON_EOF'
import json
import random

MEMORY_DIR = "/Users/zhaozhiguo/.openclaw/workspace/memory"

# 随机选择复习内容
topics = [
    "动词体 (вид глагола) - 未完成体 vs 完成体",
    "数字 1-100",
    "时间表达 (который час?)",
    "星期 (понедельник-воскресенье)",
    "专业词汇 - 科技/经济/政治",
    "购物场景对话",
    "形容词性数一致"
]

print(random.choice(topics))
PYTHON_EOF
)

    cat > "$TOMORROW_FILE" << EOF
---

## $TOMORROW

### 🎯 今日复习重点
$REVIEW_CONTENT

### 📚 学习记录

---
EOF
    echo "[$(date)] 创建明日学习任务: $TOMORROW_FILE" >> "$WORKSPACE/logs/maintenance.log"
fi

# 整理记忆文件（归档旧文件）
find "$MEMORY_DIR" -name "*.md" -mtime +30 -type f | while read file; do
    filename=$(basename "$file")
    if [[ ! "$filename" =~ ^russian- ]] && [[ "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
        mkdir -p "$MEMORY_DIR/archive"
        mv "$file" "$MEMORY_DIR/archive/"
        echo "[$(date)] 归档旧文件: $filename" >> "$WORKSPACE/logs/maintenance.log"
    fi
done

# 更新心跳状态
HEARTBEAT_STATE="$MEMORY_DIR/heartbeat-state.json"
cat > "$HEARTBEAT_STATE" << EOF
{
  "lastChecks": {
    "maintenance": "$(date +%s)",
    "learning_review": "$(date +%s)"
  },
  "next_scheduled": {
    "morning_report": "$(date -v+9H +%Y-%m-%dT08:00:00 2>/dev/null || date -d '+9 hours' +%Y-%m-%dT08:00:00)"
  }
}
EOF

echo "[$(date)] 夜间维护完成" >> "$WORKSPACE/logs/maintenance.log"
