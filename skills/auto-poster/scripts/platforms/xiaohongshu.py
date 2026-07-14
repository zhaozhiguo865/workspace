"""
小红书平台实现
基于小红书 Web 端 API
"""

import json
import re
import time
import hashlib
import uuid
from typing import Dict, Any, List, Optional
import requests
from .base import BasePlatform


class XiaohongshuPlatform(BasePlatform):
    """小红书平台"""
    
    name = "xiaohongshu"
    display_name = "小红书"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.session = requests.Session()
        self.device_id = self.config.get("device_id", self._generate_device_id())
        self.session_id = self._generate_session_id()
        
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.xiaohongshu.com/",
            "Origin": "https://www.xiaohongshu.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "X-Sign": "",
            "X-Timestamp": "",
            "X-Device-Id": self.device_id,
        })
    
    def _generate_device_id(self) -> str:
        """生成设备 ID"""
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
    
    def _generate_session_id(self) -> str:
        """生成会话 ID"""
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    
    def _generate_sign(self, url: str, data: Optional[Dict] = None) -> str:
        """生成请求签名"""
        timestamp = str(int(time.time() * 1000))
        sign_str = f"{url}{timestamp}{self.device_id}"
        if data:
            sign_str += json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return hashlib.md5(sign_str.encode()).hexdigest()
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["cookie"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"小红书配置缺少必需字段: {key}")
    
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
        
        # 验证登录状态 - 获取用户信息
        try:
            url = "https://edith.xiaohongshu.com/api/sns/web/v1/user/selfinfo"
            headers = self._get_headers(url)
            resp = self.session.get(url, headers=headers)
            data = resp.json()
            
            if data.get("success") and data.get("data"):
                user_info = data.get("data", {})
                self.user_id = user_info.get("user_id", "")
                self.nickname = user_info.get("nickname", "")
                print(f"小红书登录成功: {self.nickname}")
                return True
            else:
                print(f"小红书登录验证失败: {data.get('msg', '未知错误')}")
                return False
        except Exception as e:
            print(f"小红书登录验证失败: {e}")
            return False
    
    def _get_headers(self, url: str, data: Optional[Dict] = None) -> Dict[str, str]:
        """获取带签名的请求头"""
        timestamp = str(int(time.time() * 1000))
        sign = self._generate_sign(url, data)
        
        return {
            "X-Sign": sign,
            "X-Timestamp": timestamp,
            "X-Device-Id": self.device_id,
            "X-Session-Id": self.session_id,
        }
    
    def get_character_limit(self) -> int:
        """小红书字数限制"""
        return 1000
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """发布纯文本笔记（小红书必须带图片或视频，这里用默认封面）"""
        return {
            "success": False,
            "error": "小红书不支持纯文本发布，必须包含图片或视频"
        }
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布带图片的笔记"""
        content = self.truncate_content(content)
        
        # 1. 上传图片
        image_infos = []
        for img_path in image_paths[:18]:  # 小红书最多18张图
            img_info = self._upload_image(img_path)
            if img_info:
                image_infos.append(img_info)
        
        if not image_infos:
            return {
                "success": False,
                "error": "图片上传失败"
            }
        
        # 2. 发布笔记
        return self._publish_note(content, image_infos)
    
    def _upload_image(self, image_path: str) -> Optional[Dict]:
        """上传单张图片到小红书"""
        try:
            # 1. 获取上传凭证
            url = "https://edith.xiaohongshu.com/api/sns/web/v1/upload/prepare"
            headers = self._get_headers(url)
            
            file_name = image_path.split("/")[-1]
            file_size = self._get_file_size(image_path)
            
            data = {
                "file_type": "image/jpeg",
                "file_name": file_name,
                "file_size": file_size,
            }
            
            resp = self.session.post(url, json=data, headers=headers)
            result = resp.json()
            
            if not result.get("success"):
                print(f"获取上传凭证失败: {result.get('msg')}")
                return None
            
            upload_data = result.get("data", {})
            upload_url = upload_data.get("upload_url")
            file_id = upload_data.get("file_id")
            
            # 2. 上传图片文件
            with open(image_path, "rb") as f:
                upload_resp = self.session.put(upload_url, data=f, headers={
                    "Content-Type": "image/jpeg"
                })
            
            if upload_resp.status_code == 200:
                return {
                    "file_id": file_id,
                    "width": 1080,  # 默认值
                    "height": 1440,
                }
            else:
                print(f"图片上传失败: {upload_resp.status_code}")
                return None
                
        except Exception as e:
            print(f"图片上传失败 {image_path}: {e}")
            return None
    
    def _get_file_size(self, file_path: str) -> int:
        """获取文件大小"""
        import os
        return os.path.getsize(file_path)
    
    def _publish_note(self, content: str, image_infos: List[Dict]) -> Dict[str, Any]:
        """发布笔记"""
        url = "https://edith.xiaohongshu.com/api/sns/web/v1/note/post"
        
        # 构建图片列表
        images = []
        for info in image_infos:
            images.append({
                "file_id": info["file_id"],
                "width": info.get("width", 1080),
                "height": info.get("height", 1440),
            })
        
        # 构建请求数据
        data = {
            "common": {
                "type": "normal",
                "title": "",
                "note_id": "",
            },
            "note": {
                "type": "normal",
                "title": self._extract_title(content),
                "desc": content,
                "images": images,
                "topics": self._extract_topics(content),
                "ats": [],
            }
        }
        
        headers = self._get_headers(url, data)
        
        try:
            resp = self.session.post(url, json=data, headers=headers)
            result = resp.json()
            
            if result.get("success"):
                note_id = result.get("data", {}).get("note_id", "")
                return {
                    "success": True,
                    "post_id": note_id,
                    "url": f"https://www.xiaohongshu.com/explore/{note_id}",
                    "content": content,
                    "image_count": len(images)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("msg", "发布失败"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_title(self, content: str) -> str:
        """从内容中提取标题（前20字）"""
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                return line[:20] if len(line) > 20 else line
        return content[:20] if len(content) > 20 else content
    
    def _extract_topics(self, content: str) -> List[Dict]:
        """从内容中提取话题标签"""
        topics = []
        # 匹配 #话题# 格式
        matches = re.findall(r'#([^#]+)#', content)
        for match in matches[:5]:  # 最多5个话题
            topics.append({
                "name": match.strip(),
                "type": "topic"
            })
        return topics
