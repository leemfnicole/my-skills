---
name: aeo-youtube-optimizer
description: Optimize a YouTube video for AI engine citations using Apify to pull video metadata and transcripts, Ahrefs for SERP/AI Overview analysis, Firecrawl for citation research, and Notion for output. Produces optimized titles, description, chapters, transcript highlights, and pinned comment based on what's actually getting cited.
---

# AEO YouTube Optimizer

AI engines increasingly cite YouTube videos, especially transcripts and descriptions. When ChatGPT, Perplexity, or Google AI Overviews answer a question, they can pull direct quotes from video transcripts, reference specific timestamps, and cite description summaries. This skill pulls actual video data via Apify, researches what content is currently earning citations for your target queries, and produces optimized assets backed by evidence: titles, description, chapters, transcript highlights, and a pinned comment.

> "AI engines can extract quotes from transcripts, reference specific timestamps, and cite descriptions. This skill optimizes all three surfaces based on what's currently winning citations."

## Capabilities

- Pull video metadata (title, views, description, duration, likes) via Apify YouTube Scraper
- Extract full transcript with timestamps via Apify YouTube Transcript Scraper
- Search and analyze competitor videos for any target query via Apify keyword search
- Check AI Overview presence for target queries via Ahrefs SERP overview
- Analyze citation-winning patterns across top-ranking YouTube content
- Produce 5-7 optimized title options with rationale and competitive modeling
- Generate an optimized description with citation hooks, structured summary, and timestamps
- Create question-format chapter markers aligned with SERP queries
- Identify the top quotable transcript moments with timestamps and citation reasoning
- Evaluate and rewrite the first 30 seconds if the current intro is weak
- Draft a pinned comment reinforcing the key citable answer
- Save the complete optimization package to a Notion page

## How to Use

Provide a YouTube video URL (or a keyword for pre-production research), target queries, and a Notion page ID:

- `Optimize this video for AI citations: https://www.youtube.com/watch?v=abc123. Target queries: "what is product-led growth", "PLG examples". Save to Notion page 2fd385b8-cf47-8008-a04b-f3562b0dbe87`
- `Run an AEO YouTube audit on https://www.youtube.com/watch?v=xyz789. I want it cited when people ask "best CRM for startups". Channel focuses on SaaS reviews. Notion page: 1a2b3c4d-5e6f-7890-abcd-ef1234567890`
- `I'm planning a video on "how to reduce customer churn". Use keyword: how to reduce customer churn. Research what's getting cited and give me the full optimization package. Notion page: abc123def456`

## Input Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| YouTube video URL | Yes | - | The video to optimize, OR use "keyword: [query]" for pre-production research |
| Target queries | No | Inferred from video title and description | 1-5 questions the video should answer in AI engines |
| Channel context | No | - | Channel topic, audience, creator credentials for authority positioning |
| Notion parent page | Yes | - | Page ID where the optimization output will be saved |

## Output

A Notion page saved under the provided parent page containing:
- Citation landscape analysis (which YouTube videos appear in AI answers today)
- Competitive analysis table with description structure and chapter patterns
- Transcript analysis with quotable moments and first-30-seconds evaluation
- 5-7 optimized title options with character counts, patterns, and rationale
- Optimized description with citation hooks (ready to copy)
- Question-format chapter markers (ready to copy)
- First-30-seconds script rewrite (if needed)
- Pinned comment draft (ready to copy)
- Implementation checklist

---

## Phase 1: Pull Video Data + Research

Run Tracks A through E in parallel. If target queries are not provided, first extract them from the video title and description returned by Track A, then run Tracks D and E.

### Track A: Pull Video Metadata

Use the Apify YouTube Scraper to get full metadata for the target video:

```
mcp__apify__apidojo-slash-youtube-scraper(
  startUrls: ["https://www.youtube.com/watch?v=[VIDEO_ID]"],
  maxItems: 1,
  gl: "us",
  hl: "en"
)
```

Extract: title, channel name, view count, like count, upload date, duration, description, comment count.

If the input is a keyword instead of a URL (pre-production mode), skip Track A and Track B. Use the keyword directly for Tracks C, D, and E.

### Track B: Pull Full Transcript

