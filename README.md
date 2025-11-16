# DrissionPage MCP 浏览器自动化服务

基于 [DrissionPage](https://github.com/g1879/DrissionPage) 的 MCP (Model Context Protocol) 服务器，为 AI 模型提供强大的浏览器自动化和数据抓取功能。

## 特性

- 🌐 **浏览器自动化**：完整的浏览器控制能力（导航、点击、输入等）
- 📄 **网页转 Markdown**：智能将网页内容转换为 Markdown 格式
- 📊 **数据抓取**：结构化提取网页数据（表格、列表等）
- 🔧 **混合粒度**：提供基础操作和高级封装两种工具集
- 🎯 **单例模式**：高效管理单个浏览器实例
- 👀 **可视化调试**：默认有头模式，方便观察操作过程

## 安装

1. 克隆或下载本项目

2. 安装依赖：

```bash
cd drissionpage_mcp
pip install -r requirements.txt
```

## 快速开始

### 方式 1：直接运行测试

```bash
# 运行测试示例，验证功能
python test_example.py
```

### 方式 2：启动 MCP 服务器

```bash
python server.py
```

服务器将通过标准输入/输出与 MCP 客户端通信。

### 方式 3：配置 MCP 客户端

如果您使用支持 MCP 的 AI 工具（如 Claude Desktop、Cursor 等），可以在配置文件中添加：

**Claude Desktop 配置示例** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "drissionpage": {
      "command": "python",
      "args": ["/Users/Desktop/drissionpage_mcp/server.py"]
    }
  }
}
```

配置后重启客户端，AI 模型即可调用浏览器自动化功能。

### 使用示例

#### 示例 1：访问网页并保存为 Markdown

```python
# AI 模型可以通过 MCP 调用以下工具链：
1. init_browser()  # 启动浏览器
2. navigate(url="https://news.ycombinator.com")  # 访问网页
3. page_to_markdown(file_path="hn_news.md")  # 保存为 Markdown
4. close_browser()  # 关闭浏览器
```

#### 示例 2：自动填写表单

```python
1. init_browser()
2. navigate(url="https://example.com/login")
3. input_text(selector="#username", text="user")
4. input_text(selector="#password", text="pass")
5. click_element(selector="button[type='submit']")
6. wait_for_element(selector=".dashboard", timeout=10)
7. page_to_markdown(file_path="dashboard.md")
```

#### 示例 3：数据抓取

```python
1. init_browser()
2. navigate(url="https://example.com/data")
3. extract_table_data(selector="table.data-table", format="json")
4. close_browser()
```

## 工具列表

### 浏览器管理

- `init_browser`: 初始化浏览器实例
- `get_browser_status`: 获取浏览器状态
- `close_browser`: 关闭浏览器

### 基础操作

- `navigate`: 导航到 URL
- `find_elements`: 查找页面元素
- `click_element`: 点击元素
- `input_text`: 输入文本
- `get_element_text`: 获取元素文本
- `get_element_attribute`: 获取元素属性
- `wait_for_element`: 等待元素出现
- `scroll_page`: 滚动页面
- `take_screenshot`: 截图
- `execute_javascript`: 执行 JS 代码

### 高级功能

- `page_to_markdown`: 网页转 Markdown（核心功能）
- `extract_table_data`: 提取表格数据
- `smart_extract`: 智能数据抓取
- `fill_form`: 自动填写表单
- `handle_infinite_scroll`: 处理无限滚动
- `manage_cookies`: Cookie 管理
- `switch_to_tab`: Tab 页切换

## 技术架构

```
drissionpage_mcp/
├── __init__.py          # 包初始化
├── server.py            # MCP 服务器主入口
├── browser.py           # 浏览器单例管理器
├── tools/               # 工具集
│   ├── __init__.py
│   ├── basic.py         # 基础操作工具
│   ├── advanced.py      # 高级功能工具
│   └── markdown.py      # Markdown 转换工具
├── requirements.txt     # 依赖列表
└── README.md            # 本文档
```

## 依赖项

- **DrissionPage**: 浏览器自动化核心库
- **mcp**: Model Context Protocol 实现
- **markdownify / html2text**: HTML 转 Markdown
- **beautifulsoup4**: HTML 解析
- **lxml**: 高性能 XML/HTML 解析

## 开发指南

### 添加新工具

1. 在相应的工具文件（`basic.py`、`advanced.py` 等）中定义函数
2. 在 `tools/__init__.py` 中导出
3. 在 `server.py` 中注册到 MCP 服务器

### 错误处理

所有工具函数都应返回统一的格式：

```python
{
    "success": True/False,
    "data": {...},  # 成功时的数据
    "error": "...",  # 失败时的错误信息
}
```

## 使用注意

1. **浏览器单例**：同一时间只能有一个浏览器实例，适合顺序执行任务
2. **资源释放**：使用完毕后请调用 `close_browser()` 释放资源
3. **超时控制**：所有操作都有超时参数，避免无限等待
4. **调试模式**：默认有头模式便于调试，生产环境可配置为无头模式
5. **网络延迟**：根据网络情况调整 `timeout` 参数
6. **选择器优化**：优先使用 CSS 选择器，性能更好

## 常见问题

### Q: 如何切换为无头模式？
A: 调用 `init_browser(headless=true)` 即可。

### Q: 支持哪些浏览器？
A: 支持 Chromium 内核浏览器（Chrome、Edge 等）。

### Q: 如何处理需要登录的网站？
A: 使用 `fill_form` 工具自动填写表单，或使用 `manage_cookies` 设置已保存的 Cookie。

### Q: 可以同时打开多个标签页吗？
A: 可以，使用 `switch_to_tab(action="new")` 创建新标签页。

### Q: Markdown 转换质量如何提升？
A: 启用 `extract_main=true` 和 `remove_ads=true` 选项，只保留主要内容。

## 高级用法

### 自定义浏览器配置

```python
init_browser(
    headless=False,
    window_size=[1920, 1080],
    user_agent="Custom User Agent",
    proxy="http://proxy.example.com:8080"
)
```

### 批量数据抓取

```python
# 1. 访问列表页
navigate(url="https://example.com/articles")

# 2. 处理懒加载
handle_infinite_scroll(max_scrolls=10, check_selector=".article")

# 3. 提取所有文章
smart_extract(
    selector=".article",
    fields={
        "title": "h2.title",
        "summary": "p.summary",
        "link": "a.read-more"
    }
)
```

### 复杂表单自动化

```python
fill_form(
    fields={
        "#email": "user@example.com",
        "#password": "secure_password",
        "#country": "China",  # 下拉框
        "#agree": True,  # 复选框
        "#newsletter": False
    },
    submit_selector="button.submit"
)
```

## 性能优化建议

1. **减少等待时间**：合理设置 `timeout` 和 `wait_after` 参数
2. **批量操作**：使用 `smart_extract` 一次性提取多个元素
3. **缓存页面**：避免重复访问同一页面
4. **并发处理**：对于独立任务，可启动多个 MCP 服务器实例

## 文档资源

- **详细使用指南**：查看 `USAGE_GUIDE.md`
- **测试示例**：查看 `test_example.py`
- **DrissionPage 文档**：https://DrissionPage.cn
- **MCP 协议规范**：https://modelcontextprotocol.io/

## 许可证

本项目遵循 MIT 许可证。

## 致谢

- [DrissionPage](https://github.com/g1879/DrissionPage) - 强大的 Python 网页自动化工具
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI 模型工具调用标准

