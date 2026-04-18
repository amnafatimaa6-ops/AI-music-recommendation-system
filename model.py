import pandas as pd
import numpy as np
import pickle
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD MAIN DATA
# -------------------------
df = pd.read_csv("music_df.csv")

# -------------------------
# MERGE EXTRA DATASET (KAGGLE)
# -------------------------
try:
    extra_df = pd.read_csv("spotify_songs.csv")

    # Keep only useful columns if they exist
    keep_cols = [
        "track_artist","playlist_genre","playlist_subgenre",
        "energy","danceability","valence","tempo","loudness",
        "speechiness","acousticness","instrumentalness"
    ]

    extra_df = extra_df[[c for c in keep_cols if c in extra_df.columns]]

    # Fill missing
    for col in keep_cols:
        if col not in extra_df.columns:
            extra_df[col] = 0

    extra_df.fillna(0, inplace=True)

    # Feature engineering (same style)
    extra_df['mood_score'] = (extra_df['valence'] * 0.6) + (extra_df['energy'] * 0.4)

    # Merge
    df = pd.concat([df, extra_df], ignore_index=True)
    df.drop_duplicates(inplace=True)

except:
    pass

# -------------------------
# LOAD EMBEDDINGS
# -------------------------
@st.cache_data
def load_embeddings():
    return pickle.load(open("text_embeddings.pkl", "rb"))

text_embeddings = load_embeddings()

# -------------------------
# LOAD MODEL
# -------------------------
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()

# -------------------------
# GENRE BALANCE
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
# MAIN SEARCH
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query = expand_query(query, mode)

    query_vec = model.encode([query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio = df['mood_score'].values

    # Normalize
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

        if mode == "artist" and artist == query:
            score += 0.2

        score += np.random.uniform(-0.02, 0.02)

        seen.add(artist)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    # FALLBACK SYSTEM
    if len(results) < 3:
        fallback = df.sort_values("mood_score", ascending=False).head(10)

        for i in fallback.index:
            results.append({
                "song": df.iloc[i]["track_artist"],
                "genre": df.iloc[i]["playlist_genre"],
                "score": round(float(df.iloc[i]["mood_score"]), 3)
            })

    return results

# -------------------------
# SIMILAR ARTISTS
# -------------------------
def get_similar_artists(artist_name, top_n=5):

    idx_list = df[df['track_artist'] == artist_name].index

    if len(idx_list) == 0:
        return []

    idx = idx_list[0]

    sim_scores = cosine_similarity([text_embeddings[idx]], text_embeddings)[0]
    sorted_idx = np.argsort(sim_scores)[::-1]

    similar = []
    seen = set()

    for i in sorted_idx:

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
