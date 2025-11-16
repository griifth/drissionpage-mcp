"""高级功能工具

提供常见任务的高级封装，如表单填写、数据提取、懒加载处理等。
"""

import logging
import time
import json
import csv
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


def extract_table_data(
    selector: str = "table",
    format: str = "json",
    output_file: Optional[str] = None,
    include_header: bool = True
) -> Dict[str, Any]:
    """提取网页表格数据为结构化格式
    
    Args:
        selector: 表格选择器，默认 'table'
        format: 输出格式，'json' 或 'csv'，默认 'json'
        output_file: 可选的输出文件路径
        include_header: 是否包含表头，默认 True
    
    Returns:
        Dict[str, Any]: 包含表格数据的结果
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
        
        # 查找表格
        table = tab.ele(selector, timeout=10)
        if not table:
            return {
                "success": False,
                "error": f"未找到表格: {selector}"
            }
        
        # 提取表头
        headers = []
        thead = table.ele('tag:thead', timeout=2)
        if thead:
            header_cells = thead.eles('tag:th')
            if not header_cells:
                header_cells = thead.eles('tag:td')
            headers = [cell.text.strip() for cell in header_cells]
        
        # 如果没有 thead，尝试从第一行获取
        if not headers:
            first_row = table.ele('tag:tr', timeout=2)
            if first_row:
                cells = first_row.eles('tag:th')
                if not cells:
                    cells = first_row.eles('tag:td')
                headers = [cell.text.strip() for cell in cells]
        
        # 提取数据行
        rows = []
        tbody = table.ele('tag:tbody', timeout=2)
        if tbody:
            tr_list = tbody.eles('tag:tr')
        else:
            tr_list = table.eles('tag:tr')
            # 如果第一行是表头，跳过它
            if headers and include_header and tr_list:
                tr_list = tr_list[1:]
        
        for tr in tr_list:
            cells = tr.eles('tag:td')
            if not cells:
                cells = tr.eles('tag:th')
            
            row_data = [cell.text.strip() for cell in cells]
            if row_data:  # 跳过空行
                rows.append(row_data)
        
        # 格式化数据
        if format == "json":
            if headers:
                # 使用表头作为键
                data = [
                    dict(zip(headers, row))
                    for row in rows
                ]
            else:
                # 没有表头，使用数组
                data = rows
            
            result_data = {
                "headers": headers if include_header else None,
                "rows": data,
                "row_count": len(rows)
            }
            
            # 保存到文件
            if output_file:
                path_obj = Path(output_file)
                path_obj.parent.mkdir(parents=True, exist_ok=True)
                with open(path_obj, 'w', encoding='utf-8') as f:
                    json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "format": "json",
                "data": result_data,
                "output_file": output_file
            }
        
        elif format == "csv":
            # 保存为 CSV
            if not output_file:
                output_file = "table_data.csv"
            
            path_obj = Path(output_file)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path_obj, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                if headers and include_header:
                    writer.writerow(headers)
                writer.writerows(rows)
            
            return {
                "success": True,
                "format": "csv",
                "row_count": len(rows),
                "column_count": len(headers) if headers else (len(rows[0]) if rows else 0),
                "output_file": str(path_obj.absolute())
            }
        
        else:
            return {
                "success": False,
                "error": f"不支持的格式: {format}"
            }
        
    except Exception as e:
        logger.error(f"提取表格数据失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"提取表格数据失败: {str(e)}"
        }


def smart_extract(
    selector: str,
    fields: Dict[str, str],
    limit: int = 100
) -> Dict[str, Any]:
    """智能数据抓取
    
    根据选择器提取多个元素的结构化数据。
    
    Args:
        selector: 容器元素选择器（匹配多个项）
        fields: 字段映射，{字段名: 子选择器}
        limit: 最多提取的项数，默认 100
    
    Returns:
        Dict[str, Any]: 包含提取的结构化数据
        
    Example:
        smart_extract(
            selector="div.article",
            fields={
                "title": "h2.title",
                "author": "span.author",
                "date": "time"
            }
        )
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
        
        # 查找所有匹配的容器
        containers = tab.eles(selector, timeout=10)
        
        if not containers:
            return {
                "success": False,
                "error": f"未找到匹配的元素: {selector}"
            }
        
        # 限制数量
        containers = containers[:limit]
        
        # 提取数据
        results = []
        for container in containers:
            item = {}
            for field_name, field_selector in fields.items():
                try:
                    element = container.ele(field_selector, timeout=2)
                    if element:
                        # 尝试获取不同类型的内容
                        if element.tag == 'img':
                            item[field_name] = element.attr('src')
                        elif element.tag == 'a':
                            item[field_name] = {
                                "text": element.text,
                                "href": element.attr('href')
                            }
                        else:
                            item[field_name] = element.text.strip()
                    else:
                        item[field_name] = None
                except Exception as e:
                    logger.warning(f"提取字段 {field_name} 失败: {str(e)}")
                    item[field_name] = None
            
            results.append(item)
        
        return {
            "success": True,
            "count": len(results),
            "data": results,
            "message": f"成功提取 {len(results)} 项数据"
        }
        
    except Exception as e:
        logger.error(f"智能提取失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"智能提取失败: {str(e)}"
        }


