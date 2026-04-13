import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

df = pd.read_csv("music_df.csv")
text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))

model = SentenceTransformer('all-MiniLM-L6-v2')

MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic piano soft",
    "happy": "joyful energetic upbeat dance fun bright",
    "chill": "lo-fi ambient calm peaceful study sleep",
    "energetic": "high energy fast hype workout bass aggressive"
}

def expand_query(query, mode):
    if mode == "artist":
        return query + " similar artists songs albums music"
    if mode == "genre":
        return query + " top songs playlist hits"
    return MOOD_MAP.get(query.lower(), query)

def search_music(query, mode="mood", top_n=10):

    expanded_query = expand_query(query, mode)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio = df['mood_score'].values

    # NORMALIZED SCORING (IMPORTANT FIX)
    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
    audio = (audio - audio.min()) / (audio.max() - audio.min() + 1e-9)

    final_score = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(final_score)[::-1]

    results = []
    seen = set()

    anchor_artist = query

    for i in idxs:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        if artist in seen:
            continue

        # anchor lock for artist mode
        if mode == "artist" and artist == anchor_artist:
            boost = 0.2
        else:
            boost = 0

        score = final_score[i] + boost

        seen.add(artist)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results
