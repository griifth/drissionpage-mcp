"""Markdown 转换工具

将网页内容转换为 Markdown 格式并保存。
"""

import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import markdownify
    USE_MARKDOWNIFY = True
except ImportError:
    USE_MARKDOWNIFY = False

try:
    import html2text
    USE_HTML2TEXT = True
except ImportError:
    USE_HTML2TEXT = False

from bs4 import BeautifulSoup

try:
    from ..browser import browser_manager
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from browser import browser_manager

logger = logging.getLogger(__name__)


def _clean_html(html: str, remove_ads: bool = True) -> str:
    """清理 HTML，移除广告和不必要的元素
    
    Args:
        html: 原始 HTML
        remove_ads: 是否移除广告相关元素
    
    Returns:
        str: 清理后的 HTML
    """
    soup = BeautifulSoup(html, 'lxml')
    
    if remove_ads:
        # 移除常见的广告和无用元素
        for selector in [
            'script', 'style', 'iframe', 'noscript',
            '[class*="ad-"]', '[class*="advertisement"]',
            '[id*="ad-"]', '[id*="advertisement"]',
            '.sidebar', '.footer', '.header-ad',
            '[class*="social-share"]', '[class*="cookie"]'
        ]:
            for element in soup.select(selector):
                element.decompose()
    
    return str(soup)


def _html_to_markdown_markdownify(html: str, **options) -> str:
    """使用 markdownify 转换 HTML 到 Markdown
    
    Args:
        html: HTML 内容
        **options: markdownify 选项
    
    Returns:
        str: Markdown 内容
    """
    default_options = {
        'heading_style': 'ATX',
        'bullets': '-',
        'strong_em_symbol': '**',
        'strip': ['script', 'style']
    }
    default_options.update(options)
    
    return markdownify.markdownify(html, **default_options)


def _html_to_markdown_html2text(html: str, **options) -> str:
    """使用 html2text 转换 HTML 到 Markdown
    
    Args:
        html: HTML 内容
        **options: html2text 选项
    
    Returns:
        str: Markdown 内容
    """
    h = html2text.HTML2Text()
    
    # 默认配置
    h.ignore_links = options.get('ignore_links', False)
    h.ignore_images = options.get('ignore_images', False)
    h.ignore_emphasis = options.get('ignore_emphasis', False)
    h.body_width = options.get('body_width', 0)  # 0 表示不换行
    h.unicode_snob = options.get('unicode_snob', True)
    h.skip_internal_links = options.get('skip_internal_links', True)
    h.inline_links = options.get('inline_links', True)
    h.protect_links = options.get('protect_links', True)
    h.mark_code = options.get('mark_code', True)
    
    return h.handle(html)


