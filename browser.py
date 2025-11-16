"""浏览器单例管理器

全局管理单个 Chromium 浏览器实例，确保线程安全。
"""

import logging
import threading
from typing import Optional, Dict, Any

from DrissionPage import Chromium, ChromiumOptions

logger = logging.getLogger(__name__)


class BrowserManager:
    """浏览器单例管理器
    
    使用单例模式管理全局唯一的浏览器实例，确保线程安全。
    """
    
    _instance: Optional['BrowserManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化浏览器管理器"""
        if not hasattr(self, '_initialized'):
            self._browser: Optional[Chromium] = None
            self._current_tab = None
            self._initialized = True
            logger.info("浏览器管理器已初始化")
    
    def init_browser(
        self,
        headless: bool = False,
        window_size: tuple = (1920, 1080),
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """初始化浏览器实例
        
        Args:
            headless: 是否使用无头模式，默认 False（有头模式）
            window_size: 浏览器窗口大小，默认 (1920, 1080)
            user_agent: 自定义 User Agent
            proxy: 代理服务器地址
            **kwargs: 其他 ChromiumOptions 参数
        
        Returns:
            Dict[str, Any]: 包含成功状态和浏览器信息
        """
        with self._lock:
            try:
                if self._browser is not None:
                    logger.warning("浏览器已经在运行中，返回现有实例")
                    return {
                        "success": True,
                        "message": "浏览器已在运行",
                        "status": self.get_status()
                    }
                
                # 配置浏览器选项
                options = ChromiumOptions()
                
                if headless:
                    options.headless()
                
                # 设置窗口大小（使用参数）
                options.set_argument(f'--window-size={window_size[0]},{window_size[1]}')
                
                # 设置 User Agent
                if user_agent:
                    options.set_user_agent(user_agent)
                
                # 设置代理
                if proxy:
                    options.set_proxy(proxy)
                
                # 应用其他配置
                for key, value in kwargs.items():
                    if hasattr(options, key):
                        getattr(options, key)(value)
                
                # 创建浏览器实例
                self._browser = Chromium(addr_or_opts=options)
                self._current_tab = self._browser.latest_tab
                
                logger.info("浏览器实例已创建")
                
                return {
                    "success": True,
                    "message": "浏览器初始化成功",
                    "status": self.get_status()
                }
                
            except Exception as e:
                logger.error(f"初始化浏览器失败: {str(e)}", exc_info=True)
                return {
                    "success": False,
                    "error": f"初始化浏览器失败: {str(e)}"
                }
    
    def get_browser(self) -> Optional[Chromium]:
        """获取浏览器实例
        
        Returns:
            Optional[Chromium]: 浏览器实例，如果未初始化则返回 None
        """
        return self._browser
    
    def get_current_tab(self):
        """获取当前活跃的标签页
        
        Returns:
            当前标签页对象，如果浏览器未初始化则返回 None
        """
        if self._browser is None:
            return None
        
        # 如果没有当前标签页或标签页已关闭，获取最新的标签页
        if self._current_tab is None:
            self._current_tab = self._browser.latest_tab
        
        return self._current_tab
    
    def set_current_tab(self, tab):
        """设置当前活跃的标签页
        
        Args:
            tab: 要设置为当前的标签页对象
        """
        self._current_tab = tab
    
    def get_status(self) -> Dict[str, Any]:
        """获取浏览器状态
        
        Returns:
            Dict[str, Any]: 包含浏览器状态信息
        """
        if self._browser is None:
            return {
                "running": False,
                "message": "浏览器未初始化"
            }
        
        try:
            tab = self.get_current_tab()
            if tab is None:
                return {
                    "running": True,
                    "message": "浏览器运行中，但没有活跃标签页"
                }
            
            try:
                tab_count = len(self._browser.get_tabs()) if hasattr(self._browser, 'get_tabs') else 1
            except:
                tab_count = 1
            
            return {
                "running": True,
                "url": tab.url,
                "title": tab.title,
                "tab_count": tab_count,
                "message": "浏览器运行正常"
            }
        except Exception as e:
            logger.error(f"获取浏览器状态失败: {str(e)}")
            return {
                "running": False,
                "error": f"获取状态失败: {str(e)}"
            }
    
    def close_browser(self) -> Dict[str, Any]:
        """关闭浏览器实例
        
        Returns:
            Dict[str, Any]: 包含操作结果
        """
        with self._lock:
            try:
                if self._browser is None:
                    return {
                        "success": True,
                        "message": "浏览器未在运行"
                    }
                
                self._browser.quit()
                self._browser = None
                self._current_tab = None
                
                logger.info("浏览器已关闭")
                
                return {
                    "success": True,
                    "message": "浏览器已成功关闭"
                }
                
            except Exception as e:
                logger.error(f"关闭浏览器失败: {str(e)}", exc_info=True)
                # 即使出错也清理引用
                self._browser = None
                self._current_tab = None
                
                return {
                    "success": False,
                    "error": f"关闭浏览器失败: {str(e)}"
                }
    
    def is_running(self) -> bool:
        """检查浏览器是否在运行
        
        Returns:
            bool: 浏览器是否在运行
        """
        return self._browser is not None
    
    def ensure_browser(self) -> bool:
        """确保浏览器已初始化
        
        如果浏览器未初始化，则自动初始化。
        
        Returns:
            bool: 浏览器是否可用
        """
        if not self.is_running():
            result = self.init_browser()
            return result.get("success", False)
        return True


# 全局单例实例
browser_manager = BrowserManager()

