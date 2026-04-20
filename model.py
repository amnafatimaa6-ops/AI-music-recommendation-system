import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# SAFE LOAD DATA
# -------------------------
try:
    df = pd.read_csv("music_df.csv")
except:
    df = pd.DataFrame(columns=["track_artist", "playlist_genre", "mood_score"])

# -------------------------
# SAFE LOAD EMBEDDINGS
# -------------------------
try:
    with open("text_embeddings.pkl", "rb") as f:
        text_embeddings = pickle.load(f)
except:
    text_embeddings = None

# -------------------------
# SAFE LOAD MODEL
# -------------------------
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except:
    model = None

# -------------------------
# SEARCH (SAFE)
# -------------------------
def search_music(query, top_n=10):

    if model is None or text_embeddings is None or df.empty:
        return []

    try:
        query_vec = model.encode([query])
        sim = cosine_similarity(query_vec, text_embeddings)[0]

        sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
        audio = df["mood_score"].values

        base = 0.6 * sim + 0.4 * audio

        idxs = np.argsort(base)[::-1]

        results = []
        seen = set()

        for i in idxs:

            artist = df.iloc[i]["track_artist"]

            if artist in seen:
                continue

            seen.add(artist)

            results.append({
                "song": artist,
                "genre": df.iloc[i]["playlist_genre"],
                "score": round(float(base[i]), 3)
            })

            if len(results) == top_n:
                break

        return results

    except:
        return []

# -------------------------
# SIMILAR ARTISTS (SAFE)
# -------------------------
def get_similar_artists(artist, top_n=5):

    if text_embeddings is None or df.empty:
        return []

    try:
        idxs = df[df["track_artist"] == artist].index

        if len(idxs) == 0:
            return []

        idx = idxs[0]

        sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
        sorted_idx = np.argsort(sim_scores)[::-1]

        out = []
        seen = set()

        for i in sorted_idx:

            a = df.iloc[i]["track_artist"]

            if a == artist or a in seen:
                continue

            seen.add(a)
            out.append(a)

            if len(out) == top_n:
                break

        return out

    except:
        return []

# -------------------------
# DEEZER SAFE
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
