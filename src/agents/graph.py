"""LangGraph 工作流定义 — Collector → Editor → Publisher"""

import logging

from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.collector import build_collector_node
from src.agents.editor import build_editor_node
from src.agents.publisher import build_publisher_node
from src.config.settings import Settings
from src.tools.rss_fetcher import RSSFetcherTool
from src.tools.search import DuckDuckGoSearchTool
from src.tools.newsapi import NewsAPITool
from src.tools.newsdata import NewsDataTool

logger = logging.getLogger("news_agent")


def build_graph(settings: Settings) -> StateGraph:
    """构建 LangGraph 状态图

    流程: collector → editor → publisher → END
    """

    # 初始化工具
    rss_tool = RSSFetcherTool(
        sources=settings.rss_sources,
        lookback_hours=settings.agents.collector.news_lookback_hours,
        max_per_source=settings.agents.collector.max_rss_per_source,
    )
    search_tool = DuckDuckGoSearchTool()

    # 可选 API 数据源
    extra_news_tools = []

    if settings.newsapi.enabled:
        newsapi_tool = NewsAPITool(
            categories=settings.newsapi.categories,
            countries=settings.newsapi.countries,
            language=settings.newsapi.language,
            page_size=settings.newsapi.page_size,
            lookback_hours=settings.agents.collector.news_lookback_hours,
        )
        if newsapi_tool.available:
            extra_news_tools.append(newsapi_tool)
            logger.info("✅ NewsAPI 工具已启用")
        else:
            logger.warning("⚠️ NewsAPI 已配置但 NEWSAPI_KEY 未设置")

    if settings.newsdata.enabled:
        newsdata_tool = NewsDataTool(
            categories=settings.newsdata.categories,
            countries=settings.newsdata.countries,
            language=settings.newsdata.language,
            max_results=settings.newsdata.max_results,
        )
        if newsdata_tool.available:
            extra_news_tools.append(newsdata_tool)
            logger.info("✅ NewsData.io 工具已启用")
        else:
            logger.warning("⚠️ NewsData.io 已配置但 NEWSDATA_KEY 未设置")

    # 构建节点
    collector = build_collector_node(settings, rss_tool, search_tool, extra_news_tools)
    editor = build_editor_node(settings)
    publisher = build_publisher_node(settings)

    # 构建状态图
    graph = StateGraph(AgentState)

    graph.add_node("collector", collector)
    graph.add_node("editor", editor)
    graph.add_node("publisher", publisher)

    # 线性流程: collector → editor → publisher → END
    graph.set_entry_point("collector")
    graph.add_edge("collector", "editor")
    graph.add_edge("editor", "publisher")
    graph.add_edge("publisher", END)

    return graph.compile()
