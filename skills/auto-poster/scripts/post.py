#!/usr/bin/env python3
"""
自动发帖脚本 - 主入口
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from platforms import WeiboPlatform, TwitterPlatform, BilibiliPlatform, ZhihuPlatform, WechatMPPlatform, XiaohongshuPlatform

# 平台映射
PLATFORM_MAP = {
    "weibo": WeiboPlatform,
    "twitter": TwitterPlatform,
    "bilibili": BilibiliPlatform,
    "zhihu": ZhihuPlatform,
    "wechat_mp": WechatMPPlatform,
    "xiaohongshu": XiaohongshuPlatform,
}


def load_config():
    """加载配置文件"""
    config_path = Path.home() / ".openclaw" / "config" / "auto-poster.json"
    
    if not config_path.exists():
        print(f"配置文件不存在: {config_path}")
        print("请先创建配置文件，参考 SKILL.md 中的配置示例")
        sys.exit(1)
    
    with open(config_path, "r") as f:
        return json.load(f)


def load_template(template_name: str, vars_dict: dict = None) -> str:
    """加载并渲染模板"""
    template_path = Path(__file__).parent.parent / "templates" / f"{template_name}.md"
    
    if not template_path.exists():
        print(f"模板不存在: {template_path}")
        sys.exit(1)
    
    with open(template_path, "r") as f:
        content = f.read()
    
    # 简单的变量替换
    if vars_dict:
        for key, value in vars_dict.items():
            content = content.replace(f"{{{{{key}}}}}", value)
    
    return content


def parse_vars(vars_str: str) -> dict:
    """解析变量字符串 key=value,key2=value2"""
    result = {}
    if not vars_str:
        return result
    
    for item in vars_str.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            result[key.strip()] = value.strip()
    
    return result


def post_to_platform(platform_name: str, content: str, image_paths: list = None, config: dict = None):
    """向指定平台发帖"""
    if platform_name not in PLATFORM_MAP:
        print(f"不支持的平台: {platform_name}")
        print(f"支持的平台: {', '.join(PLATFORM_MAP.keys())}")
        return False
    
    if config is None:
        config = load_config()
    
    platform_config = config.get(platform_name, {})
    if not platform_config:
        print(f"未找到 {platform_name} 的配置")
        return False
    
    try:
        platform_class = PLATFORM_MAP[platform_name]
        platform = platform_class(platform_config)
        
        result = platform.post(content, image_paths)
        
        if result.get("success"):
            print(f"✅ {platform_name} 发帖成功")
            print(f"   链接: {result.get('url')}")
            if result.get('image_count'):
                print(f"   图片: {result['image_count']} 张")
        else:
            print(f"❌ {platform_name} 发帖失败")
            print(f"   错误: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ {platform_name} 异常: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="自动发帖工具")
    parser.add_argument("--platform", required=True, help="目标平台，多个平台用逗号分隔")
    parser.add_argument("--content", help="帖子内容")
    parser.add_argument("--image", nargs="+", help="图片路径")
    parser.add_argument("--template", help="使用模板")
    parser.add_argument("--vars", help="模板变量 (key=value,key2=value2)")
    parser.add_argument("--dry-run", action="store_true", help="测试模式，不实际发布")
    
    args = parser.parse_args()
    
    # 获取内容
    if args.template:
        vars_dict = parse_vars(args.vars) if args.vars else {}
        content = load_template(args.template, vars_dict)
    elif args.content:
        content = args.content
    else:
        print("错误: 必须提供 --content 或 --template")
        sys.exit(1)
    
    # 测试模式
    if args.dry_run:
        print("=" * 50)
        print("🧪 测试模式 - 不会实际发布")
        print("=" * 50)
        print(f"\n内容预览:\n{content}\n")
        if args.image:
            print(f"图片: {args.image}")
        print(f"平台: {args.platform}")
        return
    
    # 加载配置
    config = load_config()
    
    # 解析平台列表
    platforms = [p.strip() for p in args.platform.split(",")]
    
    # 向各平台发帖
    results = []
    for platform_name in platforms:
        success = post_to_platform(
            platform_name, 
            content, 
            args.image,
            config
        )
        results.append((platform_name, success))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 发布结果汇总")
    print("=" * 50)
    for platform_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{platform_name}: {status}")


if __name__ == "__main__":
    main()