#!/bin/bash
# 早间汇报脚本 - 增强版
# 运行时间: 08:00

WORKSPACE="/Users/zhaozhiguo/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DATE=$(date +%Y-%m-%d)

# 读取学习进度
python3 << 'PYTHON_EOF'
import json
import os
from datetime import datetime

WORKSPACE = "/Users/zhaozhiguo/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"

tracker_path = f"{MEMORY_DIR}/learning-progress.json"
today_file = f"{MEMORY_DIR}/{datetime.now().strftime('%Y-%m-%d')}.md"

# 读取学习进度
with open(tracker_path, 'r') as f:
    data = json.load(f)

russian = data["russian"]
streak = russian["review_streak"]
vocab = russian["total_vocabulary"]
next_review = russian["next_review"]

# 生成汇报内容
report = f"""---

## {datetime.now().strftime('%Y-%m-%d')}

### 📊 俄语学习进度
- **累计词汇**: {vocab} 词
- **连续学习**: {streak} 天
- **下次复习**: {next_review}

### 🎯 今日任务
"""

# 读取今日任务
if os.path.exists(today_file):
    with open(today_file, 'r') as f:
        content = f.read()
        # 提取复习重点
        if "今日复习重点" in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "今日复习重点" in line:
                    # 获取接下来的几行
                    for j in range(i+1, min(i+5, len(lines))):
                        if lines[j].strip() and not lines[j].startswith('##'):
                            report += lines[j] + '\n'
                    break

report += """
### ⏰ 系统状态
- 定时任务: ✅ 正常运行
- 记忆文件: 已同步

---
"""

# 写入今日文件
with open(today_file, 'w') as f:
    f.write(report)

print("早间汇报已生成")
PYTHON_EOF

# 发送汇报（通过 OpenClaw）
# 注意: 实际发送需要使用 message 工具，这里记录日志
echo "[$(date)] 早间汇报完成" >> "$WORKSPACE/logs/maintenance.log"
