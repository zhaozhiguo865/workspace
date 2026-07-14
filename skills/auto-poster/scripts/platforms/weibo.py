"""
微博平台实现
"""

import json
import re
import time
from typing import Dict, Any, List, Optional
import requests
from .base import BasePlatform


class WeiboPlatform(BasePlatform):
    """微博平台"""
    
    name = "weibo"
    display_name = "微博"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://weibo.com/"
        })
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["cookie"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"微博配置缺少必需字段: {key}")
    
    def login(self) -> bool:
        """使用 Cookie 登录"""
        cookie_str = self.config.get("cookie", "")
        
        # 解析 Cookie
        cookies = {}
        for item in cookie_str.split(";"):
            if "=" in item:
                key, value = item.strip().split("=", 1)
                cookies[key] = value
        
        self.session.cookies.update(cookies)
        
        # 验证登录状态
        try:
            resp = self.session.get("https://weibo.com/ajax/statuses/config")
            data = resp.json()
            return data.get("data", {}).get("login", False)
        except Exception as e:
            print(f"微博登录验证失败: {e}")
            return False
    
    def get_character_limit(self) -> int:
        """微博字数限制"""
        return 2000
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """发布纯文本微博"""
        content = self.truncate_content(content)
        
        url = "https://weibo.com/ajax/statuses/update"
        
        data = {
            "content": content,
            "visible": 0,  # 公开
            "share_id": "",
        }
        
        try:
            resp = self.session.post(url, data=data)
            result = resp.json()
            
            if result.get("ok") == 1:
                weibo_id = result.get("data", {}).get("id")
                return {
                    "success": True,
                    "post_id": weibo_id,
                    "url": f"https://weibo.com/{self.config.get('uid', '')}/{weibo_id}",
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布带图片的微博"""
        content = self.truncate_content(content)
        
        # 1. 上传图片
        pic_ids = []
        for img_path in image_paths[:9]:  # 微博最多9张图
            pic_id = self._upload_image(img_path)
            if pic_id:
                pic_ids.append(pic_id)
        
        if not pic_ids:
            return {
                "success": False,
                "error": "图片上传失败"
            }
        
        # 2. 发布微博
        url = "https://weibo.com/ajax/statuses/update"
        
        data = {
            "content": content,
            "pic_id": ",".join(pic_ids),
            "visible": 0,
        }
        
        try:
            resp = self.session.post(url, data=data)
            result = resp.json()
            
            if result.get("ok") == 1:
                weibo_id = result.get("data", {}).get("id")
                return {
                    "success": True,
                    "post_id": weibo_id,
                    "url": f"https://weibo.com/{self.config.get('uid', '')}/{weibo_id}",
                    "content": content,
                    "image_count": len(pic_ids)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_image(self, image_path: str) -> Optional[str]:
        """上传单张图片"""
        url = "https://picupload.weibo.com/interface/pic_upload.php"
        
        try:
            with open(image_path, "rb") as f:
                files = {"pic1": f}
                resp = self.session.post(url, files=files)
                
                # 解析返回的 JavaScript
                match = re.search(r'"pid":"([^"]+)"', resp.text)
                if match:
                    return match.group(1)
        except Exception as e:
            print(f"图片上传失败 {image_path}: {e}")
        
        return None