"""
Prompts for the newsletter draft agent.
"""

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


def build_user_prompt(
    past_issues: list[dict],
    notes: str,
    url_contents: list[dict],
    week_of: str,
) -> str:
    """Build the user prompt from all gathered inputs."""

    parts = [f"## Newsletter Draft Request — Week of {week_of}\n"]

    # Past issues for context/avoiding repeats
    if past_issues:
        parts.append("### Recent Issues (for context — don't repeat these angles)\n")
        for issue in past_issues[:5]:
            title = issue.get("title", "Untitled")
            pub = issue.get("published", "")[:10]
            summary = issue.get("summary", "")[:300]
            parts.append(f"**{title}** ({pub})\n{summary}\n")
        parts.append("")

    # This week's raw notes
    if notes.strip():
        parts.append("### My Notes & Observations This Week\n")
        parts.append(notes.strip())
        parts.append("")

    # Fetched URL content
    if url_contents:
        parts.append("### Saved Articles / Bookmarks\n")
        for item in url_contents:
            parts.append(f"**URL:** {item['url']}")
            parts.append(item["content"])
            parts.append("")

    parts.append(
        "---\nGenerate the newsletter draft outline with 3 angles as described. "
        "Be specific — vague angles are useless. Steal liberally from the notes above."
    )

    return "\n".join(parts)
