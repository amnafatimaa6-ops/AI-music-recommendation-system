import pandas as pd
import numpy as np
import pickle

# -------------------------
# LOAD DATASETS
# -------------------------
def load_data():

    files = [
        "data/music_df.csv",
        "data/spotify_songs.csv",
        "data/data_by_artist.csv"
    ]

    dfs = []

    for f in files:
        try:
            dfs.append(pd.read_csv(f))
        except:
            pass

    df = pd.concat(dfs, ignore_index=True)

    # -------------------------
    # STANDARDIZE COLUMNS
    # -------------------------
    if "track_artist" not in df.columns:
        if "artist" in df.columns:
            df["track_artist"] = df["artist"]
        elif "artists" in df.columns:
            df["track_artist"] = df["artists"]

    if "track_name" not in df.columns:
        if "song" in df.columns:
            df["track_name"] = df["song"]
        else:
            df["track_name"] = df["track_artist"]

    if "playlist_genre" not in df.columns:
        if "genre" in df.columns:
            df["playlist_genre"] = df["genre"]
        else:
            df["playlist_genre"] = "unknown"

    df["track_artist"] = df["track_artist"].fillna("unknown")
    df["track_name"] = df["track_name"].fillna(df["track_artist"])
    df["playlist_genre"] = df["playlist_genre"].fillna("unknown")

    df = df.drop_duplicates(subset=["track_artist", "track_name"])
    df = df.reset_index(drop=True)

    return df


df = load_data()


# -------------------------
# 🔍 SEARCH (DATASET ONLY - CLEAN & RELIABLE)
# -------------------------
def search_music(query, top_n=10):

    q = query.lower().strip()

    mask = (
        df["track_artist"].str.lower().str.contains(q) |
        df["track_name"].str.lower().str.contains(q) |
        df["playlist_genre"].str.lower().str.contains(q)
    )

    results = df[mask].head(top_n)

    if results.empty:
        results = df.sample(min(top_n, len(df)))

    return [
        {
            "song": r["track_name"],
            "artist": r["track_artist"],
            "genre": r["playlist_genre"],
            "score": 1.0
        }
        for _, r in results.iterrows()
    ]


# -------------------------
# 🎧 RECOMMENDATION ENGINE (NO RANDOM CHAOS)
# -------------------------
def recommend(query, top_n=10):

    q = query.lower()

    filtered = df.copy()

    # genre-based filtering (strong logic)
    if "pop" in q:
        filtered = df[df["playlist_genre"].str.contains("pop", na=False)]

    elif "rap" in q or "hip" in q:
        filtered = df[df["playlist_genre"].str.contains("hip-hop|rap", na=False)]

    elif "rock" in q:
        filtered = df[df["playlist_genre"].str.contains("rock", na=False)]

    # fallback
    if filtered.empty:
        filtered = df.copy()

    # ranking using stable signal only
    filtered = filtered.copy()
    filtered["score"] = (
        filtered["mood_score"].fillna(0.5)
    )

    top = filtered.sort_values("score", ascending=False).head(top_n)

    return [
        {
            "song": r["track_name"],
            "artist": r["track_artist"],
            "genre": r["playlist_genre"],
            "score": round(float(r["score"]), 3)
        }
        for _, r in top.iterrows()
    ]


# -------------------------
# 🎤 SIMILAR ARTISTS (GENRE CLUSTER BASED)
# -------------------------
def get_similar_artists(artist, top_n=5):

    subset = df[df["track_artist"].str.lower() == artist.lower()]

    if subset.empty:
        return []

    genre = subset.iloc[0]["playlist_genre"]

    similar = df[df["playlist_genre"] == genre]["track_artist"].drop_duplicates()

    return list(similar.head(top_n))


# -------------------------
# 🔥 TRENDING (POPULARITY-BASED)
# -------------------------
def get_weekly_trending(top_n=10):

    top = df["track_artist"].value_counts().head(top_n)

    return [
        {"song": artist, "genre": "trending"}
        for artist in top.index
    ]
