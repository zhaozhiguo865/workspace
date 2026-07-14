---
name: auto-poster
description: 自动发帖技能，支持在多个社交媒体平台自动发布内容。当用户需要"自动发帖"、"定时发布"、"批量发帖"、"在XX平台发帖"时使用此技能。支持平台包括：微博、Twitter/X、微信公众号、小红书、抖音、B站、知乎等。可以设置定时发布、多平台同步、内容模板等功能。
---

# 自动发帖技能

## 功能概述

本技能提供自动化社交媒体内容发布能力，支持：
- 单平台/多平台同步发帖
- 定时发布
- 内容模板管理
- 批量发帖
- 发布状态追踪

## 支持平台

| 平台 | 状态 | 说明 |
|------|------|------|
| 微博 | ✅ 支持 | 需配置 Cookie/Token |
| Twitter/X | ✅ 支持 | 需配置 API Key |
| 微信公众号 | ✅ 支持 | 需配置 AppID/AppSecret，支持图文消息 |
| 小红书 | ✅ 支持 | 需配置 Cookie |
| 抖音 | 🔄 开发中 | 需配置 Cookie |
| B站 | ✅ 支持 | 需配置 Cookie/Token |
| 知乎 | ✅ 支持 | 需配置 Cookie |

## 使用方法

### 1. 配置平台凭证

首次使用需要在 `~/.openclaw/config/auto-poster.json` 中配置各平台的访问凭证：

```json
{
  "weibo": {
    "cookie": "your_weibo_cookie_here",
    "uid": "your_uid"
  },
  "twitter": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret"
  },
  "wechat_mp": {
    "appid": "your_appid",
    "appsecret": "your_appsecret",
    "default_thumb_media_id": "optional_default_cover_media_id"
  },
  "bilibili": {
    "cookie": "your_bilibili_cookie",
    "buvid3": "your_buvid3"
  },
  "zhihu": {
    "cookie": "your_zhihu_cookie"
  },
  "xiaohongshu": {
    "cookie": "your_xiaohongshu_cookie"
  }
}
```

### 2. 立即发帖

```bash
# 发微博
python scripts/post.py --platform weibo --content "这是一条测试微博"

# 发 Twitter
python scripts/post.py --platform twitter --content "Hello World!"

# 发小红书（必须带图片）
python scripts/post.py --platform xiaohongshu --content "今日分享 #生活记录#" --image /path/to/image.jpg

# 多平台同步
python scripts/post.py --platform weibo,twitter,bilibili --content "多平台同步测试"
```

### 3. 定时发帖

```bash
# 使用 cron 设置定时任务
python scripts/schedule_post.py --platform weibo --content "定时内容" --time "2024-01-01 12:00:00"
```

### 4. 微信公众号图文消息

```bash
# 发布图文消息
python scripts/wechat_article.py --title "文章标题" --content "<p>文章内容</p>"

# 带封面图
python scripts/wechat_article.py --title "文章标题" --content "<p>内容</p>" --thumb /path/to/cover.jpg

# 预览模式（先发给指定微信号预览）
python scripts/wechat_article.py --title "测试" --content "内容" --preview wxname123

# 完整示例
python scripts/wechat_article.py \
  --title "今日推荐" \
  --content "<p>这是一篇测试文章</p><p>第二段内容</p>" \
  --digest "文章摘要" \
  --author "大卡" \
  --thumb /path/to/cover.jpg \
  --source-url "https://example.com/original"
```

### 5. 使用模板

```bash
# 从模板发帖
python scripts/post.py --platform weibo --template daily_greeting --vars "name=大卡,date=2024-01-01"
```

## 模板系统

模板存储在 `templates/` 目录下：

```
templates/
├── daily_greeting.md    # 日常问候模板
├── product_promo.md     # 产品推广模板
└── custom/              # 自定义模板
```

模板示例 (`daily_greeting.md`):
```markdown
---
name: daily_greeting
variables:
  - name
  - date
---

早安 {{name}}！今天是 {{date}}，祝你有个美好的一天！☀️
```

## 脚本说明

### post.py - 立即发帖

```bash
python scripts/post.py [选项]

选项:
  --platform PLATFORM    目标平台 (weibo/twitter/wechat/bilibili/zhihu)
  --content CONTENT      帖子内容
  --image IMAGE_PATH     图片路径 (可选)
  --template TEMPLATE    使用模板名称
  --vars VARS            模板变量 (key=value,key2=value2)
  --dry-run              测试模式，不实际发布
```

### schedule_post.py - 定时发帖

```bash
python scripts/schedule_post.py [选项]

选项:
  --platform PLATFORM    目标平台
  --content CONTENT      帖子内容
  --time TIME            发布时间 (YYYY-MM-DD HH:MM:SS)
  --recurring CRON       重复规则 (cron 表达式)
```

### batch_post.py - 批量发帖

```bash
python scripts/batch_post.py --file posts.csv

# CSV 格式:
# platform,content,image,scheduled_time
# weibo,"内容1",,/path/to/img1.jpg,2024-01-01 10:00:00
# twitter,"内容2",,2024-01-01 11:00:00
```

## 安全注意事项

1. **凭证安全**: 配置文件包含敏感信息，确保设置正确的文件权限:
   ```bash
   chmod 600 ~/.openclaw/config/auto-poster.json
   ```

2. **频率限制**: 各平台都有发帖频率限制，脚本内置了延迟和重试机制

3. **内容审核**: 自动发帖前建议开启 `--dry-run` 模式预览内容

## 故障排查

### 发帖失败

1. 检查凭证是否过期
2. 查看平台是否更新了接口
3. 检查网络连接
4. 查看日志文件 `logs/auto-poster.log`

### 更新凭证

```bash
# 重新配置单个平台
python scripts/config.py --platform weibo --update
```

## 扩展开发

添加新平台支持：

1. 在 `scripts/platforms/` 创建新的平台模块
2. 实现 `BasePlatform` 接口
3. 在 `post.py` 中注册新平台

参考 `scripts/platforms/base.py` 了解接口定义。