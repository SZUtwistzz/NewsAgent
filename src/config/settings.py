"""Pydantic 配置模型 & 加载逻辑"""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider: str = "deepseek"
    model: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com"
    temperature: float = 0.7
    max_tokens: int = 4096


class RSSSource(BaseModel):
    name: str
    url: str
    category: str = "general"


class WecomWebhookConfig(BaseModel):
    enabled: bool = True


class PushPlusConfig(BaseModel):
    enabled: bool = False


class NewsAPIConfig(BaseModel):
    """NewsAPI.org 配置 — api_key 从环境变量 NEWSAPI_KEY 读取"""
    enabled: bool = False
    categories: list[str] = ["general", "technology", "business"]
    countries: list[str] = ["cn", "us"]
    language: str = "zh"
    page_size: int = 20


class NewsDataConfig(BaseModel):
    """NewsData.io 配置 — api_key 从环境变量 NEWSDATA_KEY 读取"""
    enabled: bool = False
    categories: list[str] = ["science", "business", "politics"]
    countries: list[str] = ["cn"]
    language: str = "zh"
    max_results: int = 20


class PushChannelsConfig(BaseModel):
    wecom_webhook: WecomWebhookConfig = WecomWebhookConfig()
    pushplus: PushPlusConfig = PushPlusConfig()


class CollectorConfig(BaseModel):
    description: str = ""
    max_rss_per_source: int = 15
    news_lookback_hours: int = 24
    max_search_queries: int = 3


class EditorConfig(BaseModel):
    description: str = ""
    top_n_news: int = 10


class PublisherConfig(BaseModel):
    description: str = ""
    retry_times: int = 2
    retry_delay_seconds: int = 5


class AgentsConfig(BaseModel):
    collector: CollectorConfig = CollectorConfig()
    editor: EditorConfig = EditorConfig()
    publisher: PublisherConfig = PublisherConfig()


class LangSmithConfig(BaseModel):
    enabled: bool = False
    project: str = "news-agent"


class ObservabilityConfig(BaseModel):
    log_level: str = "INFO"
    langsmith: LangSmithConfig = LangSmithConfig()


class Settings(BaseModel):
    llm: LLMConfig = LLMConfig()
    rss_sources: list[RSSSource] = []
    newsapi: NewsAPIConfig = NewsAPIConfig()
    newsdata: NewsDataConfig = NewsDataConfig()
    push_channels: PushChannelsConfig = PushChannelsConfig()
    agents: AgentsConfig = AgentsConfig()
    observability: ObservabilityConfig = ObservabilityConfig()


def load_settings(config_path: Optional[str] = None) -> Settings:
    """从 YAML 文件加载配置，支持环境变量覆盖"""
    if config_path is None:
        config_path = os.getenv(
            "NEWS_AGENT_CONFIG",
            str(Path(__file__).parent.parent.parent / "config" / "settings.yaml"),
        )

    path = Path(config_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return Settings(**data)

    return Settings()
