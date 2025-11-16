# 更新日志

所有重要的项目变更都将记录在此文件中。

## [0.1.0] - 2025-11-16

### 新增
- ✨ 初始版本发布
- 🌐 浏览器管理功能（初始化、状态查询、关闭）
- 🔧 基础操作工具集（导航、查找、点击、输入等 10+ 工具）
- 📄 Markdown 转换功能（核心功能）
- 📊 高级功能工具（表单填写、数据抓取、Cookie 管理等）
- 🖥️ 完整的 MCP 服务器实现
- 📚 详细的文档和使用示例
- 🧪 测试用例和示例代码

### 特性
- 混合粒度设计：同时提供基础操作和高级封装
- 单例浏览器管理：高效资源利用
- 智能 Markdown 转换：自动提取主要内容、清理广告
- 统一错误处理：所有工具返回一致的 JSON 格式
- 完善的文档：README、使用指南、配置示例

### 工具清单
**浏览器管理** (3)：init_browser, get_browser_status, close_browser
**基础操作** (10)：navigate, find_elements, click_element, input_text, get_element_text, get_element_attribute, wait_for_element, scroll_page, take_screenshot, execute_javascript
**Markdown** (2)：page_to_markdown, get_page_content
**高级功能** (6)：extract_table_data, smart_extract, fill_form, handle_infinite_scroll, manage_cookies, switch_to_tab

**总计**：21 个工具

## 未来计划

### [0.2.0] - 计划中
- [ ] 添加代理支持和反爬虫策略
- [ ] 支持 iframe 操作
- [ ] 增强图片下载功能
- [ ] 添加 PDF 导出功能
- [ ] 性能监控和日志优化

### [0.3.0] - 计划中
- [ ] 支持多浏览器实例
- [ ] 添加会话管理
- [ ] 集成常见网站的登录模板
- [ ] 提供更多数据提取模板

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可

MIT License