def fill_form(
    fields: Dict[str, Any],
    submit_selector: Optional[str] = None,
    wait_after_submit: float = 2
) -> Dict[str, Any]:
    """自动填写表单
    
    Args:
        fields: 字段映射，{选择器: 值}
        submit_selector: 提交按钮选择器，如果为 None 则不提交
        wait_after_submit: 提交后等待时间（秒），默认 2
    
    Returns:
        Dict[str, Any]: 操作结果
        
    Example:
        fill_form(
            fields={
                "#username": "user@example.com",
                "#password": "password123",
                "#remember": True  # checkbox
            },
            submit_selector="button[type='submit']"
        )
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
        
        filled_fields = []
        errors = []
        
        # 填写每个字段
        for selector, value in fields.items():
            try:
                element = tab.ele(selector, timeout=10)
                if not element:
                    errors.append(f"未找到元素: {selector}")
                    continue
                
                tag = element.tag.lower()
                input_type = (element.attr('type') or '').lower()
                
                # 根据元素类型处理
                if tag == 'input':
                    if input_type in ['checkbox', 'radio']:
                        # 复选框和单选框
                        if value:
                            if not element.states.is_checked:
                                element.click()
                        else:
                            if element.states.is_checked:
                                element.click()
                    else:
                        # 文本输入框
                        element.clear()
                        element.input(str(value))
                
                elif tag == 'textarea':
                    # 文本区域
                    element.clear()
                    element.input(str(value))
                
                elif tag == 'select':
                    # 下拉框
                    element.select(str(value))
                
                else:
                    # 其他元素，尝试直接输入
                    element.clear()
                    element.input(str(value))
                
                filled_fields.append(selector)
                
            except Exception as e:
                logger.warning(f"填写字段 {selector} 失败: {str(e)}")
                errors.append(f"{selector}: {str(e)}")
        
        # 提交表单
        submitted = False
        if submit_selector:
            try:
                submit_btn = tab.ele(submit_selector, timeout=10)
                if submit_btn:
                    submit_btn.click()
                    time.sleep(wait_after_submit)
                    submitted = True
                else:
                    errors.append(f"未找到提交按钮: {submit_selector}")
            except Exception as e:
                errors.append(f"提交表单失败: {str(e)}")
        
        return {
            "success": len(errors) == 0,
            "filled_fields": filled_fields,
            "submitted": submitted,
            "errors": errors if errors else None,
            "message": f"成功填写 {len(filled_fields)} 个字段"
        }
        
    except Exception as e:
        logger.error(f"填写表单失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"填写表单失败: {str(e)}"
        }


def handle_infinite_scroll(
    max_scrolls: int = 10,
    scroll_pause: float = 2,
    check_selector: Optional[str] = None
) -> Dict[str, Any]:
    """处理无限滚动/懒加载
    
    自动滚动页面直到内容不再增加。
    
    Args:
        max_scrolls: 最大滚动次数，默认 10
        scroll_pause: 每次滚动后的等待时间（秒），默认 2
        check_selector: 用于检查新内容的选择器（可选）
    
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
        
        scroll_count = 0
        last_height = 0
        last_count = 0
        
        for i in range(max_scrolls):
            # 滚动到底部
            tab.scroll.to_bottom()
            scroll_count += 1
            
            # 等待内容加载
            time.sleep(scroll_pause)
            
            # 检查是否有新内容
            if check_selector:
                # 通过元素数量检查
                elements = tab.eles(check_selector, timeout=2)
                current_count = len(elements) if elements else 0
                
                if current_count == last_count:
                    # 没有新内容，停止滚动
                    break
                
                last_count = current_count
            else:
                # 通过页面高度检查
                current_height = tab.run_js('return document.body.scrollHeight')
                
                if current_height == last_height:
                    # 页面高度没变，停止滚动
                    break
                
                last_height = current_height
        
        return {
            "success": True,
            "scroll_count": scroll_count,
            "final_count": last_count if check_selector else None,
            "final_height": last_height if not check_selector else None,
            "message": f"完成 {scroll_count} 次滚动"
        }
        
    except Exception as e:
        logger.error(f"处理无限滚动失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"处理无限滚动失败: {str(e)}"
        }


