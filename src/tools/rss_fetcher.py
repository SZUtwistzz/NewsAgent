"""RSS 新闻抓取工具"""

from datetime import datetime, timedelta, timezone

import feedparser

from src.config.settings import RSSSource
from .base import BaseTool


class RSSFetcherTool(BaseTool):
    name = "fetch_rss_feeds"
    description = "抓取预设的多个优质 RSS 新闻源，返回过去指定小时内的热点新闻标题和摘要。"

    def __init__(self, sources: list[RSSSource], lookback_hours: int = 24, max_per_source: int = 15):
        self.sources = sources
        self.lookback_hours = lookback_hours
        self.max_per_source = max_per_source

    def run(self, **kwargs) -> str:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
        all_items = []

        for source in self.sources:
            try:
                feed = feedparser.parse(source.url)
                for entry in feed.entries[: self.max_per_source]:
                    published = entry.get("published_parsed") or entry.get("updated_parsed")
                    if published:
                        pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                        if pub_dt < cutoff:
                            continue

                    title = entry.get("title", "无标题")
                    summary = entry.get("summary", "")[:200]
                    link = entry.get("link", "")
                    all_items.append(
                        f"[{source.name}] {title}\n摘要: {summary}\n链接: {link}"
                    )
            except Exception as e:
                all_items.append(f"[{source.name}] ⚠️ 抓取失败: {e}")

        if not all_items:
            return "所有 RSS 源均未返回有效内容，可能是网络问题。"

        return f"共获取 {len(all_items)} 条新闻：\n\n" + "\n\n---\n\n".join(all_items)
