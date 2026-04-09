"""采集 Agent — 负责从 RSS 和搜索引擎收集原始新闻"""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.tools.rss_fetcher import RSSFetcherTool
from src.tools.search import DuckDuckGoSearchTool
from src.config.settings import Settings

logger = logging.getLogger("news_agent")

COLLECTOR_PROMPT = """你是一个专业的新闻采集员。
你的任务是收集最新的全球热点新闻。

请分析已获取的 RSS 新闻，如果你觉得某些重要领域（政治、科技、商业）的新闻覆盖不足，
请列出最多 {max_search_queries} 个搜索关键词，每行一个，用于补充搜索。
如果新闻已经足够丰富，请回复"无需补充"。"""


def build_collector_node(settings: Settings, rss_tool: RSSFetcherTool, search_tool: DuckDuckGoSearchTool):
    """构建采集 Agent 节点函数"""

    llm = ChatOpenAI(
        model=settings.llm.model,
        base_url=settings.llm.base_url,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )
    max_queries = settings.agents.collector.max_search_queries

    def collector_node(state: AgentState) -> dict:
        logger.info("🚀 [CollectorAgent] 开始采集新闻")

        # 1. 抓取 RSS
        logger.info("📡 抓取 RSS 源...")
        raw_news = rss_tool.run()
        logger.info(f"📡 RSS 采集完成，获取 {raw_news[:50]}...")

        # 2. 让 LLM 判断是否需要补充搜索
        search_results = []
        try:
            messages = [
                SystemMessage(content=COLLECTOR_PROMPT.format(max_search_queries=max_queries)),
                HumanMessage(content=f"以下是已获取的新闻：\n\n{raw_news[:3000]}"),
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
