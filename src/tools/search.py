"""DuckDuckGo 搜索工具"""

from .base import BaseTool


class DuckDuckGoSearchTool(BaseTool):
    name = "search_duckduckgo"
    description = "使用 DuckDuckGo 搜索引擎搜索互联网，获取指定关键词的最新信息。"

    def __init__(self, max_results: int = 8):
        self.max_results = max_results

    def run(self, *, query: str, **kwargs) -> str:
        try:
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=self.max_results))
            if not results:
                return f"搜索 '{query}' 未返回结果。"
            output = []
            for r in results:
                output.append(f"标题: {r['title']}\n摘要: {r['body']}\n链接: {r['href']}")
            return "\n\n---\n\n".join(output)
        except Exception as e:
            return f"搜索失败: {e}"
