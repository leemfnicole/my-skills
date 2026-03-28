"""Competitive Intelligence Agent — source-verified battlecard generator."""

from .agent import build_battlecard
from .battlecard import Battlecard, Confidence, SourcedClaim
from .formatter import to_markdown

__all__ = ["build_battlecard", "Battlecard", "Confidence", "SourcedClaim", "to_markdown"]