Use the Apify YouTube Transcript Scraper to get timestamped transcript:

```
mcp__apify__topaz_sharingan-slash-Youtube-Transcript-Scraper-1(
  startUrls: [
    "https://www.youtube.com/watch?v=[VIDEO_ID]"
  ],
  timestamps: true
)
```

This returns the full spoken content with timestamps for each segment. Store the complete transcript for Phase 3 analysis.

### Track C: Competitor Video Research

Search for competitor videos using the target query keywords:

```
mcp__apify__apidojo-slash-youtube-scraper(
  keywords: ["[target query]"],
  sort: "v",
  uploadDate: "y",
  maxItems: 10,
  gl: "us",
  hl: "en"
)
```

If fewer than 5 results, broaden with related keyword variations (e.g., "[query] tutorial", "[query] explained", "[query] guide").

For each competitor video, capture: title, channel, view count, duration, description, upload date.

### Track D: Ahrefs SERP Analysis for AI Overviews

For each target query, check whether YouTube videos appear in AI Overviews:

```json
mcp__claude_ai_Ahrefs__serp-overview({
  "keyword": "[target query]",
  "country": "us",
  "select": "position,url,title,type,traffic,domain_rating",
  "top_positions": 10
})
```

From the results, identify:
- Which positions contain YouTube URLs
- Which YouTube videos are cited in AI Overview results (type containing "ai_overview" or "video")
- The title and description patterns of cited videos
- Domain ratings of pages that outrank video results

Run this for each target query (up to 5 queries).

### Track E: Non-Video Citation Research

Search for non-video content getting cited for the target queries:

```
firecrawl_search(query: "[target query]", limit: 10)
```

This reveals what text-based content is winning citations, informing how the video description and transcript should be structured to compete.

### Fallback: Target Query Inference

If target queries were not provided by the user:
1. Wait for Track A to return video metadata
2. Extract candidate queries from the video title and description
3. Formulate 2-4 question-format queries (e.g., "what is [topic]", "how to [topic]", "[topic] vs [alternative]")
4. Then run Tracks D and E with the inferred queries

### Fallback: Transcript Scraper Failure

If the Apify transcript scraper returns empty or errors:
1. Try scraping the YouTube page directly via Firecrawl:
```
firecrawl_scrape(url: "https://www.youtube.com/watch?v=[VIDEO_ID]", formats: ["markdown"])
```
2. If Firecrawl also fails, note in the output that transcript analysis was unavailable
3. Proceed with metadata-only optimization (Phases 4 and 5 can still produce titles, description, chapters, and pinned comment based on the video description and competitor analysis)

---

## Phase 2: Analyze Citation Winners

### Step 2a: Identify Cited YouTube Videos

From the Ahrefs SERP data (Track D), collect every YouTube URL that appears in the top 10 results or AI Overview sections. These are the citation winners for the target queries.

### Step 2b: Scrape Citation Winner Descriptions

For each cited YouTube video (up to 5), scrape the page to get the full description:

```
firecrawl_scrape(url: "https://www.youtube.com/watch?v=[CITED_VIDEO_ID]", formats: ["markdown"])
```

### Step 2c: Build Citation Pattern Profile

Compare the cited videos against non-cited competitors. Document patterns across:

- **Title structure:** Question-format? Number-based? "Best X for Y"? "X vs Y"? Character length?
- **Description format:** Where is the summary placed? How are timestamps formatted? What links are included? Is there a "key takeaway" section?
- **Chapter patterns:** Do cited videos use chapters? Are they phrased as questions or topic labels?
- **First-30-seconds content:** Do cited videos answer the query immediately, or do they have long intros?
- **Authority signals:** Do descriptions cite sources, mention credentials, or include data?

Summarize into a "Citation Pattern Profile" with specific, actionable patterns to replicate.

---

## Phase 3: Transcript Analysis

Skip this phase if running in pre-production mode (keyword input instead of video URL) or if the transcript was unavailable.

### Step 3a: Quotable Moments

Scan the full transcript for moments that AI engines would extract as citations. Look for:

