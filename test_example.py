"""DrissionPage MCP 测试示例

这个文件展示了如何手动测试各个工具的功能。
"""

import json
import time
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import browser
from tools import basic, markdown, advanced

browser_manager = browser.browser_manager


def test_browser_lifecycle():
    """测试浏览器生命周期"""
    print("\n=== 测试 1: 浏览器生命周期 ===")
    
    # 初始化浏览器
    result = browser_manager.init_browser(headless=False, window_size=(1920, 1080))
    print(f"初始化浏览器: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "浏览器初始化失败"
    
    # 获取状态
    status = browser_manager.get_status()
    print(f"浏览器状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    assert status["running"], "浏览器未运行"
    
    print("✓ 浏览器生命周期测试通过")


def test_navigation():
    """测试导航功能"""
    print("\n=== 测试 2: 导航功能 ===")
    
    # 导航到网页
    result = basic.navigate("https://www.drissionpage.cn/")
    print(f"导航结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "导航失败"
    assert "drissionpage.cn" in result["url"].lower(), "URL 不匹配"
    
    time.sleep(2)  # 等待页面加载
    print("✓ 导航功能测试通过")


def test_element_operations():
    """测试元素操作"""
    print("\n=== 测试 3: 元素操作 ===")
    
    # 导航到测试页面
    basic.navigate("https://www.drissionpage.cn/")
    time.sleep(2)
    
    # 查找元素（查找任何标题或文本元素）
    result = basic.find_elements("div", selector_type="css", single=True)
    print(f"查找元素: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "查找元素失败"
    
    # 获取页面标题（使用 JavaScript）
    result = basic.execute_javascript("return document.title")
    print(f"页面标题: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "获取标题失败"
    
    print("✓ 元素操作测试通过")


def test_page_to_markdown():
    """测试页面转 Markdown"""
    print("\n=== 测试 4: 页面转 Markdown ===")
    
    # 导航到测试页面
    basic.navigate("https://www.drissionpage.cn/")
    time.sleep(2)
    
    # 转换为 Markdown
    result = markdown.page_to_markdown(
        file_path="test_output.md",
        include_images=True,
        remove_ads=True,
        extract_main=True
    )
    print(f"转换结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "转换 Markdown 失败"
    assert "test_output.md" in result["file_path"], "文件路径不正确"
    
    print("✓ 页面转 Markdown 测试通过")


def test_get_page_content():
    """测试获取页面内容"""
    print("\n=== 测试 5: 获取页面内容 ===")
    
    # 获取 Markdown 内容
    result = markdown.get_page_content(format="markdown")
    print(f"内容长度: {result.get('length', 0)} 字符")
    assert result["success"], "获取内容失败"
    assert len(result.get("content", "")) > 0, "内容为空"
    
    print("✓ 获取页面内容测试通过")


def test_screenshot():
    """测试截图功能"""
    print("\n=== 测试 6: 截图功能 ===")
    
    # 全屏截图
    result = basic.take_screenshot(
        file_path="test_screenshot.png",
        full_page=True
    )
    print(f"截图结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "截图失败"
    
    print("✓ 截图功能测试通过")


def test_scroll():
    """测试滚动功能"""
    print("\n=== 测试 7: 滚动功能 ===")
    
    # 滚动到底部
    result = basic.scroll_page(direction="bottom")
    print(f"滚动结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "滚动失败"
    
    time.sleep(1)
    
    # 滚动到顶部
    result = basic.scroll_page(direction="top")
    print(f"滚动结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "滚动失败"
    
    print("✓ 滚动功能测试通过")


def test_javascript():
    """测试 JavaScript 执行"""
    print("\n=== 测试 8: JavaScript 执行 ===")
    
    # 执行简单的 JavaScript
    result = basic.execute_javascript("return document.title")
    print(f"JavaScript 结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "JavaScript 执行失败"
    
    print("✓ JavaScript 执行测试通过")


def test_cleanup():
    """测试清理"""
    print("\n=== 测试 9: 清理 ===")
    
    # 关闭浏览器
    result = browser_manager.close_browser()
    print(f"关闭浏览器: {json.dumps(result, ensure_ascii=False, indent=2)}")
    assert result["success"], "关闭浏览器失败"
    
    # 验证浏览器已关闭
    assert not browser_manager.is_running(), "浏览器仍在运行"
    
    print("✓ 清理测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始运行 DrissionPage MCP 测试套件")
    print("=" * 60)
    
    try:
        test_browser_lifecycle()
        test_navigation()
        test_element_operations()
        test_page_to_markdown()
        test_get_page_content()
        test_screenshot()
        test_scroll()
        test_javascript()
        test_cleanup()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {str(e)}")
        # 确保清理
        try:
            browser_manager.close_browser()
        except:
            pass
    except Exception as e:
        print(f"\n✗ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 确保清理
        try:
            browser_manager.close_browser()
        except:
            pass


if __name__ == "__main__":
    run_all_tests()

