import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("music_df.csv")

with open("text_embeddings.pkl", "rb") as f:
    text_embeddings = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# GENRE DISTRIBUTION
# -------------------------
genre_distribution = df["playlist_genre"].value_counts(normalize=True)

# -------------------------
# QUERY EXPANSION
# -------------------------
def expand_query(query, mode):
    if mode == "artist":
        return query + " songs music albums artist"
    if mode == "genre":
        return query + " playlist top songs"
    return query

# -------------------------
# RECOMMENDER
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query = expand_query(query, mode)

    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    audio_score = df["mood_score"].values

    base_score = 0.6 * sim + 0.4 * audio_score

    idxs = np.argsort(base_score)[::-1]

    results = []
    seen = set()
    genre_count = {}

    for i in idxs:

        artist = df.iloc[i]["track_artist"]
        genre = df.iloc[i]["playlist_genre"]

        if artist in seen:
            continue

        if genre_count.get(genre, 0) >= 2:
            continue

        genre_count[genre] = genre_count.get(genre, 0) + 1
        seen.add(artist)

        penalty = genre_distribution.get(genre, 0)
        score = base_score[i] * (1 - penalty)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results

# -------------------------
# SIMILAR ARTISTS
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    idxs = df[df["track_artist"] == artist_name].index

    if len(idxs) == 0:
        return []

    idx = idxs[0]

    sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
    sorted_idx = np.argsort(sim_scores)[::-1]

    seen = set()
    out = []

    for i in sorted_idx:

        artist = df.iloc[i]["track_artist"]

        if artist == artist_name:
            continue

        if artist in seen:
            continue

        seen.add(artist)
        out.append(artist)

        if len(out) == top_n:
            break

    return out

# -------------------------
# DEEZER API
# -------------------------
def get_deezer(song):
    url = f"https://api.deezer.com/search?q={song}"
    res = requests.get(url).json()

    if "data" not in res or len(res["data"]) == 0:
        return None

    t = res["data"][0]

    return {
        "image": t["album"]["cover_big"],
        "preview": t["preview"]
    }
