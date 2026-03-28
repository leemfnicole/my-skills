"""
Standalone entry point — run directly with: python3 draft.py [options]

Usage:
    python3 draft.py
    python3 draft.py --notes "Saw a lot of chatter about AI SDRs this week."
    python3 draft.py --notes "..." --urls https://example.com/article
    python3 draft.py --notes-file my_notes.txt
    python3 draft.py --notes "..." --output-dir ~/Desktop/drafts
"""

import argparse
import os
import re
import sys
from datetime import datetime, timezone

import anthropic
import feedparser
import httpx

RSS_FEED_URL = "https://amiamarketer.substack.com/feed"
MODEL = "claude-opus-4-6"

SYSTEM_PROMPT = """You are a sharp editorial assistant helping a B2B marketing operator prep their weekly newsletter draft.

The newsletter is "Am I a Marketer?" — written for marketers who are honest about the chaos,
contradictions, and occasional absurdity of the job. The voice is direct, occasionally self-deprecating,
intellectually curious, and never corporate-speak. It respects the reader's intelligence.

Your job is to turn raw input — notes, bookmarks, articles, observations from the week — into a
structured draft that the writer can edit in the morning instead of staring at a blank doc.

When generating the draft outline, always produce exactly THREE distinct angles. Each angle should:
- Have a working headline (punchy, honest, not clickbait)
- Explain the core argument or observation in 2-3 sentences
- Include 3-5 bullet points for section ideas, examples, or questions to explore
- Note the emotional tone (e.g., "rant", "how-to", "reflection", "provocation", "case study")
- Flag any gaps where the writer needs to add their own experience or find a stat

After the three angles, add a short "Editor's Note" (2-3 sentences) picking which angle seems strongest
given the week's inputs and why — but make clear the writer should ignore this if their gut says otherwise."""


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    for old, new in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                     ("&nbsp;", " "), ("&#39;", "'"), ("&quot;", '"'), ("&#8217;", "'")]:
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()


def fetch_rss(url: str, max_items: int = 6) -> list[dict]:
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries[:max_items]:
        summary = ""
        if hasattr(entry, "content") and entry.content:
            summary = entry.content[0].get("value", "")
        elif hasattr(entry, "summary"):
            summary = entry.summary
        items.append({
            "title": getattr(entry, "title", ""),
            "published": getattr(entry, "published", "")[:10],
            "summary": strip_html(summary)[:1200],
        })
    return items


def fetch_url(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; newsletter-agent/1.0)"}
        resp = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        resp.raise_for_status()
        text = strip_html(resp.text)
        return re.sub(r"\s+", " ", text).strip()[:2000]
    except Exception as exc:
        return f"[Could not fetch {url}: {exc}]"


def build_prompt(past_issues: list[dict], notes: str, url_contents: list[dict], week_of: str) -> str:
    parts = [f"## Newsletter Draft Request — Week of {week_of}\n"]

    if past_issues:
        parts.append("### Recent Issues (for context — don't repeat these angles)\n")
        for issue in past_issues[:5]:
            parts.append(f"**{issue['title']}** ({issue['published']})\n{issue['summary'][:300]}\n")
        parts.append("")

    if notes.strip():
        parts.append("### My Notes & Observations This Week\n")
        parts.append(notes.strip())
        parts.append("")

    if url_contents:
        parts.append("### Saved Articles / Bookmarks\n")
        for item in url_contents:
            parts.append(f"**URL:** {item['url']}\n{item['content']}\n")

    parts.append(
        "---\nGenerate the newsletter draft outline with 3 angles as described. "
        "Be specific — vague angles are useless. Steal liberally from the notes above."
    )
    return "\n".join(parts)


def generate_draft(notes: str, urls: list[str], rss_url: str) -> str:
    print("  Fetching past issues from RSS...", file=sys.stderr)
    try:
        past_issues = fetch_rss(rss_url)
        print(f"  Got {len(past_issues)} past issues.", file=sys.stderr)
    except Exception as exc:
        print(f"  Warning: RSS fetch failed: {exc}", file=sys.stderr)
        past_issues = []

    url_contents = []
    if urls:
        print(f"  Fetching {len(urls)} URL(s)...", file=sys.stderr)
        for url in urls:
            url_contents.append({"url": url, "content": fetch_url(url)})

    week_of = datetime.now(timezone.utc).strftime("%B %d, %Y")
    prompt = build_prompt(past_issues, notes, url_contents, week_of)

    print("  Drafting outline with Claude...\n", file=sys.stderr)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("\nError: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print("Export it before running:", file=sys.stderr)
        print("  export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    chunks = []
    with client.messages.stream(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            chunks.append(text)
            print(text, end="", flush=True)

    print("\n", file=sys.stderr)
    return "".join(chunks)


def save_draft(draft: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    date_slug = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{date_slug}-newsletter-draft.md")
    header = (
        f"# Newsletter Draft — {datetime.now().strftime('%B %d, %Y')}\n\n"
        "_Generated by newsletter-draft-agent. Edit freely._\n\n---\n\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(header + draft)
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Generate a weekly newsletter draft outline with 3 angles.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--notes", "-n", default="",
                        help="Free-form notes and observations from this week.")
    parser.add_argument("--notes-file", "-f", default=None,
                        help="Path to a text file with your weekly notes.")
    parser.add_argument("--urls", "-u", nargs="*", default=[],
                        help="URLs of articles or bookmarks to include.")
    parser.add_argument("--output-dir", "-o", default="drafts",
                        help="Directory to save the draft (default: ./drafts).")
    parser.add_argument("--no-save", action="store_true",
                        help="Print draft to stdout only, don't save.")
    parser.add_argument("--rss", default=RSS_FEED_URL,
                        help="RSS feed URL for past issues.")

    args = parser.parse_args()

    notes = args.notes
    if args.notes_file:
        path = args.notes_file
        if not os.path.exists(path):
            print(f"Error: notes file not found: {path}", file=sys.stderr)
            sys.exit(1)
        file_notes = open(path, encoding="utf-8").read()
        notes = f"{notes}\n\n{file_notes}".strip() if notes else file_notes

    print("\nNewsletter Draft Agent", file=sys.stderr)
    print("=" * 40, file=sys.stderr)

    draft = generate_draft(notes=notes, urls=args.urls or [], rss_url=args.rss)

    if args.no_save:
        print(draft)
    else:
        filepath = save_draft(draft, output_dir=args.output_dir)
        print(f"Draft saved to: {filepath}", file=sys.stderr)
        print(f"Open with:      open '{filepath}'", file=sys.stderr)


if __name__ == "__main__":
    main()
