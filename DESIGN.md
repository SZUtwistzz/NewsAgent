**概述**
- **代码仓库**:https://github.com/SZUtwistzz/NewsAgent
- **目标**: 自动采集全球优质新闻，使用 LLM 编辑为幽默早报并推送到企业微信/PushPlus。
- **定位**: 多 Agent 管道，基于 LangGraph 协调 `Collector` → `Editor` → `Publisher`。

**总体架构**
- **工作流**: 由 [src/agents/graph.py](src/agents/graph.py) 构建并编排，流程为 `collector` → `editor` → `publisher`。
- **插件化工具**: 所有外部功能封装为 `BaseTool` 的子类（见 [src/tools/base.py](src/tools/base.py)），可注册并转换为 LangChain 的 StructuredTool。
- **核心依赖**: DeepSeek（LLM）、LangGraph、feedparser、requests、duckduckgo-search 等（见 `requirements.txt`）。

**主要组件**
- **入口**: `main.py` — 加载配置、初始化日志/追踪、构建并运行 LangGraph。
- **配置模型**: `src/config/settings.py` — 使用 Pydantic 定义 `Settings`，从 `config/settings.yaml` 加载并支持环境变量覆盖。
- **采集 Agent**: `src/agents/collector.py` — 抓取 RSS（`RSSFetcherTool`），可使用 `NewsAPITool`/`NewsDataTool`，并调用 `DuckDuckGoSearchTool` 补充搜索。
- **编辑 Agent**: `src/agents/editor.py` — 合并素材后调用 LLM（system+human prompts）生成 Markdown 早报。
- **推送 Agent**: `src/agents/publisher.py` — 将早报推送到 `WeComWebhookTool`、`PushPlusTool` 等渠道，包含重试与分片逻辑。
- **抓取工具**: `src/tools/rss_fetcher.py` — 基于 feedparser，按时间窗口与每源上限抓取条目。
- **搜索工具**: `src/tools/search.py` — DuckDuckGo 搜索封装。
- **推送工具**: `src/tools/push_wecom.py` 与 `src/tools/push_pushplus.py` — 实现消息分片、重试与可用性检查。
- **可观测性**: `src/observability.py` — `AgentLogger` 与 LangSmith 环境开关。

**数据流与状态**
- **共享状态**: `AgentState` TypedDict 包含 `raw_news`, `search_results`, `report`, `push_results`, `stage`, `errors`。
- **Collector 输出**: 写入 `raw_news` 与 `search_results`（纯文本拼接）。
- **Editor 输出**: 生成 `report`（Markdown 格式的早报）。
- **Publisher 输出**: 遍历已配置渠道调用 `run(content, title)`，收集 `push_results`。
- **错误处理**: 各工具内部捕获异常并返回可读错误；节点将错误追加到 `errors`。

**配置与运行**
- **主配置**: `config/settings.yaml`（LLM、RSS 源、Agents 参数、推送渠道、可观测性）。
- **必要环境变量**: `DEEPSEEK_KEY`（必需）、可选 `WECOM_WEBHOOK`、`PUSH_TOKEN`、`NEWSAPI_KEY`、`NEWSDATA_KEY`、`LANGCHAIN_API_KEY`。
- **本地运行**:

```bash
python main.py
```

**扩展性设计**
- **新增数据源/渠道**: 实现 `BaseTool` 子类并在 `src/agents/graph.py` 中按配置实例化即可加入 Collector 或 Publisher。
- **提示模板管理**: Editor/Collector 的 prompt 在各自文件顶部，建议抽取到配置或模板库以便版本控制与 A/B 测试。
- **并行化**: 当前流程为线性同步，若需扩展吞吐可将 Collector 抓取并行化并在 Editor 加入并发控制。

**可观测性与可靠性**
- **日志**: 通过 `AgentLogger` 打点（开始/结束、工具调用、工具结果），可在 `config` 中设置日志等级。
- **追踪**: 支持 LangSmith（通过 `LANGCHAIN_TRACING_V2` 与 `LANGCHAIN_API_KEY` 启用）。
- **限流与重试**: 推送工具实现重试与内容分片（企业微信 4096 字限制）。

**已知限制与改进建议**
- **LLM 健壮性**: 增加 LLM 超时/重试与费用监控，避免单次调用成本过高。
- **输入清洗**: 对搜索与抓取结果进一步清洗以降低注入或不可信信息风险。
- **测试覆盖**: 添加工具层单元测试与端到端集成测试（可 mock 网络与 LLM）。
- **配置安全**: CI/Secrets 管理敏钥，避免写入仓库。

**部署与运维**
- 使用 GitHub Actions 定时触发（README 已示例），并把密钥写入 repository secrets。
- 将关键日志导出到集中日志系统，必要时开启 LangSmith 追踪以诊断 LLM 调用链路。

