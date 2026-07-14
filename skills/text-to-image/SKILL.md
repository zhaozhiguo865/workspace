---
name: text-to-image
description: |
  文字生图技能。根据文字描述生成图片，支持多种风格和场景。
  当用户需要"生成图片"、"画一张图"、"根据描述创建图像"、"AI绘画"时使用此技能。
  支持写实风格、动漫风格、油画风格、水彩风格、像素风格等多种艺术风格。
---

# 文字生图技能

## 核心功能

### 1. 图像生成
- **文生图** - 根据文字描述生成图像
- **风格控制** - 指定艺术风格、画风
- **构图控制** - 指定画面构图、视角
- **质量优化** - 自动优化提示词获得更好效果

### 2. 支持风格
| 风格 | 描述 | 适用场景 |
|------|------|----------|
| 写实/照片级 | photorealistic | 产品图、人像、风景 |
| 动漫/二次元 | anime, manga | 角色设计、插画 |
| 油画 | oil painting | 艺术画、装饰画 |
| 水彩 | watercolor | 柔和场景、插画 |
| 像素风 | pixel art | 游戏素材、复古风 |
| 赛博朋克 | cyberpunk | 科幻场景、未来感 |
| 国风/水墨 | chinese ink | 古风、传统文化 |
| 3D渲染 | 3D render | 产品展示、概念设计 |
| 扁平插画 | flat illustration | UI插画、图标 |
| 素描/线稿 | sketch, line art | 草图、设计稿 |

### 3. 画面控制
- **画幅比例** - 1:1, 16:9, 9:16, 4:3, 3:4, 21:9
- **视角** - 正视、俯视、仰视、特写、全景
- **光影** - 自然光、逆光、侧光、柔光、硬光
- **色调** - 暖色调、冷色调、高饱和、低饱和、黑白

## 提示词优化

### 基础结构
```
[主体描述] + [环境/背景] + [风格] + [质量词] + [技术参数]
```

### 示例
**简单版**：
> "一只橘猫在窗台上晒太阳，写实风格"

**优化版**：
> "A fluffy orange tabby cat sitting on a wooden windowsill, warm sunlight streaming through the window, cozy living room background, photorealistic style, soft natural lighting, shallow depth of field, highly detailed, 8k quality --ar 16:9"

### 质量增强词
- 基础：high quality, detailed
- 进阶：highly detailed, intricate details, sharp focus
- 专业：8k resolution, masterpiece, best quality, professional photography

## 工作流程

### Step 1: 理解需求
- 用户想画什么？（主体）
- 什么风格？（写实/动漫/艺术等）
- 什么用途？（头像/壁纸/素材/参考）
- 特殊要求？（比例、色调、构图）

### Step 2: 优化提示词
- 将中文描述转换为优化后的英文提示词
- 添加风格关键词
- 添加质量增强词
- 指定画面比例

### Step 3: 生成图像
使用 DALL-E 3 API 生成图片

**命令行工具**:
```bash
# 基础用法
node skills/text-to-image/generate-image.js "你的描述"

# 完整参数
node skills/text-to-image/generate-image.js "A cute cat" \
  --size=1024x1792 \
  --quality=hd \
  --style=vivid \
  --output=cat.png

# 尺寸选项
# 1024x1024 (1:1 正方形)
# 1792x1024 (16:9 横屏)
# 1024x1792 (9:16 竖屏/手机)
```

**配置 API Key**:
```bash
export OPENAI_API_KEY="your-api-key-here"
# 添加到 ~/.zshrc 永久保存
```

**费用参考**:
- Standard 质量: $0.04/张 (1024x1024)
- HD 质量: $0.08/张 (1024x1024), $0.12/张 (其他尺寸)

### Step 4: 反馈调整
根据用户反馈迭代优化

## 使用示例

### 用户："画一只赛博朋克风格的猫"

**分析**：
- 主体：猫
- 风格：赛博朋克
- 元素：霓虹灯、机械、未来感

**优化提示词**：
> "A cyberpunk cat with glowing neon circuits on its fur, wearing futuristic mechanical armor, sitting on a rainy rooftop at night, neon signs in the background, blue and purple lighting, cyberpunk aesthetic, highly detailed, digital art, 8k --ar 16:9"

### 用户："生成一张中国风山水画"

**优化提示词**：
> "Traditional Chinese landscape painting, misty mountains with pine trees, a small pavilion by the lake, ink wash style, black and white with subtle gray tones, poetic atmosphere, classical composition, masterwork quality --ar 3:4"

## 注意事项

1. **内容安全** - 拒绝生成违规内容（暴力、色情、政治敏感等）
2. **版权提示** - 生成的图片仅供参考，商用需注意版权风险
3. **多次尝试** - AI生图有随机性，可多次生成选择最佳结果
4. **提示词优化** - 英文提示词通常效果更好

## 相关技能

- ad-design - 广告创意设计（可配合生图使用）
- short-video-editor - 短视频剪辑（可用生图做素材）
