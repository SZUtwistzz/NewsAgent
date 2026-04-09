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

    # 构建节点
    collector = build_collector_node(settings, rss_tool, search_tool)
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
