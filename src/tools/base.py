"""工具基类 & 注册表"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """所有工具的抽象基类"""

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, **kwargs: Any) -> str:
        """执行工具，返回结果字符串"""
        ...


class ToolRegistry:
    """工具注册表，支持动态注册和查找"""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def as_langchain_tools(self):
        """将注册的工具转换为 LangChain Tool 列表"""
        from langchain_core.tools import StructuredTool
        lc_tools = []
        for tool in self._tools.values():
            lc_tools.append(
                StructuredTool.from_function(
                    func=tool.run,
                    name=tool.name,
                    description=tool.description,
                )
            )
        return lc_tools
