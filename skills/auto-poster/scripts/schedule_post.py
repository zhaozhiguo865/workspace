#!/usr/bin/env python3
"""
定时发帖脚本
使用系统 cron 或 at 命令实现定时发布
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def create_cron_job(platform: str, content: str, schedule_time: str, image_paths: list = None):
    """创建定时任务"""
    
    # 解析时间
    try:
        dt = datetime.strptime(schedule_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("时间格式错误，请使用: YYYY-MM-DD HH:MM:SS")
        sys.exit(1)
    
    # 构建命令
    script_path = Path(__file__).parent / "post.py"
    
    cmd_parts = [
        sys.executable,
        str(script_path),
        "--platform", platform,
        "--content", content
    ]
    
    if image_paths:
        cmd_parts.extend(["--image"] + image_paths)
    
    cmd = " ".join(f'"{part}"' for part in cmd_parts)
    
    # 使用 at 命令（macOS/Linux）
    at_time = dt.strftime("%H:%M %m%d%y")
    
    at_cmd = f'echo "{cmd}" | at {at_time}'
    
    try:
        result = subprocess.run(at_cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 定时任务已创建")
            print(f"   执行时间: {schedule_time}")
            print(f"   平台: {platform}")
            print(f"   任务ID: {result.stdout.strip()}")
        else:
            print(f"❌ 创建失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def list_scheduled_jobs():
    """列出所有定时任务"""
    try:
        result = subprocess.run(["atq"], capture_output=True, text=True)
        if result.stdout:
            print("📋 定时任务列表:")
            print(result.stdout)
        else:
            print("暂无定时任务")
    except Exception as e:
        print(f"无法获取任务列表: {e}")


def remove_job(job_id: str):
    """删除定时任务"""
    try:
        result = subprocess.run(["atrm", job_id], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 任务 {job_id} 已删除")
        else:
            print(f"❌ 删除失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 错误: {e}")


def main():
    parser = argparse.ArgumentParser(description="定时发帖工具")
    parser.add_argument("--platform", help="目标平台")
    parser.add_argument("--content", help="帖子内容")
    parser.add_argument("--image", nargs="+", help="图片路径")
    parser.add_argument("--time", help="发布时间 (YYYY-MM-DD HH:MM:SS)")
    parser.add_argument("--list", action="store_true", help="列出所有定时任务")
    parser.add_argument("--remove", help="删除指定任务ID")
    
    args = parser.parse_args()
    
    if args.list:
        list_scheduled_jobs()
        return
    
    if args.remove:
        remove_job(args.remove)
        return
    
    if not all([args.platform, args.content, args.time]):
        print("错误: 必须提供 --platform, --content 和 --time")
        parser.print_help()
        sys.exit(1)
    
    create_cron_job(args.platform, args.content, args.time, args.image)


if __name__ == "__main__":
    main()