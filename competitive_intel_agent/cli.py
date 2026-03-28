"""
Multi-competitor competitive intelligence CLI.

Takes N competitors, a company name, and a description of what to compare,
then researches all competitors in parallel and produces a combined
comparison report as Markdown and PDF.

Usage:
    python -m competitive_intel_agent.cli "Acme Corp" "Rival A" "Rival B" "Rival C" \
        --compare "pricing models, AI features, enterprise readiness" \
        --output reports/landscape

    python -m competitive_intel_agent.cli "Acme Corp" "Rival A" "Rival B" \
        --compare "developer experience and API quality" \
        --context "We are a developer-first platform targeting mid-market"
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import anyio
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(Path(__file__).parent / ".env", override=True)
load_dotenv(ROOT / ".env", override=True)

import anthropic

MODEL = "claude-sonnet-4-6"
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {
        "type": "web_fetch_20260209",
        "name": "web_fetch",
        "cache_control": {"type": "ephemeral"},
    },
]

RESEARCHER_SYSTEM = [
    {
        "type": "text",
        "text": """\
You are a competitive intelligence researcher. You will research a single \
competitor across multiple dimensions: their website, pricing, reviews, \
news, blog, and social media presence.

## Rules
- Include the exact URL for every claim.
- Quote directly when possible.
- Include both positive and negative findings.
- If you can't find data for something, say so explicitly.
- Be concise — return findings as a structured text report, not JSON.""",
        "cache_control": {"type": "ephemeral"},
    }
]


# ---------------------------------------------------------------------------
# Research: one call per competitor with server-side web tools
# ---------------------------------------------------------------------------

def _research_competitor(
    client: anthropic.Anthropic,
    competitor: str,
    compare_description: str,
    context: str,
) -> str:
    """Run a single research loop for one competitor. Returns raw text findings."""
    prompt = f"""Research **{competitor}** across these dimensions:

{compare_description}

Specifically check:
1. Their homepage — positioning, messaging, design quality, CTAs
2. Their pricing page — tiers, model (per-seat/usage/flat), actual prices
3. Review sites (G2, Capterra) and Reddit — what users praise and complain about
4. Recent news (last 30 days) — launches, funding, press
5. Their blog — topics, frequency, quality, SEO approach
6. Social media (LinkedIn, X/Twitter) — follower counts, posting frequency, engagement
7. Key features and product capabilities

{f"Context: {context}" if context else ""}

Return a concise research report with URLs for every claim."""

    messages = [{"role": "user", "content": prompt}]
    container_id = None

    for _ in range(3):
        kwargs = dict(
            model=MODEL,
            max_tokens=8000,
            system=RESEARCHER_SYSTEM,
            tools=WEB_TOOLS,
            messages=messages,
            thinking={"type": "adaptive"},
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

        # pause_turn or tool_use — continue loop
    return ""


async def _async_research(
    client: anthropic.Anthropic,
    competitor: str,
    compare_description: str,
    context: str,
) -> tuple[str, str]:
    """Run research in a thread pool. Returns (competitor_name, findings)."""
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, _research_competitor, client, competitor, compare_description, context
    )
    return competitor, result


# ---------------------------------------------------------------------------
# Synthesis: one call to produce the final comparison report
# ---------------------------------------------------------------------------

SYNTHESIS_SYSTEM = [
    {
        "type": "text",
        "text": """\
You are a competitive intelligence analyst. You will receive research \
reports for multiple competitors and produce a single comparison report \
as clean Markdown.

## Rules
- Only use facts from the research provided. Do not invent claims.
- Note confidence: if something appears in multiple sources say "confirmed", \
  single source say "reported", if you're inferring say "inferred".
- Be honest about gaps — if data is missing for a competitor, say so.
- Include source URLs inline as markdown links.""",
        "cache_control": {"type": "ephemeral"},
    }
]


def _synthesize(
    client: anthropic.Anthropic,
    your_company: str,
    compare_description: str,
    research_reports: List[tuple[str, str]],
    context: str,
) -> str:
    competitors = [name for name, _ in research_reports]
    reports_block = "\n\n---\n\n".join(
        f"## {name}\n\n{findings}" for name, findings in research_reports
    )
    context_block = f"\nAbout {your_company}: {context}\n" if context else ""

    prompt = f"""Compare {len(competitors)} competitors to **{your_company}**: {', '.join(competitors)}.
{context_block}
## Comparison focus
{compare_description}

