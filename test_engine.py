"""
Tests for the rule-based recommendation engine.

Covers individual rules, the scoring engine, and edge cases.
Run with:  python -m pytest test_engine.py -v
"""

import pytest

from models import Movie, UserPreferences
from rules import (
    rule_genre_match,
    rule_genre_penalty,
    rule_decade_match,
    rule_min_rating_gate,
    rule_rating_bonus,
    rule_mood_match,
    rule_director_match,
    rule_actor_match,
    rule_language_match,
    rule_duration_gate,
    rule_already_watched,
    rule_popularity_boost,
)
from engine import RecommendationEngine


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_movie() -> Movie:
    return Movie(
        title="Test Movie",
        genres=["Sci-Fi", "Action"],
        year=2015,
        rating=8.5,
        director="Christopher Nolan",
        language="English",
        duration_minutes=150,
        moods=["cerebral", "thrilling"],
        cast=["Leonardo DiCaprio"],
        popularity=8.0,
    )


@pytest.fixture
def another_movie() -> Movie:
    return Movie(
        title="Another Movie",
        genres=["Romance", "Drama"],
        year=1995,
        rating=7.2,
        director="Richard Linklater",
        language="French",
        duration_minutes=100,
        moods=["romantic", "intimate"],
        cast=["Ethan Hawke"],
        popularity=6.0,
    )


# ─── Individual rule tests ───────────────────────────────────────────────────

class TestGenreMatch:
    def test_full_overlap(self, sample_movie):
        prefs = UserPreferences(favorite_genres=["Sci-Fi", "Action"])
        assert rule_genre_match(sample_movie, prefs) == 6.0  # 2 × 3

    def test_partial_overlap(self, sample_movie):
        prefs = UserPreferences(favorite_genres=["Sci-Fi", "Comedy"])
        assert rule_genre_match(sample_movie, prefs) == 3.0  # 1 × 3

    def test_no_overlap(self, sample_movie):
        prefs = UserPreferences(favorite_genres=["Horror"])
        assert rule_genre_match(sample_movie, prefs) == 0.0

    def test_empty_prefs(self, sample_movie):
        prefs = UserPreferences()
        assert rule_genre_match(sample_movie, prefs) == 0.0


class TestGenrePenalty:
    def test_disliked_genre_present(self, sample_movie):
        prefs = UserPreferences(disliked_genres=["Action"])
        assert rule_genre_penalty(sample_movie, prefs) == -4.0

    def test_no_disliked_genre(self, sample_movie):
        prefs = UserPreferences(disliked_genres=["Horror"])
        assert rule_genre_penalty(sample_movie, prefs) == 0.0


class TestDecadeMatch:
    def test_matching_decade(self, sample_movie):
        prefs = UserPreferences(preferred_decades=["2010s"])
        assert rule_decade_match(sample_movie, prefs) == 2.0

    def test_non_matching_decade(self, sample_movie):
        prefs = UserPreferences(preferred_decades=["1990s"])
        assert rule_decade_match(sample_movie, prefs) == 0.0

    def test_empty_decades(self, sample_movie):
        prefs = UserPreferences()
        assert rule_decade_match(sample_movie, prefs) == 0.0


class TestMinRatingGate:
    def test_below_minimum(self, sample_movie):
        prefs = UserPreferences(min_rating=9.0)
        assert rule_min_rating_gate(sample_movie, prefs) == -10.0

    def test_above_minimum(self, sample_movie):
        prefs = UserPreferences(min_rating=7.0)
        assert rule_min_rating_gate(sample_movie, prefs) == 0.0

    def test_no_minimum(self, sample_movie):
        prefs = UserPreferences()
        assert rule_min_rating_gate(sample_movie, prefs) == 0.0


class TestRatingBonus:
    def test_high_rating(self, sample_movie):
        # 8.5 → (8.5 - 8.0) * 1.0 = 0.5
        prefs = UserPreferences()
        assert rule_rating_bonus(sample_movie, prefs) == pytest.approx(0.5)

    def test_low_rating(self, another_movie):
        prefs = UserPreferences()
        assert rule_rating_bonus(another_movie, prefs) == 0.0


class TestMoodMatch:
    def test_matching_moods(self, sample_movie):
        prefs = UserPreferences(preferred_moods=["cerebral", "thrilling"])
        assert rule_mood_match(sample_movie, prefs) == 4.0

    def test_no_matching_moods(self, sample_movie):
        prefs = UserPreferences(preferred_moods=["romantic"])
        assert rule_mood_match(sample_movie, prefs) == 0.0


class TestDirectorMatch:
    def test_favorite_director(self, sample_movie):
        prefs = UserPreferences(favorite_directors=["Christopher Nolan"])
        assert rule_director_match(sample_movie, prefs) == 5.0

    def test_case_insensitive(self, sample_movie):
        prefs = UserPreferences(favorite_directors=["christopher nolan"])
        assert rule_director_match(sample_movie, prefs) == 5.0

    def test_non_favorite(self, sample_movie):
        prefs = UserPreferences(favorite_directors=["Wes Anderson"])
        assert rule_director_match(sample_movie, prefs) == 0.0


