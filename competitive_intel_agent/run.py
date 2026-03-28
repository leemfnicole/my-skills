"""
CLI entry point for the Competitive Intelligence Agent.

Usage:
    python -m competitive_intel_agent.run "Notion" "Coda"
    python -m competitive_intel_agent.run "HubSpot" "Attio" --context "We focus on PLG companies"
    python -m competitive_intel_agent.run "Gong" "Chorus" --output gong_vs_chorus.md
    python -m competitive_intel_agent.run "Salesforce" "Pipedrive" --format json --output sf.json
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

import anyio

from .agent import build_battlecard, update_battlecard_from_file
from .formatter import to_markdown


def _json_path_for(output: Optional[str], competitor: str) -> Path:
    """Return the canonical .json path that persists the battlecard between runs."""
    if output:
        base = Path(output).with_suffix("")
    else:
        slug = competitor.lower().replace(" ", "_")
        base = Path(f"battlecards/{slug}")
    return base.with_suffix(".json")


async def _run(args: argparse.Namespace) -> None:
    mode = "update" if args.update else "first run"
    print(
        f"🔍  Researching {args.competitor!r} for {args.your_company!r} ({mode})...",
        file=sys.stderr,
    )
    print(
        "     Running 3 research agents in parallel "
        "(G2 reviews · website · news)...",
        file=sys.stderr,
    )

    json_path = _json_path_for(args.output, args.competitor)

    try:
        if args.update:
            card, saved_json = await update_battlecard_from_file(
                json_path=json_path,
                competitor=args.competitor,
                your_company=args.your_company,
                your_context=args.context or None,
            )
        else:
            card, saved_json = await build_battlecard(
                competitor=args.competitor,
                your_company=args.your_company,
                your_context=args.context or None,
            )
    except ValueError as exc:
        print(f"\n❌  Schema validation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Summary to stderr
    summary = card.confidence_summary()
    cl = card.latest_changelog

    print(f"\n✅  Battlecard {'updated' if args.update else 'built'} successfully!", file=sys.stderr)
    print(f"     Sources consulted : {len(card.sources_consulted)}", file=sys.stderr)
    print(
        f"     Claim breakdown   : "
        f"{summary['confirmed']} confirmed · "
        f"{summary['reported']} reported · "
        f"{summary['inferred']} inferred",
        file=sys.stderr,
    )
    if cl and args.update:
        print(f"     Changes this run  : {cl.new_claims} new · {cl.stale_claims} stale · "
              f"{cl.confidence_upgrades} upgraded · {cl.confidence_downgrades} downgraded",
              file=sys.stderr)
    if card.intel_gaps:
        print(f"     ⚠️  Intel gaps      : {len(card.intel_gaps)} need verification", file=sys.stderr)

    # Always save JSON (source of truth for future --update runs)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(saved_json, encoding="utf-8")
    print(f"     JSON saved to     : {json_path}", file=sys.stderr)

    # Format markdown/json output
    if args.format == "json":
        output = saved_json
    else:
        output = to_markdown(card)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"💾  Markdown saved to  : {out_path}", file=sys.stderr)
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a source-verified competitive battlecard using AI agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("competitor",   help="Competitor name  (e.g. 'Notion')")
    parser.add_argument("your_company", help="Your company name (e.g. 'Coda')")
    parser.add_argument(
        "--context", "-c",
        help="Optional context about your product, ICP, or known competitive angles.",
        default="",
    )
    parser.add_argument(
        "--output", "-o",
        help="File to write output to (default: stdout).",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown).",
    )
    parser.add_argument(
        "--update", "-u",
        action="store_true",
        help="Load existing battlecard JSON and merge new research into it (weekly update mode).",
    )

    args = parser.parse_args()
    anyio.run(_run, args)


if __name__ == "__main__":
    main()
