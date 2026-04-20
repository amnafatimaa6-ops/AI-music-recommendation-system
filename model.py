import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA (FIXED PATH SAFETY)
# -------------------------
try:
    df = pd.read_csv("data/music_df.csv")
except:
    try:
        df = pd.read_csv("music_df.csv")
    except:
        df = pd.DataFrame()

# -------------------------
# COLUMN FIX (SAFE)
# -------------------------
if not df.empty:

    if "track_artist" not in df.columns:
        if "artist" in df.columns:
            df["track_artist"] = df["artist"]
        elif "artists" in df.columns:
            df["track_artist"] = df["artists"]
        else:
            df["track_artist"] = "unknown"

    if "playlist_genre" not in df.columns:
        if "genre" in df.columns:
            df["playlist_genre"] = df["genre"]
        else:
            df["playlist_genre"] = "unknown"

    if "mood_score" not in df.columns:
        df["mood_score"] = np.random.rand(len(df))

    df = df.dropna()
    df = df.reset_index(drop=True)

# -------------------------
# LOAD EMBEDDINGS
# -------------------------
try:
    with open("text_embeddings.pkl", "rb") as f:
        text_embeddings = pickle.load(f)
except:
    text_embeddings = None

# -------------------------
# LOAD MODEL
# -------------------------
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except:
    model = None


# -------------------------
# 🔍 SEARCH (UNCHANGED LOGIC)
# -------------------------
def search_music(query, top_n=10):

    if df.empty:
        return []

    try:
        query_vec = model.encode([query])
        sim = cosine_similarity(query_vec, text_embeddings)[0]

        sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

        audio = df["mood_score"].values[:len(sim)]

        base = 0.6 * sim + 0.4 * audio

        idxs = np.argsort(base)[::-1]

        results = []
        seen = set()

        for i in idxs:

            if i >= len(df):
                continue

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
# 🎤 SIMILAR ARTISTS (WITH ALBUM COVERS)
# -------------------------
def get_similar_artists(artist, top_n=5):

    if df.empty:
        return []

    try:
        subset = df[df["track_artist"] == artist]

        if subset.empty:
            return []

        genre = subset.iloc[0]["playlist_genre"]

        similar = df[df["playlist_genre"] == genre]["track_artist"].drop_duplicates()

        results = []

        for a in similar.head(top_n):

            cover = get_deezer(a)

            results.append({
                "artist": a,
                "image": cover["image"] if cover else None
            })

        return results

    except:
        return []


# -------------------------
# 🔥 WEEKLY TRENDING AI SONGS (WITH COVERS)
# -------------------------
def get_weekly_trending(top_n=10):

    if df.empty:
        return []

    try:
        top = df["track_artist"].value_counts().head(top_n)

        results = []

        for artist in top.index:

            cover = get_deezer(artist)

            results.append({
                "artist": artist,
                "image": cover["image"] if cover else None
            })

        return results

    except:
        return []


# -------------------------
# 🎧 DEEZER API (UNCHANGED)
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
