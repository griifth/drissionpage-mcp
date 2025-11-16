# DrissionPage MCP 使用指南

本指南详细说明如何使用 DrissionPage MCP 服务器。

## 快速开始

### 1. 安装依赖

```bash
cd drissionpage_mcp
pip install -r requirements.txt
```

### 2. 启动 MCP 服务器

```bash
python server.py
```

服务器将通过标准输入/输出与 MCP 客户端通信。

### 3. 配置 MCP 客户端

如果您使用支持 MCP 的 AI 工具（如 Claude Desktop），需要在配置文件中添加：

```json
{
  "mcpServers": {
    "drissionpage": {
      "command": "python",
      "args": ["/path/to/drissionpage_mcp/server.py"]
    }
  }
}
```

## 工具列表

### 浏览器管理

#### init_browser
初始化浏览器实例。

**参数：**
- `headless` (boolean): 是否使用无头模式，默认 False
- `window_size` (array): 窗口大小 [宽, 高]，默认 [1920, 1080]

**示例：**
```json
{
  "name": "init_browser",
  "arguments": {
    "headless": false,
    "window_size": [1920, 1080]
  }
}
```

#### get_browser_status
获取浏览器当前状态。

**返回：**
- URL、标题、标签页数量等信息

#### close_browser
关闭浏览器并释放资源。

---

### 基础操作

#### navigate
导航到指定 URL。

**参数：**
- `url` (string, 必需): 目标网址
- `timeout` (integer): 超时时间（秒），默认 30

**示例：**
```json
{
  "name": "navigate",
  "arguments": {
    "url": "https://www.example.com"
  }
}
```

#### find_elements
查找页面元素。

**参数：**
- `selector` (string, 必需): 选择器字符串
- `selector_type` (string): 选择器类型 (css/xpath/text)，默认 css
- `single` (boolean): 是否只返回第一个，默认 false
- `timeout` (number): 超时时间（秒），默认 10

**示例：**
```json
{
  "name": "find_elements",
  "arguments": {
    "selector": "h1.title",
    "selector_type": "css",
    "single": true
  }
}
```

#### click_element
点击指定元素。

**参数：**
- `selector` (string, 必需): 选择器字符串
- `selector_type` (string): 选择器类型，默认 css
- `timeout` (number): 超时时间（秒），默认 10

#### input_text
向元素输入文本。

**参数：**
- `selector` (string, 必需): 选择器字符串
- `text` (string, 必需): 要输入的文本
- `selector_type` (string): 选择器类型，默认 css
- `clear_first` (boolean): 是否先清空，默认 true

**示例：**
```json
{
  "name": "input_text",
  "arguments": {
    "selector": "#username",
    "text": "user@example.com"
  }
}
```

#### get_element_text
获取元素的文本内容。

#### get_element_attribute
获取元素的属性值。

**参数：**
- `selector` (string, 必需): 选择器
- `attribute` (string, 必需): 属性名（如 href, src）

#### wait_for_element
等待元素出现。

#### scroll_page
滚动页面。

**参数：**
- `direction` (string): 方向 (up/down/left/right/top/bottom)
- `amount` (string/integer): 滚动量 (page/half/像素数)

#### take_screenshot
页面截图。

**参数：**
- `file_path` (string): 保存路径
- `full_page` (boolean): 是否全页截图，默认 false

#### execute_javascript
执行 JavaScript 代码。

**参数：**
- `script` (string, 必需): JavaScript 代码

---

### Markdown 转换（核心功能）

#### page_to_markdown
**将当前页面转换为 Markdown 并保存。**

**参数：**
- `file_path` (string, 必需): 保存路径
- `include_images` (boolean): 是否包含图片，默认 true
- `remove_ads` (boolean): 是否移除广告，默认 true
- `extract_main` (boolean): 是否只提取主要内容，默认 true
- `add_metadata` (boolean): 是否添加元数据，默认 true

**示例：**
```json
{
  "name": "page_to_markdown",
  "arguments": {
    "file_path": "article.md",
    "remove_ads": true,
    "extract_main": true
  }
}
```

#### get_page_content
获取页面内容（不保存文件）。

**参数：**
- `format` (string): 格式 (markdown/html/text)，默认 markdown
- `extract_main` (boolean): 是否只提取主要内容
- `remove_ads` (boolean): 是否移除广告

---

