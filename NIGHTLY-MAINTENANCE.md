# NIGHTLY-MAINTENANCE.md - 夜间自我维护系统

## 执行计划

### 23:00 - 维护开始
运行 `scripts/nightly-maintenance.sh`

**任务清单**:
1. ✅ 系统健康检查 (openclaw status, openclaw doctor)
2. ✅ 安全扫描 (配置文件权限、异常进程检测)
3. ✅ 记忆整理 (分析昨日对话，提取关键信息)
4. ✅ 学习更新 (检查技能状态，寻找改进点)
5. ✅ 生成报告 (保存到 memory/nightly-reports/)

### 08:00 - 早间汇报
运行 `scripts/morning-report.sh`

**汇报内容**:
- 系统整体状态
- 发现的安全问题
- 记忆更新摘要
- 建议操作

## 手动触发

```bash
# 夜间维护
/Users/zhaozhiguo/.openclaw/workspace/scripts/nightly-maintenance.sh

# 早间汇报
/Users/zhaozhiguo/.openclaw/workspace/scripts/morning-report.sh
```

## 报告位置

- 详细报告: `memory/nightly-reports/YYYY-MM-DD.md`
- 运行日志: `logs/nightly-YYYY-MM-DD.log`

## 自动化状态

- [x] 维护脚本已创建
- [x] 汇报脚本已创建
- [ ] 需要配置 cron 定时任务（需要用户授权）

## 注意事项

目前脚本需要手动运行或配置系统 cron。OpenClaw 的 cron 插件如果可用，可以改用：

```bash
openclaw cron add --name nightly --schedule "0 23 * * *" --command "/Users/zhaozhiguo/.openclaw/workspace/scripts/nightly-maintenance.sh"
openclaw cron add --name morning --schedule "0 8 * * *" --command "/Users/zhaozhiguo/.openclaw/workspace/scripts/morning-report.sh"
```
