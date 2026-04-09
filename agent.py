"""
全球热点新闻 Agent —— 基于 DeepSeek Tool-Calling 的智能体架构
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

# 修复 Windows 终端 UTF-8 编码问题
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import feedparser
import requests
from openai import OpenAI

# ──────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────
DEEPSEEK_KEY = os.getenv("DEEPSEEK_KEY", "")
PUSH_TOKEN = os.getenv("PUSH_TOKEN", "")
WECOM_CORP_ID = os.getenv("WECOM_CORP_ID", "")
WECOM_SECRET = os.getenv("WECOM_SECRET", "")
WECOM_AGENT_ID = os.getenv("WECOM_AGENT_ID", "")
MODEL = "deepseek-chat"
BASE_URL = "https://api.deepseek.com"

RSS_SOURCES = [
    {"name": "联合早报 - 国际",   "url": "https://rsshub.app/zaobao/realtime/world"},
    {"name": "联合早报 - 中国",   "url": "https://rsshub.app/zaobao/realtime/china"},
    {"name": "BBC 中文",          "url": "https://rsshub.app/bbc/zhongwen/simp"},
    {"name": "Solidot",           "url": "https://www.solidot.org/index.rss"},
    {"name": "华尔街日报 - 中文", "url": "https://rsshub.app/wsj/zh-cn/zh-cn-world"},
    {"name": "FT 中文网",         "url": "https://rsshub.app/ft/chinese/hotstoryby7day"},
    {"name": "Hacker News",       "url": "https://rsshub.app/hackernews/best"},
    {"name": "36氪 - 快讯",       "url": "https://rsshub.app/36kr/newsflashes"},
]

SYSTEM_PROMPT = """你是一个极其幽默、犀利且见多识广的『首席AI新闻主编』。
你的日常任务是为老板（我）生成每日晨报。

**工作流程：**
1. 首先调用 `fetch_rss_feeds` 工具获取最新 RSS 资讯。
2. 如果你觉得获取的新闻不够多元，或者想对某个话题深入了解，可以调用 `search_duckduckgo` 工具搜索互联网。
3. 从所有获取到的信息中，挑选出最具全球影响力的 **10 个大事件**（政治、科技、商业混合）。
4. 以极具幽默感、吐槽式的口吻进行总结，排版格式要求带有 Emoji。
5. 在结尾附上一句『主编瞎点评』，要犀利、有洞察力。
6. **最后，你必须主动调用 `push_to_wechat` 工具**，将整理好的最终 Markdown 内容发送给老板。