## Research data

{reports_block}

---

Produce a Markdown report with these sections:

# Competitive Landscape: {your_company} vs {', '.join(competitors)}
Date and overview.

## Executive Summary
2-3 paragraphs on the competitive landscape.

## Head-to-Head Comparison
Markdown table. Columns: Dimension | {' | '.join(competitors)} | {your_company} Advantage

## Competitor Profiles
Per competitor: positioning, strengths, weaknesses, recent moves, pricing.

## Where We Win
Advantages with proof points.

## Where We're Vulnerable
Honest gaps — which competitors and what to avoid.

## Recommended Battleplan
Top talking points, trap questions per competitor, objection responses.

## Intel Gaps
What needs follow-up.

## Sources
All URLs from the research.

Return ONLY the Markdown."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYNTHESIS_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        thinking={"type": "adaptive"},
    )

    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            return block.text
    return ""


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def _build_pdf(md: str, out_path: Path) -> None:
    from fpdf import FPDF

    PURPLE = (124, 58, 237)
    DARK_BG = (15, 15, 17)
    MUTED = (136, 136, 136)
    WHITE = (255, 255, 255)
    BORDER = (42, 42, 48)

    EMOJI_MAP = {
        "\u2705": "[OK]", "\u26a0\ufe0f": "[~]", "\U0001f52e": "[?]",
        "\U0001f195": "[NEW]", "\U0001f4dd": "[UPD]", "\U0001f570\ufe0f": "[OLD]",
        "\u2b06\ufe0f": "[UP]", "\u2b07\ufe0f": "[DN]", "\U0001f504": ">>",
        "\u26a0": "[!]",
    }

    def strip_emoji(text: str) -> str:
        for emoji, repl in EMOJI_MAP.items():
            text = text.replace(emoji, repl)
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def inline_strip(text: str) -> str:
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)
        text = re.sub(r"`(.+?)`", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        return text.strip()

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(*DARK_BG)
            self.rect(0, 0, 210, 14, "F")
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(*PURPLE)
            self.set_xy(8, 4)
            self.cell(0, 6, "COMPETITIVE LANDSCAPE REPORT", ln=0)
            self.set_text_color(*MUTED)
            self.set_font("Helvetica", "", 7)
            self.set_xy(0, 4)
            self.cell(200, 6, f"Generated {datetime.utcnow().strftime('%Y-%m-%d')}", align="R")

        def footer(self):
            self.set_y(-10)
            self.set_font("Helvetica", "", 7)
            self.set_text_color(*MUTED)
            self.cell(0, 6, f"Page {self.page_no()} -- Competitive Intel", align="C")

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(14, 18, 14)
    pdf.add_page()
    pdf.set_fill_color(*WHITE)

    for raw_line in md.splitlines():
        line = strip_emoji(raw_line)

        if line.startswith("# "):
            pdf.ln(2)
            pdf.set_fill_color(*PURPLE)
            pdf.rect(14, pdf.get_y(), 4, 10, "F")
            pdf.set_x(20)
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*DARK_BG)
            pdf.multi_cell(0, 10, inline_strip(line[2:]), ln=1)
            pdf.ln(2)

        elif line.startswith("## "):
            pdf.ln(3)
            pdf.set_fill_color(*DARK_BG)
            pdf.rect(14, pdf.get_y(), 182, 8, "F")
            pdf.set_x(14)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*PURPLE)
            pdf.cell(0, 8, inline_strip(line[3:]).upper(), ln=1)
            pdf.ln(1)

        elif line.startswith("### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*DARK_BG)
            pdf.cell(0, 7, inline_strip(line[4:]), ln=1)

        elif line.startswith("---"):
            pdf.set_draw_color(*BORDER)
            pdf.set_line_width(0.3)
            pdf.line(14, pdf.get_y(), 196, pdf.get_y())
            pdf.ln(4)

        elif re.match(r"^\|[-| ]+\|$", line):
            pass

        elif line.startswith("|") and line.endswith("|"):
            cells = [inline_strip(c.strip()) for c in line.strip("|").split("|")]
            col_w = 182 / max(len(cells), 1)
            is_header = all(c == c.upper() or len(c) < 3 for c in cells[:1])
            if is_header:
                pdf.set_fill_color(*DARK_BG)
                pdf.set_font("Helvetica", "B", 7)
                pdf.set_text_color(*PURPLE)
            else:
                pdf.set_font("Helvetica", "", 7)
                pdf.set_text_color(*DARK_BG)
            pdf.set_x(14)
            for cell in cells:
                pdf.cell(col_w, 6, cell[:35], border=0, fill=is_header)
            pdf.ln(6)
            if not is_header:
                pdf.set_draw_color(*BORDER)
                pdf.set_line_width(0.1)
                pdf.line(14, pdf.get_y(), 196, pdf.get_y())

        elif line.startswith("- "):
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*DARK_BG)
            pdf.set_x(14)
            pdf.cell(4, 5, "-")
            pdf.set_x(19)
            pdf.multi_cell(173, 5, inline_strip(line[2:]), ln=1)
            pdf.ln(0.5)

        elif line.strip() == "":
            pdf.ln(2)

        elif line.startswith(">"):
            txt = inline_strip(line.lstrip("> "))
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*MUTED)
            pdf.set_x(18)
            pdf.multi_cell(174, 5, txt, ln=1)
            pdf.set_text_color(*DARK_BG)

        else:
            txt = inline_strip(line)
            if txt:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(*DARK_BG)
                pdf.multi_cell(0, 5, txt, ln=1)
            pdf.ln(0.5)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

