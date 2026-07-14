---
name: russian-tts
description: 俄语语音合成技能。使用 macOS 本地语音 Milena 朗读俄语文本。当用户需要朗读俄语单词、句子、文章或练习俄语听力时触发。使用关键词如"朗读俄语"、"俄语语音"、"俄语发音"、"读俄语"。
metadata:
  openclaw:
    emoji: "🇷🇺"
    requires:
      bins: ["say"]
      os: ["darwin"]
---

# Russian TTS / 俄语语音合成

使用 macOS 本地俄语语音 `Milena` 朗读俄语文本，无需 API Key，完全离线。

## 使用方法

### 朗读俄语文本

```bash
say -v Milena "俄语文本"
```

### 常用命令

| 场景 | 命令 |
|------|------|
| 朗读单词 | `say -v Milena "здравствуйте"` |
| 朗读句子 | `say -v Milena "Как дела?"` |
| 朗读文章 | `say -v Milena "$(cat article.txt)"` |

## 语音特点

- **语音名称**: Milena (Милена)
- **语言**: 俄语 (ru_RU)
- **性别**: 女声
- **质量**: 清晰自然，语速适中

## 学习应用场景

1. **单词发音练习**
   ```bash
   say -v Milena "спасибо"
   say -v Milena "до свидания"
   ```

2. **句子听力训练**
   ```bash
   say -v Milena "Как вас зовут?"
   say -v Milena "Я китаец"
   ```

3. **文章朗读**
   ```bash
   say -v Milena "Мой цифровой помощник..."
   ```

## 与其他语音对比

| 语言 | 语音 | 命令示例 |
|------|------|---------|
| 俄语 | Milena | `say -v Milena "Привет"` |
| 中文 | Tingting | `say -v Tingting "你好"` |
| 英语 | Samantha | `say "Hello"` |

## 注意事项

- 确保系统已安装俄语语音（系统设置 → 辅助功能 → 朗读内容 → 系统语音 → 管理语音）
- 如 Milena 不可用，系统会自动使用默认语音
- 长文本朗读可能需要较长时间
