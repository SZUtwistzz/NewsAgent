"""全球热点新闻 Agent — LangGraph 多 Agent 架构入口"""

import os
import sys
from datetime import datetime

# 修复 Windows 终端 UTF-8 编码问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from src.config.settings import load_settings
from src.observability import setup_logging, setup_langsmith
from src.agents.graph import build_graph


def main():
    # 1. 加载配置
    settings = load_settings()

    # 2. 初始化可观测性
    logger = setup_logging(settings.observability.log_level)
    setup_langsmith(
        project=settings.observability.langsmith.project,
        enabled=settings.observability.langsmith.enabled,
    )

    # 3. 环境检查
    if not os.getenv("DEEPSEEK_KEY"):
        logger.error("❌ 请设置环境变量 DEEPSEEK_KEY")
        sys.exit(1)

    # LangChain 需要通过 OPENAI_API_KEY 或自定义方式传入 key
    os.environ.setdefault("OPENAI_API_KEY", os.getenv("DEEPSEEK_KEY", ""))

    logger.info("🚀 全球热点新闻 Agent 启动")
    logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 4. 构建并运行 LangGraph
    graph = build_graph(settings)

    initial_state = {
        "raw_news": "",
        "search_results": [],
        "report": "",
        "push_results": [],
        "stage": "init",
        "errors": [],
    }

    result = graph.invoke(initial_state)

    # 5. 输出结果摘要
    logger.info("=" * 50)
    logger.info("📊 运行结果摘要")
    logger.info("=" * 50)
    for pr in result.get("push_results", []):
        logger.info(f"  {pr}")
    if result.get("errors"):
        for err in result["errors"]:
            logger.error(f"  ❌ {err}")

    logger.info("🏁 Agent 运行结束")


if __name__ == "__main__":
    main()