- **Definitive statements:** "X is the best approach for Y because..."
- **Statistics or data points:** "According to [source], 73% of..."
- **Clear explanations:** Concise definitions or step-by-step breakdowns
- **Unique insights:** Original frameworks, coined terms, or proprietary findings

For each quotable moment, capture:
- Timestamp
- Exact quote (verbatim from transcript)
- Why it is citable (what makes it extractable by an AI engine)

### Step 3b: First 30 Seconds Evaluation

Evaluate the current video intro against these criteria:

1. Does it state the question being answered? (Yes/No)
2. Does it give the direct answer within 30 seconds? (Yes/No)
3. Does it establish the speaker's credibility? (Yes/No)
4. Does it preview the rest of the content? (Yes/No)

**Score:**
- **Strong (3-4 criteria met):** No rewrite needed. Note strengths.
- **Moderate (2 criteria met):** Rewrite recommended. Note what is missing.
- **Weak (0-1 criteria met):** Rewrite required. Flag as high priority.

### Step 3c: Natural Chapter Breaks

Identify topic transitions in the transcript that align with related queries. For each break:
- Timestamp where the new topic begins
- What question this segment answers
- Related search queries that map to this segment

### Step 3d: Weak Spots

Flag sections that hurt citation potential:
- **Hedging language:** "I think maybe...", "It could possibly...", "This might work..."
- **Long tangents:** Sections that drift from the core query for more than 60 seconds
- **Filler content:** Repeated asks to subscribe, extended personal anecdotes without informational value
- **Unclear explanations:** Points that need tightening or restructuring for clarity

---

## Phase 4: Competitive Title/Description Analysis

### Step 4a: Title Pattern Analysis

From the top 10 competitor videos (Track C), categorize each title by pattern:

| Title | Channel | Views | Pattern | Length (chars) |
|-------|---------|-------|---------|----------------|
| [title] | [channel] | [views] | Question / Number / "Best X for Y" / "X vs Y" / How-to / Other | [count] |

Identify:
- Which patterns correlate with highest view counts
- Average title length of top performers
- Whether top performers use the exact query in the title

### Step 4b: Description Structure Analysis

For each competitor video with an accessible description (from Track C metadata or Firecrawl scrapes):

| Video | Summary Placement | Has Timestamps? | Timestamp Format | Links Included? | Key Takeaway Section? |
|-------|-------------------|-----------------|------------------|-----------------|-----------------------|
| [title] | First line / First paragraph / Below fold / None | Yes / No | Question-format / Topic labels / Timestamps only | Yes / No | Yes / No |

### Step 4c: Engagement Correlation

Note any observable correlation between description completeness and engagement metrics. Videos with structured descriptions and chapters tend to correlate with higher view counts, but flag this as observational rather than causal.

---

## Phase 5: Generate Optimized Assets

### 5A: Title Options (5-7)

Generate 5-7 title options. For each:

| # | Title | Chars | Pattern | Rationale | Modeled After |
|---|-------|-------|---------|-----------|---------------|
| 1 | [title text] | [count] | [pattern type] | [why this works for the query] | [competitor title or "original"] |
| 2 | [title text] | [count] | [pattern type] | [why this works] | [competitor reference] |

**Recommended pick:** Highlight the recommended title in a green callout with explanation of why it best balances citation potential, click-through rate, and query alignment.

Title rules:
- Preferred length: under 60 characters (displays fully in search and AI citations)
- Include the primary query or a close variant
- At least one question-format option
- At least one number-based option
- At least one "X vs Y" or comparison option if relevant to the topic

### 5B: Optimized Description

Structure the description in this order:

1. **Hook sentence:** One sentence that directly answers the primary query. This is the most likely line to be extracted by AI engines.
2. **Summary paragraph:** 2-3 sentences expanding on the answer with citation hooks. Citation hooks are standalone, quotable sentences that make factual claims or provide clear definitions.
3. **Timestamps/chapters:** Question-format chapter markers (see 5C below).
4. **Key takeaways:** 3-5 bullet points summarizing the main points. Each bullet should be independently citable.
5. **Links and resources:** Relevant links mentioned in the video.
6. **About section:** Brief channel/creator description with authority signals.

