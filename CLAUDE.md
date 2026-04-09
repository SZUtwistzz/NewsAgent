# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An enterprise-grade multi-agent news aggregation system built with LangChain/LangGraph and DeepSeek API. The system uses three specialized agents (Collector, Editor, Publisher) orchestrated via LangGraph to fetch global news from RSS feeds, compose humorous daily briefings, and push to WeChat channels.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent locally (requires env vars)
DEEPSEEK_KEY="sk-xxx" WECOM_WEBHOOK="https://..." python main.py

# Run with old single-file version (deprecated)
DEEPSEEK_KEY="sk-xxx" WECOM_WEBHOOK="https://..." python agent.py
```

## Architecture

**Multi-Agent Pipeline (LangGraph):**
- `CollectorAgent` → fetches RSS feeds, optionally searches web via DuckDuckGo
- `EditorAgent` → filters and composes humorous briefing with LLM
- `PublisherAgent` → pushes to WeChat Work webhook and/or PushPlus

**Key Components:**
- `src/agents/graph.py` — LangGraph state machine definition
- `src/agents/state.py` — shared state schema (AgentState TypedDict)
- `src/tools/` — pluggable tool system (BaseTool abstract class)
- `config/settings.yaml` — YAML config loaded via Pydantic models in `src/config/settings.py`
- `src/observability.py` — structured logging + optional LangSmith tracing

**Tool Plugin System:**
All tools inherit from `BaseTool` and implement `run(**kwargs) -> str`. Tools are registered and converted to LangChain StructuredTools in `src/tools/base.py`.

## Configuration

All runtime config lives in `config/settings.yaml`:
- RSS sources list
- LLM settings (model, temperature, etc.)
- Agent parameters (max search queries, top N news, retry times)
- Push channel toggles
- Observability settings (log level, LangSmith project)

Environment variables:
- `DEEPSEEK_KEY` (required) — DeepSeek API key, also set as `OPENAI_API_KEY` for langchain_openai
- `WECOM_WEBHOOK` (optional) — WeChat Work group bot webhook URL
- `PUSH_TOKEN` (optional) — PushPlus token
- `LANGCHAIN_API_KEY` (optional) — for LangSmith tracing
- `NEWS_AGENT_CONFIG` (optional) — custom config file path

## Deployment

GitHub Actions workflow at `.github/workflows/agent_daily.yml` runs daily at UTC 00:00 (Beijing 08:00) and supports `workflow_dispatch`. Requires repository secrets: `DEEPSEEK_KEY`, `WECOM_WEBHOOK`, optionally `PUSH_TOKEN` and `LANGCHAIN_API_KEY`.

## Migration Notes

The old single-file `agent.py` is deprecated. New entry point is `main.py`. Key differences:
- Monolithic → modular structure
- Hardcoded config → YAML + Pydantic
- Single agent loop → LangGraph multi-agent pipeline
- No observability → structured logs + LangSmith

## Language

Codebase uses English for code/comments, Chinese for prompts/logs/commit messages. Respond in Chinese when interacting with the user.
