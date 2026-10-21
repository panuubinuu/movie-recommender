"""
Recommendation engine — orchestrates rules over the movie database
to produce ranked, explainable recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from models import Movie, UserPreferences
from rules import DEFAULT_RULES, WeightedRule


@dataclass
class ScoredMovie:
    """A movie paired with its total score and per-rule breakdown."""
    movie: Movie
    total_score: float
    rule_scores: Dict[str, float] = field(default_factory=dict)

    def explain(self) -> str:
        """Return a human-readable explanation of why this movie scored the way it did."""
        lines = [f"  {self.movie}  →  Score: {self.total_score:+.1f}"]
        # Only show rules that actually contributed (non-zero)
        active = {k: v for k, v in self.rule_scores.items() if v != 0.0}
        if active:
            for rule_name, score in sorted(active.items(), key=lambda x: -x[1]):
                sign = "+" if score > 0 else ""
                lines.append(f"    • {rule_name}: {sign}{score:.1f}")
        return "\n".join(lines)


class RecommendationEngine:
    """
    Applies a list of weighted rules to every movie and returns
    a ranked list of recommendations.
    """

    def __init__(
        self,
        movies: List[Movie],
        rules: Optional[List[WeightedRule]] = None,
    ):
        self.movies = movies
        self.rules = rules or DEFAULT_RULES

    def _score_movie(self, movie: Movie, prefs: UserPreferences) -> ScoredMovie:
        """Compute the aggregate score for a single movie."""
        rule_scores: Dict[str, float] = {}
        total = 0.0
        for wr in self.rules:
            raw = wr.func(movie, prefs)
            weighted = raw * wr.weight
            rule_scores[wr.name] = weighted
            total += weighted
        return ScoredMovie(movie=movie, total_score=round(total, 2), rule_scores=rule_scores)

    def recommend(
        self,
        prefs: UserPreferences,
        top_n: int = 5,
        min_score: Optional[float] = None,
    ) -> List[ScoredMovie]:
        """
        Return the top-N movies ranked by descending score.

        Args:
            prefs:     User preferences to match against.
            top_n:     Number of recommendations to return.
            min_score: Optional floor — exclude movies scoring below this.
        """
        scored = [self._score_movie(m, prefs) for m in self.movies]

        if min_score is not None:
            scored = [s for s in scored if s.total_score >= min_score]

        # Sort by score descending, break ties by rating descending
        scored.sort(key=lambda s: (s.total_score, s.movie.rating), reverse=True)
        return scored[:top_n]

    def list_all_scored(self, prefs: UserPreferences) -> List[ScoredMovie]:
        """Score every movie and return the full ranked list (for debugging)."""
        scored = [self._score_movie(m, prefs) for m in self.movies]
        scored.sort(key=lambda s: (s.total_score, s.movie.rating), reverse=True)
        return scored
