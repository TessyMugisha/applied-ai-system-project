"""
Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main                # run both scoring and RAG modes
    python -m src.main --mode scores  # rule-based scoring only
    python -m src.main --mode rag     # AI-generated RAG recommendations only
    python -m src.main --mode all     # explicit: both modes (same as default)

RAG mode requires the ANTHROPIC_API_KEY environment variable to be set.
"""

import argparse
import logging
import os

from .recommender import load_songs, recommend_songs

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


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
        "favorite_genre": "blues",
        "favorite_mood": "sad",
        "target_energy": 0.95,
        "target_valence": 0.20,
        "likes_acoustic": False,
    },
    "ADVERSARIAL: Genre Ghost": {
        "favorite_genre": "classical",
        "favorite_mood": "happy",
        "target_energy": 0.70,
        "target_valence": 0.90,
        "likes_acoustic": False,
    },
    "ADVERSARIAL: Acoustic Metalhead": {
        "favorite_genre": "metal",
        "favorite_mood": "aggressive",
        "target_energy": 0.97,
        "target_valence": 0.30,
        "likes_acoustic": True,
    },
    "ADVERSARIAL: Valence Blindspot": {
        "favorite_genre": "ambient",
        "favorite_mood": "melancholic",
        "target_energy": 0.50,
        "target_valence": 0.95,
        "likes_acoustic": True,
    },
}

# Natural language queries that map each profile into the RAG retrieval step.
# These replace the structured dicts and let TF-IDF + Claude do the work.
RAG_QUERIES = {
    "Late Night Jazz":              "relaxing jazz late night acoustic low energy calm mellow saxophone",
    "Synthwave Night Drive":        "moody synthwave electronic night driving atmospheric medium energy",
    "Nostalgic Country Road":       "nostalgic country acoustic warm folk wistful medium energy guitar",
    "ADVERSARIAL: Sad Bangers":     "sad blues but very high energy intense powerful non-acoustic",
    "ADVERSARIAL: Genre Ghost":     "classical orchestral peaceful happy high energy",
    "ADVERSARIAL: Acoustic Metalhead": "aggressive metal acoustic high energy very intense",
    "ADVERSARIAL: Valence Blindspot":  "ambient melancholic acoustic medium energy atmospheric background",
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


def run_scores_mode(songs: list) -> None:
    """Run the rule-based scoring recommender for every profile."""
    logger.info("Starting scores mode for %d profiles", len(PROFILES))
    print("\n" + "#" * 50)
    print("  SCORING MODE — Rule-Based Recommendations")
    print("#" * 50)
    for label, user_prefs in PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print_recommendations(label, recommendations)
    logger.info("Scores mode complete")


def run_rag_mode(songs: list) -> None:
    """
    Run the RAG pipeline for every profile.

    Retrieval: TF-IDF cosine similarity over song descriptions selects the
               most relevant songs for each natural language query.
    Generation: Claude receives ONLY the retrieved songs and must recommend
                from them, grounding every suggestion in catalog data.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            "\n[RAG mode skipped] ANTHROPIC_API_KEY is not set.\n"
            "  Set it with:  export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  Then re-run:  python -m src.main --mode rag"
        )
        logger.warning("RAG mode skipped: ANTHROPIC_API_KEY not set")
        return

    try:
        import anthropic
        from .rag_recommender import build_index, rag_recommend
    except ImportError as exc:
        print(f"\n[RAG mode error] Missing dependency: {exc}")
        print("  Install with: pip install anthropic scikit-learn")
        logger.error("Import error in RAG mode: %s", exc)
        return

    client = anthropic.Anthropic(api_key=api_key)

    try:
        vectorizer, matrix = build_index(songs)
    except Exception as exc:
        print(f"\n[RAG mode error] Failed to build TF-IDF index: {exc}")
        logger.exception("build_index failed")
        return

    print("\n" + "#" * 50)
    print("  RAG MODE — AI-Generated Recommendations")
    print("  (Retrieve → Augment → Generate via Claude)")
    print("#" * 50)

    for label, query in RAG_QUERIES.items():
        print("\n" + "=" * 50)
        print(f"  {label.upper()}")
        print(f"  Query : \"{query}\"")
        print("=" * 50)

        try:
            recommendation, retrieved = rag_recommend(
                query=query,
                songs=songs,
                vectorizer=vectorizer,
                matrix=matrix,
                client=client,
                k=5,
            )
        except anthropic.APIStatusError as exc:
            print(f"  [API error] {exc.status_code}: {exc.message}")
            logger.error("Anthropic API error for '%s': %s", label, exc)
            continue
        except Exception as exc:
            print(f"  [Error] RAG failed: {exc}")
            logger.exception("RAG pipeline failed for profile '%s'", label)
            continue

        print(f"\n  Retrieved context ({len(retrieved)} songs):")
        for s in retrieved:
            print(f"    - {s['title']} by {s['artist']} "
                  f"[{s['genre']}, {s['mood']}, energy={s['energy']}, "
                  f"sim={s['_similarity']}]")

        print("\n  Claude's recommendation:\n")
        for line in recommendation.splitlines():
            print(f"    {line}")
        print("-" * 50)

    logger.info("RAG mode complete")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Music Recommender — rule-based scoring and/or RAG via Claude"
    )
    parser.add_argument(
        "--mode",
        choices=["scores", "rag", "all"],
        default="all",
        help=(
            "scores: rule-based scoring only | "
            "rag: AI-generated RAG recommendations only | "
            "all: both modes (default)"
        ),
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    logger.info("Loaded %d songs from catalog", len(songs))
    print(f"Loaded {len(songs)} songs from catalog.")

    if args.mode in ("scores", "all"):
        run_scores_mode(songs)

    if args.mode in ("rag", "all"):
        run_rag_mode(songs)


if __name__ == "__main__":
    main()