def _extract_main_content(html: str) -> str:
    """尝试提取页面主要内容
    
    Args:
        html: 完整的 HTML
    
    Returns:
        str: 主要内容的 HTML
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # 尝试查找主要内容区域
    main_selectors = [
        'main', 'article', '[role="main"]',
        '.main-content', '#main-content',
        '.content', '#content',
        '.post-content', '.article-content'
    ]
    
    for selector in main_selectors:
        main = soup.select_one(selector)
        if main:
            return str(main)
    
    # 如果没找到，尝试找 body
    body = soup.find('body')
    if body:
        return str(body)
    
    # 否则返回原始 HTML
    return html


def page_to_markdown(
    file_path: str,
    include_images: bool = True,
    remove_ads: bool = True,
    extract_main: bool = True,
    converter: str = "auto",
    add_metadata: bool = True
) -> Dict[str, Any]:
    """将当前页面转换为 Markdown 并保存
    
    这是核心功能，将网页内容智能转换为 Markdown 格式。
    
    Args:
        file_path: 保存的文件路径
        include_images: 是否包含图片，默认 True
        remove_ads: 是否移除广告元素，默认 True
        extract_main: 是否只提取主要内容区域，默认 True
        converter: 转换器选择，'markdownify', 'html2text', 'auto'，默认 'auto'
        add_metadata: 是否添加元数据（标题、URL等），默认 True
    
    Returns:
        Dict[str, Any]: 操作结果，包含保存路径和统计信息
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
        
        # 获取页面信息
        url = tab.url
        title = tab.title
        
        # 获取 HTML
        html = tab.html
        
        if not html:
            return {
                "success": False,
                "error": "无法获取页面 HTML"
            }
        
        # 提取主要内容
        if extract_main:
            html = _extract_main_content(html)
        
        # 清理 HTML
        if remove_ads:
            html = _clean_html(html, remove_ads=True)
        
        # 选择转换器
        if converter == "auto":
            if USE_MARKDOWNIFY:
                converter = "markdownify"
            elif USE_HTML2TEXT:
                converter = "html2text"
            else:
                return {
                    "success": False,
                    "error": "未安装 Markdown 转换库，请安装 markdownify 或 html2text"
                }
        
        # 转换为 Markdown
        if converter == "markdownify":
            if not USE_MARKDOWNIFY:
                return {
                    "success": False,
                    "error": "markdownify 未安装"
                }
            markdown_content = _html_to_markdown_markdownify(
                html,
                strip=['script', 'style']
            )
        elif converter == "html2text":
            if not USE_HTML2TEXT:
                return {
                    "success": False,
                    "error": "html2text 未安装"
                }
            markdown_content = _html_to_markdown_html2text(
                html,
                ignore_images=not include_images
            )
        else:
            return {
                "success": False,
                "error": f"不支持的转换器: {converter}"
            }
        
        # 清理 Markdown（移除过多的空行）
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # 添加元数据
        if add_metadata:
            metadata = f"""# {title}

**URL**: {url}  
**转换时间**: {Path(file_path).stem}

---

"""
            markdown_content = metadata + markdown_content
        
        # 确保目录存在
        path_obj = Path(file_path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(path_obj, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # 统计信息
        line_count = len(markdown_content.split('\n'))
        char_count = len(markdown_content)
        word_count = len(markdown_content.split())
        
        return {
            "success": True,
            "message": "网页已成功转换为 Markdown",
            "file_path": str(path_obj.absolute()),
            "url": url,
            "title": title,
            "converter": converter,
            "stats": {
                "lines": line_count,
                "characters": char_count,
                "words": word_count
            }
        }
        
    except Exception as e:
        logger.error(f"转换 Markdown 失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"转换 Markdown 失败: {str(e)}"
        }


def get_page_content(
    format: str = "markdown",
    extract_main: bool = True,
    remove_ads: bool = True
) -> Dict[str, Any]:
    """获取当前页面内容（不保存文件）
    
    Args:
        format: 返回格式，'markdown', 'html', 'text'
        extract_main: 是否只提取主要内容
        remove_ads: 是否移除广告
    
    Returns:
        Dict[str, Any]: 包含页面内容的结果
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
        
        url = tab.url
        title = tab.title
        
        if format == "text":
            # 直接获取纯文本
            content = tab.text
        elif format == "html":
            # 获取 HTML
            html = tab.html
            if extract_main:
                html = _extract_main_content(html)
            if remove_ads:
                html = _clean_html(html)
            content = html
        elif format == "markdown":
            # 转换为 Markdown
            html = tab.html
            if extract_main:
                html = _extract_main_content(html)
            if remove_ads:
                html = _clean_html(html)
            
            if USE_MARKDOWNIFY:
                content = _html_to_markdown_markdownify(html)
            elif USE_HTML2TEXT:
                content = _html_to_markdown_html2text(html)
            else:
                # 降级到纯文本
                content = tab.text
                format = "text"
        else:
            return {
                "success": False,
                "error": f"不支持的格式: {format}"
            }
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "format": format,
            "content": content,
            "length": len(content)
        }
        
    except Exception as e:
        logger.error(f"获取页面内容失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"获取页面内容失败: {str(e)}"
        }

