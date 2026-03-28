"""
CLI entry point for the Newsletter Draft Agent.

Usage:
    python -m newsletter_draft_agent.run
    python -m newsletter_draft_agent.run --notes "Saw a lot of chatter about AI SDRs this week. Feels like everyone is lying to themselves about pipeline."
    python -m newsletter_draft_agent.run --urls https://example.com/article1 https://example.com/article2
    python -m newsletter_draft_agent.run --notes "..." --urls https://... --output-dir ~/drafts
    python -m newsletter_draft_agent.run --notes-file my_notes.txt --urls https://...
"""

import argparse
import sys
from pathlib import Path

from .agent import generate_newsletter_draft, save_draft


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a weekly newsletter draft outline with 3 angles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--notes", "-n",
        default="",
        help="Free-form notes, observations, and half-formed ideas from this week.",
    )
    parser.add_argument(
        "--notes-file", "-f",
        default=None,
        help="Path to a text file containing your weekly notes (alternative to --notes).",
    )
    parser.add_argument(
        "--urls", "-u",
        nargs="*",
        default=[],
        help="URLs of articles, tweets, or bookmarks to pull into the draft.",
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="drafts",
        help="Directory to save the draft markdown file (default: ./drafts).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Print draft to stdout only, don't save to file.",
    )
    parser.add_argument(
        "--rss",
        default="https://amiamarketer.substack.com/feed",
        help="RSS feed URL to pull past issues from (default: amiamarketer.substack.com).",
    )

    args = parser.parse_args()

    # Resolve notes
    notes = args.notes
    if args.notes_file:
        notes_path = Path(args.notes_file)
        if not notes_path.exists():
            print(f"Error: notes file not found: {notes_path}", file=sys.stderr)
            sys.exit(1)
        file_notes = notes_path.read_text(encoding="utf-8")
        notes = f"{notes}\n\n{file_notes}".strip() if notes else file_notes

    print("Newsletter Draft Agent", file=sys.stderr)
    print("=" * 40, file=sys.stderr)

    draft = generate_newsletter_draft(
        notes=notes,
        urls=args.urls or [],
        rss_url=args.rss,
        verbose=True,
    )

    if args.no_save:
        print(draft)
    else:
        filepath = save_draft(draft, output_dir=args.output_dir)
        print(f"\nDraft saved to: {filepath}", file=sys.stderr)
        print(f"\nOpen and edit: open '{filepath}'", file=sys.stderr)


if __name__ == "__main__":
    main()
