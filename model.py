import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# DATA
# -------------------------
df = pd.read_csv("music_df.csv")

with open("text_embeddings.pkl", "rb") as f:
    text_embeddings = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# GLOBAL GENRE STATS
# -------------------------
genre_distribution = df["playlist_genre"].value_counts(normalize=True)

# -------------------------
# 🧠 LAYER 1: EMOTION BRAIN
# -------------------------
MOOD_MAP = {
    "energetic": {"energy": 0.7, "valence": 0.3},
    "sad": {"energy": -0.5, "valence": -0.6},
    "happy": {"energy": 0.4, "valence": 0.7},
    "chill": {"energy": -0.5},
    "romantic": {"valence": 0.5},
    "party": {"energy": 0.8},
    "focus": {"energy": -0.2}
}

def get_mood_vector(query):
    q = query.lower()
    for mood in MOOD_MAP:
        if mood in q:
            return MOOD_MAP[mood]
    return {}

# -------------------------
# 🧠 LAYER 2: QUERY EXPANSION
# -------------------------
def expand_query(query, mode):
    if mode == "artist":
        return query + " similar artists songs albums music"
    if mode == "genre":
        return query + " top playlist songs trending"
    return query

# -------------------------
# 🚀 MAIN BRAIN ENGINE
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query_expanded = expand_query(query, mode)

    query_vec = model.encode([query_expanded])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    audio_energy = df["energy"].values
    audio_valence = df["valence"].values

    base_score = 0.65 * sim + 0.35 * df["mood_score"].values

    # -------------------------
    # 🧠 APPLY MOOD BRAIN
    # -------------------------
    mood = get_mood_vector(query)

    if "energy" in mood:
        base_score += mood["energy"] * audio_energy

    if "valence" in mood:
        base_score += mood["valence"] * audio_valence

    # -------------------------
    # SORTING
    # -------------------------
    idxs = np.argsort(base_score)[::-1]

    results = []

    # 🧠 LAYER 3: DIVERSITY BRAIN
    genre_count = {}
    seen_artists = set()

    for i in idxs:

        artist = df.iloc[i]["track_artist"]
        genre = df.iloc[i]["playlist_genre"]

        # avoid duplicates
        if artist in seen_artists:
            continue

        # HARD genre limit (Spotify style)
        if genre_count.get(genre, 0) >= 2:
            continue

        genre_count[genre] = genre_count.get(genre, 0) + 1
        seen_artists.add(artist)

        # rarity boost (underground discovery)
        rarity_boost = np.log1p(1 / (genre_distribution.get(genre, 0) + 1e-6))

        score = base_score[i] + 0.1 * rarity_boost
        score += np.random.uniform(-0.015, 0.015)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results

# -------------------------
# 🎤 SIMILAR ARTISTS ENGINE (IMPROVED)
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    idxs = df[df["track_artist"] == artist_name].index

    if len(idxs) == 0:
        return []

    idx = idxs[0]

    sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
    sorted_idx = np.argsort(sim_scores)[::-1]

    seen = set()
    results = []

    for i in sorted_idx:

        artist = df.iloc[i]["track_artist"]

        if artist == artist_name:
            continue

        if artist in seen:
            continue

        seen.add(artist)
        results.append(artist)

        if len(results) == top_n:
            break

    return results
