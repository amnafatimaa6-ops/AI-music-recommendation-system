import pandas as pd
import numpy as np
import pickle
import requests
import urllib.parse
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# -------------------------
# LOAD DATA SAFELY
# -------------------------
df = pd.read_csv("music_df.csv")

# -------------------------
# LOAD EMBEDDINGS SAFELY
# -------------------------
with open("text_embeddings.pkl", "rb") as f:
    text_embeddings = pickle.load(f)

# -------------------------
# TRANSFORMER MODEL
# -------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# SEARCH MUSIC ENGINE
# -------------------------
def search_music(query, mode="artist", top_n=10):

    query_vec = model.encode([query])

    sim = cosine_similarity(query_vec, text_embeddings)[0]

    sim = (sim - sim.min()) / (sim.max() - sim.min() + 1e-9)

    audio = df["mood_score"].values

    base_score = 0.6 * sim + 0.4 * audio

    idxs = np.argsort(base_score)[::-1]

    results = []

    for i in idxs[:top_n]:

        results.append({
            "song": df.iloc[i]["track_artist"],
            "genre": df.iloc[i]["playlist_genre"],
            "score": round(float(base_score[i]), 3)
        })

    return results

# -------------------------
# SIMILAR ARTISTS ENGINE
# -------------------------
def get_similar_artists(artist_name, top_n=5):

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
# DEEZER API (ALBUM + PREVIEW)
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

# -------------------------
# ITUNES API (FULL TRACK SAFE)
# -------------------------
def get_itunes(song, artist):
    try:
        query = urllib.parse.quote(f"{song} {artist}")
        url = f"https://itunes.apple.com/search?term={query}&limit=1"

        res = requests.get(url).json()

        if res["resultCount"] > 0:
            item = res["results"][0]

            return {
                "track": item.get("trackName"),
                "artist": item.get("artistName"),
                "preview": item.get("previewUrl"),
                "image": item.get("artworkUrl100"),
                "url": item.get("trackViewUrl")
            }

        return None

    except:
        return None

# -------------------------
# YOUTUBE SAFE LINK (NO SCRAPING)
# -------------------------
def get_youtube(song, artist):
    try:
        query = f"{artist} {song} official audio"
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)

        return {
            "query": query,
            "url": url
        }

    except:
        return None
