"""
Competitive intelligence change tracker.

Checks pricing pages, feature announcements, job postings, and press mentions
for each competitor in watch.json and appends changes to competitive-intel/changelog.md.
"""

from __future__ import annotations
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import anthropic

MODEL = "claude-opus-4-6"
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {
        "type": "web_fetch_20260209",
        "name": "web_fetch",
        "cache_control": {"type": "ephemeral"},
    },
]

WATCH_FILE     = ROOT / "competitive_intel_agent" / "watch.json"
CHANGELOG_FILE = ROOT / "competitive-intel" / "changelog.md"

TRACKER_SYSTEM = """You are a competitive intelligence tracker for a B2B SaaS company.

Your job is to detect CHANGES and NEW DEVELOPMENTS for a competitor in the last 7 days.
You will search for and report on:

1. **Pricing changes** — any changes to pricing page, new tiers, removed plans, price increases/decreases
2. **Feature announcements** — new features, product updates, blog posts about product changes
3. **Job postings** — new open roles, especially in Sales (AE, SDR, BDR, VP Sales) and Engineering
4. **Press mentions** — news articles, funding announcements, press releases, notable mentions

Be specific and factual. Include URLs. If nothing changed, say "No significant changes detected."

Output format — return a clean markdown section like this:

### {CompetitorName}
**Pricing:** [what changed, or "No changes detected"]
**Features:** [what was announced, or "No new announcements"]
**Jobs:** [new roles found, count by dept, or "No new postings found"]
**Press:** [notable mentions with URLs, or "Nothing notable"]

Keep it tight. Bullet points for multiple items. Always include a source URL where relevant."""


def _run_tracker_loop(client: anthropic.Anthropic, competitor: str, your_company: str) -> str:
    """Run the tracker research loop for one competitor."""
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    prompt = f"""Today is {today}. Research {competitor} (competitor to {your_company}) for changes in the LAST 7 DAYS ONLY.

Check:
1. Their pricing page — any changes to plans, pricing, or packaging?
2. Their blog/changelog/product updates — any new feature announcements?
3. Their jobs page or LinkedIn — any new open roles in Sales or Engineering?
4. Google News + tech press — any press coverage, funding news, or notable mentions?

Use date filters in your searches (past week / past 7 days). Be specific — include numbers, role titles, URLs.
"""
    cached_sys = [
        {
            "type": "text",
            "text": TRACKER_SYSTEM,
            "cache_control": {"type": "ephemeral"},
        }
    ]
    messages = [{"role": "user", "content": prompt}]
    container_id = None

    for _ in range(12):
        kwargs = dict(
            model=MODEL,
            max_tokens=4000,
            system=cached_sys,
            tools=WEB_TOOLS,
            messages=messages,
        )
        if container_id:
            kwargs["container"] = container_id

        response = client.messages.create(**kwargs)

        if hasattr(response, "container") and response.container:
            container_id = response.container.id

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "type") and block.type == "text":
                    return block.text
            return ""

        if response.stop_reason in ("pause_turn", "tool_use"):
            continue

    return ""


def run_tracker(verbose: bool = True) -> str:
    """
    Run the tracker for all competitors in watch.json.
    Returns the changelog entry string (also appended to file).
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    if not WATCH_FILE.exists():
        print(f"Error: watch.json not found at {WATCH_FILE}", file=sys.stderr)
        sys.exit(1)

    watched = json.loads(WATCH_FILE.read_text())
    if not watched:
        print("No competitors in watch.json.", file=sys.stderr)
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sections = []
    for w in watched:
        competitor   = w.get("competitor", "")
        your_company = w.get("your_company", "")
        if not competitor:
            continue
        if verbose:
            print(f"  Tracking {competitor}…", file=sys.stderr)
        result = _run_tracker_loop(client, competitor, your_company)
        sections.append(result.strip())

    # Build changelog entry
    entry = f"\n\n## {today} — Weekly Tracker Run ({now_ts})\n\n"
    entry += "\n\n".join(sections)
    entry += "\n\n---"

    # Append to changelog file
    CHANGELOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CHANGELOG_FILE.exists():
        header = "# Competitive Intelligence Changelog\n\n_Auto-generated by tracker. Each entry covers the prior 7 days._\n"
        CHANGELOG_FILE.write_text(header, encoding="utf-8")

    with open(CHANGELOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

    if verbose:
        print(f"\n  Changelog updated: {CHANGELOG_FILE}", file=sys.stderr)

    return entry
