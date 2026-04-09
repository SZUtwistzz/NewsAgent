"""LangGraph 状态定义"""

from typing import TypedDict


class AgentState(TypedDict):
    """Agent 工作流的共享状态"""
    # 原始新闻数据（采集 Agent 输出）
    raw_news: str
    # 补充搜索结果
    search_results: list[str]
    # 编辑后的早报内容（编辑 Agent 输出）
    report: str
    # 推送结果
    push_results: list[str]
    # 当前阶段
    stage: str
    # 错误信息
    errors: list[str]
