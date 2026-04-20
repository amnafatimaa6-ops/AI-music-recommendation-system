import pandas as pd
import numpy as np
import pickle
import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATASETS
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

        if "track_artist" not in df.columns:
            if "artist" in df.columns:
                df["track_artist"] = df["artist"]
            elif "artists" in df.columns:
                df["track_artist"] = df["artists"]

        if "playlist_genre" not in df.columns:
            if "genre" in df.columns:
                df["playlist_genre"] = df["genre"]
            else:
                df["playlist_genre"] = "unknown"

        if "mood_score" not in df.columns:
            df["mood_score"] = np.random.rand(len(df))

        return df[["track_artist", "playlist_genre", "mood_score"]]

    df = pd.concat([clean(df1), clean(df2), clean(df3)], ignore_index=True)

    df.dropna(inplace=True)
    df.drop_duplicates(subset=["track_artist"], inplace=True)

    return df


df = load_data()

# -------------------------
# EMBEDDINGS + MODEL
# -------------------------
try:
    with open("text_embeddings.pkl", "rb") as f:
        text_embeddings = pickle.load(f)
except:
    text_embeddings = None

try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
except:
    model = None


# -------------------------
# MAIN SEARCH (IMPROVED LOGIC)
# -------------------------
def search_music(query, top_n=10):

    if df.empty:
        return []

    # fallback mode
    if model is None or text_embeddings is None:

        filtered = df[df["track_artist"].str.contains(query, case=False, na=False)]

        if filtered.empty:
            filtered = df.sample(min(top_n, len(df)))

        return [
            {
                "song": r["track_artist"],
                "genre": r["playlist_genre"],
                "score": 0.5
            }
            for _, r in filtered.head(top_n).iterrows()
        ]

    # -------------------------
    # SEMANTIC SIMILARITY
    # -------------------------
    q_vec = model.encode([query])
    sim = cosine_similarity(q_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    # -------------------------
    # AUDIO SIGNAL
    # -------------------------
    audio = df["mood_score"].values
    audio = (audio - audio.min()) / (audio.max() - audio.min() + 1e-9)

    # -------------------------
    # GENRE BOOST LOGIC
    # -------------------------
    genre_boost = np.ones(len(df))

    q = query.lower()

    if "taylor" in q or "swift" in q:
        genre_boost += (df["playlist_genre"] == "pop") * 0.4

    if "drake" in q or "rap" in q:
        genre_boost += (df["playlist_genre"].isin(["hip-hop", "rap"])) * 0.5

    if "rock" in q:
        genre_boost += (df["playlist_genre"] == "rock") * 0.4

    # -------------------------
    # FINAL SCORE
    # -------------------------
    score = (0.65 * sim) + (0.25 * audio) + (0.10 * genre_boost)

    idxs = np.argsort(score)[::-1]

    results = []
    seen = set()

    for i in idxs:

        artist = df.iloc[i]["track_artist"]

        if artist in seen:
            continue

        if score[i] < 0.55:
            continue

        seen.add(artist)

        results.append({
            "song": artist,
            "genre": df.iloc[i]["playlist_genre"],
            "score": round(float(score[i]), 3)
        })

        if len(results) == top_n:
            break

    return results


# -------------------------
# SIMILAR ARTISTS
# -------------------------
def get_similar_artists(artist, top_n=5):

    if df.empty or text_embeddings is None:
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
# WEEKLY TRENDING
# -------------------------
def get_weekly_trending(top_n=10):

    temp = df.copy()
    temp["trend"] = temp["mood_score"] + np.random.rand(len(temp)) * 0.3

    top = temp.sort_values("trend", ascending=False).head(top_n)

    return [
        {
            "song": r["track_artist"],
            "genre": r["playlist_genre"]
        }
        for _, r in top.iterrows()
    ]


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
