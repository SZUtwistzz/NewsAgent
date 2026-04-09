"""NewsAPI.org 新闻抓取工具"""

import os
import logging
from datetime import datetime, timedelta, timezone

import requests

from .base import BaseTool

logger = logging.getLogger("news_agent")

NEWSAPI_BASE = "https://newsapi.org/v2"


class NewsAPITool(BaseTool):
    """通过 NewsAPI.org 获取全球热点新闻"""

    name = "fetch_newsapi"
    description = "通过 NewsAPI.org 获取全球热点新闻，支持按国家和分类筛选"

    def __init__(self, categories: list[str], countries: list[str],
                 language: str = "zh", page_size: int = 20,
                 lookback_hours: int = 24):
        self.categories = categories
        self.countries = countries
        self.language = language
        self.page_size = page_size
        self.lookback_hours = lookback_hours
        self.api_key = os.getenv("NEWSAPI_KEY", "")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def run(self, **kwargs) -> str:
        if not self.available:
            return ""

        all_items = []

        for country in self.countries:
            for category in self.categories:
                try:
                    resp = requests.get(
                        f"{NEWSAPI_BASE}/top-headlines",
                        params={
                            "apiKey": self.api_key,
                            "country": country,
                            "category": category,
                            "pageSize": self.page_size,
                        },
                        timeout=15,
                    )
                    resp.raise_for_status()
                    data = resp.json()

                    for article in data.get("articles", []):
                        title = article.get("title", "无标题")
                        desc = (article.get("description") or "")[:200]
                        url = article.get("url", "")
                        source_name = article.get("source", {}).get("name", "NewsAPI")
                        all_items.append(
                            f"[NewsAPI/{source_name}] {title}\n摘要: {desc}\n链接: {url}"
                        )
                except Exception as e:
                    logger.warning(f"NewsAPI 请求失败 (country={country}, category={category}): {e}")

        if not all_items:
            return ""

        return f"NewsAPI 获取 {len(all_items)} 条新闻：\n\n" + "\n\n---\n\n".join(all_items)
