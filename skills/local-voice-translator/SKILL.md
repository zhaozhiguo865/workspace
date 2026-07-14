---
name: local-voice-translator
description: 本地语音翻译器，无需 API Key。使用 Google Translate 免费接口 + 系统 TTS，支持 8 种语言互译。
---

# 本地语音翻译器

无需注册账号，无需 API Key，开箱即用的语音翻译工具。

## 功能

- ✅ 中文 → 英/俄/日/韩/法/德/西/意 语音翻译
- ✅ 使用 Google Translate 免费接口
- ✅ 使用 macOS/Linux/Windows 系统 TTS 朗读
- ✅ 收藏常用句子
- ✅ 交互式命令行界面

## 使用方法

### 命令行交互模式

```bash
python3 ~/.openclaw/workspace/skills/local-voice-translator/local_translator.py
```

### Python API

```python
from local_translator import LocalVoiceTranslator

# 创建翻译器（俄语）
translator = LocalVoiceTranslator(target_lang="ru")

# 翻译并朗读
result = translator.translate_and_speak("你好，谢谢")
# 输出: Привет, спасибо

# 收藏句子
translator.add_favorite(result)

# 保存收藏
translator.save_favorites()
```

## 支持语言

| 代码 | 语言 | 状态 |
|------|------|------|
| en | 英语 | ✅ |
| ru | 俄语 | ✅ |
| ja | 日语 | ✅ |
| ko | 韩语 | ✅ |
| fr | 法语 | ✅ |
| de | 德语 | ✅ |
| es | 西班牙语 | ✅ |
| it | 意大利语 | ✅ |

## 交互命令

| 命令 | 功能 |
|------|------|
| /fav | 收藏上一条翻译 |
| /list | 显示收藏列表 |
| /save | 保存收藏到文件 |
| /quit | 退出 |

## 系统要求

- Python 3.6+
- macOS: 内置 `say` 命令
- Linux: `espeak` (`sudo apt-get install espeak`)
- Windows: `pip install pyttsx3`