**Citation hook examples:**
- "Product-led growth is a business strategy where the product itself drives customer acquisition, conversion, and retention."
- "Companies using PLG grow 2x faster than sales-led competitors, according to OpenView's 2025 benchmark report."

Each citation hook should be a complete, standalone sentence that an AI engine could quote without additional context.

### 5C: Chapter Markers

Format chapters as questions aligned with SERP queries:

```
0:00 - What is [topic]? (The direct answer)
[M:SS] - Why does [topic] matter for [audience]?
[M:SS] - How do you [specific action]? (Step-by-step)
[M:SS] - What are the most common [topic] mistakes?
[M:SS] - [Topic] vs [alternative]: which is better?
[M:SS] - Key takeaways and next steps
```

Each chapter's opening sentence in the transcript (or recommended opening sentence) should be independently citable. Write a suggested opening line for each chapter that directly answers the chapter's question.

### 5D: Transcript Highlight Reel

Select the top 5 quotable moments from Phase 3 analysis:

| # | Timestamp | Quote | Why Citable | Suggested Use |
|---|-----------|-------|-------------|---------------|
| 1 | [M:SS] | "[exact quote]" | [definitive statement / statistic / clear explanation] | [description hook / pinned comment / social clip] |
| 2 | [M:SS] | "[exact quote]" | [reason] | [suggested use] |
| 3 | [M:SS] | "[exact quote]" | [reason] | [suggested use] |
| 4 | [M:SS] | "[exact quote]" | [reason] | [suggested use] |
| 5 | [M:SS] | "[exact quote]" | [reason] | [suggested use] |

If running in pre-production mode, skip this section.

### 5E: First 30 Seconds Script

If the first-30-seconds evaluation scored **weak** or **moderate** in Phase 3, provide a rewritten intro script.

The rewritten intro must:
1. State the question being answered (seconds 1-5)
2. Give the direct answer (seconds 5-15)
3. Establish credibility briefly (seconds 15-20)
4. Preview the rest of the content (seconds 20-30)

**Good example:**
> "What's the best CRM for startups in 2026? After testing 12 CRMs with my team over the past year, HubSpot's free tier is the clear winner for early-stage companies. I've built sales systems at three startups from zero to Series A, and I'll walk you through exactly why HubSpot wins, plus three alternatives depending on your specific needs."

**Bad example:**
> "Hey everyone, welcome back to the channel! Before we get started, make sure to like and subscribe. Today we're going to be talking about something I get asked a lot, which is CRMs. So let's get into it."

If the evaluation scored **strong**, note this and skip the rewrite.

### 5F: Pinned Comment Draft

Draft a pinned comment that:
- Restates the key answer from the video in 1-2 sentences
- Adds one supporting detail or statistic
- Asks an engagement question related to the topic
- Keeps the total length under 500 characters

The pinned comment serves as an additional citation surface. AI engines can extract text from pinned comments, so the first sentence should be the most citable statement from the video.

---

## Phase 6: Save to Notion

Use `mcp__notion__notion-create-pages` to save the full optimization package:

```json
{
  "parent": {
    "page_id": "[USER_PROVIDED_PAGE_ID]"
  },
  "pages": [
    {
      "properties": {
        "title": "AEO YouTube Optimizer: [Video Title or Keyword] - [Date]"
      },
      "content": "[Notion-flavored Markdown below]"
    }
  ]
}
```

### Notion Page Content Template