async def _run(args: argparse.Namespace) -> None:
    your_company = args.your_company
    competitors = args.competitors
    compare = args.compare
    context = args.context or ""

    n = len(competitors)
    print(f"Researching {n} competitor(s) for {your_company!r}...", file=sys.stderr)
    print(f"  Competitors: {', '.join(competitors)}", file=sys.stderr)
    print(f"  Comparing: {compare}", file=sys.stderr)

    client = anthropic.Anthropic()

    # Phase 1: research all competitors in parallel (1 call each)
    print(f"  Phase 1: {n} research agents in parallel...", file=sys.stderr)
    tasks = [
        _async_research(client, comp, compare, context)
        for comp in competitors
    ]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    research_reports: List[tuple[str, str]] = []
    for comp, result in zip(competitors, raw_results):
        if isinstance(result, Exception):
            print(f"  [error] {comp}: {result}", file=sys.stderr)
        else:
            name, findings = result
            print(f"  {name}: {len(findings)} chars of research", file=sys.stderr)
            if findings:
                research_reports.append((name, findings))

    if not research_reports:
        print("No research completed. Exiting.", file=sys.stderr)
        sys.exit(1)

    # Phase 2: synthesize comparison (1 call)
    print(f"  Phase 2: synthesizing comparison...", file=sys.stderr)
    comparison_md = _synthesize(client, your_company, compare, research_reports, context)

    # Output paths
    if args.output:
        out_base = Path(args.output)
    else:
        slug = "_vs_".join(c.lower().replace(" ", "_") for c in competitors[:4])
        out_base = ROOT / "reports" / slug

    md_path = out_base.with_suffix(".md")
    pdf_path = out_base.with_suffix(".pdf")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(comparison_md, encoding="utf-8")
    print(f"\n  Markdown -> {md_path}", file=sys.stderr)

    print("  Building PDF...", file=sys.stderr)
    _build_pdf(comparison_md, pdf_path)
    print(f"  PDF      -> {pdf_path}", file=sys.stderr)

    print("\nDone.", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare N competitors with AI-powered research. Outputs Markdown + PDF.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("your_company", help="Your company name (e.g. 'Acme Corp')")
    parser.add_argument("competitors", nargs="+", help="Competitor names")
    parser.add_argument("--compare", "-d", required=True, help="What to compare")
    parser.add_argument("--context", "-c", default="", help="Optional company context")
    parser.add_argument("--output", "-o", help="Base output path (no extension)")

    args = parser.parse_args()
    anyio.run(_run, args)


if __name__ == "__main__":
    main()
