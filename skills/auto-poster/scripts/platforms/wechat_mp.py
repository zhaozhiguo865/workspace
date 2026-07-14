"""
微信公众号平台实现
支持发布图文消息
"""

import json
import time
from typing import Dict, Any, List, Optional
import requests
from .base import BasePlatform


class WechatMPPlatform(BasePlatform):
    """微信公众号平台"""
    
    name = "wechat_mp"
    display_name = "微信公众号"
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.access_token = None
        self.token_expires_at = 0
        self.base_url = "https://api.weixin.qq.com/cgi-bin"
    
    def _validate_config(self) -> None:
        """验证配置"""
        required = ["appid", "appsecret"]
        for key in required:
            if key not in self.config:
                raise ValueError(f"微信公众号配置缺少必需字段: {key}")
    
    def _get_access_token(self) -> str:
        """获取或刷新 access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = f"{self.base_url}/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.config["appid"],
            "secret": self.config["appsecret"]
        }
        
        try:
            resp = requests.get(url, params=params)
            result = resp.json()
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                # 提前5分钟过期
                self.token_expires_at = time.time() + result.get("expires_in", 7200) - 300
                return self.access_token
            else:
                raise Exception(f"获取 access_token 失败: {result.get('errmsg')}")
        except Exception as e:
            raise Exception(f"获取 access_token 异常: {e}")
    
    def login(self) -> bool:
        """验证 API 凭证"""
        try:
            token = self._get_access_token()
            # 测试获取素材列表验证 token 有效性
            url = f"{self.base_url}/material/batchget_material"
            params = {"access_token": token}
            data = {
                "type": "news",
                "offset": 0,
                "count": 1
            }
            resp = requests.post(url, params=params, json=data)
            result = resp.json()
            return "errcode" not in result or result["errcode"] == 0
        except Exception as e:
            print(f"微信公众号登录验证失败: {e}")
            return False
    
    def get_character_limit(self) -> int:
        """公众号文章字数限制"""
        return 20000  # 图文消息正文限制
    
    def post_text(self, content: str) -> Dict[str, Any]:
        """
        发布纯文本（作为单图文消息）
        """
        return self.post_article(
            title="动态消息",
            content=content,
            digest=content[:50] + "..." if len(content) > 50 else content
        )
    
    def post_article(self, title: str, content: str, digest: str = "", 
                     thumb_media_id: str = None, author: str = "",
                     content_source_url: str = "", show_cover_pic: int = 0) -> Dict[str, Any]:
        """
        发布图文消息
        
        Args:
            title: 标题
            content: 图文消息页面内容（支持HTML）
            digest: 图文消息描述
            thumb_media_id: 封面图片素材ID
            author: 作者
            content_source_url: 原文链接
            show_cover_pic: 是否显示封面（0/1）
        """
        token = self._get_access_token()
        
        # 1. 上传图文消息素材
        url = f"{self.base_url}/material/add_news"
        params = {"access_token": token}
        
        # 如果没有封面图，尝试使用默认图或不上传
        if not thumb_media_id:
            thumb_media_id = self.config.get("default_thumb_media_id", "")
        
        articles = [{
            "title": title,
            "thumb_media_id": thumb_media_id,
            "author": author,
            "digest": digest,
            "show_cover_pic": show_cover_pic,
            "content": content,
            "content_source_url": content_source_url
        }]
        
        data = {"articles": articles}
        
        try:
            resp = requests.post(url, params=params, json=data)
            result = resp.json()
            
            if "media_id" in result:
                media_id = result["media_id"]
                
                # 2. 群发消息
                return self._mass_send(media_id, "mpnews")
            else:
                return {
                    "success": False,
                    "error": f"上传素材失败: {result.get('errmsg', '未知错误')}",
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mass_send(self, media_id: str, msgtype: str = "mpnews", 
                   send_ignore_reprint: int = 0) -> Dict[str, Any]:
        """
        群发消息
        
        Args:
            media_id: 素材ID
            msgtype: 消息类型
            send_ignore_reprint: 是否忽略转载校验（0/1）
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/message/mass/sendall"
        params = {"access_token": token}
        
        data = {
            "filter": {
                "is_to_all": True
            },
            msgtype: {
                "media_id": media_id
            },
            "send_ignore_reprint": send_ignore_reprint
        }
        
        try:
            resp = requests.post(url, params=params, json=data)
            result = resp.json()
            
            if result.get("errcode") == 0:
                msg_id = result.get("msg_id")
                return {
                    "success": True,
                    "post_id": msg_id,
                    "media_id": media_id,
                    "url": f"https://mp.weixin.qq.com/s/{media_id}",  # 预览链接
                    "msg_data_id": result.get("msg_data_id")
                }
            else:
                return {
                    "success": False,
                    "error": f"群发失败: {result.get('errmsg', '未知错误')}",
                    "raw_response": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到公众号素材库
        返回图片URL（用于图文消息正文）
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/media/uploadimg"
        params = {"access_token": token}
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": f}
                resp = requests.post(url, params=params, files=files)
                result = resp.json()
                
                if "url" in result:
                    return result["url"]
                else:
                    print(f"上传图片失败: {result.get('errmsg')}")
        except Exception as e:
            print(f"上传图片异常: {e}")
        
        return None
    
    def upload_thumb(self, image_path: str) -> Optional[str]:
        """
        上传封面图片（缩略图）
        返回 media_id（用于图文消息封面）
        图片大小限制：2MB，支持JPG/PNG
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/material/add_material"
        params = {
            "access_token": token,
            "type": "thumb"
        }
        
        try:
            with open(image_path, "rb") as f:
                files = {"media": f}
                resp = requests.post(url, params=params, files=files)
                result = resp.json()
                
                if "media_id" in result:
                    return result["media_id"]
                else:
                    print(f"上传封面失败: {result.get('errmsg')}")
        except Exception as e:
            print(f"上传封面异常: {e}")
        
        return None
    
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        发布带图片的图文消息
        注意：微信公众号的图片需要分两步处理
        1. 正文图片：上传后获取URL插入HTML
        2. 封面图片：上传后获取media_id
        """
        # 上传正文图片并构建HTML内容
        html_content = f"<p>{content}</p>"
        
        for img_path in image_paths:
            img_url = self.upload_image(img_path)
            if img_url:
                html_content += f'<p><img src="{img_url}" /></p>'
        
        # 发布图文消息
        return self.post_article(
            title="图文消息",
            content=html_content,
            digest=content[:50] + "..." if len(content) > 50 else content
        )
    
    def preview_message(self, title: str, content: str, wxname: str) -> Dict[str, Any]:
        """
        预览消息（发送给指定用户）
        
        Args:
            title: 标题
            content: 内容
            wxname: 接收者的微信号
        """
        token = self._get_access_token()
        
        # 先上传素材
        url = f"{self.base_url}/material/add_news"
        params = {"access_token": token}
        
        articles = [{
            "title": title,
            "thumb_media_id": self.config.get("default_thumb_media_id", ""),
            "content": content,
            "show_cover_pic": 0
        }]
        
        resp = requests.post(url, params=params, json={"articles": articles})
        result = resp.json()
        
        if "media_id" not in result:
            return {
                "success": False,
                "error": f"上传素材失败: {result.get('errmsg')}"
            }
        
        media_id = result["media_id"]
        
        # 发送预览
        url = f"{self.base_url}/message/mass/preview"
        params = {"access_token": token}
        
        data = {
            "touser": wxname,
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews"
        }
        
        try:
            resp = requests.post(url, params=params, json=data)
            result = resp.json()
            
            if result.get("errcode") == 0:
                return {
                    "success": True,
                    "message": "预览消息已发送"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errmsg", "预览发送失败")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_message_status(self, msg_id: str) -> Dict[str, Any]:
        """
        查询群发消息状态
        
        Args:
            msg_id: 消息ID
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}/message/mass/get"
        params = {"access_token": token}
        
        data = {"msg_id": msg_id}
        
        try:
            resp = requests.post(url, params=params, json=data)
            result = resp.json()
            
            if result.get("errcode") == 0:
                return {
                    "success": True,
                    "msg_id": msg_id,
                    "msg_status": result.get("msg_status"),
                    "send_status": "SEND_SUCCESS" if result.get("msg_status") == "SEND_SUCCESS" else result.get("msg_status")
                }
            else:
                return {
                    "success": False,
                    "error": result.get("errmsg", "查询失败")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }