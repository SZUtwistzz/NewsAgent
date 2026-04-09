# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A single-file AI news agent (`agent.py`) that uses DeepSeek's tool-calling API to autonomously fetch global news from RSS feeds, optionally search the web via DuckDuckGo, compose a humorous Chinese-language morning briefing, and push it to WeChat via PushPlus.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the agent locally (requires env vars)
DEEPSEEK_KEY="sk-xxx" PUSH_TOKEN="xxx" python agent.py
```

No tests, linter, or build system — this is a single-script project.

## Architecture

The entire agent lives in `agent.py` and follows an agentic tool-calling loop:

1. An OpenAI-compatible client connects to DeepSeek (`BASE_URL = "https://api.deepseek.com"`, model `deepseek-chat`)
2. The agent loop (`run_agent()`) sends messages with `TOOLS_SCHEMA` and iterates up to 10 rounds
3. Each round: DeepSeek returns tool calls → `execute_tool()` dispatches to Python functions → results fed back as `tool` messages
4. Three tools are registered in `TOOL_MAP`:
   - `fetch_rss_feeds` — parses 8 RSS sources via `feedparser`, filters to last 24h
   - `search_duckduckgo` — web search via `duckduckgo-search` library
   - `push_to_wechat` — POST to PushPlus API for WeChat delivery

## Environment Variables

- `DEEPSEEK_KEY` — DeepSeek API key (required, agent exits if missing)
- `PUSH_TOKEN` — PushPlus token (optional locally, but push will fail without it)

In CI, these are read from GitHub Actions secrets in `.github/workflows/agent_daily.yml`.

## Deployment

GitHub Actions workflow (`.github/workflows/agent_daily.yml`) runs daily at UTC 00:00 (Beijing 08:00) and supports `workflow_dispatch` for manual triggers.
