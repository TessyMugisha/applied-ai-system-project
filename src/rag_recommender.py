import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Synonym maps make TF-IDF match natural language queries to song attribute vocabulary
MOOD_SYNONYMS: Dict[str, str] = {
    "relaxed":    "relaxing calm soothing peaceful mellow quiet",
    "chill":      "chilled laid-back easy casual relaxed gentle",
    "happy":      "upbeat joyful cheerful positive bright fun",
    "intense":    "powerful energetic strong forceful driven hard",
    "focused":    "concentrated steady productive calm clear sharp",
    "melancholic": "melancholy sad wistful bittersweet somber pensive",
    "moody":      "dark brooding atmospheric introspective mysterious",
    "nostalgic":  "retro warm old-fashioned past wistful sentimental",
    "uplifting":  "inspiring motivating positive hopeful encouraging",
    "energetic":  "lively active dynamic vibrant bouncy",
    "sad":        "sorrowful blue melancholy heartfelt somber tearful",
    "aggressive": "intense fierce powerful hard heavy raw angry",
}

GENRE_SYNONYMS: Dict[str, str] = {
    "jazz":       "jazz saxophone piano swing bebop smooth",
    "lofi":       "lo-fi lofi study chill beats background",
    "rock":       "rock guitar band loud driven powerful",
    "ambient":    "ambient atmospheric background soundscape environmental peaceful",
    "pop":        "pop popular mainstream catchy radio commercial",
    "synthwave":  "synthwave electronic retro synth 80s neon futuristic",
    "country":    "country folk americana guitar fiddle southern",
    "electronic": "electronic edm dance beats club digital",
    "kpop":       "kpop k-pop korean pop",
    "folk":       "folk acoustic storytelling traditional singer-songwriter",
    "gospel":     "gospel choir uplifting spiritual religious",
    "latin":      "latin salsa tropical rhythmic caribbean",
    "metal":      "metal heavy guitars aggressive loud intense",
    "blues":      "blues soul rhythm guitar soulful expressive",
    "indie pop":  "indie alternative pop guitar art",
}


def _energy_label(val: float) -> str:
    if val < 0.3:
        return "very low low quiet soft gentle"
    if val < 0.55:
        return "medium moderate mid"
    if val < 0.75:
        return "high energetic active"
    return "very high intense powerful maximum"


def _acoustic_label(val: float) -> str:
    if val >= 0.65:
        return "acoustic unplugged natural warm organic"
    if val >= 0.35:
        return "semi-acoustic mixed"
    return "electric non-acoustic digital synthetic"


def build_song_descriptions(songs: List[Dict]) -> List[str]:
    """Convert each song into a rich text description including synonym expansions."""
    descriptions = []
    for song in songs:
        genre = song["genre"]
        mood = song["mood"]
        desc = (
            f"{song['title']} by {song['artist']}. "
            f"Genre: {genre} {GENRE_SYNONYMS.get(genre, '')}. "
            f"Mood: {mood} {MOOD_SYNONYMS.get(mood, '')}. "
            f"Energy: {_energy_label(song['energy'])} ({song['energy']}). "
            f"Sound: {_acoustic_label(song['acousticness'])} "
            f"(acousticness={song['acousticness']}). "
            f"Valence: {song['valence']}. Tempo: {song['tempo_bpm']} BPM."
        )
        descriptions.append(desc)
    return descriptions


def build_index(songs: List[Dict]):
    """Fit a TF-IDF vectorizer over song descriptions. Returns (vectorizer, matrix)."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError as exc:
        raise ImportError(
            "scikit-learn is required for RAG retrieval. "
            "Install it with: pip install scikit-learn"
        ) from exc

    descriptions = build_song_descriptions(songs)
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", min_df=1)
    matrix = vectorizer.fit_transform(descriptions)
    logger.info("TF-IDF index built: %d songs, %d features", len(songs), matrix.shape[1])
    return vectorizer, matrix


def retrieve(query: str, vectorizer, matrix, songs: List[Dict], k: int = 5) -> List[Dict]:
    """Return the top-k songs most similar to the query using cosine similarity."""
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    query_vec = vectorizer.transform([query])
    sims = cosine_similarity(query_vec, matrix).flatten()
    top_indices = np.argsort(sims)[-k:][::-1]

    retrieved = []
    for idx in top_indices:
        song = dict(songs[idx])
        song["_similarity"] = round(float(sims[idx]), 4)
        retrieved.append(song)

    logger.info(
        "Retrieved %d songs for query %r: %s",
        len(retrieved),
        query[:70],
        [(s["title"], s["_similarity"]) for s in retrieved],
    )
    return retrieved


def generate(query: str, retrieved_songs: List[Dict], client) -> str:
    """
    Call Claude API with retrieved songs as context and return a grounded recommendation.

    Claude must only recommend from the retrieved list, ensuring the generated
    response is fully anchored to the retrieval step.
    """
    if not retrieved_songs:
        logger.warning("No songs retrieved — returning fallback message without calling API")
        return "No relevant songs were found in the catalog for this query."

    context = "\n".join(
        f"  [{i + 1}] \"{s['title']}\" by {s['artist']} | "
        f"genre={s['genre']} | mood={s['mood']} | energy={s['energy']} | "
        f"acousticness={s['acousticness']} | valence={s['valence']}"
        for i, s in enumerate(retrieved_songs)
    )

    prompt = (
        f"You are a music recommendation assistant with access to a song catalog.\n\n"
        f"User request: \"{query}\"\n\n"
        f"Songs retrieved from catalog:\n{context}\n\n"
        f"Instructions:\n"
        f"- Select the 1–3 best matches from the retrieved list for this user's request.\n"
        f"- For each chosen song, write 1–2 sentences explaining WHY it fits — "
        f"reference its specific attributes (mood, genre, energy, acousticness).\n"
        f"- Do NOT recommend any song that is not in the retrieved list.\n"
        f"- If none of the retrieved songs are a good fit, say so clearly and explain the mismatch.\n"
        f"- Keep your tone friendly and conversational."
    )

    logger.info("Calling Claude API with %d songs as context", len(retrieved_songs))

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    logger.info("Claude response: %d characters", len(text))
    return text


def rag_recommend(
    query: str,
    songs: List[Dict],
    vectorizer,
    matrix,
    client,
    k: int = 5,
) -> Tuple[str, List[Dict]]:
    """Full RAG pipeline: retrieve relevant songs from catalog, then generate via Claude."""
    retrieved = retrieve(query, vectorizer, matrix, songs, k=k)
    recommendation = generate(query, retrieved, client)
    return recommendation, retrieved
