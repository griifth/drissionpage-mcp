"""工具模块初始化"""

from .basic import (
    navigate,
    find_elements,
    click_element,
    input_text,
    get_element_text,
    get_element_attribute,
    wait_for_element,
    scroll_page,
    take_screenshot,
    execute_javascript,
)
from .markdown import page_to_markdown
from .advanced import (
    extract_table_data,
    smart_extract,
    fill_form,
    handle_infinite_scroll,
    manage_cookies,
    switch_to_tab,
)

__all__ = [
    # 基础工具
    "navigate",
    "find_elements",
    "click_element",
    "input_text",
    "get_element_text",
    "get_element_attribute",
    "wait_for_element",
    "scroll_page",
    "take_screenshot",
    "execute_javascript",
    # Markdown 工具
    "page_to_markdown",
    # 高级工具
    "extract_table_data",
    "smart_extract",
    "fill_form",
    "handle_infinite_scroll",
    "manage_cookies",
    "switch_to_tab",
]

