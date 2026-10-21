"""
Interactive CLI for the Movie Recommendation System.

Provides two modes:
  1. Interactive — walks the user through preference questions and shows results.
  2. Demo — runs preset profiles to showcase the engine immediately.
"""

from __future__ import annotations

import sys
from typing import List, Optional

from data import MOVIE_DATABASE
from engine import RecommendationEngine
from models import UserPreferences


# ─── Available values (for display to user) ──────────────────────────────────

ALL_GENRES = sorted({g for m in MOVIE_DATABASE for g in m.genres})
ALL_MOODS = sorted({mood for m in MOVIE_DATABASE for mood in m.moods})
ALL_DIRECTORS = sorted({m.director for m in MOVIE_DATABASE})
ALL_LANGUAGES = sorted({m.language for m in MOVIE_DATABASE})

SEPARATOR = "─" * 60


# ─── Input helpers ───────────────────────────────────────────────────────────

def _prompt_list(prompt: str, valid_options: List[str]) -> List[str]:
    """Ask the user for a comma-separated list; shows valid options."""
    print(f"\n  Available: {', '.join(valid_options)}")
    raw = input(f"  {prompt} (comma-separated, or press Enter to skip): ").strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _prompt_float(prompt: str, default: Optional[float] = None) -> Optional[float]:
    """Ask for a float value."""
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"  {prompt}{suffix}: ").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        print("  ⚠ Invalid number, using default.")
        return default


def _prompt_int(prompt: str, default: Optional[int] = None) -> Optional[int]:
    """Ask for an integer value."""
    suffix = f" [{default}]" if default is not None else ""
    raw = input(f"  {prompt}{suffix}: ").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        print("  ⚠ Invalid number, using default.")
        return default


# ─── Display ─────────────────────────────────────────────────────────────────

def display_recommendations(results, label: str = "Recommendations") -> None:
    """Pretty-print a list of scored movies with explanations."""
    print(f"\n{'═' * 60}")
    print(f"  🎬  {label}")
    print(f"{'═' * 60}")
    if not results:
        print("  No movies matched your preferences. Try relaxing your filters!")
        return
    for rank, scored in enumerate(results, 1):
        print(f"\n  #{rank}")
        print(scored.explain())
    print(f"\n{SEPARATOR}")


# ─── Interactive mode ────────────────────────────────────────────────────────

def collect_preferences() -> UserPreferences:
    """Walk the user through a series of prompts to build preferences."""
    print(f"\n{SEPARATOR}")
    print("  📋  Let's learn about your movie tastes!")
    print(SEPARATOR)

    fav_genres = _prompt_list("Favorite genres?", ALL_GENRES)
    dis_genres = _prompt_list("Genres you dislike?", ALL_GENRES)
    decades = _prompt_list(
        "Preferred decades?",
        ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
    )
    min_rating = _prompt_float("Minimum acceptable rating (0-10)?", default=0.0)
    moods = _prompt_list("Preferred moods/vibes?", ALL_MOODS)
    directors = _prompt_list("Favorite directors?", ALL_DIRECTORS)
    languages = _prompt_list("Preferred languages?", ALL_LANGUAGES)
    max_dur = _prompt_int("Maximum duration in minutes? (Enter to skip)")
    watched_raw = input("  Movies already watched? (comma-separated, Enter to skip): ").strip()
    watched = [x.strip() for x in watched_raw.split(",") if x.strip()] if watched_raw else []

    return UserPreferences(
        favorite_genres=fav_genres,
        disliked_genres=dis_genres,
        preferred_decades=decades,
        min_rating=min_rating or 0.0,
        preferred_moods=moods,
        favorite_directors=directors,
        preferred_languages=languages,
        max_duration_minutes=max_dur,
        already_watched=watched,
    )


def interactive_mode() -> None:
    """Full interactive session."""
    prefs = collect_preferences()
    engine = RecommendationEngine(MOVIE_DATABASE)

    top_n = _prompt_int("How many recommendations?", default=5) or 5
    results = engine.recommend(prefs, top_n=top_n)
    display_recommendations(results, "Your Personalized Recommendations")


# ─── Demo mode ───────────────────────────────────────────────────────────────

def demo_mode() -> None:
    """Run through several preset profiles to showcase the system."""
    engine = RecommendationEngine(MOVIE_DATABASE)

    profiles = [
        (
            "🧪 Profile 1: Sci-Fi Fan Who Loves Nolan",
            UserPreferences(
                favorite_genres=["Sci-Fi", "Action"],
                preferred_moods=["cerebral", "thrilling", "mind-bending"],
                favorite_directors=["Christopher Nolan"],
                min_rating=7.5,
                preferred_decades=["2000s", "2010s"],
                preferred_languages=["English"],
            ),
        ),
        (
            "🧪 Profile 2: Romantic Drama Lover",
            UserPreferences(
                favorite_genres=["Romance", "Drama"],
                disliked_genres=["Horror", "Action"],
                preferred_moods=["emotional", "romantic", "heartwarming"],
                min_rating=7.0,
                preferred_languages=["English", "French"],
            ),
        ),
        (
            "🧪 Profile 3: World Cinema Enthusiast",
            UserPreferences(
                favorite_genres=["Drama", "Fantasy"],
                preferred_moods=["magical", "dark", "atmospheric"],
                preferred_languages=["Japanese", "Korean", "Spanish"],
                min_rating=7.5,
                favorite_directors=["Hayao Miyazaki", "Bong Joon-ho"],
            ),
        ),
        (
            "🧪 Profile 4: Short & Funny — Keep It Light",
            UserPreferences(
                favorite_genres=["Comedy"],
                disliked_genres=["Horror", "War"],
                preferred_moods=["hilarious", "lighthearted", "quirky", "fun"],
                max_duration_minutes=120,
                min_rating=7.0,
            ),
        ),
        (
            "🧪 Profile 5: Hardcore Cinephile (seen many classics)",
            UserPreferences(
                favorite_genres=["Drama", "Crime", "Thriller"],
                preferred_moods=["dark", "intense", "suspenseful"],
                min_rating=8.0,
                already_watched=[
                    "The Godfather",
                    "The Shawshank Redemption",
                    "The Dark Knight",
                    "Parasite",
                ],
                favorite_actors=["Al Pacino", "Anthony Hopkins"],
            ),
        ),
    ]

    for label, prefs in profiles:
        results = engine.recommend(prefs, top_n=5)
        display_recommendations(results, label)


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    print("\n" + "═" * 60)
    print("  🎬  RULE-BASED MOVIE RECOMMENDATION SYSTEM")
    print("═" * 60)
    print("  1. Interactive mode — answer questions, get recommendations")
    print("  2. Demo mode — see preset profiles in action")
    print("  3. Exit")
    print(SEPARATOR)

    choice = input("  Select mode [1/2/3]: ").strip()
    if choice == "1":
        interactive_mode()
    elif choice == "2":
        demo_mode()
    else:
        print("  Goodbye! 🍿")
        sys.exit(0)


if __name__ == "__main__":
    main()
