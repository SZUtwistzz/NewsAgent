# 📰 全球热点新闻 Agent

基于 **DeepSeek API** 和 **Agentic Architecture** 的智能新闻助手，每天自动抓取全球热点、生成幽默犀利的早报并推送到微信。

## ✨ 特性

- 🤖 **智能体架构**：使用 DeepSeek Tool Calling，Agent 自主决策调用工具
- 📡 **多源新闻聚合**：联合早报、BBC 中文、Solidot、华尔街日报等 8+ RSS 源
- 🔍 **互联网搜索**：Agent 可主动使用 DuckDuckGo 补充信息
- 😄 **幽默风格**：AI 主编以吐槽式口吻总结全球大事
- 📱 **微信推送**：通过 PushPlus 自动推送 Markdown 格式早报
- ⏰ **定时执行**：GitHub Actions 每天自动运行

## 🏗️ 架构设计

```
用户指令 → DeepSeek Agent
              ↓
         [工具调用循环]
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
fetch_rss_feeds    search_duckduckgo
    ↓                   ↓
    └─────────┬─────────┘
              ↓
      [Agent 总结分析]
              ↓
       push_to_wechat
              ↓
          微信接收
```

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd NewsAgent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
export DEEPSEEK_KEY="sk-xxxxxxxxxxxxxxxx"
export PUSH_TOKEN="xxxxxxxxxxxxxxxx"
```

### 4. 本地测试

```bash
python agent.py
```

## 📦 部署到 GitHub Actions

### 1. 在 GitHub 仓库设置 Secrets

进入仓库 `Settings` → `Secrets and variables` → `Actions`，添加：

- `DEEPSEEK_KEY`: 你的 DeepSeek API Key
- `PUSH_TOKEN`: 你的 PushPlus Token

### 2. 推送代码

```bash
git add .
git commit -m "🚀 部署 AI 新闻 Agent"
git push origin main
```

### 3. 触发方式

- **自动触发**：每天 UTC 00:00（北京时间 08:00）
- **手动触发**：进入 `Actions` 标签页，点击 `Run workflow`

## 🛠️ 工具说明

### `fetch_rss_feeds()`
抓取 8 个预设 RSS 源的最新新闻（过去 24 小时）

### `search_duckduckgo(query: str)`
使用 DuckDuckGo 搜索引擎补充信息，Agent 可自主决定是否调用

### `push_to_wechat(content: str)`
通过 PushPlus 将 Markdown 内容推送到微信

## 📝 System Prompt

Agent 被设定为"首席 AI 新闻主编"，具备以下特质：
- 极其幽默、犀利且见多识广
- 挑选 10 个最具全球影响力的大事件
- 以吐槽式口吻总结，带 Emoji 排版
- 结尾附上"主编瞎点评"

## 🔧 自定义

### 修改 RSS 源

编辑 `agent.py` 中的 `RSS_SOURCES` 列表：

```python
RSS_SOURCES = [
    {"name": "你的源名称", "url": "RSS 地址"},
    # ...
]
```

### 调整定时任务

编辑 `.github/workflows/agent_daily.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: "0 0 * * *"  # 修改为你想要的时间
```

## 📄 许可证

MIT License

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的 AI 模型
- [PushPlus](http://www.pushplus.plus/) - 微信推送服务
- [RSSHub](https://rsshub.app/) - RSS 源聚合服务
