"""
Rule-based scoring engine for movie recommendations.

Each rule is a self-contained function that takes a Movie and UserPreferences
and returns a numeric score contribution. Rules are combined with configurable
weights to produce a final recommendation score.

Design Principles:
  - Each rule is independent and testable in isolation.
  - Weights are explicit and tunable without changing rule logic.
  - Rules can return negative scores to penalize poor matches.
  - New rules can be added by writing a function and registering it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from models import Movie, UserPreferences


# ─── Helper ──────────────────────────────────────────────────────────────────

def _year_to_decade(year: int) -> str:
    """Convert a year to its decade label, e.g. 1994 → '1990s'."""
    return f"{(year // 10) * 10}s"


def _normalize(text: str) -> str:
    """Case-insensitive comparison helper."""
    return text.strip().lower()


def _overlap(list_a: List[str], list_b: List[str]) -> int:
    """Count case-insensitive matches between two lists."""
    set_b = {_normalize(x) for x in list_b}
    return sum(1 for x in list_a if _normalize(x) in set_b)


# ─── Individual Rules ────────────────────────────────────────────────────────

def rule_genre_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    Core rule: award points for every genre overlap.
    +3 points per matching genre (strong signal).
    """
    return _overlap(movie.genres, prefs.favorite_genres) * 3.0


def rule_genre_penalty(movie: Movie, prefs: UserPreferences) -> float:
    """
    Penalize movies containing genres the user dislikes.
    -4 per disliked genre (slightly stronger than the positive match
    so that an explicitly disliked genre outweighs a single liked genre).
    """
    return _overlap(movie.genres, prefs.disliked_genres) * -4.0


def rule_decade_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    Reward movies from preferred decades.
    +2 if the movie's decade matches any preferred decade.
    """
    if not prefs.preferred_decades:
        return 0.0
    movie_decade = _year_to_decade(movie.year)
    if _normalize(movie_decade) in {_normalize(d) for d in prefs.preferred_decades}:
        return 2.0
    return 0.0


def rule_min_rating_gate(movie: Movie, prefs: UserPreferences) -> float:
    """
    Hard gate: strongly penalize movies below the user's minimum rating.
    This effectively filters them out without removing them entirely
    (they could still appear if every other signal is very strong).
    """
    if prefs.min_rating and movie.rating < prefs.min_rating:
        return -10.0
    return 0.0


def rule_rating_bonus(movie: Movie, prefs: UserPreferences) -> float:
    """
    Slight bonus for highly rated movies (above 8.0).
    Scales linearly: an 8.0 gets +0, a 9.0 gets +1, a 10.0 gets +2.
    """
    if movie.rating >= 8.0:
        return (movie.rating - 8.0) * 1.0
    return 0.0


def rule_mood_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    Mood/atmosphere alignment: +2 per matching mood tag.
    """
    return _overlap(movie.moods, prefs.preferred_moods) * 2.0


def rule_director_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    Strong bonus if the movie is by a favorite director.
    +5 — director preference is typically a strong signal.
    """
    if not prefs.favorite_directors:
        return 0.0
    if _normalize(movie.director) in {_normalize(d) for d in prefs.favorite_directors}:
        return 5.0
    return 0.0


def rule_actor_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    Bonus for movies featuring favorite actors: +2 per matching actor.
    """
    return _overlap(movie.cast, prefs.favorite_actors) * 2.0


def rule_language_match(movie: Movie, prefs: UserPreferences) -> float:
    """
    +1 if the movie's language is in the user's preferred list.
    Mild signal — shouldn't dominate, but breaks ties nicely.
    """
    if not prefs.preferred_languages:
        return 0.0
    if _normalize(movie.language) in {_normalize(l) for l in prefs.preferred_languages}:
        return 1.0
    return 0.0


def rule_duration_gate(movie: Movie, prefs: UserPreferences) -> float:
    """
    Penalize movies exceeding the user's maximum duration tolerance.
    -3 per extra 30-min block over the limit.
    """
    if prefs.max_duration_minutes is None:
        return 0.0
    overage = movie.duration_minutes - prefs.max_duration_minutes
    if overage > 0:
        return -3.0 * ((overage // 30) + 1)
    return 0.0


def rule_already_watched(movie: Movie, prefs: UserPreferences) -> float:
    """
    Exclude movies the user has already seen.
    Heavy penalty to push them to the bottom.
    """
    if _normalize(movie.title) in {_normalize(t) for t in prefs.already_watched}:
        return -100.0
    return 0.0


def rule_popularity_boost(movie: Movie, prefs: UserPreferences) -> float:
    """
    Mild tiebreaker: popular movies get a small nudge.
    Scaled 0–1 based on a 1-10 popularity score.
    """
    return movie.popularity / 10.0


# ─── Rule Registry ───────────────────────────────────────────────────────────

@dataclass
class WeightedRule:
    """Associates a rule function with its weight and a human-readable name."""
    name: str
    func: Callable[[Movie, UserPreferences], float]
    weight: float = 1.0


# Default rule set with weights — edit weights here to tune behavior
DEFAULT_RULES: List[WeightedRule] = [
    WeightedRule("Genre Match",        rule_genre_match,       weight=1.0),
    WeightedRule("Genre Penalty",      rule_genre_penalty,     weight=1.0),
    WeightedRule("Decade Match",       rule_decade_match,      weight=1.0),
    WeightedRule("Min Rating Gate",    rule_min_rating_gate,   weight=1.0),
    WeightedRule("Rating Bonus",       rule_rating_bonus,      weight=1.0),
    WeightedRule("Mood Match",         rule_mood_match,        weight=1.0),
    WeightedRule("Director Match",     rule_director_match,    weight=1.0),
    WeightedRule("Actor Match",        rule_actor_match,       weight=1.0),
    WeightedRule("Language Pref",      rule_language_match,    weight=1.0),
    WeightedRule("Duration Gate",      rule_duration_gate,     weight=1.0),
    WeightedRule("Already Watched",    rule_already_watched,   weight=1.0),
    WeightedRule("Popularity Boost",   rule_popularity_boost,  weight=0.5),
]
