import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# LOAD DATA
df = pd.read_csv("music_df.csv")

with open("text_embeddings.pkl", "rb") as f:
    text_embeddings = pickle.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# CORE SEARCH (FIXED DIVERSITY)
# -------------------------
def search_music(query, top_n=10):

    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    audio = df["mood_score"].values
    base = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(base)[::-1]

    results = []
    seen_artists = set()
    genre_count = {}

    for i in idxs:
        artist = df.iloc[i]["track_artist"]
        genre = df.iloc[i]["playlist_genre"]

        if artist in seen_artists:
            continue

        if genre_count.get(genre, 0) >= 2:
            continue

        seen_artists.add(artist)
        genre_count[genre] = genre_count.get(genre, 0) + 1

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(base[i]), 3)
        })

        if len(results) == top_n:
            break

    return results

# -------------------------
# SIMILAR ARTISTS
# -------------------------
def get_similar_artists(artist, top_n=5):

    idxs = df[df["track_artist"] == artist].index
    if len(idxs) == 0:
        return []

    idx = idxs[0]

    sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
    sorted_idx = np.argsort(sim_scores)[::-1]

    seen = set()
    out = []

    for i in sorted_idx:
        a = df.iloc[i]["track_artist"]

        if a == artist or a in seen:
            continue

        seen.add(a)
        out.append(a)

        if len(out) == top_n:
            break

    return out

# -------------------------
# WEEKLY AI PICKS (TREND STYLE)
# -------------------------
def weekly_ai_picks(top_n=10):

    sample = df.sample(frac=0.2, random_state=42)

    picks = sample.sort_values("mood_score", ascending=False).head(top_n)

    return [
        {
            "song": row["track_artist"],
            "genre": row["playlist_genre"]
        }
        for _, row in picks.iterrows()
    ]

# -------------------------
# DEEZER
# -------------------------
def get_deezer(song):
    try:
        url = f"https://api.deezer.com/search?q={song}"
        res = requests.get(url).json()

        if "data" not in res or len(res["data"]) == 0:
            return None

        t = res["data"][0]

        return {
            "image": t["album"]["cover_big"],
            "preview": t["preview"]
        }

    except:
        return None
