"""
自动发帖平台基类
所有平台实现都需要继承此类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BasePlatform(ABC):
    """平台基类"""
    
    name: str = ""
    display_name: str = ""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化平台
        
        Args:
            config: 平台配置字典
        """
        self.config = config
        self.session = None
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置是否完整"""
        pass
    
    @abstractmethod
    def login(self) -> bool:
        """
        登录平台
        
        Returns:
            登录是否成功
        """
        pass
    
    @abstractmethod
    def post_text(self, content: str) -> Dict[str, Any]:
        """
        发布纯文本内容
        
        Args:
            content: 帖子内容
            
        Returns:
            发布结果，包含 post_id, url, status 等
        """
        pass
    
    @abstractmethod
    def post_with_image(self, content: str, image_paths: List[str]) -> Dict[str, Any]:
        """
        发布带图片的内容
        
        Args:
            content: 帖子内容
            image_paths: 图片路径列表
            
        Returns:
            发布结果
        """
        pass
    
    def post(self, content: str, image_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        通用发帖接口
        
        Args:
            content: 帖子内容
            image_paths: 图片路径列表（可选）
            
        Returns:
            发布结果
        """
        if not self.login():
            return {
                "success": False,
                "error": "登录失败",
                "platform": self.name
            }
        
        try:
            if image_paths and len(image_paths) > 0:
                result = self.post_with_image(content, image_paths)
            else:
                result = self.post_text(content)
            
            result["platform"] = self.name
            return result
            
        except Exception as e:
            logger.error(f"{self.name} 发帖失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": self.name
            }
    
    def check_rate_limit(self) -> bool:
        """
        检查是否超过发帖频率限制
        
        Returns:
            是否可以发帖
        """
        # 子类可以重写此方法实现自定义频率限制
        return True
    
    def get_character_limit(self) -> int:
        """
        获取平台字符限制
        
        Returns:
            最大字符数
        """
        return 2000  # 默认值
    
    def truncate_content(self, content: str) -> str:
        """
        截断内容以适应平台限制
        
        Args:
            content: 原始内容
            
        Returns:
            截断后的内容
        """
        limit = self.get_character_limit()
        if len(content) <= limit:
            return content
        return content[:limit-3] + "..."