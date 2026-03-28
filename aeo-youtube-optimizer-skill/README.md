# AEO YouTube Optimizer

Optimize YouTube videos for AI engine citations. Pulls video metadata and transcripts via Apify, checks AI Overview presence via Ahrefs, analyzes citation-winning patterns via Firecrawl, and produces optimized titles, descriptions, chapters, transcript highlights, and pinned comments. Saves everything to Notion.

## Required MCP Servers

This skill requires four MCP servers to be configured in your Claude Code environment:

| MCP Server | Purpose | Setup |
|------------|---------|-------|
| **Apify** | Pulls YouTube video metadata (title, views, description) and full timestamped transcripts via YouTube Scraper and Transcript Scraper actors | [apify.com](https://apify.com) - requires API token |
| **Firecrawl** | Scrapes cited video descriptions and searches for non-video citation content | [firecrawl.dev](https://firecrawl.dev) - requires API key |
| **Ahrefs** | Runs SERP overviews to identify YouTube videos in AI Overviews and top search positions | Requires Ahrefs API key with SERP overview access |
| **Notion** | Saves the complete optimization package as a structured, shareable Notion page | [Notion API](https://developers.notion.com/) - requires integration token |

## Notion Setup

### 1. Create a Parent Page

Create a Notion page where optimization reports will be saved as child pages. This can be any page in your workspace, for example "YouTube AEO Optimizations" or "Video Optimization Reports".

### 2. Find Your Page ID

1. Open the parent page in Notion
2. Click **Share** in the top right
3. Click **Copy link**
4. Extract the 32-character ID from the URL

The URL format is: `https://www.notion.so/Your-Page-Title-[PAGE_ID]`

The page ID is the last 32 characters. Format it with dashes as: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### 3. Connect Your Notion Integration

Make sure your Notion integration (the one whose token you configured for the MCP server) has access to the parent page. In Notion, go to the parent page, click the three-dot menu, select **Connections**, and add your integration.

## Quick Start

```
Optimize this video for AI citations: https://www.youtube.com/watch?v=abc123
Target queries: "what is product-led growth", "PLG examples"
Save to Notion page 2fd385b8-cf47-8008-a04b-f3562b0dbe87
```

That single prompt will:
1. Pull video metadata and full transcript via Apify
2. Search for competitor videos on the same topic
3. Check Ahrefs SERP data for YouTube videos in AI Overviews
4. Analyze citation-winning patterns across description structure, titles, and chapters
5. Identify the top quotable moments from the transcript
6. Generate 5-7 optimized title options with rationale
7. Produce an optimized description, chapter markers, and pinned comment
8. Evaluate the first 30 seconds and rewrite if needed
9. Save everything to your Notion page

For pre-production research (no video yet), use a keyword instead:

```
keyword: how to reduce customer churn
Save to Notion page 2fd385b8-cf47-8008-a04b-f3562b0dbe87
```

## What the Output Looks Like

The skill creates a Notion page with the following structure:

- **Header Callout** - Purple header with video title (or keyword), target queries, and date
- **Citation Landscape** - Which YouTube videos currently appear in AI answers for the target queries, with commonalities noted
- **Competitive Analysis Table** - Top 10 competitor videos with columns for description structure, chapter presence, and whether they are cited in AI results
- **Transcript Analysis** - Quotable moments table (timestamp, exact quote, why citable, suggested use) and first-30-seconds evaluation with a strong/moderate/weak score
- **Title Options Table** - 5-7 options with character counts, pattern types, rationale, and a green callout highlighting the recommended pick
- **Optimized Description** - Full description in a code block, ready to copy into YouTube
- **Chapter Markers** - Question-format timestamps in a code block, ready to copy
- **First 30 Seconds Script** - Rewritten intro in a code block (included only when the evaluation scored moderate or weak)
- **Pinned Comment Draft** - Under-500-character comment in a code block, ready to copy
- **Implementation Checklist** - Step-by-step action items for applying the optimizations

## Files

```
aeo-youtube-optimizer/
├── SKILL.md           # Full skill definition with phased execution
├── sample_prompt.md   # Example prompts for common use cases
└── README.md          # This file
```

See `sample_prompt.md` for detailed usage examples including existing-video optimization, pre-production keyword research, comparison videos, and batch optimization.
