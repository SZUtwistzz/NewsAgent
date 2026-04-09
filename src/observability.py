"""结构化日志 & LangSmith 可观测性"""

import logging
import os
import sys


class AgentLogger:
    """Agent 专用日志器"""

    def __init__(self, name: str = "news_agent", level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                fmt="%(asctime)s | %(levelname)-7s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def agent_start(self, agent_name: str):
        self.logger.info(f"🚀 [{agent_name}] 开始执行")

    def agent_end(self, agent_name: str, status: str = "success"):
        emoji = "✅" if status == "success" else "⚠️"
        self.logger.info(f"{emoji} [{agent_name}] 执行完成 | status={status}")

    def tool_call(self, tool_name: str, args_preview: str = ""):
        self.logger.info(f"🔧 调用工具: {tool_name} | {args_preview}")

    def tool_result(self, tool_name: str, result_preview: str = ""):
        preview = result_preview[:200] + "..." if len(result_preview) > 200 else result_preview
        self.logger.info(f"📋 工具结果: {tool_name} | {preview}")

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)


def setup_logging(log_level: str = "INFO") -> AgentLogger:
    """创建并返回 AgentLogger 实例"""
    return AgentLogger(level=log_level)


def setup_langsmith(project: str = "news-agent", enabled: bool = False) -> None:
    """配置 LangSmith 追踪"""
    if not enabled:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        return

    api_key = os.getenv("LANGCHAIN_API_KEY", "")
    if not api_key:
        logging.getLogger("news_agent").warning(
            "LangSmith 已启用但 LANGCHAIN_API_KEY 未设置，跳过"
        )
        return

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project
