"""采集 Agent — 负责从 RSS、API 和搜索引擎收集原始新闻"""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.tools.base import BaseTool
from src.tools.rss_fetcher import RSSFetcherTool
from src.tools.search import DuckDuckGoSearchTool
from src.config.settings import Settings

logger = logging.getLogger("news_agent")

COLLECTOR_PROMPT = """你是一个专业的新闻采集员。
你的任务是收集最新的全球热点新闻。

请分析已获取的新闻（来自 RSS 和 API 数据源），如果你觉得某些重要领域（政治、科技、商业）的新闻覆盖不足，
请列出最多 {max_search_queries} 个搜索关键词，每行一个，用于补充搜索。
如果新闻已经足够丰富，请回复"无需补充"。"""


def build_collector_node(
    settings: Settings,
    rss_tool: RSSFetcherTool,
    search_tool: DuckDuckGoSearchTool,
    extra_news_tools: list[BaseTool] | None = None,
):
    """构建采集 Agent 节点函数"""

    extra_news_tools = extra_news_tools or []

    llm = ChatOpenAI(
        model=settings.llm.model,
        base_url=settings.llm.base_url,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )
    max_queries = settings.agents.collector.max_search_queries

    def collector_node(state: AgentState) -> dict:
        logger.info("🚀 [CollectorAgent] 开始采集新闻")

        # 1. 抓取 RSS（主数据源）
        logger.info("📡 抓取 RSS 源...")
        raw_news = rss_tool.run()
        logger.info(f"📡 RSS 采集完成，{raw_news[:60]}...")

        # 2. 抓取 API 数据源（可选）
        for tool in extra_news_tools:
            try:
                logger.info(f"📡 抓取 {tool.name}...")
                result = tool.run()
                if result:
                    raw_news = raw_news + "\n\n" + result
                    logger.info(f"📡 {tool.name} 采集完成")
            except Exception as e:
                logger.warning(f"{tool.name} 采集失败: {e}")

        # 3. 让 LLM 判断是否需要补充搜索
        search_results = []
        try:
            messages = [
                SystemMessage(content=COLLECTOR_PROMPT.format(max_search_queries=max_queries)),
                HumanMessage(content=f"以下是已获取的新闻：\n\n{raw_news[:5000]}"),
            ]
            resp = llm.invoke(messages)
            reply = resp.content.strip()

            if "无需补充" not in reply:
                queries = [q.strip() for q in reply.strip().split("\n") if q.strip()][:max_queries]
                for q in queries:
                    logger.info(f"🔍 补充搜索: {q}")
                    result = search_tool.run(query=q)
                    search_results.append(result)
        except Exception as e:
            logger.warning(f"补充搜索判断失败: {e}")

        logger.info("✅ [CollectorAgent] 采集完成")
        return {
            "raw_news": raw_news,
            "search_results": search_results,
            "stage": "collected",
            "errors": [],
        }

    return collector_node
