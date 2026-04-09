"""推送 Agent — 负责将早报推送到各渠道"""

import logging
from datetime import datetime

from src.agents.state import AgentState
from src.config.settings import Settings
from src.tools.push_wecom import WeComWebhookTool
from src.tools.push_pushplus import PushPlusTool

logger = logging.getLogger("news_agent")


def build_publisher_node(settings: Settings):
    """构建推送 Agent 节点函数"""

    pub_cfg = settings.agents.publisher
    channels = []

    if settings.push_channels.wecom_webhook.enabled:
        channels.append(
            WeComWebhookTool(
                retry_times=pub_cfg.retry_times,
                retry_delay=pub_cfg.retry_delay_seconds,
            )
        )

    if settings.push_channels.pushplus.enabled:
        channels.append(
            PushPlusTool(
                retry_times=pub_cfg.retry_times,
                retry_delay=pub_cfg.retry_delay_seconds,
            )
        )

    def publisher_node(state: AgentState) -> dict:
        logger.info("🚀 [PublisherAgent] 开始推送")

        report = state.get("report", "")
        if not report or report.startswith("⚠️"):
            logger.warning("早报内容为空或异常，跳过推送")
            return {
                "push_results": ["⏭️ 早报内容异常，跳过推送"],
                "stage": "done",
                "errors": [],
            }

        today = datetime.now().strftime("%Y-%m-%d")
        title = f"📰 AI 早报 | {today}"
        results = []

        for channel in channels:
            if not channel.available:
                msg = f"⏭️ {channel.name} 未配置环境变量，跳过"
                logger.info(msg)
                results.append(msg)
                continue

            logger.info(f"📤 推送到: {channel.name}")
            result = channel.run(content=report, title=title)
            logger.info(f"📤 {channel.name} 结果: {result}")
            results.append(result)

        if not channels:
            results.append("⚠️ 未配置任何推送渠道")

        logger.info("✅ [PublisherAgent] 推送完成")
        return {
            "push_results": results,
            "stage": "done",
            "errors": [],
        }

    return publisher_node
