"""
Data models for the rule-based movie recommendation system.

Defines the core entities: Movie and UserPreferences, using dataclasses
for clean, self-documenting structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Movie:
    """Represents a movie with its attributes used for rule matching."""

    title: str
    genres: List[str]              # e.g. ["Action", "Sci-Fi"]
    year: int                      # Release year
    rating: float                  # Average rating out of 10
    director: str                  # Director name
    language: str                  # Primary language, e.g. "English"
    duration_minutes: int          # Runtime in minutes
    moods: List[str]               # e.g. ["thrilling", "dark", "cerebral"]
    cast: List[str] = field(default_factory=list)  # Notable actors
    popularity: float = 5.0        # Popularity score 1-10

    def __str__(self) -> str:
        genres_str = ", ".join(self.genres)
        return f"{self.title} ({self.year}) [{genres_str}] — ★ {self.rating}/10"


@dataclass
class UserPreferences:
    """Captures a user's movie preferences for rule-based matching."""

    favorite_genres: List[str] = field(default_factory=list)
    disliked_genres: List[str] = field(default_factory=list)
    preferred_decades: List[str] = field(default_factory=list)  # e.g. ["1990s", "2000s"]
    min_rating: float = 0.0
    preferred_moods: List[str] = field(default_factory=list)
    favorite_directors: List[str] = field(default_factory=list)
    favorite_actors: List[str] = field(default_factory=list)
    preferred_languages: List[str] = field(default_factory=list)
    max_duration_minutes: Optional[int] = None  # None means no limit
    already_watched: List[str] = field(default_factory=list)  # Titles to exclude
