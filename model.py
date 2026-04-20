import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD & MERGE DATASETS
# -------------------------
def load_data():

    try:
        df1 = pd.read_csv("data/music_df.csv")
    except:
        df1 = pd.DataFrame()

    try:
        df2 = pd.read_csv("data/spotify_songs.csv")
    except:
        df2 = pd.DataFrame()

    try:
        df3 = pd.read_csv("data/data_by_artist.csv")
    except:
        df3 = pd.DataFrame()

    def clean(df):

        if df.empty:
            return df

        df = df.copy()

        # Artist column
        if "track_artist" not in df.columns:
            if "artist" in df.columns:
                df["track_artist"] = df["artist"]
            elif "artists" in df.columns:
                df["track_artist"] = df["artists"]

        # Genre column
        if "playlist_genre" not in df.columns:
            if "genre" in df.columns:
                df["playlist_genre"] = df["genre"]
            else:
                df["playlist_genre"] = "unknown"

        # Mood score
        if "mood_score" not in df.columns:
            df["mood_score"] = np.random.rand(len(df))

        return df[["track_artist", "playlist_genre", "mood_score"]]

    df1 = clean(df1)
    df2 = clean(df2)
    df3 = clean(df3)

    df = pd.concat([df1, df2, df3], ignore_index=True)

    df.dropna(inplace=True)
    df.drop_duplicates(subset=["track_artist"], inplace=True)

    return df


df = load_data()

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
# SEARCH FUNCTION
# -------------------------
def search_music(query, top_n=10):

    if df.empty:
        return []

    # Fallback if embeddings not available
    if model is None or text_embeddings is None:

        filtered = df[df["track_artist"].str.contains(str(query), case=False, na=False)]

        if filtered.empty:
            filtered = df.sample(min(top_n, len(df)))

        return [
            {
                "song": row["track_artist"],
                "genre": row["playlist_genre"],
                "score": 0.5
            }
            for _, row in filtered.head(top_n).iterrows()
        ]

    # AI search
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

# -------------------------
# DEEZER API
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