def manage_cookies(
    action: str,
    name: Optional[str] = None,
    value: Optional[str] = None,
    domain: Optional[str] = None
) -> Dict[str, Any]:
    """Cookie 管理
    
    Args:
        action: 操作类型，'get', 'set', 'delete', 'clear'
        name: Cookie 名称（get/set/delete 时需要）
        value: Cookie 值（set 时需要）
        domain: Cookie 域名（set 时可选）
    
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
        
        if action == "get":
            if name:
                # 获取特定 Cookie
                cookie = tab.cookies(name)
                return {
                    "success": True,
                    "action": "get",
                    "name": name,
                    "value": cookie
                }
            else:
                # 获取所有 Cookies
                cookies = tab.cookies()
                return {
                    "success": True,
                    "action": "get",
                    "cookies": cookies,
                    "count": len(cookies) if cookies else 0
                }
        
        elif action == "set":
            if not name or value is None:
                return {
                    "success": False,
                    "error": "设置 Cookie 需要 name 和 value"
                }
            
            # 设置 Cookie
            tab.set.cookies([(name, value, domain or tab.url)])
            
            return {
                "success": True,
                "action": "set",
                "name": name,
                "message": f"Cookie {name} 已设置"
            }
        
        elif action == "delete":
            if not name:
                return {
                    "success": False,
                    "error": "删除 Cookie 需要指定 name"
                }
            
            # 删除特定 Cookie
            tab.remove_cookies(name)
            
            return {
                "success": True,
                "action": "delete",
                "name": name,
                "message": f"Cookie {name} 已删除"
            }
        
        elif action == "clear":
            # 清除所有 Cookies
            tab.remove_cookies()
            
            return {
                "success": True,
                "action": "clear",
                "message": "所有 Cookies 已清除"
            }
        
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {action}"
            }
        
    except Exception as e:
        logger.error(f"Cookie 管理失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Cookie 管理失败: {str(e)}"
        }


def switch_to_tab(
    action: str,
    url: Optional[str] = None,
    index: Optional[int] = None,
    title_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """Tab 页切换管理
    
    Args:
        action: 操作类型，'new', 'switch', 'close', 'list'
        url: 新标签页 URL（new 时）或要切换到的 URL（switch 时）
        index: 标签页索引（switch/close 时）
        title_pattern: 标签页标题模式（switch 时）
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not browser_manager.ensure_browser():
            return {
                "success": False,
                "error": "无法初始化浏览器"
            }
        
        browser = browser_manager.get_browser()
        if browser is None:
            return {
                "success": False,
                "error": "浏览器未初始化"
            }
        
        if action == "new":
            # 创建新标签页
            new_tab = browser.new_tab(url or "about:blank")
            browser_manager.set_current_tab(new_tab)
            
            return {
                "success": True,
                "action": "new",
                "url": new_tab.url,
                "title": new_tab.title,
                "message": "新标签页已创建"
            }
        
        elif action == "switch":
            # 切换标签页
            try:
                tabs = browser.get_tabs() if hasattr(browser, 'get_tabs') else [browser_manager.get_current_tab()]
            except:
                tabs = [browser_manager.get_current_tab()]
            
            if index is not None:
                # 按索引切换
                if 0 <= index < len(tabs):
                    target_tab = tabs[index]
                    browser_manager.set_current_tab(target_tab)
                    return {
                        "success": True,
                        "action": "switch",
                        "index": index,
                        "url": target_tab.url,
                        "title": target_tab.title
                    }
                else:
                    return {
                        "success": False,
                        "error": f"标签页索引 {index} 超出范围"
                    }
            
            elif url:
                # 按 URL 切换
                for tab in tabs:
                    if url in tab.url:
                        browser_manager.set_current_tab(tab)
                        return {
                            "success": True,
                            "action": "switch",
                            "url": tab.url,
                            "title": tab.title
                        }
                return {
                    "success": False,
                    "error": f"未找到匹配 URL 的标签页: {url}"
                }
            
            elif title_pattern:
                # 按标题切换
                for tab in tabs:
                    if title_pattern in tab.title:
                        browser_manager.set_current_tab(tab)
                        return {
                            "success": True,
                            "action": "switch",
                            "url": tab.url,
                            "title": tab.title
                        }
                return {
                    "success": False,
                    "error": f"未找到匹配标题的标签页: {title_pattern}"
                }
            
            else:
                return {
                    "success": False,
                    "error": "切换标签页需要指定 index、url 或 title_pattern"
                }
        
        elif action == "close":
            # 关闭标签页
            current_tab = browser_manager.get_current_tab()
            
            if index is not None:
                try:
                    tabs = browser.get_tabs() if hasattr(browser, 'get_tabs') else [current_tab]
                except:
                    tabs = [current_tab]
                if 0 <= index < len(tabs):
                    tabs[index].close()
                    # 如果关闭的是当前标签页，切换到最新的
                    if tabs[index] == current_tab:
                        browser_manager.set_current_tab(browser.latest_tab)
                    return {
                        "success": True,
                        "action": "close",
                        "index": index,
                        "message": f"标签页 {index} 已关闭"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"标签页索引 {index} 超出范围"
                    }
            else:
                # 关闭当前标签页
                if current_tab:
                    current_tab.close()
                    browser_manager.set_current_tab(browser.latest_tab)
                    return {
                        "success": True,
                        "action": "close",
                        "message": "当前标签页已关闭"
                    }
                else:
                    return {
                        "success": False,
                        "error": "没有可关闭的标签页"
                    }
        
        elif action == "list":
            # 列出所有标签页
            try:
                tabs = browser.get_tabs() if hasattr(browser, 'get_tabs') else [browser_manager.get_current_tab()]
            except:
                tabs = [browser_manager.get_current_tab()]
            
            tab_list = [
                {
                    "index": i,
                    "url": tab.url,
                    "title": tab.title,
                    "is_current": tab == browser_manager.get_current_tab()
                }
                for i, tab in enumerate(tabs)
            ]
            
            return {
                "success": True,
                "action": "list",
                "tabs": tab_list,
                "count": len(tab_list)
            }
        
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {action}"
            }
        
    except Exception as e:
        logger.error(f"Tab 管理失败: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Tab 管理失败: {str(e)}"
        }

