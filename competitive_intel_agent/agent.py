"""
Competitive Intelligence Agent — uses Anthropic API directly with server-side
web_search and web_fetch tools instead of the Agent SDK.

Architecture:
  Three async research calls run in parallel (asyncio.gather):
    ├── g2_research()       → G2, Capterra, Reddit reviews
    ├── website_research()  → pricing, features, job postings
    └── news_research()     → last 30 days: news, Reddit, X/Twitter

  Then a synthesis call cross-references the three reports and outputs
  the final battlecard JSON.

Web search/fetch run server-side on Anthropic's infrastructure — no
extra packages needed beyond `anthropic`.
"""

from __future__ import annotations
import asyncio
import json
import re
from pathlib import Path
from typing import Optional, Tuple

import anthropic

from .battlecard import Battlecard
from .updater import merge as merge_battlecards
from .prompts import (
    G2_RESEARCHER_SYSTEM,
    WEBSITE_RESEARCHER_SYSTEM,
    NEWS_RESEARCHER_SYSTEM,
    ORCHESTRATOR_SYSTEM,
    BATTLECARD_JSON_SCHEMA,
)

MODEL = "claude-opus-4-6"
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209",  "name": "web_fetch"},
]


# ---------------------------------------------------------------------------
# Low-level: run one agentic research loop until end_turn
# ---------------------------------------------------------------------------

def _run_research_loop(
    client: anthropic.Anthropic,
    system: str,
    user_prompt: str,
    max_iterations: int = 15,
) -> str:
    """
    Run a single-agent research loop with web search/fetch until end_turn.
    Returns the final text response.
    """
    messages = [{"role": "user", "content": user_prompt}]

    for _ in range(max_iterations):
        response = client.messages.create(
            model=MODEL,
            max_tokens=8000,
            system=system,
            tools=WEB_TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
        )

        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract the final text block
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    return block.text
            return ""

        if response.stop_reason == "pause_turn":
            # Server-side tool hit iteration limit — re-send to continue
            continue

        # Handle tool_use: collect all tool results, send back
        if response.stop_reason == "tool_use":
            # Server-side tools (web_search, web_fetch) execute automatically —
            # we never see tool_use for them. If we somehow get here, just continue.
            continue

    return ""


# ---------------------------------------------------------------------------
# Async wrappers — each runs a research agent in a thread pool
# ---------------------------------------------------------------------------

async def _async_research(
    client: anthropic.Anthropic,
    system: str,
    prompt: str,
) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _run_research_loop, client, system, prompt
    )


# ---------------------------------------------------------------------------
# Research prompts per domain
# ---------------------------------------------------------------------------

def _g2_prompt(competitor: str) -> str:
    return (
        f"Research {competitor} on review sites (G2, Capterra, TrustRadius, Clutch) "
        f"and Reddit. Find what customers praise, complain about, and why they switch. "
        f"Return a JSON report following the format in your instructions."
    )

def _website_prompt(competitor: str) -> str:
    return (
        f"Fetch and analyze {competitor}'s homepage, pricing page, features page, "
        f"recent blog posts, and job postings on LinkedIn/their careers page. "
        f"Return a JSON report following the format in your instructions."
    )

def _news_prompt(competitor: str) -> str:
    return (
        f"Search for everything about {competitor} from the LAST 30 DAYS ONLY: "
        f"news, funding, product launches, Reddit threads, X/Twitter mentions, "
        f"community discussions. Use date filters. Return a JSON report."
    )


# ---------------------------------------------------------------------------
# Orchestrator synthesis
# ---------------------------------------------------------------------------

def _synthesize(
    client: anthropic.Anthropic,
    competitor: str,
    your_company: str,
    your_context: str,
    g2_report: str,
    website_report: str,
    news_report: str,
) -> str:
    """
    Cross-reference three research reports and produce the final battlecard JSON.
    """
    context_block = (
        f"\n## Context about {your_company}\n{your_context}\n"
        if your_context else ""
    )

    user_prompt = f"""
You have three research reports about **{competitor}** (a competitor to **{your_company}**).
Cross-reference them, assign confidence tiers, and output the battlecard JSON.
{context_block}

## Report 1 — Reviews (G2, Capterra, Reddit)
{g2_report or "No data returned."}

## Report 2 — Website & Pricing
{website_report or "No data returned."}

## Report 3 — Last 30 Days: News, Reddit, X/Twitter
{news_report or "No data returned."}

---

## Your job
1. Cross-reference all three reports. Where the same fact appears in 2+ reports → "confirmed". One report → "reported". You're inferring → "inferred".
2. Build the battlecard JSON using the schema below.
3. The "recent_news" array should include the most important items from Report 3 (last 30 days), including Reddit/X community sentiment.
4. Include honest landmines — areas where {competitor} genuinely outperforms {your_company}.
5. Return ONLY the JSON object. No markdown fences, no commentary.

## Schema
{BATTLECARD_JSON_SCHEMA}
""".strip()

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=ORCHESTRATOR_SYSTEM,
        messages=[{"role": "user", "content": user_prompt}],
        thinking={"type": "adaptive"},
    )

    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            return block.text
    return ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def build_battlecard(
    competitor: str,
    your_company: str,
    your_context: Optional[str] = None,
) -> Tuple[Battlecard, str]:
    """
    Run G2 / website / news research in parallel, then synthesize.
    Returns a validated Battlecard and the raw JSON string.
    """
    client = anthropic.Anthropic()
    context = your_context or ""

    print(f"  → Running 3 research agents in parallel for {competitor}...", flush=True)

    g2_report, website_report, news_report = await asyncio.gather(
        _async_research(client, G2_RESEARCHER_SYSTEM,      _g2_prompt(competitor)),
        _async_research(client, WEBSITE_RESEARCHER_SYSTEM, _website_prompt(competitor)),
        _async_research(client, NEWS_RESEARCHER_SYSTEM,    _news_prompt(competitor)),
    )

    print(f"  → Synthesizing battlecard for {competitor}...", flush=True)

    raw = _synthesize(
        client, competitor, your_company, context,
        g2_report, website_report, news_report,
    )

    card = _parse_and_validate(raw)
    return card, raw


async def update_battlecard_from_file(
    json_path: Path,
    competitor: str,
    your_company: str,
    your_context: Optional[str] = None,
) -> Tuple[Battlecard, str]:
    """
    Load existing battlecard, run fresh research, merge, return updated card.
    Falls back to full first-run if json_path doesn't exist or is corrupt.
    """
    fresh_card, raw_json = await build_battlecard(competitor, your_company, your_context)

    if json_path.exists():
        try:
            old_card = Battlecard.model_validate_json(json_path.read_text())
            merged = merge_battlecards(old=old_card, new=fresh_card)
            return merged, merged.model_dump_json(indent=2)
        except Exception as exc:
            print(f"  [warn] Could not load existing battlecard ({exc}). Starting fresh.")

    return fresh_card, raw_json


def _parse_and_validate(raw: str) -> Battlecard:
    """
    Extract JSON from model output and validate against Battlecard schema.
    Strips markdown code fences if present.
    """
    fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", raw)
    json_str = fence_match.group(1) if fence_match else raw.strip()

    obj_match = re.search(r"\{[\s\S]+\}", json_str)
    if obj_match:
        json_str = obj_match.group(0)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model output is not valid JSON: {exc}") from exc

    try:
        return Battlecard(**data)
    except Exception as exc:
        raise ValueError(
            f"Model output does not match the Battlecard schema: {exc}"
        ) from exc