```markdown
<callout icon="🎬" color="purple_bg">
	**AEO YouTube Optimization**
	**Video:** [video title or "Pre-Production: [keyword]"]
	**Target Queries:** [query 1], [query 2], [query 3]
	**Date:** [today's date]
</callout>

---

## Citation Landscape

Which YouTube videos currently appear in AI answers for the target queries, and what they have in common.

[For each target query, list the YouTube URLs found in SERP top 10 or AI Overviews. Note commonalities: title patterns, description structures, whether they use chapters.]

<callout icon="🔍" color="blue_bg">
	**Key Finding:** [1-2 sentence summary of the citation landscape, e.g., "3 of 5 target queries show YouTube videos in AI Overviews. All cited videos use question-format titles and structured descriptions with timestamps."]
</callout>

---

## Competitive Analysis

<table header-row="true">
	<tr>
		<td>**Video Title**</td>
		<td>**Channel**</td>
		<td>**Views**</td>
		<td>**Description Structure**</td>
		<td>**Chapters?**</td>
		<td>**Cited in AI?**</td>
	</tr>
	<tr>
		<td>[title]</td>
		<td>[channel]</td>
		<td>[views]</td>
		<td>[summary first / timestamps / links / minimal]</td>
		<td>[Yes (question-format) / Yes (topic labels) / No]</td>
		<td>[Yes (query) / No]</td>
	</tr>
</table>

---

## Transcript Analysis

### Quotable Moments

<table header-row="true">
	<tr>
		<td>**#**</td>
		<td>**Timestamp**</td>
		<td>**Quote**</td>
		<td>**Why Citable**</td>
		<td>**Suggested Use**</td>
	</tr>
	<tr>
		<td>1</td>
		<td>[M:SS]</td>
		<td>"[exact quote]"</td>
		<td>[reason]</td>
		<td>[use]</td>
	</tr>
</table>

### First 30 Seconds Evaluation

**Score:** [Strong / Moderate / Weak]
- States the question: [Yes / No]
- Gives direct answer: [Yes / No]
- Establishes credibility: [Yes / No]
- Previews content: [Yes / No]

[If moderate or weak, note what is missing and that a rewrite is provided below.]

---

## Title Options

<table header-row="true">
	<tr>
		<td>**#**</td>
		<td>**Title**</td>
		<td>**Chars**</td>
		<td>**Pattern**</td>
		<td>**Rationale**</td>
		<td>**Modeled After**</td>
	</tr>
	<tr>
		<td>1</td>
		<td>[title]</td>
		<td>[count]</td>
		<td>[pattern]</td>
		<td>[rationale]</td>
		<td>[reference]</td>
	</tr>
</table>

<callout icon="✅" color="green_bg">
	**Recommended Title:** [recommended title]
	**Why:** [2-3 sentence explanation of why this title best balances citation potential, CTR, and query alignment.]
</callout>

---

## Optimized Description

```
[Full optimized description, ready to copy-paste into YouTube. Includes hook sentence, summary paragraph, timestamps, key takeaways, links placeholder, and about section.]
```

---

## Chapter Markers

```
0:00 - [Question-format chapter 1]
[M:SS] - [Question-format chapter 2]
[M:SS] - [Question-format chapter 3]
[M:SS] - [Question-format chapter 4]
[M:SS] - [Question-format chapter 5]
[M:SS] - [Question-format chapter 6]
```

---

## First 30 Seconds Script

[Include only if the evaluation scored moderate or weak. Skip this section entirely if the intro scored strong.]

**Current intro issues:** [what is missing]

**Rewritten intro:**

```
[Full 30-second script, ready to use. Approximately 75-80 words.]
```

---

## Pinned Comment Draft

```
[Full pinned comment, under 500 characters. Restates key answer, adds supporting detail, asks engagement question.]
```

---

## Implementation Checklist

- [ ] Update video title to recommended option
- [ ] Replace description with optimized version
- [ ] Add chapter markers to description
- [ ] Record or re-record first 30 seconds (if rewrite provided)
- [ ] Pin the drafted comment
- [ ] Verify timestamps match actual video content
- [ ] Check that description displays correctly on mobile (first 2 lines visible)
- [ ] Re-run AEO audit in 30 days to measure citation improvement

---

<span color="gray">Generated by AEO YouTube Optimizer skill | [Date]</span>
```

**Notion Markdown Syntax Notes:**
- Callouts use `<callout icon="emoji" color="color_bg">` with content indented by a tab
- Background colors end in `_bg`: `green_bg`, `blue_bg`, `purple_bg`, `orange_bg`, `red_bg`
- Inline colors use `<span color="gray">text</span>`
- Use `---` for dividers between sections
- Use standard markdown for bold, links, lists, and tables
- Checkbox items use `- [ ]` for action items
- Code blocks with triple backticks for copy-paste ready content

---

## Writing Guidelines

