# 🎬 Rule-Based Movie Recommendation System

A complete, explainable rule-based movie recommendation system built in Python and Flask. It uses a transparent scoring engine with 12 hand-crafted heuristics and rules applied to user preferences and item attributes — **without using machine learning**.

Includes an interactive web interface with user authentication, consent agreement, and support for English, Hindi, and Marathi cinema.

---

## 🌟 Key Features

- **Explainable Scoring Engine**: 12 modular, weighted rules that output exact match scores and per-rule score breakdowns.
- **Rich Movie Database**: 50+ curated films spanning Hollywood, Bollywood (Hindi), and Marathi cinema across multiple genres, eras, and moods.
- **Web Application**:
  - Secure **Login and Signup** with password hashing (`scrypt`/`pbkdf2`) and session management.
  - Formal **Terms of Service & Privacy Policy** consent agreement recorded on registration.
  - Interactive preference selector using tags/chips (Genres, Moods, Directors, Actors, Decades, Languages).
  - Penalty tags for disliked genres and strict gates for runtime and minimum rating.
  - Curated preset demo profiles (Sci-Fi, Romantic Drama, Bollywood, World Cinema, Comedy).
- **Dual Interface**: Run either as a full web app or via an interactive terminal CLI.
- **Comprehensive Unit Testing**: 36 automated pytest cases covering individual rules, edge cases, and the engine orchestrator.

---

## 🏗️ Architecture

```
movie_recommender/
├── models.py          # Dataclasses: Movie and UserPreferences
├── data.py            # Curated catalog of 50+ movies (English, Hindi, Marathi)
├── rules.py           # 12 weighted scoring heuristics & rule registry
├── engine.py          # RecommendationEngine (scoring, ranking, breakdown)
├── app.py             # Flask Web application & REST APIs
├── main.py            # Interactive Command-Line Interface (CLI)
├── test_engine.py     # Test suite (36 unit & integration tests)
├── requirements.txt   # Python dependencies
├── users.json         # Local user store with consent tracking
└── templates/
    ├── index.html     # Main recommendation dashboard
    ├── login.html     # User login page
    └── signup.html    # User registration with Terms & Privacy consent
```

---

## ⚖️ The 12 Recommendation Rules

| # | Rule | Description | Impact |
|---|------|-------------|--------|
| 1 | **Genre Match** | Reward matching favorite genres | +3.0 pts per match |
| 2 | **Genre Penalty** | Penalize disliked genres | -4.0 pts per match |
| 3 | **Decade Match** | Match preferred era (e.g., 1990s, 2010s) | +2.0 pts |
| 4 | **Min Rating Gate** | Hard gate below user's minimum acceptable rating | -10.0 pts penalty |
| 5 | **Rating Bonus** | Additional boost for critically acclaimed films (> 8.0) | Up to +2.0 pts |
| 6 | **Mood Match** | Match vibe/atmosphere tags (e.g., cerebral, heartwarming) | +2.0 pts per match |
| 7 | **Director Match** | Strong bonus for favorite directors | +5.0 pts |
| 8 | **Actor Match** | Bonus for preferred cast members | +2.0 pts per match |
| 9 | **Language Preference** | Preferred audio/language match | +1.0 pt |
| 10 | **Duration Gate** | Penalty for exceeding user duration limit | -3.0 pts per 30 min overage |
| 11 | **Already Watched** | Strong exclusion for films user has already seen | -100.0 pts |
| 12 | **Popularity Boost** | Tiebreaker based on popularity metric | +0.0 to +0.5 pts |

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/panuubinuu/movie-recommender.git
cd movie-recommender
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```
- Sign up with a new account and accept the consent agreement.
- Select your preferences or click a demo profile to view recommendations with score breakdowns.

### 4. Run via Terminal (CLI Mode)
```bash
python main.py
```

### 5. Run the Test Suite
```bash
python -m pytest test_engine.py -v
```

---

## 🔒 Privacy & Consent

The application includes user consent tracking adhering to standard data protection principles:
- User consent timestamp recorded upon registration.
- Passwords are securely hashed with industry-standard cryptographic hashing.
- No third-party data tracking or external data sharing.

---

## 📜 License

This project is licensed under the MIT License.
