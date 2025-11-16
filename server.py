"""DrissionPage MCP 服务器

基于 MCP (Model Context Protocol) 的浏览器自动化服务。
"""

import logging
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .browser import browser_manager
from .tools import basic, markdown, advanced

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器实例
app = Server("drissionpage-mcp")


# ============================================================================
# 浏览器管理工具
# ============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        # 浏览器管理
        Tool(
            name="init_browser",
            description="初始化浏览器实例，支持自定义配置（无头/有头模式、窗口大小等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {
                        "type": "boolean",
                        "description": "是否使用无头模式，默认 False",
                        "default": False
                    },
                    "window_size": {
                        "type": "array",
                        "description": "浏览器窗口大小 [width, height]",
                        "items": {"type": "integer"},
                        "default": [1920, 1080]
                    }
                }
            }
        ),
        Tool(
            name="get_browser_status",
            description="获取当前浏览器状态（URL、标题、是否活跃等）",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="close_browser",
            description="关闭浏览器实例，释放资源",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # 基础操作
        Tool(
            name="navigate",
            description="导航到指定 URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "目标网址"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "超时时间（秒）",
                        "default": 30
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="find_elements",
            description="查找页面元素，支持 CSS、XPath、文本选择器",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath, text",
                        "enum": ["css", "xpath", "text"],
                        "default": "css"
                    },
                    "single": {
                        "type": "boolean",
                        "description": "是否只返回第一个元素",
                        "default": False
                    },
                    "timeout": {
                        "type": "number",
                        "description": "等待超时时间（秒）",
                        "default": 10
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="click_element",
            description="点击指定元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath, text",
                        "enum": ["css", "xpath", "text"],
                        "default": "css"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "等待超时时间（秒）",
                        "default": 10
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="input_text",
            description="向元素输入文本",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "text": {
                        "type": "string",
                        "description": "要输入的文本"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    },
                    "clear_first": {
                        "type": "boolean",
                        "description": "是否先清空原有内容",
                        "default": True
                    }
                },
                "required": ["selector", "text"]
            }
        ),
        Tool(
            name="get_element_text",
            description="获取元素文本内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="get_element_attribute",
            description="获取元素属性值",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "attribute": {
                        "type": "string",
                        "description": "属性名"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    }
                },
                "required": ["selector", "attribute"]
            }
        ),
        Tool(
            name="wait_for_element",
            description="等待元素出现",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "选择器字符串"
                    },
                    "selector_type": {
                        "type": "string",
                        "description": "选择器类型：css, xpath",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "超时时间（秒）",
                        "default": 30
                    }
                },
                "required": ["selector"]
            }
        ),
        Tool(
            name="scroll_page",
            description="滚动页面",
            inputSchema={
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "description": "滚动方向",
                        "enum": ["up", "down", "left", "right", "top", "bottom"],
                        "default": "down"
                    },
                    "amount": {
                        "type": ["string", "integer"],
                        "description": "滚动量：page, half, 或具体像素数",
                        "default": "page"
                    }
                }
            }
        ),
        Tool(
            name="take_screenshot",
            description="页面截图",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "保存路径，如果为空则自动生成"
                    },
                    "full_page": {
                        "type": "boolean",
                        "description": "是否截取整个页面",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="execute_javascript",
            description="执行自定义 JavaScript 代码",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "JavaScript 代码"
                    }
                },
                "required": ["script"]
            }
        ),
        
        # Markdown 转换
        Tool(
            name="page_to_markdown",
            description="将当前页面转换为 Markdown 并保存（核心功能）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "保存的文件路径"
                    },
                    "include_images": {
                        "type": "boolean",
                        "description": "是否包含图片",
                        "default": True
                    },
                    "remove_ads": {
                        "type": "boolean",
                        "description": "是否移除广告元素",
                        "default": True
                    },
                    "extract_main": {
                        "type": "boolean",
                        "description": "是否只提取主要内容区域",
                        "default": True
                    },
                    "add_metadata": {
                        "type": "boolean",
                        "description": "是否添加元数据（标题、URL等）",
                        "default": True
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_page_content",
            description="获取当前页面内容（不保存文件）",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "description": "返回格式",
                        "enum": ["markdown", "html", "text"],
                        "default": "markdown"
                    },
                    "extract_main": {
                        "type": "boolean",
                        "description": "是否只提取主要内容",
                        "default": True
                    },
                    "remove_ads": {
                        "type": "boolean",
                        "description": "是否移除广告",
                        "default": True
                    }
                }
            }
        ),
        
        # 高级功能
        Tool(
            name="extract_table_data",
            description="提取网页表格数据为结构化格式（JSON/CSV）",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "表格选择器",
                        "default": "table"
                    },
                    "format": {
                        "type": "string",
                        "description": "输出格式",
                        "enum": ["json", "csv"],
                        "default": "json"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "可选的输出文件路径"
                    }
                }
            }
        ),
        Tool(
            name="smart_extract",
            description="智能数据抓取，根据选择器提取多个元素的结构化数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "容器元素选择器"
                    },
                    "fields": {
                        "type": "object",
                        "description": "字段映射，{字段名: 子选择器}",
                        "additionalProperties": {"type": "string"}
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最多提取的项数",
                        "default": 100
                    }
                },
                "required": ["selector", "fields"]
            }
        ),
        Tool(
            name="fill_form",
            description="自动填写表单",
            inputSchema={
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "object",
                        "description": "字段映射，{选择器: 值}",
                        "additionalProperties": True
                    },
                    "submit_selector": {
                        "type": "string",
                        "description": "提交按钮选择器，如果为空则不提交"
                    }
                },
                "required": ["fields"]
            }
        ),
        Tool(
            name="handle_infinite_scroll",
            description="处理无限滚动/懒加载，自动滚动直到内容不再增加",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_scrolls": {
                        "type": "integer",
                        "description": "最大滚动次数",
                        "default": 10
                    },
                    "scroll_pause": {
                        "type": "number",
                        "description": "每次滚动后的等待时间（秒）",
                        "default": 2
                    },
                    "check_selector": {
                        "type": "string",
                        "description": "用于检查新内容的选择器"
                    }
                }
            }
        ),
        Tool(
            name="manage_cookies",
            description="Cookie 管理（获取、设置、删除）",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型",
                        "enum": ["get", "set", "delete", "clear"]
                    },
                    "name": {
                        "type": "string",
                        "description": "Cookie 名称"
                    },
                    "value": {
                        "type": "string",
                        "description": "Cookie 值（set 时需要）"
                    },
                    "domain": {
                        "type": "string",
                        "description": "Cookie 域名"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="switch_to_tab",
            description="Tab 页切换管理（新建、切换、关闭、列表）",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "操作类型",
                        "enum": ["new", "switch", "close", "list"]
                    },
                    "url": {
                        "type": "string",
                        "description": "新标签页 URL 或要切换到的 URL"
                    },
                    "index": {
                        "type": "integer",
                        "description": "标签页索引"
                    },
                    "title_pattern": {
                        "type": "string",
                        "description": "标签页标题模式"
                    }
                },
                "required": ["action"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """调用工具"""
    try:
        logger.info(f"调用工具: {name}, 参数: {arguments}")
        
        # 浏览器管理
        if name == "init_browser":
            window_size = arguments.get("window_size", [1920, 1080])
            result = browser_manager.init_browser(
                headless=arguments.get("headless", False),
                window_size=tuple(window_size)
            )
        elif name == "get_browser_status":
            result = browser_manager.get_status()
        elif name == "close_browser":
            result = browser_manager.close_browser()
        
        # 基础操作
        elif name == "navigate":
            result = basic.navigate(
                url=arguments["url"],
                timeout=arguments.get("timeout", 30)
            )
        elif name == "find_elements":
            result = basic.find_elements(
                selector=arguments["selector"],
                selector_type=arguments.get("selector_type", "css"),
                single=arguments.get("single", False),
                timeout=arguments.get("timeout", 10)
            )
        elif name == "click_element":
            result = basic.click_element(
                selector=arguments["selector"],
                selector_type=arguments.get("selector_type", "css"),
                timeout=arguments.get("timeout", 10)
            )
        elif name == "input_text":
            result = basic.input_text(
                selector=arguments["selector"],
                text=arguments["text"],
                selector_type=arguments.get("selector_type", "css"),
                clear_first=arguments.get("clear_first", True)
            )
        elif name == "get_element_text":
            result = basic.get_element_text(
                selector=arguments["selector"],
                selector_type=arguments.get("selector_type", "css")
            )
        elif name == "get_element_attribute":
            result = basic.get_element_attribute(
                selector=arguments["selector"],
                attribute=arguments["attribute"],
                selector_type=arguments.get("selector_type", "css")
            )
        elif name == "wait_for_element":
            result = basic.wait_for_element(
                selector=arguments["selector"],
                selector_type=arguments.get("selector_type", "css"),
                timeout=arguments.get("timeout", 30)
            )
        elif name == "scroll_page":
            result = basic.scroll_page(
                direction=arguments.get("direction", "down"),
                amount=arguments.get("amount", "page")
            )
        elif name == "take_screenshot":
            result = basic.take_screenshot(
                file_path=arguments.get("file_path"),
                full_page=arguments.get("full_page", False)
            )
        elif name == "execute_javascript":
            result = basic.execute_javascript(
                script=arguments["script"]
            )
        
        # Markdown 转换
        elif name == "page_to_markdown":
            result = markdown.page_to_markdown(
                file_path=arguments["file_path"],
                include_images=arguments.get("include_images", True),
                remove_ads=arguments.get("remove_ads", True),
                extract_main=arguments.get("extract_main", True),
                add_metadata=arguments.get("add_metadata", True)
            )
        elif name == "get_page_content":
            result = markdown.get_page_content(
                format=arguments.get("format", "markdown"),
                extract_main=arguments.get("extract_main", True),
                remove_ads=arguments.get("remove_ads", True)
            )
        
        # 高级功能
        elif name == "extract_table_data":
            result = advanced.extract_table_data(
                selector=arguments.get("selector", "table"),
                format=arguments.get("format", "json"),
                output_file=arguments.get("output_file")
            )
        elif name == "smart_extract":
            result = advanced.smart_extract(
                selector=arguments["selector"],
                fields=arguments["fields"],
                limit=arguments.get("limit", 100)
            )
        elif name == "fill_form":
            result = advanced.fill_form(
                fields=arguments["fields"],
                submit_selector=arguments.get("submit_selector")
            )
        elif name == "handle_infinite_scroll":
            result = advanced.handle_infinite_scroll(
                max_scrolls=arguments.get("max_scrolls", 10),
                scroll_pause=arguments.get("scroll_pause", 2),
                check_selector=arguments.get("check_selector")
            )
        elif name == "manage_cookies":
            result = advanced.manage_cookies(
                action=arguments["action"],
                name=arguments.get("name"),
                value=arguments.get("value"),
                domain=arguments.get("domain")
            )
        elif name == "switch_to_tab":
            result = advanced.switch_to_tab(
                action=arguments["action"],
                url=arguments.get("url"),
                index=arguments.get("index"),
                title_pattern=arguments.get("title_pattern")
            )
        
        else:
            result = {
                "success": False,
                "error": f"未知的工具: {name}"
            }
        
        # 格式化结果
        result_text = json.dumps(result, ensure_ascii=False, indent=2)
        logger.info(f"工具执行结果: {result_text[:200]}...")
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"工具执行失败: {str(e)}", exc_info=True)
        error_result = {
            "success": False,
            "error": str(e)
        }
        return [TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]


async def main():
    """启动 MCP 服务器"""
    logger.info("启动 DrissionPage MCP 服务器...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