1. **Titles under 60 characters preferred.** Longer titles get truncated in search results and AI citation displays. Every title option should include a character count.
2. **Descriptions front-load keywords.** The hook sentence and summary paragraph should contain the primary query and close variants within the first 150 characters, since that is what displays before the "Show more" fold.
3. **Chapters as questions.** Every chapter marker should be phrased as a question users would actually search. "What is [topic]?" and "How do you [action]?" outperform topic-label chapters like "Introduction" or "Overview" for AI extraction.
4. **Copy-paste sections in code blocks.** The optimized description, chapter markers, first-30-seconds script, and pinned comment must all be in code blocks so the user can copy them without formatting issues.
5. **No em dashes anywhere.** Use commas, periods, or semicolons instead.
6. **Write for both humans and AI extraction.** Every optimized asset should read naturally to a human viewer while also containing standalone, quotable sentences that AI engines can extract cleanly.

---

## Best Practices

1. **Run all five research tracks in parallel** to minimize total execution time. Tracks A through E are independent and should execute simultaneously.
2. **Use actual SERP data to drive recommendations.** Every title pattern, description structure, and chapter format recommendation should reference specific evidence from the Ahrefs SERP overview or competitor analysis.
3. **Let the citation winners lead.** If a specific description format or title pattern is shared by videos that already appear in AI Overviews, prioritize replicating that pattern.
4. **Score the first 30 seconds honestly.** A generous "strong" score that skips a needed rewrite is less valuable than an honest "moderate" with a concrete rewrite.
5. **Prioritize the hook sentence in the description.** AI engines disproportionately cite the first 1-2 sentences of a YouTube description. This single line may be the highest-impact optimization in the entire package.
6. **Include pre-production mode output for keyword inputs.** When no video URL is provided, the skill should still deliver title options, description template, chapter structure, and a first-30-seconds script based on competitive research.
7. **Flag when transcript data is missing.** If the transcript scraper fails, note this clearly in the output rather than silently omitting transcript-dependent sections.
8. **Keep the pinned comment under 500 characters.** Longer comments get collapsed on mobile, reducing their citation surface area.
9. **Validate chapter timestamps against the actual video.** Include a checklist reminder to verify that the suggested chapter timestamps match the real content transitions. Mismatched chapters hurt both user experience and citation accuracy.

---

## Limitations

- Apify YouTube Scraper may return limited results for very niche keywords; broaden search terms if fewer than 5 competitors are found
- Transcript scraper may fail for videos with disabled captions, auto-generated subtitles in non-English languages, or very recently uploaded videos
- Ahrefs SERP data is a point-in-time snapshot; AI Overview presence changes frequently as search engines update their models
- Cannot determine whether a specific video is actually being quoted inside an AI Overview response; can only confirm that YouTube URLs appear in the SERP data
- Firecrawl may not capture the full YouTube description if the page uses dynamic rendering or bot protection
- View counts and engagement metrics from Apify are snapshots and may shift after the analysis
- Pre-production mode (keyword input) cannot provide transcript analysis, quotable moments, or first-30-seconds evaluation since no video exists yet

---

## Quality Checklist

Before saving to Notion:

**Data Collection**
- [ ] Video metadata pulled from Apify (or noted as pre-production mode)
- [ ] Transcript pulled with timestamps (or fallback attempted and noted)
- [ ] At least 5 competitor videos found and analyzed
- [ ] Ahrefs SERP overview run for each target query

**Analysis**
- [ ] Citation pattern profile documents specific patterns from cited videos
- [ ] Competitive analysis table includes description structure and chapter presence
- [ ] Quotable moments identified with timestamps and citation reasoning (if transcript available)
- [ ] First-30-seconds evaluation completed with honest score and criteria

**Optimized Assets**
- [ ] 5-7 title options with character counts, patterns, and rationale; recommended pick highlighted
- [ ] Optimized description includes hook sentence, summary, timestamps, key takeaways
- [ ] Chapter markers in question-format aligned with SERP queries
- [ ] Pinned comment under 500 characters with citable opening sentence
- [ ] First-30-seconds rewrite provided if evaluation scored moderate or weak

**Notion Output**
- [ ] All sections populated: callout header, tables, code blocks, implementation checklist
- [ ] No em dashes anywhere in the document