### 高级功能

#### extract_table_data
提取表格数据。

**参数：**
- `selector` (string): 表格选择器，默认 "table"
- `format` (string): 输出格式 (json/csv)，默认 json
- `output_file` (string): 可选的输出文件

**示例：**
```json
{
  "name": "extract_table_data",
  "arguments": {
    "selector": "table.data",
    "format": "json"
  }
}
```

#### smart_extract
智能数据抓取。

**参数：**
- `selector` (string, 必需): 容器选择器
- `fields` (object, 必需): 字段映射
- `limit` (integer): 最大数量，默认 100

**示例：**
```json
{
  "name": "smart_extract",
  "arguments": {
    "selector": "div.article",
    "fields": {
      "title": "h2.title",
      "author": "span.author",
      "date": "time"
    },
    "limit": 50
  }
}
```

#### fill_form
自动填写表单。

**参数：**
- `fields` (object, 必需): 字段映射 {选择器: 值}
- `submit_selector` (string): 提交按钮选择器

**示例：**
```json
{
  "name": "fill_form",
  "arguments": {
    "fields": {
      "#email": "user@example.com",
      "#password": "password123",
      "#remember": true
    },
    "submit_selector": "button[type='submit']"
  }
}
```

#### handle_infinite_scroll
处理无限滚动。

**参数：**
- `max_scrolls` (integer): 最大滚动次数，默认 10
- `scroll_pause` (number): 滚动间隔（秒），默认 2
- `check_selector` (string): 检查新内容的选择器

#### manage_cookies
Cookie 管理。

**参数：**
- `action` (string, 必需): 操作 (get/set/delete/clear)
- `name` (string): Cookie 名称
- `value` (string): Cookie 值
- `domain` (string): Cookie 域名

#### switch_to_tab
标签页管理。

**参数：**
- `action` (string, 必需): 操作 (new/switch/close/list)
- `url` (string): URL
- `index` (integer): 标签页索引
- `title_pattern` (string): 标题模式

---

## 完整使用示例

### 示例 1：抓取文章并保存为 Markdown

```python
# AI 模型调用流程：
1. init_browser()
2. navigate(url="https://news.ycombinator.com")
3. wait_for_element(selector=".title")
4. page_to_markdown(file_path="hn_news.md")
5. close_browser()
```

### 示例 2：表单自动化

```python
# AI 模型调用流程：
1. init_browser()
2. navigate(url="https://example.com/login")
3. input_text(selector="#username", text="user")
4. input_text(selector="#password", text="pass")
5. click_element(selector="button[type='submit']")
6. wait_for_element(selector=".dashboard")
7. take_screenshot(file_path="dashboard.png")
8. close_browser()
```

### 示例 3：数据抓取

```python
# AI 模型调用流程：
1. init_browser()
2. navigate(url="https://example.com/products")
3. handle_infinite_scroll(max_scrolls=5)
4. smart_extract(
     selector="div.product",
     fields={
       "name": "h3.name",
       "price": "span.price",
       "image": "img"
     }
   )
5. close_browser()
```

---

## 错误处理

所有工具返回统一的 JSON 格式：

**成功：**
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

**失败：**
```json
{
  "success": false,
  "error": "错误描述"
}
```

---

## 最佳实践

1. **始终初始化浏览器**：在使用任何操作前先调用 `init_browser()`
2. **合理使用等待**：使用 `wait_for_element()` 确保页面加载完成
3. **及时清理资源**：操作完成后调用 `close_browser()`
4. **使用合适的选择器**：CSS 选择器最快，XPath 更灵活
5. **处理动态内容**：使用 `handle_infinite_scroll()` 处理懒加载
6. **提取主要内容**：使用 `page_to_markdown` 的 `extract_main` 选项过滤无关内容

---

## 故障排除

### 问题：浏览器无法启动
- 确保已安装 Chrome 或 Edge 浏览器
- 检查 DrissionPage 是否正确安装

### 问题：元素找不到
- 增加 `timeout` 参数
- 使用 `wait_for_element()` 等待元素出现
- 检查选择器是否正确

### 问题：Markdown 转换失败
- 确保已安装 `markdownify` 或 `html2text`
- 检查页面是否完全加载

---

## 技术支持

如有问题，请查看：
- GitHub Issues
- 项目文档
- DrissionPage 官方文档：https://DrissionPage.cn

