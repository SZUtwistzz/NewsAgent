"""编辑 Agent — 负责筛选新闻、撰写幽默早报"""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.agents.state import AgentState
from src.config.settings import Settings

logger = logging.getLogger("news_agent")

EDITOR_PROMPT = """你是一个极其幽默、犀利且见多识广的『首席AI新闻主编』。

**你的任务：**
从采集员提供的原始新闻中，挑选出最具全球影响力的 {top_n} 个大事件（政治、科技、商业混合），撰写每日晨报。

**排版要求：**
- 标题用 `#`
- 每条新闻用编号 + Emoji
- 摘要简洁有力，吐槽穿插其中
- 结尾附上一句『主编瞎点评』，要犀利、有洞察力

**注意：直接输出最终的 Markdown 早报内容，不要输出多余的解释。**"""


def build_editor_node(settings: Settings):
    """构建编辑 Agent 节点函数"""

    llm = ChatOpenAI(
        model=settings.llm.model,
        base_url=settings.llm.base_url,
        temperature=settings.llm.temperature,
        max_tokens=settings.llm.max_tokens,
    )
    top_n = settings.agents.editor.top_n_news

    def editor_node(state: AgentState) -> dict:
        logger.info("🚀 [EditorAgent] 开始编辑早报")

        # 合并所有素材
        materials = [state.get("raw_news", "")]
        for sr in state.get("search_results", []):
            materials.append(sr)
        all_news = "\n\n---\n\n".join(m for m in materials if m)

        if not all_news.strip():
            logger.warning("没有收到任何原始新闻素材")
            return {
                "report": "⚠️ 今日未采集到任何新闻，早报生成失败。",
                "stage": "edited",
                "errors": ["无新闻素材"],
            }

        messages = [
            SystemMessage(content=EDITOR_PROMPT.format(top_n=top_n)),
            HumanMessage(content=f"以下是今日采集到的原始新闻素材：\n\n{all_news}"),
        ]

        response = llm.invoke(messages)
        report = response.content or ""

        logger.info(f"📝 早报生成完毕，长度: {len(report)} 字符")
        logger.info("✅ [EditorAgent] 编辑完成")

        return {
            "report": report,
            "stage": "edited",
            "errors": [],
        }

    return editor_node
