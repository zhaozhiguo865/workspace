"""
知乎平台实现
支持发布想法
"""

import json
import time
from typing import Dict, Any, List, Optional
import requests
from .base import BasePlatform


class ZhihuPlatform(BasePlatform):
    """知乎平台"""
    
    name = "zhihu"
    display_name = "知乎"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.zhihu.com/",
            "x-zse-93": "101_3_3.0"
        })
        self.xsrftoken = None
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["cookie"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"知乎配置缺少必需字段: {key}")
    
    def login(self) -> bool:
        """使用 Cookie 登录"""
        cookie_str = self.config.get("cookie", "")
        
        # 解析 Cookie
        cookies = {}
        for item in cookie_str.split(";"):
            if "=" in item:
                key, value = item.strip().split("=", 1)
                cookies[key] = value
                if key == "_xsrf":
                    self.xsrftoken = value
        
        self.session.cookies.update(cookies)
        
        # 验证登录状态
        try:
            resp = self.session.get("https://www.zhihu.com/api/v4/me")
            data = resp.json()
            return not data.get("error")
        except Exception as e:
            print(f"知乎登录验证失败: {e}")
            return False
    
    def get_character_limit(self) -> int:
        """知乎想法字数限制"""
        return 2000
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """发布纯文本想法"""
        content = self.truncate_content(content)
        
        url = "https://www.zhihu.com/api/v4/pins"
        
        headers = {
            "x-xsrftoken": self.xsrftoken,
            "Content-Type": "application/json"
        }
        
        data = {
            "content": content,
            "type": "pin"
        }
        
        try:
            resp = self.session.post(url, headers=headers, json=data)
            result = resp.json()
            
            if "id" in result:
                pin_id = result.get("id")
                return {
                    "success": True,
                    "post_id": pin_id,
                    "url": f"https://www.zhihu.com/pin/{pin_id}",
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布带图片的想法"""
        content = self.truncate_content(content)
        
        # 1. 上传图片
        image_tokens = []
        for img_path in image_paths[:9]:  # 知乎最多9张图
            token = self._upload_image(img_path)
            if token:
                image_tokens.append(token)
        
        if not image_tokens:
            return {
                "success": False,
                "error": "图片上传失败"
            }
        
        # 2. 构建内容（带图片）
        content_html = f"<p>{content}</p>"
        for token in image_tokens:
            content_html += f'<figure data-size="normal"><img src="{token}" /></figure>'
        
        # 3. 发布想法
        url = "https://www.zhihu.com/api/v4/pins"
        
        headers = {
            "x-xsrftoken": self.xsrftoken,
            "Content-Type": "application/json"
        }
        
        data = {
            "content": content,
            "type": "pin",
            "content_html": content_html
        }
        
        try:
            resp = self.session.post(url, headers=headers, json=data)
            result = resp.json()
            
            if "id" in result:
                pin_id = result.get("id")
                return {
                    "success": True,
                    "post_id": pin_id,
                    "url": f"https://www.zhihu.com/pin/{pin_id}",
                    "content": content,
                    "image_count": len(image_tokens)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """上传单张图片"""
        url = "https://www.zhihu.com/api/v4/upload_images"
        
        try:
            with open(image_path, "rb") as f:
                files = {"file": ("image.jpg", f, "image/jpeg")}
                headers = {"x-xsrftoken": self.xsrftoken}
                resp = self.session.post(url, headers=headers, files=files)
                
                result = resp.json()
                if "img_url" in result:
                    return result.get("img_url")
        except Exception as e:
            print(f"图片上传失败 {image_path}: {e}")
        
        return None