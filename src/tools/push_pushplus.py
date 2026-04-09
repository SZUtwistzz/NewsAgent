"""PushPlus 推送工具"""

import json
import os
import time

import requests

from .base import BaseTool


class PushPlusTool(BaseTool):
    name = "push_pushplus"
    description = "通过 PushPlus 推送 Markdown 内容到微信。"

    def __init__(self, retry_times: int = 2, retry_delay: int = 5):
        self.token = os.getenv("PUSH_TOKEN", "")
        self.retry_times = retry_times
        self.retry_delay = retry_delay

    @property
    def available(self) -> bool:
        return bool(self.token)

    def run(self, *, content: str, title: str = "", **kwargs) -> str:
        if not self.available:
            return "⏭️ PushPlus 未配置，跳过。"

        for attempt in range(1, self.retry_times + 1):
            try:
                payload = {
                    "token": self.token,
                    "title": title or "AI 早报",
                    "content": content,
                    "template": "markdown",
                }
                resp = requests.post(
                    "http://www.pushplus.plus/send",
                    json=payload,
                    timeout=30,
                )
                data = resp.json()
                if data.get("code") == 200:
                    return "✅ PushPlus 推送成功！"
                else:
                    msg = f"⚠️ PushPlus 推送异常: {json.dumps(data, ensure_ascii=False)}"
                    if attempt < self.retry_times:
                        time.sleep(self.retry_delay)
                        continue
                    return msg
            except Exception as e:
                if attempt < self.retry_times:
                    time.sleep(self.retry_delay)
                    continue
                return f"❌ PushPlus 推送失败: {e}"

        return "❌ PushPlus 推送失败: 超过最大重试次数"
