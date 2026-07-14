#!/bin/bash
# setup-launchd.sh - 配置macOS定时任务

WORKSPACE="/Users/zhaozhiguo/.openclaw/workspace"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$LAUNCHD_DIR"
mkdir -p "$WORKSPACE/logs"

echo "=== OpenClaw 定时任务配置 ==="
echo ""

# 复制plist文件
cp "$WORKSPACE/scripts/com.openclaw.nightly-maintenance.plist" "$LAUNCHD_DIR/"
cp "$WORKSPACE/scripts/com.openclaw.morning-report.plist" "$LAUNCHD_DIR/"

# 加载任务
echo "加载夜间维护任务 (23:00)..."
launchctl load "$LAUNCHD_DIR/com.openclaw.nightly-maintenance.plist" 2>/dev/null || echo "任务已加载或需要手动加载"

echo "加载早间汇报任务 (08:00)..."
launchctl load "$LAUNCHD_DIR/com.openclaw.morning-report.plist" 2>/dev/null || echo "任务已加载或需要手动加载"

echo ""
echo "=== 配置完成 ==="
echo ""
echo "查看任务状态:"
echo "  launchctl list | grep openclaw"
echo ""
echo "手动运行测试:"
echo "  launchctl start com.openclaw.nightly-maintenance"
echo "  launchctl start com.openclaw.morning-report"
echo ""
echo "查看日志:"
echo "  tail -f $WORKSPACE/logs/nightly.log"
echo "  tail -f $WORKSPACE/logs/morning.log"