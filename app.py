"""
Flask web application for the Rule-Based Movie Recommendation System.

Features:
  - User authentication (login / signup) with hashed passwords
  - Consent agreement on signup (Terms of Service & Privacy Policy)
  - Session-based access control
  - JSON API endpoints for recommendations
"""

import json
import os
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from data import MOVIE_DATABASE
from engine import RecommendationEngine
from models import UserPreferences

app = Flask(__name__)
app.secret_key = "movie-recommender-secret-key-change-in-production"

engine = RecommendationEngine(MOVIE_DATABASE)

# ── User storage (JSON file) ────────────────────────────────────────────────

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load_users() -> dict:
    """Load user data from the JSON file."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_users(users: dict) -> None:
    """Save user data to the JSON file."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


# ── Auth decorator ───────────────────────────────────────────────────────────

def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access the recommender.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ── Precompute available filter options from the database ────────────────────

ALL_GENRES = sorted({g for m in MOVIE_DATABASE for g in m.genres})
ALL_MOODS = sorted({mood for m in MOVIE_DATABASE for mood in m.moods})
ALL_DIRECTORS = sorted({m.director for m in MOVIE_DATABASE})
ALL_LANGUAGES = sorted({m.language for m in MOVIE_DATABASE})
ALL_ACTORS = sorted({a for m in MOVIE_DATABASE for a in m.cast if a})

FILTER_OPTIONS = {
    "genres": ALL_GENRES,
    "moods": ALL_MOODS,
    "directors": ALL_DIRECTORS,
    "languages": ALL_LANGUAGES,
    "actors": ALL_ACTORS,
    "decades": ["1970s", "1980s", "1990s", "2000s", "2010s", "2020s"],
}

# ── Demo profiles ────────────────────────────────────────────────────────────

DEMO_PROFILES = [
    {
        "name": "Sci-Fi & Nolan Fan",
        "icon": "🚀",
        "description": "Loves mind-bending sci-fi, Christopher Nolan, and intense action.",
        "prefs": {
            "favorite_genres": ["Sci-Fi", "Action"],
            "disliked_genres": [],
            "preferred_decades": ["2000s", "2010s"],
            "min_rating": 7.5,
            "preferred_moods": ["cerebral", "thrilling", "mind-bending"],
            "favorite_directors": ["Christopher Nolan"],
            "favorite_actors": [],
            "preferred_languages": ["English"],
            "max_duration_minutes": None,
        },
    },
    {
        "name": "Romantic Drama Lover",
        "icon": "💕",
        "description": "All about emotional, heartwarming romances. No horror please!",
        "prefs": {
            "favorite_genres": ["Romance", "Drama"],
            "disliked_genres": ["Horror", "Action"],
            "preferred_decades": [],
            "min_rating": 7.0,
            "preferred_moods": ["emotional", "romantic", "heartwarming"],
            "favorite_directors": [],
            "favorite_actors": [],
            "preferred_languages": ["English", "French", "Hindi"],
            "max_duration_minutes": None,
        },
    },
    {
        "name": "Bollywood Buff",
        "icon": "🇮🇳",
        "description": "Hindi & Marathi cinema enthusiast — loves Aamir Khan films.",
        "prefs": {
            "favorite_genres": ["Drama", "Comedy"],
            "disliked_genres": [],
            "preferred_decades": ["2000s", "2010s"],
            "min_rating": 7.5,
            "preferred_moods": ["inspiring", "emotional", "hilarious"],
            "favorite_directors": ["Rajkumar Hirani", "Zoya Akhtar"],
            "favorite_actors": ["Aamir Khan"],
            "preferred_languages": ["Hindi", "Marathi"],
            "max_duration_minutes": None,
        },
    },
    {
        "name": "World Cinema Buff",
        "icon": "🌍",
        "description": "Seeks magical, atmospheric films from around the globe.",
        "prefs": {
            "favorite_genres": ["Drama", "Fantasy"],
            "disliked_genres": [],
            "preferred_decades": [],
            "min_rating": 7.5,
            "preferred_moods": ["magical", "dark", "atmospheric"],
            "favorite_directors": ["Hayao Miyazaki", "Bong Joon-ho"],
            "favorite_actors": [],
            "preferred_languages": ["Japanese", "Korean", "Spanish", "Marathi"],
            "max_duration_minutes": None,
        },
    },
    {
        "name": "Short & Funny",
        "icon": "😂",
        "description": "Quick, hilarious watches under 2 hours. Keep it light!",
        "prefs": {
            "favorite_genres": ["Comedy"],
            "disliked_genres": ["Horror", "War"],
            "preferred_decades": [],
            "min_rating": 7.0,
            "preferred_moods": ["hilarious", "lighthearted", "quirky", "fun"],
            "favorite_directors": [],
            "favorite_actors": [],
            "preferred_languages": [],
            "max_duration_minutes": 120,
        },
    },
]


