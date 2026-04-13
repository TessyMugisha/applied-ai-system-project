"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from .recommender import load_songs, recommend_songs


PROFILES = {
    "Late Night Jazz": {
        "favorite_genre": "jazz",
        "favorite_mood": "relaxed",
        "target_energy": 0.37,
        "target_valence": 0.70,
        "likes_acoustic": True,
    },
    "Synthwave Night Drive": {
        "favorite_genre": "synthwave",
        "favorite_mood": "moody",
        "target_energy": 0.75,
        "target_valence": 0.50,
        "likes_acoustic": False,
    },
    "Nostalgic Country Road": {
        "favorite_genre": "country",
        "favorite_mood": "nostalgic",
        "target_energy": 0.60,
        "target_valence": 0.72,
        "likes_acoustic": True,
    },
    # --- Adversarial / Edge-Case Profiles ---
    "ADVERSARIAL: Sad Bangers": {
        # Conflict: wants maximum energy but sad mood.
        # Blues/sad song (Broken Clock Blues, energy=0.45) vs high-energy tracks.
        # Does mood match (+1.0) override the huge energy mismatch?
        "favorite_genre": "blues",
        "favorite_mood": "sad",
        "target_energy": 0.95,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },
    "ADVERSARIAL: Genre Ghost": {
        # Genre 'classical' does not exist in songs.csv.
        # The +2.0 genre bonus NEVER fires — all songs score at most 3.0.
        # Does the recommender degrade gracefully when no genre matches?
        "favorite_genre": "classical",
        "favorite_mood": "happy",
        "target_energy": 0.70,
        "target_valence": 0.90,
        "likes_acoustic": False,
    },
    "ADVERSARIAL: Acoustic Metalhead": {
        # Conflict: likes_acoustic=True but wants metal (Arctic Pulse, acousticness=0.07).
        # Arctic Pulse earns genre+mood+energy but misses the acoustic bonus.
        # Do highly acoustic soft songs sneak in over the perfect genre/mood match?
        "favorite_genre": "metal",
        "favorite_mood": "aggressive",
        "target_energy": 0.97,
        "target_valence": 0.30,
        "likes_acoustic": True,
    },
    "ADVERSARIAL: Valence Blindspot": {
        # target_valence=0.95 (very bright/positive), but score_song() never scores valence.
        # Expect the recommender to surface low-valence ambient/melancholic songs
        # because genre+mood+acoustic dominate and valence is silently ignored.
        "favorite_genre": "ambient",
        "favorite_mood": "melancholic",
        "target_energy": 0.50,
        "target_valence": 0.95,
        "likes_acoustic": True,
    },
}


def print_recommendations(label: str, recommendations: list) -> None:
    print("\n" + "=" * 40)
    print(f"  {label.upper()}")
    print("=" * 40)
    for i, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n#{i}  {song['title']} by {song['artist']}")
        print(f"    Score : {score:.2f} / 5.00")
        print(f"    Genre : {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"    Why   : {explanation}")
        print("-" * 40)


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for label, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)


if __name__ == "__main__":
    main()
