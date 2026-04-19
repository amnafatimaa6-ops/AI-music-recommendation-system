import pandas as pd
import numpy as np
import pickle
import streamlit as st
import os
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA
# -------------------------
df1 = pd.read_csv("music_df.csv")
df2 = pd.read_csv("spotify_songs.csv")

df = pd.concat([df1, df2], ignore_index=True)
df = df.reset_index(drop=True)

df.drop_duplicates(subset=["track_artist", "playlist_genre"], inplace=True)

# SAFE CLEANING
num_cols = df.select_dtypes(include=["number"]).columns
str_cols = df.select_dtypes(include=["object", "string"]).columns

df[num_cols] = df[num_cols].fillna(0)
df[str_cols] = df[str_cols].fillna("Unknown")

# -------------------------
# MODEL
# -------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# -------------------------
# EMBEDDINGS FILE
# -------------------------
EMBED_PATH = "text_embeddings.pkl"

def build_embeddings():
    df["text"] = df["track_artist"].astype(str) + " " + df["playlist_genre"].astype(str)
    emb = model.encode(df["text"].tolist(), show_progress_bar=True)
    pickle.dump(emb, open(EMBED_PATH, "wb"))
    return emb

# -------------------------
# LOAD OR REBUILD EMBEDDINGS (FIX)
# -------------------------
if os.path.exists(EMBED_PATH):
    text_embeddings = pickle.load(open(EMBED_PATH, "rb"))

    # AUTO FIX MISMATCH
    if len(text_embeddings) != len(df):
        print("⚠️ Mismatch detected → rebuilding embeddings...")
        text_embeddings = build_embeddings()
else:
    print("⚠️ No embeddings found → building new ones...")
    text_embeddings = build_embeddings()

# -------------------------
# GENRE DISTRIBUTION
# -------------------------
genre_distribution = df['playlist_genre'].value_counts(normalize=True)

# -------------------------
# QUERY EXPANSION
# -------------------------
def expand_query(query, mode):
    if mode == "artist":
        return query + " similar artists songs albums music"
    if mode == "genre":
        return query + " playlist top songs artists"
    return query

# -------------------------
# RECOMMENDER
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query = expand_query(query, mode)

    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio = df['mood_score'].values

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
    audio = (audio - audio.min()) / (audio.max() - audio.min() + 1e-9)

    base_score = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(base_score)[::-1]

    results = []
    seen = set()

    for i in idxs:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        if artist in seen:
            continue

        penalty = genre_distribution.get(genre, 0)
        score = base_score[i] * (1 - penalty)

        seen.add(artist)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results

# -------------------------
# SIMILAR ARTISTS (FIXED + SAFE)
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    idx_list = df[df['track_artist'] == artist_name].index

    if len(idx_list) == 0:
        return ["No similar artists found"]

    idx = idx_list[0]

    if idx >= len(text_embeddings):
        return ["Rebuilding embeddings... restart app"]

    sim_scores = cosine_similarity(
        [text_embeddings[idx]],
        text_embeddings
    )[0]

    sorted_idx = np.argsort(sim_scores)[::-1]

    similar = []
    seen = set()

    for i in sorted_idx:

        if i >= len(df):
            continue

        artist = df.iloc[i]['track_artist']

        if artist == artist_name:
            continue

        if artist in seen:
            continue

        seen.add(artist)
        similar.append(artist)

        if len(similar) == top_n:
            break

    return similar
