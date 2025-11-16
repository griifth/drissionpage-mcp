"""基础操作工具集

提供细粒度的浏览器控制操作，包括导航、元素查找、点击、输入等。
"""

import logging
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

try:
    from ..browser import browser_manager
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from browser import browser_manager

logger = logging.getLogger(__name__)


def navigate(url: str, timeout: int = 30) -> Dict[str, Any]:
    """导航到指定 URL
    
    Args:
        url: 目标网址
        timeout: 超时时间（秒），默认 30
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 导航到 URL
        tab.get(url, timeout=timeout)
        
        # 等待页面加载
        time.sleep(1)
        
        return {
            "success": True,
            "url": tab.url,
            "title": tab.title,
            "message": f"已成功导航到 {url}"
        }
        
    except Exception as e:
        logger.error(f"导航失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"导航失败: {str(e)}"
        }


def find_elements(
    selector: str,
    selector_type: str = "css",
    single: bool = False,
    timeout: float = 10
) -> Dict[str, Any]:
    """查找页面元素
    
    Args:
        selector: 选择器字符串
        selector_type: 选择器类型，支持 'css', 'xpath', 'text'，默认 'css'
        single: 是否只返回第一个匹配元素，默认 False
        timeout: 等待超时时间（秒），默认 10
    
    Returns:
        Dict[str, Any]: 包含找到的元素信息
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 根据选择器类型查找元素
        if selector_type == "css":
            if single:
                element = tab.ele(selector, timeout=timeout)
            else:
                element = tab.eles(selector, timeout=timeout)
        elif selector_type == "xpath":
            if single:
                element = tab.ele(f"xpath:{selector}", timeout=timeout)
            else:
                element = tab.eles(f"xpath:{selector}", timeout=timeout)
        elif selector_type == "text":
            if single:
                element = tab.ele(f"text:{selector}", timeout=timeout)
            else:
                element = tab.eles(f"text:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        # 处理结果
        if single:
            if element:
                return {
                    "success": True,
                    "found": True,
                    "count": 1,
                    "element": {
                        "tag": element.tag,
                        "text": element.text,
                        "attrs": element.attrs
                    }
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "count": 0,
                    "message": "未找到匹配的元素"
                }
        else:
            if element:
                elements_info = [
                    {
                        "tag": el.tag,
                        "text": el.text,
                        "attrs": el.attrs
                    }
                    for el in element[:10]  # 限制返回前 10 个元素
                ]
                return {
                    "success": True,
                    "found": True,
                    "count": len(element),
                    "elements": elements_info,
                    "message": f"找到 {len(element)} 个元素（显示前 10 个）"
                }
            else:
                return {
                    "success": True,
                    "found": False,
                    "count": 0,
                    "message": "未找到匹配的元素"
                }
        
    except Exception as e:
        logger.error(f"查找元素失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"查找元素失败: {str(e)}"
        }


def click_element(
    selector: str,
    selector_type: str = "css",
    timeout: float = 10,
    wait_after: float = 1
) -> Dict[str, Any]:
    """点击指定元素
    
    Args:
        selector: 选择器字符串
        selector_type: 选择器类型，支持 'css', 'xpath', 'text'，默认 'css'
        timeout: 等待元素出现的超时时间（秒），默认 10
        wait_after: 点击后等待时间（秒），默认 1
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 查找元素
        if selector_type == "css":
            element = tab.ele(selector, timeout=timeout)
        elif selector_type == "xpath":
            element = tab.ele(f"xpath:{selector}", timeout=timeout)
        elif selector_type == "text":
            element = tab.ele(f"text:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        if not element:
            return {
                "success": False,
                "error": f"未找到元素: {selector}"
            }
        
        # 点击元素
        element.click()
        
        # 等待
        if wait_after > 0:
            time.sleep(wait_after)
        
        return {
            "success": True,
            "message": f"已成功点击元素: {selector}",
            "element": {
                "tag": element.tag,
                "text": element.text
            }
        }
        
    except Exception as e:
        logger.error(f"点击元素失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"点击元素失败: {str(e)}"
        }


def input_text(
    selector: str,
    text: str,
    selector_type: str = "css",
    clear_first: bool = True,
    timeout: float = 10
) -> Dict[str, Any]:
    """向元素输入文本
    
    Args:
        selector: 选择器字符串
        text: 要输入的文本
        selector_type: 选择器类型，支持 'css', 'xpath'，默认 'css'
        clear_first: 是否先清空原有内容，默认 True
        timeout: 等待元素出现的超时时间（秒），默认 10
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 查找元素
        if selector_type == "css":
            element = tab.ele(selector, timeout=timeout)
        elif selector_type == "xpath":
            element = tab.ele(f"xpath:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        if not element:
            return {
                "success": False,
                "error": f"未找到元素: {selector}"
            }
        
        # 清空并输入文本
        if clear_first:
            element.clear()
        
        element.input(text)
        
        return {
            "success": True,
            "message": f"已成功输入文本到元素: {selector}",
            "text": text
        }
        
    except Exception as e:
        logger.error(f"输入文本失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"输入文本失败: {str(e)}"
        }


def get_element_text(
    selector: str,
    selector_type: str = "css",
    timeout: float = 10
) -> Dict[str, Any]:
    """获取元素文本内容
    
    Args:
        selector: 选择器字符串
        selector_type: 选择器类型，支持 'css', 'xpath'，默认 'css'
        timeout: 等待元素出现的超时时间（秒），默认 10
    
    Returns:
        Dict[str, Any]: 包含元素文本的结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 查找元素
        if selector_type == "css":
            element = tab.ele(selector, timeout=timeout)
        elif selector_type == "xpath":
            element = tab.ele(f"xpath:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        if not element:
            return {
                "success": False,
                "error": f"未找到元素: {selector}"
            }
        
        return {
            "success": True,
            "text": element.text,
            "tag": element.tag
        }
        
    except Exception as e:
        logger.error(f"获取元素文本失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"获取元素文本失败: {str(e)}"
        }


def get_element_attribute(
    selector: str,
    attribute: str,
    selector_type: str = "css",
    timeout: float = 10
) -> Dict[str, Any]:
    """获取元素属性值
    
    Args:
        selector: 选择器字符串
        attribute: 属性名
        selector_type: 选择器类型，支持 'css', 'xpath'，默认 'css'
        timeout: 等待元素出现的超时时间（秒），默认 10
    
    Returns:
        Dict[str, Any]: 包含属性值的结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 查找元素
        if selector_type == "css":
            element = tab.ele(selector, timeout=timeout)
        elif selector_type == "xpath":
            element = tab.ele(f"xpath:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        if not element:
            return {
                "success": False,
                "error": f"未找到元素: {selector}"
            }
        
        value = element.attr(attribute)
        
        return {
            "success": True,
            "attribute": attribute,
            "value": value
        }
        
    except Exception as e:
        logger.error(f"获取元素属性失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"获取元素属性失败: {str(e)}"
        }


def wait_for_element(
    selector: str,
    selector_type: str = "css",
    timeout: float = 30,
    visible: bool = True
) -> Dict[str, Any]:
    """等待元素出现
    
    Args:
        selector: 选择器字符串
        selector_type: 选择器类型，支持 'css', 'xpath'，默认 'css'
        timeout: 超时时间（秒），默认 30
        visible: 是否要求元素可见，默认 True
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 查找元素
        start_time = time.time()
        if selector_type == "css":
            element = tab.ele(selector, timeout=timeout)
        elif selector_type == "xpath":
            element = tab.ele(f"xpath:{selector}", timeout=timeout)
        else:
            return {
                "success": False,
                "error": f"不支持的选择器类型: {selector_type}"
            }
        
        elapsed = time.time() - start_time
        
        if not element:
            return {
                "success": False,
                "error": f"等待超时，未找到元素: {selector}",
                "elapsed": elapsed
            }
        
        # 检查可见性
        if visible:
            # DrissionPage 的元素默认会等待可见
            pass
        
        return {
            "success": True,
            "message": f"元素已出现: {selector}",
            "elapsed": elapsed,
            "element": {
                "tag": element.tag,
                "text": element.text
            }
        }
        
    except Exception as e:
        logger.error(f"等待元素失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"等待元素失败: {str(e)}"
        }


def scroll_page(
    direction: str = "down",
    amount: Union[int, str] = "page",
    wait_after: float = 0.5
) -> Dict[str, Any]:
    """滚动页面
    
    Args:
        direction: 滚动方向，'up', 'down', 'left', 'right', 'top', 'bottom'
        amount: 滚动量，'page'（一屏）, 'half'（半屏）, 或具体像素数
        wait_after: 滚动后等待时间（秒），默认 0.5
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 执行滚动
        if direction == "bottom":
            tab.scroll.to_bottom()
        elif direction == "top":
            tab.scroll.to_top()
        elif direction == "down":
            if amount == "page":
                tab.scroll.down(1000)
            elif amount == "half":
                tab.scroll.down(500)
            else:
                tab.scroll.down(int(amount))
        elif direction == "up":
            if amount == "page":
                tab.scroll.up(1000)
            elif amount == "half":
                tab.scroll.up(500)
            else:
                tab.scroll.up(int(amount))
        else:
            return {
                "success": False,
                "error": f"不支持的滚动方向: {direction}"
            }
        
        # 等待
        if wait_after > 0:
            time.sleep(wait_after)
        
        return {
            "success": True,
            "message": f"已滚动页面: {direction} {amount}"
        }
        
    except Exception as e:
        logger.error(f"滚动页面失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"滚动页面失败: {str(e)}"
        }


def take_screenshot(
    file_path: Optional[str] = None,
    full_page: bool = False
) -> Dict[str, Any]:
    """页面截图
    
    Args:
        file_path: 保存路径，如果为 None 则自动生成
        full_page: 是否截取整个页面，默认 False（只截取视口）
    
    Returns:
        Dict[str, Any]: 操作结果，包含保存路径
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 生成默认文件名
        if file_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            file_path = f"screenshot_{timestamp}.png"
        
        # 确保目录存在
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 截图
        if full_page:
            tab.get_screenshot(path=str(file_path), full_page=True)
        else:
            tab.get_screenshot(path=str(file_path))
        
        return {
            "success": True,
            "message": "截图成功",
            "file_path": str(path_obj.absolute()),
            "full_page": full_page
        }
        
    except Exception as e:
        logger.error(f"截图失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"截图失败: {str(e)}"
        }


def execute_javascript(
    script: str,
    *args
) -> Dict[str, Any]:
    """执行自定义 JavaScript 代码
    
    Args:
        script: JavaScript 代码
        *args: 传递给 JavaScript 的参数
    
    Returns:
        Dict[str, Any]: 执行结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        tab = browser_manager.get_current_tab()
        if tab is None:
            return {
                "success": False,
                "error": "没有可用的标签页"
            }
        
        # 执行 JavaScript
        result = tab.run_js(script, *args)
        
        return {
            "success": True,
            "result": result,
            "message": "JavaScript 执行成功"
        }
        
    except Exception as e:
        logger.error(f"执行 JavaScript 失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"执行 JavaScript 失败: {str(e)}"
        }

