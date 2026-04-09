"""企业微信群机器人推送工具"""

import os
import logging
import time

import requests

from .base import BaseTool

logger = logging.getLogger("news_agent")

WECOM_MAX_LENGTH = 4096


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

    def _split_content(self, content: str, title: str = "") -> list[str]:
        """将超长内容按段落拆分为多条消息，每条不超过 4096 字符"""
        header = f"# {title}\n\n" if title else ""
        # 预留 header 和分页标记的空间
        max_body = WECOM_MAX_LENGTH - len(header.encode("utf-8")) - 30

        if len(content.encode("utf-8")) <= max_body:
            return [header + content]

        # 按双换行（段落）拆分
        paragraphs = content.split("\n\n")
        chunks = []
        current = ""

        for para in paragraphs:
            candidate = (current + "\n\n" + para).strip() if current else para
            if len(candidate.encode("utf-8")) > max_body:
                if current:
                    chunks.append(current)
                current = para
            else:
                current = candidate

        if current:
            chunks.append(current)

        # 组装最终消息，加上分页标记
        total = len(chunks)
        if total == 1:
            return [header + chunks[0]]

        messages = []
        for i, chunk in enumerate(chunks, 1):
            page_header = f"# {title}（{i}/{total}）\n\n" if title else f"**（{i}/{total}）**\n\n"
            messages.append(page_header + chunk)

        return messages

    def _send_one(self, markdown_content: str) -> tuple[bool, str]:
        """发送单条消息，带重试"""
        for attempt in range(1, self.retry_times + 1):
            try:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {"content": markdown_content},
                }
                resp = requests.post(self.webhook_url, json=payload, timeout=30)
                data = resp.json()
                if data.get("errcode") == 0:
                    return True, ""
                else:
                    msg = data.get("errmsg", "未知错误")
                    if attempt < self.retry_times:
                        time.sleep(self.retry_delay)
                        continue
                    return False, msg
            except Exception as e:
                if attempt < self.retry_times:
                    time.sleep(self.retry_delay)
                    continue
                return False, str(e)

        return False, "超过最大重试次数"

    def run(self, *, content: str, title: str = "", **kwargs) -> str:
        if not self.available:
            return "⏭️ 企业微信 Webhook 未配置，跳过。"

        messages = self._split_content(content, title)
        logger.info(f"📤 企业微信推送: {len(messages)} 条消息")

        success_count = 0
        last_error = ""

        for i, msg in enumerate(messages):
            ok, err = self._send_one(msg)
            if ok:
                success_count += 1
            else:
                last_error = err
                logger.warning(f"企业微信第 {i+1} 条推送失败: {err}")
            # 多条消息间隔 1 秒，避免频率限制
            if i < len(messages) - 1:
                time.sleep(1)

        if success_count == len(messages):
            return "✅ 企业微信群机器人推送成功！"
        elif success_count > 0:
            return f"⚠️ 企业微信推送部分成功 ({success_count}/{len(messages)}): {last_error}"
        else:
            return f"❌ 企业微信推送失败: {last_error}"
