"""
Renders a Battlecard as readable Markdown.

Every claim is prefixed with a confidence emoji so sales reps can instantly
see which claims are safe to use vs. which need more digging.

  ✅ confirmed  = 2+ independent sources, safe to use in deals
  ⚠️  reported   = 1 source, use with a qualifier
  🔮 inferred   = LLM synthesis, do NOT use externally without validation
"""

from __future__ import annotations
from typing import List
from .battlecard import Battlecard, ChangeType, Confidence, SourcedClaim, WeeklyChangelog

_EMOJI = {
    Confidence.CONFIRMED: "✅",
    Confidence.REPORTED:  "⚠️",
    Confidence.INFERRED:  "🔮",
}


def _conf(c) -> str:
    key = Confidence(c) if isinstance(c, str) else c
    return _EMOJI.get(key, "❓")


def _source_link(sources: List[str]) -> str:
    if not sources:
        return ""
    return f" [[source]]({sources[0]})"


def _claim_line(claim: SourcedClaim, bullet: str = "-") -> str:
    src = _source_link(claim.sources)
    return f"{bullet} {_conf(claim.confidence)} {claim.claim}{src}"


_CHANGE_EMOJI = {
    ChangeType.ADDED:      "🆕",
    ChangeType.UPDATED:    "📝",
    ChangeType.STALE:      "🕰️",
    ChangeType.UPGRADED:   "⬆️",
    ChangeType.DOWNGRADED: "⬇️",
}


def _changelog_section(cl: WeeklyChangelog) -> List[str]:
    """Render the 'What changed this week' block at the top of the card."""
    if not cl.has_changes():
        return [
            "## 🔄 This Week's Update",
            "",
            f"*No significant changes detected on {cl.run_date.strftime('%Y-%m-%d')}. "
            f"{cl.sources_consulted} sources re-checked.*",
            "",
            "---\n",
        ]

    lines = [
        "## 🔄 What Changed This Week",
        f"*Run date: {cl.run_date.strftime('%Y-%m-%d')} · "
        f"{cl.sources_consulted} sources · "
        f"{cl.new_claims} new · {cl.stale_claims} stale · "
        f"{cl.confidence_upgrades} upgraded · {cl.confidence_downgrades} downgraded*",
        "",
    ]

    for entry in cl.entries:
        icon = _CHANGE_EMOJI.get(entry.change_type, "•")
        lines.append(f"- {icon} **{entry.change_type.value.upper()}** `{entry.field}` — {entry.summary}")

    lines += ["", "---\n"]
    return lines


def to_markdown(card: Battlecard) -> str:
    summary = card.confidence_summary()
    lines: List[str] = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        f"# Competitive Battlecard: {card.competitor}",
        f"*vs {card.your_company}  ·  "
        f"Last updated: {card.last_updated.strftime('%Y-%m-%d')}  ·  "
        f"Overall confidence: {_conf(card.overall_confidence)} {card.overall_confidence}*",
        "",
        "> **Confidence key**",
        "> - ✅ **Confirmed** — same claim in 2+ independent sources — safe to use in deals",
        "> - ⚠️ **Reported** — found in 1 source — use with a qualifier",
        "> - 🔮 **Inferred** — LLM synthesis, no direct source — **do not use externally without validation**",
        "",
        f"*Claim breakdown: "
        f"{summary['confirmed']} confirmed · "
        f"{summary['reported']} reported · "
        f"{summary['inferred']} inferred · "
        f"{len(card.sources_consulted)} sources consulted*",
        "",
        "---",
        "",
    ]

    # ── Weekly changelog (most recent run) ──────────────────────────────────
    if card.latest_changelog:
        lines += _changelog_section(card.latest_changelog)

    # ── 1. Competitor Snapshot ───────────────────────────────────────────────
    s = card.snapshot
    lines += [
        "## 1. Competitor Snapshot",
        "",
        f"**Website:** {s.website}",
        _claim_line(s.founded,       "**Founded:**"),
        _claim_line(s.headcount,     "**Headcount:**"),
        _claim_line(s.funding,       "**Funding:**"),
        _claim_line(s.pricing_model, "**Pricing Model:**"),
        _claim_line(s.positioning,   "**Positioning:**"),
        _claim_line(s.icp,           "**Ideal Customer:**"),
        "",
    ]

    if s.recent_news:
        lines.append("**Recent News:**")
        for news in s.recent_news[:6]:
            lines.append(_claim_line(news))
        lines.append("")

    lines.append("---\n")

    # ── 2. Competitive Positioning Matrix ────────────────────────────────────
    if card.feature_matrix:
        lines += [
            "## 2. Competitive Positioning Matrix",
            "",
            "| Dimension | Us | Them | Intel | Talking Point |",
            "|-----------|-----|------|-------|---------------|",
        ]
        for f in card.feature_matrix:
            src = f"[[src]]({f.sources[0]})" if f.sources else "—"
            lines.append(
                f"| {f.dimension} | {f.us} | {f.them} "
                f"| {_conf(f.confidence)} {src} | {f.talking_point} |"
            )
        lines += ["", "---\n"]

    # ── 3. Win Themes ────────────────────────────────────────────────────────
    if card.win_themes:
        lines.append("## 3. Win Themes\n")
        for i, theme in enumerate(card.win_themes, 1):
            lines.append(f"### {i}. {theme.theme} {_conf(theme.confidence)}")
            if theme.proof_points:
                lines.append("\n**Proof points:**")
                for pp in theme.proof_points:
                    lines.append(_claim_line(pp))
            if theme.discovery_questions:
                lines.append("\n**Discovery questions to surface this need:**")
                for q in theme.discovery_questions:
                    lines.append(f"- {q}")
            lines.append("")
        lines.append("---\n")

    # ── 4. Trap Questions ────────────────────────────────────────────────────
    if card.trap_questions:
        lines += ["## 4. Trap Questions", ""]
        for q in card.trap_questions:
            lines.append(f"- {q}")
        lines += ["", "---\n"]

    # ── 5. Objection Handling ────────────────────────────────────────────────
    if card.objections:
        lines += ["## 5. Objection Handling", ""]
        for obj in card.objections:
            src = _source_link(obj.proof.sources)
            lines += [
                f"**\"{obj.objection}\"**",
                f"- *Reality:* {obj.reality}",
                f"- *Response:* {obj.response}",
                f"- *Proof:* {_conf(obj.proof.confidence)} {obj.proof.claim}{src}",
                "",
            ]
        lines.append("---\n")

    # ── 6. Landmines to Avoid ────────────────────────────────────────────────
    if card.landmines:
        lines += ["## 6. Landmines to Avoid", ""]
        for mine in card.landmines:
            lines.append(_claim_line(mine))
        lines += ["", "---\n"]

    # ── Intel Gaps ───────────────────────────────────────────────────────────
    if card.intel_gaps:
        lines += [
            "## ⚠️ Intel Gaps — Needs Validation Before Use in Deals",
            "",
        ]
        for gap in card.intel_gaps:
            lines.append(f"- [ ] {gap}")
        lines += ["", "---\n"]

    # ── Sources ──────────────────────────────────────────────────────────────
    if card.sources_consulted:
        lines += ["## Sources Consulted", ""]
        for src in card.sources_consulted:
            lines.append(f"- {src}")
        lines.append("")

    return "\n".join(lines)
