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
# LOAD MODEL
# -------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# SEARCH FUNCTION (SAFE)
# -------------------------
def search_music(query, mode="artist", top_n=10):

    if text_embeddings is None or df.empty:
        return []

    query_vec = model.encode([query])

    sim = cosine_similarity(query_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    audio = df["mood_score"].values

    base = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(base)[::-1]

    results = []

    for i in idxs[:top_n]:

        results.append({
            "song": str(df.iloc[i]["track_artist"]),
            "genre": str(df.iloc[i]["playlist_genre"]),
            "score": round(float(base[i]), 3)
        })

    return results

# -------------------------
# SIMILAR ARTISTS
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    if text_embeddings is None or df.empty:
        return []

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
# DEEZER API (SAFE)
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
