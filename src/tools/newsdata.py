"""NewsData.io 新闻抓取工具"""

import os
import logging

import requests

from .base import BaseTool

logger = logging.getLogger("news_agent")

NEWSDATA_BASE = "https://newsdata.io/api/1"


class NewsDataTool(BaseTool):
    """通过 NewsData.io 获取全球最新新闻"""

    name = "fetch_newsdata"
    description = "通过 NewsData.io 获取全球最新新闻，支持按国家、语言和分类筛选"

    def __init__(self, categories: list[str], countries: list[str],
                 language: str = "zh", max_results: int = 20):
        self.categories = categories
        self.countries = countries
        self.language = language
        self.max_results = max_results
        self.api_key = os.getenv("NEWSDATA_KEY", "")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def run(self, **kwargs) -> str:
        if not self.available:
            return ""

        all_items = []
        country_str = ",".join(self.countries)

        for category in self.categories:
            try:
                params = {
                    "apikey": self.api_key,
                    "country": country_str,
                    "category": category,
                    "size": self.max_results,
                }
                # language 和 country 同时使用容易超时，只在无 country 时传 language
                if not self.countries:
                    params["language"] = self.language

                resp = requests.get(
                    f"{NEWSDATA_BASE}/latest",
                    params=params,
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()

                for item in data.get("results", []):
                    title = item.get("title", "无标题")
                    desc = (item.get("description") or "")[:200]
                    link = item.get("link", "")
                    source = item.get("source_id", "NewsData")
                    all_items.append(
                        f"[NewsData/{source}] {title}\n摘要: {desc}\n链接: {link}"
                    )
            except Exception as e:
                logger.warning(f"NewsData.io 请求失败 (category={category}): {e}")

        if not all_items:
            return ""

        return f"NewsData.io 获取 {len(all_items)} 条新闻：\n\n" + "\n\n---\n\n".join(all_items)
