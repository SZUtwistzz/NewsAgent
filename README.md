# 📰 全球热点新闻 Agent

基于 **LangChain/LangGraph** 和 **DeepSeek API** 的企业级多 Agent 新闻助手，每天自动抓取全球热点、生成幽默犀利的早报并推送到微信。

## ✨ 特性

- 🤖 **多 Agent 协作**：采集 Agent、编辑 Agent、推送 Agent 分工明确
- 🔧 **可配置化**：YAML 配置文件管理 RSS 源、Prompt、推送渠道
- 🔍 **可扩展性**：插件化工具注册，方便新增数据源和推送渠道
- 📊 **可观测性**：结构化日志 + LangSmith 追踪（可选）
- 📡 **多源新闻聚合**：联合早报、BBC 中文、Solidot、华尔街日报等 8+ RSS 源
- 😄 **幽默风格**：AI 主编以吐槽式口吻总结全球大事
- 📱 **微信推送**：支持企业微信群机器人 + PushPlus
- ⏰ **定时执行**：GitHub Actions 每天自动运行

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────┐
│              LangGraph 状态图                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  CollectorAgent  →  EditorAgent  →  PublisherAgent
│       ↓                  ↓                ↓     │
│   RSS + 搜索          筛选编辑          多渠道推送 │
│                                                 │
└─────────────────────────────────────────────────┘

工具插件系统:
  - RSSFetcherTool
  - DuckDuckGoSearchTool
  - WeComWebhookTool
  - PushPlusTool
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
export WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
# 可选
export PUSH_TOKEN="xxxxxxxxxxxxxxxx"
export LANGCHAIN_API_KEY="xxx"  # 启用 LangSmith 追踪
```

### 4. 修改配置文件（可选）

编辑 `config/settings.yaml`，自定义 RSS 源、Agent 参数、推送渠道等。

### 5. 本地测试

```bash
python main.py
```

## 📦 部署到 GitHub Actions

### 1. 在 GitHub 仓库设置 Secrets

进入仓库 `Settings` → `Secrets and variables` → `Actions`，添加：

- `DEEPSEEK_KEY`: 你的 DeepSeek API Key
- `WECOM_WEBHOOK`: 企业微信群机器人 Webhook URL
- `PUSH_TOKEN`: （可选）PushPlus Token
- `LANGCHAIN_API_KEY`: （可选）LangSmith API Key

### 2. 推送代码

```bash
git add .
git commit -m "🚀 升级为企业级多 Agent 架构"
git push origin main
```

### 3. 触发方式

- **自动触发**：每天 UTC 00:00（北京时间 08:00）
- **手动触发**：进入 `Actions` 标签页，点击 `Run workflow`

## 🛠️ 项目结构

```
NewsAgent/
├── config/
│   └── settings.yaml          # 配置文件
├── src/
│   ├── agents/
│   │   ├── state.py           # LangGraph 状态定义
│   │   ├── collector.py       # 采集 Agent
│   │   ├── editor.py          # 编辑 Agent
│   │   ├── publisher.py       # 推送 Agent
│   │   └── graph.py           # LangGraph 状态图
│   ├── tools/
│   │   ├── base.py            # 工具基类
│   │   ├── rss_fetcher.py     # RSS 抓取工具
│   │   ├── search.py          # DuckDuckGo 搜索
│   │   ├── push_wecom.py      # 企业微信推送
│   │   └── push_pushplus.py   # PushPlus 推送
│   ├── config/
│   │   └── settings.py        # Pydantic 配置模型
│   └── observability.py       # 日志 & LangSmith
├── main.py                    # 入口文件
├── agent.py                   # 旧版单文件（已废弃）
├── requirements.txt
└── README.md
```

## 🔧 自定义

### 修改 RSS 源

编辑 `config/settings.yaml` 中的 `rss_sources` 列表。

### 调整 Agent 参数

在 `config/settings.yaml` 的 `agents` 部分修改：
- `collector.max_search_queries`: 最多补充搜索次数
- `editor.top_n_news`: 筛选新闻数量
- `publisher.retry_times`: 推送重试次数

### 启用 LangSmith 追踪

在 `config/settings.yaml` 中设置：
```yaml
observability:
  langsmith:
    enabled: true
    project: "news-agent"
```

并设置环境变量 `LANGCHAIN_API_KEY`。

## 📝 从旧版迁移

旧版 `agent.py` 已废弃，新版使用 `main.py` 作为入口。

主要变化：
- 单文件 → 模块化结构
- 硬编码 → YAML 配置
- 单 Agent → 多 Agent 协作
- 无追踪 → LangSmith 可观测性

## 📄 许可证

MIT License

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的 AI 模型
- [LangChain](https://www.langchain.com/) - Agent 编排框架
- [PushPlus](http://www.pushplus.plus/) - 微信推送服务
- [RSSHub](https://rsshub.app/) - RSS 源聚合服务
