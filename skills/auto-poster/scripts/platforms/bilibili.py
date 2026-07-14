"""
B站平台实现
支持发布动态
"""

import json
import re
import time
from typing import Dict, Any, List, Optional
import requests
from .base import BasePlatform


class BilibiliPlatform(BasePlatform):
    """Bilibili 平台"""
    
    name = "bilibili"
    display_name = "哔哩哔哩"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://t.bilibili.com/"
        })
        self.csrf = None
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["cookie"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"B站配置缺少必需字段: {key}")
    
    def login(self) -> bool:
        """使用 Cookie 登录"""
        cookie_str = self.config.get("cookie", "")
        
        # 解析 Cookie
        cookies = {}
        for item in cookie_str.split(";"):
            if "=" in item:
                key, value = item.strip().split("=", 1)
                cookies[key] = value
                if key == "bili_jct":
                    self.csrf = value
        
        self.session.cookies.update(cookies)
        
        # 验证登录状态
        try:
            resp = self.session.get("https://api.bilibili.com/x/web-interface/nav")
            data = resp.json()
            return data.get("data", {}).get("isLogin", False)
        except Exception as e:
            print(f"B站登录验证失败: {e}")
            return False
    
    def get_character_limit(self) -> int:
        """B站动态字数限制"""
        return 2000
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """发布纯文本动态"""
        content = self.truncate_content(content)
        
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create"
        
        data = {
            "dynamic_id": 0,
            "type": 4,  # 纯文本
            "rid": 0,
            "content": content,
            "csrf": self.csrf,
        }
        
        try:
            resp = self.session.post(url, data=data)
            result = resp.json()
            
            if result.get("code") == 0:
                dynamic_id = result.get("data", {}).get("dynamic_id")
                return {
                    "success": True,
                    "post_id": dynamic_id,
                    "url": f"https://t.bilibili.com/{dynamic_id}",
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布带图片的动态"""
        content = self.truncate_content(content)
        
        # 1. 上传图片
        image_infos = []
        for img_path in image_paths[:9]:  # B站最多9张图
            img_info = self._upload_image(img_path)
            if img_info:
                image_infos.append(img_info)
        
        if not image_infos:
            return {
                "success": False,
                "error": "图片上传失败"
            }
        
        # 2. 发布动态
        url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create"
        
        # 构建图片数据
        pics = []
        for info in image_infos:
            pics.append({
                "img_src": info["url"],
                "img_width": info.get("width", 1000),
                "img_height": info.get("height", 1000)
            })
        
        data = {
            "dynamic_id": 0,
            "type": 2,  # 图文
            "rid": 0,
            "content": content,
            "pics": json.dumps(pics),
            "csrf": self.csrf,
        }
        
        try:
            resp = self.session.post(url, data=data)
            result = resp.json()
            
            if result.get("code") == 0:
                dynamic_id = result.get("data", {}).get("dynamic_id")
                return {
                    "success": True,
                    "post_id": dynamic_id,
                    "url": f"https://t.bilibili.com/{dynamic_id}",
                    "content": content,
                    "image_count": len(image_infos)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """上传单张图片"""
        url = "https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs"
        
        try:
            with open(image_path, "rb") as f:
                files = {"file_up": ("image.jpg", f, "image/jpeg")}
                resp = self.session.post(
                    url,
                    files=files,
                    data={"csrf": self.csrf}
                )
                
                result = resp.json()
                if result.get("code") == 0:
                    data = result.get("data", {})
                    return {
                        "url": data.get("image_url"),
                        "width": data.get("image_width"),
                        "height": data.get("image_height")
                    }
        except Exception as e:
            print(f"图片上传失败 {image_path}: {e}")
        
        return None