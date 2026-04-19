import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("music_df.csv")

# -------------------------
# LOAD EMBEDDINGS
# -------------------------
def load_embeddings():
    with open("text_embeddings.pkl", "rb") as f:
        return pickle.load(f)

text_embeddings = load_embeddings()

# -------------------------
# LOAD MODEL
# -------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# GENRE DISTRIBUTION (for balancing)
# -------------------------
genre_distribution = df['playlist_genre'].value_counts(normalize=True)

# -------------------------
# MOOD BIAS ENGINE (FIX FOR POP BIAS)
# -------------------------
def mood_bias(query):
    q = query.lower()

    if "sad" in q:
        return {"valence": -0.5, "energy": -0.2}
    elif "happy" in q:
        return {"valence": 0.5, "energy": 0.2}
    elif "chill" in q:
        return {"energy": -0.3}
    elif "gym" in q or "hype" in q:
        return {"energy": 0.6}
    elif "love" in q:
        return {"valence": 0.3}
    else:
        return {}

# -------------------------
# EXPAND QUERY (your original idea preserved)
# -------------------------
def expand_query(query, mode):
    if mode == "artist":
        return query + " similar artists songs albums music"
    if mode == "genre":
        return query + " playlist top songs artists"
    return query

# -------------------------
# MAIN RECOMMENDER (UPGRADED)
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query = expand_query(query, mode)

    # embeddings similarity
    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    # audio features
    energy = df["energy"].values
    valence = df["valence"].values

    # normalize similarity
    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    # base score
    base_score = 0.6 * sim + 0.4 * (df["mood_score"].values)

    # -------------------------
    # APPLY MOOD BIAS (IMPORTANT FIX)
    # -------------------------
    bias = mood_bias(query)

    if "energy" in bias:
        base_score += bias["energy"] * energy

    if "valence" in bias:
        base_score += bias["valence"] * valence

    # -------------------------
    # SORT
    # -------------------------
    idxs = np.argsort(base_score)[::-1]

    results = []
    seen_artists = set()
    seen_genres = set()

    for i in idxs:

        artist = df.iloc[i]["track_artist"]
        genre = df.iloc[i]["playlist_genre"]

        # -------------------------
        # DIVERSITY CONTROL (CRITICAL FIX)
        # -------------------------
        if artist in seen_artists:
            continue

        # avoid genre flooding
        if genre in seen_genres and len(seen_genres) < 5:
            continue

        seen_artists.add(artist)
        seen_genres.add(genre)

        # genre penalty (keeps balance)
        penalty = genre_distribution.get(genre, 0)

        score = base_score[i] * (1 - penalty)

        # slight randomness for discovery
        score += np.random.uniform(-0.02, 0.02)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results

# -------------------------
# SIMILAR ARTISTS (UNCHANGED LOGIC, SAFE VERSION)
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    matches = df[df["track_artist"] == artist_name].index

    if len(matches) == 0:
        return []

    idx = matches[0]

    sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
    sorted_idx = np.argsort(sim_scores)[::-1]

    similar = []
    seen = set()

    for i in sorted_idx:

        artist = df.iloc[i]["track_artist"]

        if artist == artist_name:
            continue

        if artist in seen:
            continue

        seen.add(artist)
        similar.append(artist)

        if len(similar) == top_n:
            break

    return similar
