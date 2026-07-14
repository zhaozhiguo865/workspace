#!/usr/bin/env python3
"""
微信公众号图文消息专用脚本
支持更完整的图文消息发布功能
"""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from platforms.wechat_mp import WechatMPPlatform


def load_config():
    """加载配置文件"""
    config_path = Path.home() / ".openclaw" / "config" / "auto-poster.json"
    
    if not config_path.exists():
        print(f"配置文件不存在: {config_path}")
        sys.exit(1)
    
    with open(config_path, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="微信公众号图文消息发布工具")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--content", required=True, help="文章内容（支持HTML）")
    parser.add_argument("--digest", help="文章摘要（可选）")
    parser.add_argument("--author", help="作者名称")
    parser.add_argument("--thumb", help="封面图片路径")
    parser.add_argument("--source-url", help="原文链接")
    parser.add_argument("--preview", help="预览模式：接收者的微信号")
    parser.add_argument("--dry-run", action="store_true", help="测试模式")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("=" * 60)
        print("🧪 测试模式 - 不会实际发布")
        print("=" * 60)
        print(f"\n标题: {args.title}")
        print(f"作者: {args.author or '未设置'}")
        print(f"摘要: {args.digest or '自动提取'}")
        print(f"封面: {args.thumb or '未设置'}")
        print(f"原文链接: {args.source_url or '无'}")
        print(f"\n内容预览:\n{args.content[:500]}...")
        return
    
    # 加载配置
    config = load_config()
    mp_config = config.get("wechat_mp", {})
    
    if not mp_config:
        print("错误: 未找到微信公众号配置")
        sys.exit(1)
    
    # 初始化平台
    platform = WechatMPPlatform(mp_config)
    
    if not platform.login():
        print("错误: 微信公众号登录失败，请检查 AppID 和 AppSecret")
        sys.exit(1)
    
    print("✅ 微信公众号登录成功")
    
    # 上传封面图
    thumb_media_id = None
    if args.thumb:
        print(f"📤 正在上传封面图: {args.thumb}")
        thumb_media_id = platform.upload_thumb(args.thumb)
        if thumb_media_id:
            print(f"✅ 封面上传成功")
        else:
            print("⚠️ 封面上传失败，将使用默认封面")
    
    # 预览模式
    if args.preview:
        print(f"📤 发送预览给: {args.preview}")
        result = platform.preview_message(
            title=args.title,
            content=args.content,
            wxname=args.preview
        )
        
        if result.get("success"):
            print("✅ 预览消息已发送")
        else:
            print(f"❌ 预览发送失败: {result.get('error')}")
        return
    
    # 发布图文消息
    print("📤 正在发布图文消息...")
    result = platform.post_article(
        title=args.title,
        content=args.content,
        digest=args.digest or args.content[:100] + "...",
        author=args.author or "",
        thumb_media_id=thumb_media_id,
        content_source_url=args.source_url or ""
    )
    
    if result.get("success"):
        print("✅ 图文消息发布成功！")
        print(f"   消息ID: {result.get('post_id')}")
        print(f"   素材ID: {result.get('media_id')}")
    else:
        print(f"❌ 发布失败: {result.get('error')}")


if __name__ == "__main__":
    main()