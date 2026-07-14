"""
Twitter/X 平台实现
使用 Twitter API v2
"""

import json
from typing import Dict, Any, List, Optional
import requests
import base64
from .base import BasePlatform


class TwitterPlatform(BasePlatform):
    """Twitter/X 平台"""
    
    name = "twitter"
    display_name = "Twitter/X"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://api.twitter.com/2"
        self.media_url = "https://upload.twitter.com/1.1/media/upload.json"
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["api_key", "api_secret", "access_token", "access_token_secret"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"Twitter 配置缺少必需字段: {key}")
    
    def login(self) -> bool:
        """验证 API 凭证"""
        try:
            # 测试获取用户信息
            headers = self._get_auth_headers()
            resp = requests.get(
                f"{self.base_url}/users/me",
                headers=headers
            )
            return resp.status_code == 200
        except Exception as e:
            print(f"Twitter 登录验证失败: {e}")
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取 OAuth 1.0a 认证头"""
        import oauthlib.oauth1
        
        client = oauthlib.oauth1.Client(
            client_key=self.config["api_key"],
            client_secret=self.config["api_secret"],
            resource_owner_key=self.config["access_token"],
            resource_owner_secret=self.config["access_token_secret"]
        )
        
        uri = f"{self.base_url}/tweets"
        method = "POST"
        headers = {"Content-Type": "application/json"}
        
        uri, headers, body = client.sign(uri, method, headers=headers)
        
        return headers
    
    def get_character_limit(self) -> int:
        """Twitter 字数限制"""
        return 280
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """发布纯文本推文"""
        content = self.truncate_content(content)
        
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        data = {"text": content}
        
        try:
            resp = requests.post(
                f"{self.base_url}/tweets",
                headers=headers,
                json=data
            )
            result = resp.json()
            
            if resp.status_code == 201:
                tweet_id = result.get("data", {}).get("id")
                username = self.config.get("username", "")
                return {
                    "success": True,
                    "post_id": tweet_id,
                    "url": f"https://twitter.com/{username}/status/{tweet_id}",
                    "content": content
                }
            else:
                return {
                    "success": False,
                    "error": result.get("detail", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """发布带图片的推文"""
        content = self.truncate_content(content)
        
        # 1. 上传图片
        media_ids = []
        for img_path in image_paths[:4]:  # Twitter 最多4张图
            media_id = self._upload_media(img_path)
            if media_id:
                media_ids.append(media_id)
        
        if not media_ids:
            return {
                "success": False,
                "error": "图片上传失败"
            }
        
        # 2. 发布推文
        headers = self._get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        data = {
            "text": content,
            "media": {"media_ids": media_ids}
        }
        
        try:
            resp = requests.post(
                f"{self.base_url}/tweets",
                headers=headers,
                json=data
            )
            result = resp.json()
            
            if resp.status_code == 201:
                tweet_id = result.get("data", {}).get("id")
                username = self.config.get("username", "")
                return {
                    "success": True,
                    "post_id": tweet_id,
                    "url": f"https://twitter.com/{username}/status/{tweet_id}",
                    "content": content,
                    "image_count": len(media_ids)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("detail", "未知错误"),
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _upload_media(self, image_path: str) -> Optional[str]:
        """上传媒体文件"""
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # INIT
            headers = self._get_auth_headers()
            
            init_resp = requests.post(
                self.media_url,
                headers=headers,
                data={
                    "command": "INIT",
                    "total_bytes": len(image_data),
                    "media_type": "image/jpeg"
                }
            )
            
            if init_resp.status_code != 202:
                return None
            
            media_id = init_resp.json().get("media_id_string")
            
            # APPEND
            requests.post(
                self.media_url,
                headers=headers,
                data={
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": 0
                },
                files={"media": image_data}
            )
            
            # FINALIZE
            finalize_resp = requests.post(
                self.media_url,
                headers=headers,
                data={
                    "command": "FINALIZE",
                    "media_id": media_id
                }
            )
            
            if finalize_resp.status_code == 200:
                return media_id
                
        except Exception as e:
            print(f"媒体上传失败 {image_path}: {e}")
        
        return None