from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float."""
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score a song 0–5 using genre (+2), mood (+1), energy proximity (+1.5), and acoustic bonus (+0.5)."""
    score = 0.0
    reasons = []

    # Rule 1 — Genre match (+2.0)
    if song["genre"] == user_prefs.get("favorite_genre", ""):
        score += 2.0
        reasons.append(f"genre match ({song['genre']})")

    # Rule 2 — Mood match (+1.0)
    if song["mood"] == user_prefs.get("favorite_mood", ""):
        score += 1.0
        reasons.append(f"mood match ({song['mood']})")

    # Rule 3 — Energy proximity (up to +1.5)
    energy_diff = abs(song["energy"] - user_prefs.get("target_energy", 0.5))
    energy_score = max(0.0, 1.5 * (1.0 - energy_diff))
    score += energy_score
    reasons.append(f"energy score {energy_score:.2f} (diff={energy_diff:.2f})")

    # Rule 4 — Acoustic bonus (+0.5)
    if user_prefs.get("likes_acoustic", False) and song["acousticness"] >= 0.6:
        score += 0.5
        reasons.append(f"acoustic bonus (acousticness={song['acousticness']})")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs against user preferences and return the top k sorted by score descending."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