# ── Auth Routes ──────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page and handler."""
    if "user" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in all fields.", "error")
            return render_template("login.html")

        users = _load_users()
        user = users.get(username)

        if not user or not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        session["user"] = {
            "username": username,
            "full_name": user["full_name"],
        }
        flash(f"Welcome back, {user['full_name']}! 🎬", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Signup page with consent agreement."""
    if "user" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        consent = request.form.get("consent")

        # Validation
        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if not consent:
            errors.append("You must agree to the Terms of Service and Privacy Policy.")

        users = _load_users()
        if username in users:
            errors.append("Username is already taken.")
        if any(u.get("email") == email for u in users.values()):
            errors.append("Email is already registered.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("signup.html")

        # Create user
        users[username] = {
            "full_name": full_name,
            "email": email,
            "password": generate_password_hash(password),
            "consent_given": True,
            "consent_timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        _save_users(users)

        session["user"] = {
            "username": username,
            "full_name": full_name,
        }
        flash(f"Account created successfully! Welcome, {full_name}! 🎬", "success")
        return redirect(url_for("index"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Clear session and redirect to login."""
    session.pop("user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ── App Routes ───────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    """Serve the main single-page application."""
    return render_template("index.html", user=session["user"])


@app.route("/api/options")
@login_required
def api_options():
    """Return available filter options for the UI dropdowns/chips."""
    return jsonify(FILTER_OPTIONS)


@app.route("/api/demos")
@login_required
def api_demos():
    """Return the list of demo profiles."""
    return jsonify(DEMO_PROFILES)


@app.route("/api/recommend", methods=["POST"])
@login_required
def api_recommend():
    """Accept user preferences as JSON and return ranked recommendations."""
    data = request.get_json(force=True)

    prefs = UserPreferences(
        favorite_genres=data.get("favorite_genres", []),
        disliked_genres=data.get("disliked_genres", []),
        preferred_decades=data.get("preferred_decades", []),
        min_rating=float(data.get("min_rating", 0)),
        preferred_moods=data.get("preferred_moods", []),
        favorite_directors=data.get("favorite_directors", []),
        favorite_actors=data.get("favorite_actors", []),
        preferred_languages=data.get("preferred_languages", []),
        max_duration_minutes=data.get("max_duration_minutes"),
        already_watched=data.get("already_watched", []),
    )

    top_n = int(data.get("top_n", 10))
    results = engine.recommend(prefs, top_n=top_n)

    response = []
    for rank, scored in enumerate(results, 1):
        m = scored.movie
        breakdown = {
            k: round(v, 1)
            for k, v in sorted(scored.rule_scores.items(), key=lambda x: -x[1])
            if v != 0.0
        }
        response.append({
            "rank": rank,
            "title": m.title,
            "year": m.year,
            "genres": m.genres,
            "rating": m.rating,
            "director": m.director,
            "language": m.language,
            "duration": m.duration_minutes,
            "moods": m.moods,
            "cast": m.cast,
            "popularity": m.popularity,
            "score": scored.total_score,
            "breakdown": breakdown,
        })

    return jsonify({"recommendations": response, "total_movies": len(MOVIE_DATABASE)})


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n  🎬  Movie Recommender Web App")
    print("  → Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
