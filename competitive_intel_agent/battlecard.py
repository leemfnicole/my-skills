"""
Pydantic models for the competitive battlecard.

Every claim in a battlecard is a SourcedClaim — it carries:
  - The actual claim text
  - A confidence tier (CONFIRMED / REPORTED / INFERRED)
  - Source URLs the agent actually fetched (not invented)
  - A scrape timestamp

This schema is what makes the agent's output verifiable.
The three confidence tiers map directly to how sales reps should treat a claim:
  CONFIRMED  = use it freely, multiple sources agree
  REPORTED   = use with a qualifier, single source
  INFERRED   = do not use externally without validation
"""

from enum import Enum
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Weekly changelog — tracks what changed between agent runs
# ---------------------------------------------------------------------------

class ChangeType(str, Enum):
    ADDED    = "added"      # New claim not in previous version
    UPDATED  = "updated"    # Claim text or confidence changed
    STALE    = "stale"      # Claim was in old card but not found in new research
    UPGRADED = "upgraded"   # Confidence went up  (reported → confirmed)
    DOWNGRADED = "downgraded"  # Confidence went down (confirmed → reported)


class ChangelogEntry(BaseModel):
    change_type: ChangeType
    field: str               # e.g. "snapshot.funding", "feature_matrix[API integrations]"
    summary: str             # Human-readable one-liner for sales team
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class WeeklyChangelog(BaseModel):
    run_date: datetime = Field(default_factory=datetime.utcnow)
    entries: List[ChangelogEntry] = Field(default_factory=list)
    sources_consulted: int = 0
    confidence_upgrades: int = 0
    confidence_downgrades: int = 0
    new_claims: int = 0
    stale_claims: int = 0

    def has_changes(self) -> bool:
        return bool(self.entries)


class Confidence(str, Enum):
    CONFIRMED = "confirmed"   # Found in 2+ independent sources
    REPORTED  = "reported"    # Found in exactly 1 source
    INFERRED  = "inferred"    # LLM synthesis — no direct source, must be verified


class SourcedClaim(BaseModel):
    claim: str
    confidence: Confidence
    sources: List[str] = Field(
        default_factory=list,
        description="Actual URLs fetched by the research agent. Empty only when confidence=inferred.",
    )
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    def is_trustworthy(self) -> bool:
        return self.confidence in (Confidence.CONFIRMED, Confidence.REPORTED)


class CompetitorSnapshot(BaseModel):
    name: str
    website: str
    funding: SourcedClaim
    headcount: SourcedClaim
    founded: SourcedClaim
    positioning: SourcedClaim
    icp: SourcedClaim
    pricing_model: SourcedClaim
    recent_news: List[SourcedClaim] = Field(default_factory=list)


class FeatureComparison(BaseModel):
    dimension: str
    us: str
    them: str
    confidence: Confidence
    sources: List[str] = Field(default_factory=list)
    talking_point: str


class WinTheme(BaseModel):
    theme: str
    confidence: Confidence
    proof_points: List[SourcedClaim] = Field(default_factory=list)
    discovery_questions: List[str] = Field(default_factory=list)


class Objection(BaseModel):
    objection: str
    reality: str
    response: str
    proof: SourcedClaim


class Battlecard(BaseModel):
    competitor: str
    your_company: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    first_created: datetime = Field(default_factory=datetime.utcnow)
    overall_confidence: Confidence

    snapshot: CompetitorSnapshot
    feature_matrix: List[FeatureComparison] = Field(default_factory=list)
    win_themes: List[WinTheme] = Field(default_factory=list)
    trap_questions: List[str] = Field(default_factory=list)
    objections: List[Objection] = Field(default_factory=list)
    landmines: List[SourcedClaim] = Field(default_factory=list)

    intel_gaps: List[str] = Field(
        default_factory=list,
        description="Claims that need manual validation before use in deals.",
    )
    sources_consulted: List[str] = Field(
        default_factory=list,
        description="All URLs actually fetched during research.",
    )

    # History — the most recent run's changelog is kept here;
    # the full list is kept in memory only (JSON gets last 8 weeks)
    changelogs: List[WeeklyChangelog] = Field(
        default_factory=list,
        description="One entry per agent run, newest first. Capped at 8 weeks.",
    )

    @property
    def latest_changelog(self) -> Optional[WeeklyChangelog]:
        return self.changelogs[0] if self.changelogs else None

    def confidence_summary(self) -> dict:
        """Return a count of claims by confidence tier across the whole card."""
        all_claims: List[SourcedClaim] = [
            self.snapshot.funding,
            self.snapshot.headcount,
            self.snapshot.founded,
            self.snapshot.positioning,
            self.snapshot.icp,
            self.snapshot.pricing_model,
            *self.snapshot.recent_news,
            *[obj.proof for obj in self.objections],
            *self.landmines,
            *[pp for t in self.win_themes for pp in t.proof_points],
        ]
        counts = {c: 0 for c in Confidence}
        for claim in all_claims:
            counts[claim.confidence] += 1
        return {k.value: v for k, v in counts.items()}
