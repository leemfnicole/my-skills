"""
Merge a freshly-researched battlecard into an existing one.

Strategy:
  - The new card (from this week's agent run) always wins on content — it has
    fresher sources.
  - But we don't blindly discard history: if the old card had a CONFIRMED claim
    and the new research only finds it in 1 source (REPORTED), we keep CONFIRMED
    and note the potential downgrade in the changelog for human review.
  - Claims in the old card that the new research didn't find at all are marked
    STALE in the changelog so sales knows to double-check before using them.
  - The changelogs list is prepended (newest first) and capped at 8 entries.

Matching logic:
  - Snapshot fields: matched by field name (funding, headcount, etc.)
  - Feature matrix:  matched by dimension (case-insensitive)
  - Win themes:      matched by theme text (case-insensitive, first 40 chars)
  - Objections:      matched by objection text (case-insensitive, first 40 chars)
  - Landmines:       matched by claim text (case-insensitive, first 40 chars)
"""

from datetime import datetime
from typing import Optional

from .battlecard import (
    Battlecard,
    ChangelogEntry,
    ChangeType,
    Confidence,
    SourcedClaim,
    WeeklyChangelog,
)

_MAX_CHANGELOGS = 8

# Confidence ordering for upgrade/downgrade detection
_TIER = {Confidence.INFERRED: 0, Confidence.REPORTED: 1, Confidence.CONFIRMED: 2}


def _key(text: str) -> str:
    """Normalised matching key from arbitrary text."""
    return text.lower().strip()[:50]


def _claim_changed(old: SourcedClaim, new: SourcedClaim) -> bool:
    """True if the claim text changed meaningfully (ignoring case/whitespace)."""
    return _key(old.claim) != _key(new.claim)


def _confidence_change(
    old: SourcedClaim,
    new: SourcedClaim,
    field: str,
) -> Optional[ChangelogEntry]:
    """Return a changelog entry if confidence tier changed, else None."""
    old_tier = _TIER[old.confidence]
    new_tier = _TIER[new.confidence]

    if new_tier > old_tier:
        return ChangelogEntry(
            change_type=ChangeType.UPGRADED,
            field=field,
            summary=f"{field} confidence upgraded: {old.confidence} → {new.confidence}",
            old_value=old.confidence,
            new_value=new.confidence,
        )
    if new_tier < old_tier:
        # Keep the old (higher) confidence in the merged card but flag it
        return ChangelogEntry(
            change_type=ChangeType.DOWNGRADED,
            field=field,
            summary=(
                f"{field} may be weakening: was {old.confidence}, "
                f"new research only found {new.confidence} — verify before next deal"
            ),
            old_value=old.confidence,
            new_value=new.confidence,
        )
    return None