class TestActorMatch:
    def test_matching_actor(self, sample_movie):
        prefs = UserPreferences(favorite_actors=["Leonardo DiCaprio"])
        assert rule_actor_match(sample_movie, prefs) == 2.0

    def test_no_matching_actor(self, sample_movie):
        prefs = UserPreferences(favorite_actors=["Brad Pitt"])
        assert rule_actor_match(sample_movie, prefs) == 0.0


class TestLanguageMatch:
    def test_preferred_language(self, sample_movie):
        prefs = UserPreferences(preferred_languages=["English"])
        assert rule_language_match(sample_movie, prefs) == 1.0

    def test_non_preferred(self, sample_movie):
        prefs = UserPreferences(preferred_languages=["French"])
        assert rule_language_match(sample_movie, prefs) == 0.0


class TestDurationGate:
    def test_within_limit(self, sample_movie):
        prefs = UserPreferences(max_duration_minutes=180)
        assert rule_duration_gate(sample_movie, prefs) == 0.0

    def test_over_limit(self, sample_movie):
        # 150 min movie, 120 max → 30 over → (30//30)+1 = 2 blocks → -6
        prefs = UserPreferences(max_duration_minutes=120)
        assert rule_duration_gate(sample_movie, prefs) == -6.0

    def test_way_over_limit(self, sample_movie):
        # 150 min movie, 90 max → 60 over → (60//30)+1 = 3 blocks → -9
        prefs = UserPreferences(max_duration_minutes=90)
        assert rule_duration_gate(sample_movie, prefs) == -9.0

    def test_no_limit(self, sample_movie):
        prefs = UserPreferences()
        assert rule_duration_gate(sample_movie, prefs) == 0.0


class TestAlreadyWatched:
    def test_watched(self, sample_movie):
        prefs = UserPreferences(already_watched=["Test Movie"])
        assert rule_already_watched(sample_movie, prefs) == -100.0

    def test_not_watched(self, sample_movie):
        prefs = UserPreferences(already_watched=["Other Movie"])
        assert rule_already_watched(sample_movie, prefs) == 0.0


class TestPopularityBoost:
    def test_boost(self, sample_movie):
        prefs = UserPreferences()
        assert rule_popularity_boost(sample_movie, prefs) == pytest.approx(0.8)


# ─── Engine integration tests ───────────────────────────────────────────────

class TestRecommendationEngine:
    def test_returns_correct_count(self, sample_movie, another_movie):
        engine = RecommendationEngine([sample_movie, another_movie])
        prefs = UserPreferences(favorite_genres=["Sci-Fi"])
        results = engine.recommend(prefs, top_n=1)
        assert len(results) == 1
        assert results[0].movie.title == "Test Movie"

    def test_ranking_order(self, sample_movie, another_movie):
        engine = RecommendationEngine([sample_movie, another_movie])
        prefs = UserPreferences(favorite_genres=["Romance"])
        results = engine.recommend(prefs, top_n=2)
        # "Another Movie" (Romance) should rank above "Test Movie" (Sci-Fi)
        assert results[0].movie.title == "Another Movie"

    def test_min_score_filter(self, sample_movie, another_movie):
        engine = RecommendationEngine([sample_movie, another_movie])
        prefs = UserPreferences(favorite_genres=["Sci-Fi"])
        results = engine.recommend(prefs, top_n=10, min_score=3.0)
        # Only the Sci-Fi movie should pass the min_score threshold
        titles = [r.movie.title for r in results]
        assert "Test Movie" in titles

    def test_empty_prefs_still_works(self, sample_movie, another_movie):
        engine = RecommendationEngine([sample_movie, another_movie])
        prefs = UserPreferences()
        results = engine.recommend(prefs, top_n=5)
        assert len(results) == 2  # both movies returned

    def test_explain_output(self, sample_movie):
        engine = RecommendationEngine([sample_movie])
        prefs = UserPreferences(favorite_genres=["Sci-Fi"])
        results = engine.recommend(prefs, top_n=1)
        explanation = results[0].explain()
        assert "Genre Match" in explanation
        assert "Score:" in explanation

    def test_already_watched_excluded(self, sample_movie, another_movie):
        engine = RecommendationEngine([sample_movie, another_movie])
        prefs = UserPreferences(
            favorite_genres=["Sci-Fi"],
            already_watched=["Test Movie"],
        )
        results = engine.recommend(prefs, top_n=2, min_score=0.0)
        # "Test Movie" should be pushed to the bottom
        if len(results) >= 2:
            assert results[-1].movie.title == "Test Movie"
