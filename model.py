import pandas as pd
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("music_df.csv")
text_embeddings = pickle.load(open("text_embeddings.pkl", "rb"))

model = SentenceTransformer('all-MiniLM-L6-v2')

# -------------------------
# MOOD MAP
# -------------------------
MOOD_MAP = {
    "sad": "melancholy emotional slow acoustic piano soft",
    "happy": "joyful energetic upbeat dance fun bright",
    "chill": "lofi ambient calm peaceful study sleep",
    "energetic": "high energy fast hype workout bass"
}

# -------------------------
# GENRE DISTRIBUTION (KEY FIX)
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
    return MOOD_MAP.get(query.lower(), query)

# -------------------------
# MAIN RECOMMENDER
# -------------------------
def search_music(query, mode="mood", top_n=10):

    expanded_query = expand_query(query, mode)

    query_vec = model.encode([expanded_query])
    sim = cosine_similarity(query_vec, text_embeddings)[0]

    audio = df['mood_score'].values

    # -------------------------
    # NORMALIZATION (IMPORTANT)
    # -------------------------
    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)
    audio = (audio - audio.min()) / (audio.max() - audio.min() + 1e-9)

    base_score = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(base_score)[::-1]

    results = []
    seen_artists = set()

    for i in idxs:

        artist = df.iloc[i]['track_artist']
        genre = df.iloc[i]['playlist_genre']

        if artist in seen_artists:
            continue

        # -------------------------
        # GENRE PENALTY (POP FIX 🔥)
        # -------------------------
        penalty = genre_distribution.get(genre, 0)
        score = base_score[i] * (1 - penalty)

        # -------------------------
        # ARTIST BOOST
        # -------------------------
        if mode == "artist" and artist == query:
            score += 0.2

        # -------------------------
        # RANDOM DISCOVERY (SPOTIFY FEEL)
        # -------------------------
        score += np.random.uniform(-0.02, 0.02)

        seen_artists.add(artist)

        results.append({
            "song": artist,
            "genre": genre,
            "score": round(float(score), 3)
        })

        if len(results) == top_n:
            break

    return results