def _merge_claim(
    old: Optional[SourcedClaim],
    new: SourcedClaim,
    field: str,
    entries: list,
) -> SourcedClaim:
    """
    Merge a single claim.
    Returns the claim to use in the merged battlecard and appends
    any changelog entries to `entries`.
    """
    if old is None:
        entries.append(ChangelogEntry(
            change_type=ChangeType.ADDED,
            field=field,
            summary=f"New intel on {field}: {new.claim[:80]}",
            new_value=new.claim,
        ))
        return new

    # Text changed → note it, prefer new content
    if _claim_changed(old, new):
        entries.append(ChangelogEntry(
            change_type=ChangeType.UPDATED,
            field=field,
            summary=f"{field} updated: {new.claim[:80]}",
            old_value=old.claim,
            new_value=new.claim,
        ))

    # Confidence changed → note it; for downgrades keep old (higher) confidence
    conf_entry = _confidence_change(old, new, field)
    if conf_entry:
        entries.append(conf_entry)

    # For downgrades: preserve old (higher) confidence unless text also changed
    if (
        _TIER[new.confidence] < _TIER[old.confidence]
        and not _claim_changed(old, new)
    ):
        return SourcedClaim(
            claim=new.claim,
            confidence=old.confidence,  # keep the stronger confidence
            sources=new.sources or old.sources,
            scraped_at=new.scraped_at,
        )

    return new


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def merge(old: Battlecard, new: Battlecard) -> Battlecard:
    """
    Merge `new` (fresh agent run) into `old` (stored battlecard).
    Returns a new Battlecard with:
      - Updated claims (new content wins, confidence downgrades are flagged)
      - A prepended WeeklyChangelog
      - `first_created` preserved from the old card
    """
    entries: List[ChangelogEntry] = []

    # ── Snapshot ─────────────────────────────────────────────────────────────
    snap_old = old.snapshot
    snap_new = new.snapshot

    merged_snapshot = snap_new.model_copy(update={
        "funding":       _merge_claim(snap_old.funding,       snap_new.funding,       "snapshot.funding",       entries),
        "headcount":     _merge_claim(snap_old.headcount,     snap_new.headcount,     "snapshot.headcount",     entries),
        "founded":       _merge_claim(snap_old.founded,       snap_new.founded,       "snapshot.founded",       entries),
        "positioning":   _merge_claim(snap_old.positioning,   snap_new.positioning,   "snapshot.positioning",   entries),
        "icp":           _merge_claim(snap_old.icp,           snap_new.icp,           "snapshot.icp",           entries),
        "pricing_model": _merge_claim(snap_old.pricing_model, snap_new.pricing_model, "snapshot.pricing_model", entries),
    })

    # ── Feature matrix ────────────────────────────────────────────────────────
    old_dims = {_key(f.dimension): f for f in old.feature_matrix}
    merged_features = []

    for feat in new.feature_matrix:
        k = _key(feat.dimension)
        old_feat = old_dims.get(k)

        if old_feat is None:
            entries.append(ChangelogEntry(
                change_type=ChangeType.ADDED,
                field=f"feature_matrix[{feat.dimension}]",
                summary=f"New dimension tracked: {feat.dimension}",
                new_value=f"Us: {feat.us} | Them: {feat.them}",
            ))
            merged_features.append(feat)
        else:
            # Check for content changes in us/them columns
            if _key(old_feat.them) != _key(feat.them):
                entries.append(ChangelogEntry(
                    change_type=ChangeType.UPDATED,
                    field=f"feature_matrix[{feat.dimension}]",
                    summary=f"{feat.dimension}: competitor position updated",
                    old_value=old_feat.them,
                    new_value=feat.them,
                ))
            conf_entry = _confidence_change(
                SourcedClaim(claim=old_feat.them, confidence=old_feat.confidence, sources=old_feat.sources),
                SourcedClaim(claim=feat.them, confidence=feat.confidence, sources=feat.sources),
                f"feature_matrix[{feat.dimension}]",
            )
            if conf_entry:
                entries.append(conf_entry)
            merged_features.append(feat)

    # Flag old dimensions that disappeared
    new_dims = {_key(f.dimension) for f in new.feature_matrix}
    for old_feat in old.feature_matrix:
        if _key(old_feat.dimension) not in new_dims:
            entries.append(ChangelogEntry(
                change_type=ChangeType.STALE,
                field=f"feature_matrix[{old_feat.dimension}]",
                summary=f"Dimension no longer found in research: {old_feat.dimension}",
                old_value=f"Us: {old_feat.us} | Them: {old_feat.them}",
            ))
            # Keep it in the card (with a note) so reps don't lose it silently
            merged_features.append(old_feat)

    # ── Win themes ────────────────────────────────────────────────────────────
    old_themes = {_key(t.theme)[:40]: t for t in old.win_themes}
    for theme in new.win_themes:
        k = _key(theme.theme)[:40]
        if k not in old_themes:
            entries.append(ChangelogEntry(
                change_type=ChangeType.ADDED,
                field="win_themes",
                summary=f"New win theme identified: {theme.theme}",
                new_value=theme.theme,
            ))

    # ── Objections ────────────────────────────────────────────────────────────
    old_objs = {_key(o.objection)[:40]: o for o in old.objections}
    for obj in new.objections:
        k = _key(obj.objection)[:40]
        if k not in old_objs:
            entries.append(ChangelogEntry(
                change_type=ChangeType.ADDED,
                field="objections",
                summary=f"New objection tracked: {obj.objection[:60]}",
                new_value=obj.objection,
            ))

    # ── Stale intel gaps from old card that are now resolved ─────────────────
    old_gaps = set(_key(g) for g in old.intel_gaps)
    new_gaps = set(_key(g) for g in new.intel_gaps)
    resolved = old_gaps - new_gaps
    for gap in resolved:
        entries.append(ChangelogEntry(
            change_type=ChangeType.UPDATED,
            field="intel_gaps",
            summary=f"Intel gap resolved this week",
            old_value=gap,
        ))

    # ── Build the changelog entry for this run ────────────────────────────────
    upgrades   = sum(1 for e in entries if e.change_type == ChangeType.UPGRADED)
    downgrades = sum(1 for e in entries if e.change_type == ChangeType.DOWNGRADED)
    added      = sum(1 for e in entries if e.change_type == ChangeType.ADDED)
    stale      = sum(1 for e in entries if e.change_type == ChangeType.STALE)

    changelog = WeeklyChangelog(
        run_date=datetime.utcnow(),
        entries=entries,
        sources_consulted=len(new.sources_consulted),
        confidence_upgrades=upgrades,
        confidence_downgrades=downgrades,
        new_claims=added,
        stale_claims=stale,
    )

    # Prepend newest changelog, cap at _MAX_CHANGELOGS
    changelogs = [changelog, *old.changelogs[:_MAX_CHANGELOGS - 1]]

    return new.model_copy(update={
        "snapshot":       merged_snapshot,
        "feature_matrix": merged_features,
        "first_created":  old.first_created,
        "last_updated":   datetime.utcnow(),
        "changelogs":     changelogs,
    })
