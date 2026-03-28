"""
RSS and URL fetching utilities.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import feedparser
import httpx


def fetch_rss_feed(feed_url: str, max_items: int = 6) -> list[dict]:
    """
    Fetch recent items from an RSS feed.
    Returns a list of dicts with title, published, summary, link.
    """
    feed = feedparser.parse(feed_url)
    items = []
    for entry in feed.entries[:max_items]:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        # Strip HTML tags from summary/content
        summary = ""
        if hasattr(entry, "content") and entry.content:
            summary = entry.content[0].get("value", "")
        elif hasattr(entry, "summary"):
            summary = entry.summary

        summary = _strip_html(summary)[:1200]  # keep it lean

        items.append(
            {
                "title": getattr(entry, "title", ""),
                "published": published.isoformat() if published else "",
                "summary": summary,
                "link": getattr(entry, "link", ""),
            }
        )
    return items


def fetch_url_content(url: str, timeout: float = 10.0) -> str:
    """
    Fetch plain text content from a URL (basic extraction).
    Returns up to 2000 chars of visible text.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; newsletter-agent/1.0)"}
        resp = httpx.get(url, headers=headers, timeout=timeout, follow_redirects=True)
        resp.raise_for_status()
        text = _strip_html(resp.text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text[:2000]
    except Exception as exc:
        return f"[Could not fetch {url}: {exc}]"


def _strip_html(html: str) -> str:
    """Remove HTML tags and decode common entities."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&#39;", "'").replace("&quot;", '"')
    text = re.sub(r"\s+", " ", text).strip()
    return text
