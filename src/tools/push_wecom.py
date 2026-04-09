"""企业微信群机器人推送工具"""

import os
import time

import requests

from .base import BaseTool


class WeComWebhookTool(BaseTool):
    name = "push_wecom"
    description = "通过企业微信群机器人 Webhook 推送消息。"

    def __init__(self, retry_times: int = 2, retry_delay: int = 5):
        self.webhook_url = os.getenv("WECOM_WEBHOOK", "")
        self.retry_times = retry_times
        self.retry_delay = retry_delay

    @property
    def available(self) -> bool:
        return bool(self.webhook_url)

    def run(self, *, content: str, title: str = "", **kwargs) -> str:
        if not self.available:
            return "⏭️ 企业微信 Webhook 未配置，跳过。"

        markdown_content = f"# {title}\n\n{content}" if title else content

        for attempt in range(1, self.retry_times + 1):
            try:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"content": markdown_content},
                }
                resp = requests.post(self.webhook_url, json=payload, timeout=30)
                data = resp.json()
                if data.get("errcode") == 0:
                    return "✅ 企业微信群机器人推送成功！"
                else:
                    msg = f"⚠️ 企业微信推送异常: {data.get('errmsg')}"
                    if attempt < self.retry_times:
                        time.sleep(self.retry_delay)
                        continue
                    return msg
            except Exception as e:
                if attempt < self.retry_times:
                    time.sleep(self.retry_delay)
                    continue
                return f"❌ 企业微信推送失败: {e}"

        return "❌ 企业微信推送失败: 超过最大重试次数"
