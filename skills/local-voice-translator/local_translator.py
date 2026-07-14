#!/usr/bin/env python3
"""
本地语音翻译器 - 无需 API Key
使用系统 TTS + Google Translate
"""

import os
import sys
import subprocess
import tempfile
import json
import urllib.parse
import urllib.request


class LocalVoiceTranslator:
    """本地语音翻译，使用系统 TTS 和免费翻译服务"""
    
    LANGUAGES = {
        "en": {"name": "英语", "tts_lang": "en-US"},
        "ru": {"name": "俄语", "tts_lang": "ru-RU"},
        "ja": {"name": "日语", "tts_lang": "ja-JP"},
        "ko": {"name": "韩语", "tts_lang": "ko-KR"},
        "fr": {"name": "法语", "tts_lang": "fr-FR"},
        "de": {"name": "德语", "tts_lang": "de-DE"},
        "es": {"name": "西班牙语", "tts_lang": "es-ES"},
        "it": {"name": "意大利语", "tts_lang": "it-IT"},
    }
    
    SCENES = {
        "restaurant": "餐厅",
        "airport": "机场", 
        "hotel": "酒店",
        "taxi": "出租车",
        "shopping": "购物",
        "medical": "就医",
        "daily": "日常",
    }
    
    def __init__(self, target_lang="en", scene="daily"):
        self.target_lang = target_lang
        self.scene = scene
        self.favorites = []
        
    def translate_text(self, text: str, target_lang: str = None) -> str:
        """使用 Google Translate 免费接口翻译"""
        if target_lang is None:
            target_lang = self.target_lang
            
        try:
            # Google Translate 免费接口
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "zh-CN",
                "tl": target_lang,
                "dt": "t",
                "q": text,
            }
            
            url_with_params = f"{url}?{urllib.parse.urlencode(params)}"
            
            req = urllib.request.Request(
                url_with_params,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                translated = "".join([item[0] for item in data[0] if item[0]])
                return translated
                
        except Exception as e:
            print(f"翻译出错: {e}")
            return f"[翻译失败] {text}"
    
    def speak_text(self, text: str, lang: str = None):
        """使用系统 TTS 朗读文本"""
        if lang is None:
            lang = self.target_lang
            
        tts_lang = self.LANGUAGES.get(lang, {}).get("tts_lang", "en-US")
        
        # macOS say 命令
        if sys.platform == "darwin":
            # macOS 内置 say 命令，但只支持部分语言
            # 对于不支持的语言，使用 say 默认声音
            try:
                subprocess.run(["say", text], check=True)
                return True
            except subprocess.CalledProcessError:
                print(f"⚠️ 系统 TTS 不支持该语言，仅显示文本")
                return False
        
        # Linux - 尝试 espeak
        elif sys.platform == "linux":
            try:
                subprocess.run(["espeak", "-v", tts_lang, text], check=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"⚠️ 请先安装 espeak: sudo apt-get install espeak")
                return False
        
        # Windows
        elif sys.platform == "win32":
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                return True
            except ImportError:
                print(f"⚠️ 请先安装 pyttsx3: pip install pyttsx3")
                return False
        
        return False
    
    def translate_and_speak(self, chinese_text: str) -> dict:
        """翻译并朗读"""
        print(f"📝 原文: {chinese_text}")
        
        # 翻译
        translated = self.translate_text(chinese_text)
        lang_name = self.LANGUAGES.get(self.target_lang, {}).get("name", self.target_lang)
        print(f"🌐 翻译 ({lang_name}): {translated}")
        
        # 朗读
        print("🔊 朗读中...")
        success = self.speak_text(translated)
        
        result = {
            "original": chinese_text,
            "translated": translated,
            "lang": self.target_lang,
            "scene": self.scene,
            "spoken": success
        }
        
        return result
    
    def add_favorite(self, result: dict):
        """收藏句子"""
        if result not in self.favorites:
            self.favorites.append(result)
            print(f"⭐ 已收藏: {result['original']} → {result['translated']}")
    
    def list_favorites(self):
        """列出收藏"""
        if not self.favorites:
            print("📭 收藏夹为空")
            return
            
        print("\n📚 收藏列表:")
        for i, item in enumerate(self.favorites, 1):
            lang_name = self.LANGUAGES.get(item['lang'], {}).get('name', item['lang'])
            print(f"{i}. {item['original']} → [{lang_name}] {item['translated']}")
    
    def play_favorite(self, index: int):
        """播放收藏"""
        if 0 <= index < len(self.favorites):
            item = self.favorites[index]
            print(f"🔊 播放收藏 {index + 1}: {item['translated']}")
            self.speak_text(item['translated'], item['lang'])
        else:
            print("❌ 无效的索引")
    
    def save_favorites(self, path: str = "favorites.json"):
        """保存收藏到文件"""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        print(f"💾 收藏已保存到: {path}")
    
    def load_favorites(self, path: str = "favorites.json"):
        """从文件加载收藏"""
        try:
            with open(path, encoding="utf-8") as f:
                self.favorites = json.load(f)
            print(f"📂 已加载 {len(self.favorites)} 条收藏")
        except FileNotFoundError:
            pass


def interactive_mode():
    """交互模式"""
    print("=" * 50)
    print("🌏 本地语音翻译器 (无需 API)")
    print("=" * 50)
    
    # 选择语言
    print("\n选择目标语言:")
    langs = list(LocalVoiceTranslator.LANGUAGES.keys())
    for i, (code, info) in enumerate(LocalVoiceTranslator.LANGUAGES.items(), 1):
        print(f"{i}. {info['name']} ({code})")
    
    choice = input("\n输入数字 (默认 1-英语): ").strip() or "1"
    try:
        target_lang = langs[int(choice) - 1]
    except (ValueError, IndexError):
        target_lang = "en"
    
    # 创建翻译器
    translator = LocalVoiceTranslator(target_lang=target_lang)
    translator.load_favorites()
    
    print(f"\n✅ 已选择: {translator.LANGUAGES[target_lang]['name']}")
    print("💡 输入中文，按回车翻译并朗读")
    print("💡 命令: /fav (收藏) /list (列表) /save (保存) /quit (退出)\n")
    
    last_result = None
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
                
            if user_input == "/quit":
                break
            elif user_input == "/fav":
                if last_result:
                    translator.add_favorite(last_result)
                else:
                    print("⚠️ 先输入要翻译的内容")
            elif user_input == "/list":
                translator.list_favorites()
            elif user_input == "/save":
                translator.save_favorites()
            else:
                last_result = translator.translate_and_speak(user_input)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n👋 再见!")


if __name__ == "__main__":
    interactive_mode()