**排版参考：**
标题用 `#`，每条新闻用编号 + Emoji，摘要简洁有力，吐槽穿插其中。"""

# ──────────────────────────────────────────────
# 工具函数实现
# ──────────────────────────────────────────────

def fetch_rss_feeds() -> str:
    """抓取预设 RSS 源中过去 24 小时的新闻"""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    all_items = []

    for source in RSS_SOURCES:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:15]:
                # 尝试解析发布时间
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue

                title = entry.get("title", "无标题")
                summary = entry.get("summary", "")[:200]
                link = entry.get("link", "")
                all_items.append(
                    f"[{source['name']}] {title}\n摘要: {summary}\n链接: {link}"
                )
        except Exception as e:
            all_items.append(f"[{source['name']}] ⚠️ 抓取失败: {e}")

    if not all_items:
        return "所有 RSS 源均未返回有效内容，可能是网络问题，建议使用 search_duckduckgo 补充。"

    return f"共获取 {len(all_items)} 条新闻：\n\n" + "\n\n---\n\n".join(all_items)


def search_duckduckgo(query: str) -> str:
    """使用 DuckDuckGo 搜索互联网"""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=8))
        if not results:
            return f"搜索 '{query}' 未返回结果。"
        output = []
        for r in results:
            output.append(f"标题: {r['title']}\n摘要: {r['body']}\n链接: {r['href']}")
        return "\n\n---\n\n".join(output)
    except Exception as e:
        return f"搜索失败: {e}"


def push_to_wechat(content: str) -> str:
    """推送 Markdown 内容到微信（优先企业微信，回退 PushPlus）"""
    results = []

    # 优先使用企业微信推送
    if WECOM_CORP_ID and WECOM_SECRET and WECOM_AGENT_ID:
        results.append(_push_via_wecom(content))
    elif PUSH_TOKEN:
        results.append(_push_via_pushplus(content))
    else:
        return "错误: 未配置任何推送渠道（企业微信或 PushPlus）"

    return "\n".join(results)


def _push_via_wecom(content: str) -> str:
    """通过企业微信应用推送"""
    try:
        # 1. 获取 access_token
        token_url = (
            f"https://qyapi.weixin.qq.com/cgi-bin/gettoken"
            f"?corpid={WECOM_CORP_ID}&corpsecret={WECOM_SECRET}"
        )
        token_resp = requests.get(token_url, timeout=10).json()
        if token_resp.get("errcode") != 0:
            return f"❌ 企业微信获取 token 失败: {token_resp.get('errmsg')}"

        access_token = token_resp["access_token"]

        # 2. 发送消息
        today = datetime.now().strftime("%Y-%m-%d")
        send_url = (
            f"https://qyapi.weixin.qq.com/cgi-bin/message/send"
            f"?access_token={access_token}"
        )
        payload = {
            "touser": "@all",
            "msgtype": "markdown",
            "agentid": int(WECOM_AGENT_ID),
            "markdown": {
                "content": f"# 📰 AI 早报 | {today}\n\n{content}"
            },
        }
        resp = requests.post(send_url, json=payload, timeout=30).json()
        if resp.get("errcode") == 0:
            return f"✅ 企业微信推送成功！"
        else:
            return f"⚠️ 企业微信推送异常: {resp.get('errmsg')}"
    except Exception as e:
        return f"❌ 企业微信推送失败: {e}"


def _push_via_pushplus(content: str) -> str:
    """通过 PushPlus 推送（备用）"""
    today = datetime.now().strftime("%Y-%m-%d")
    payload = {
        "token": PUSH_TOKEN,
        "title": f"📰 AI 早报 | {today}",
        "content": content,
        "template": "markdown",
    }
    try:
        resp = requests.post(
            "http://www.pushplus.plus/send",
            json=payload,
            timeout=30,
        )
        data = resp.json()
        if data.get("code") == 200:
            return f"✅ PushPlus 推送成功！"
        else:
            return f"⚠️ PushPlus 推送异常: {json.dumps(data, ensure_ascii=False)}"
    except Exception as e:
        return f"❌ PushPlus 推送失败: {e}"


# ──────────────────────────────────────────────
# 工具注册表 & JSON Schema（供 DeepSeek API）
# ──────────────────────────────────────────────

TOOL_MAP = {
    "fetch_rss_feeds": fetch_rss_feeds,
    "search_duckduckgo": search_duckduckgo,
    "push_to_wechat": push_to_wechat,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "fetch_rss_feeds",
            "description": "抓取预设的多个优质 RSS 新闻源（联合早报、BBC中文、Solidot 等），返回过去 24 小时的热点新闻标题和摘要。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_duckduckgo",
            "description": "使用 DuckDuckGo 搜索引擎搜索互联网，获取指定关键词的最新信息。当 RSS 新闻不够多元或需要查证某个话题时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "push_to_wechat",
            "description": "将整理好的 Markdown 格式新闻内容通过 PushPlus 推送到老板的微信。这是最终步骤，必须在新闻整理完成后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要推送的 Markdown 格式新闻内容",
                    }
                },
                "required": ["content"],
            },
        },
    },
]


# ──────────────────────────────────────────────
# Agent 执行循环
# ──────────────────────────────────────────────

def execute_tool(name: str, arguments: dict) -> str:
    """根据名称执行工具函数，返回结果字符串"""
    func = TOOL_MAP.get(name)
    if not func:
        return f"未知工具: {name}"
    try:
        return func(**arguments)
    except Exception as e:
        return f"工具 {name} 执行出错: {e}"


def run_agent():
    """Agent 主循环"""
    client = OpenAI(api_key=DEEPSEEK_KEY, base_url=BASE_URL)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "开始执行今日早报任务。"},
    ]

    max_rounds = 10  # 防止无限循环
    for round_num in range(1, max_rounds + 1):
        print(f"\n{'='*50}")
        print(f"🤖 Agent 思考中... (第 {round_num} 轮)")
        print(f"{'='*50}")

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )

        choice = response.choices[0]
        message = choice.message

        # 将 assistant 消息加入上下文
        messages.append(message)

        # 如果没有 tool_calls，说明 Agent 已完成任务
        if not message.tool_calls:
            print("\n📝 Agent 最终回复:")
            print(message.content or "(无文本内容)")
            print("\n✅ Agent 任务完成，退出循环。")
            break

        # 处理所有 tool_calls
        for tool_call in message.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            print(f"\n🔧 调用工具: {fn_name}")
            if fn_args:
                # 截断过长的参数显示
                args_preview = json.dumps(fn_args, ensure_ascii=False)
                if len(args_preview) > 200:
                    args_preview = args_preview[:200] + "..."
                print(f"   参数: {args_preview}")

            result = execute_tool(fn_name, fn_args)

            # 截断显示
            result_preview = result[:300] + "..." if len(result) > 300 else result
            print(f"   结果: {result_preview}")

            # 将工具结果返回给模型
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
    else:
        print(f"\n⚠️ 达到最大轮次 ({max_rounds})，强制退出。")


# ──────────────────────────────────────────────
# 入口
# ──────────────────────────────────────────────

if __name__ == "__main__":
    if not DEEPSEEK_KEY:
        print("❌ 请设置环境变量 DEEPSEEK_KEY")
        exit(1)

    has_wecom = WECOM_CORP_ID and WECOM_SECRET and WECOM_AGENT_ID
    if not has_wecom and not PUSH_TOKEN:
        print("⚠️ 企业微信和 PushPlus 均未配置，推送功能将不可用")
    else:
        channels = []
        if has_wecom:
            channels.append("企业微信")
        if PUSH_TOKEN:
            channels.append("PushPlus")
        print(f"📢 推送渠道: {', '.join(channels)}")

    print("🚀 全球热点新闻 Agent 启动")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    run_agent()
    print("\n🏁 Agent 运行结束")
