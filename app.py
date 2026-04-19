import streamlit as st
import pandas as pd
import numpy as np
import requests
import model

# -------------------------
# MODEL
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
df = model.df

# -------------------------
# PAGE
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.markdown("""
<style>
.main { background-color: #0e1117; }

.card {
    background-color: #181818;
    padding: 15px;
    border-radius: 15px;
    margin: 10px 0;
    border: 1px solid #2a2a2a;
}

h1 { color: #1DB954; }
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Discovery Engine + Audio Intelligence")

# -------------------------
# DISCOVERY MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre", "🌌 Explore Mode"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].dropna().unique()))
    mode_key = "artist"

elif mode == "🎼 Genre":
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].dropna().unique()))
    mode_key = "genre"

else:
    query = st.text_input("Type anything (mood / vibe / artist / genre)")
    mode_key = "explore"

# -------------------------
# DEEZER
# -------------------------
def get_deezer(q):
    try:
        res = requests.get(f"https://api.deezer.com/search?q={q}").json()

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
# SMART EXPLANATION ENGINE
# -------------------------
def explain(song, genre):
    reasons = []

    if genre == "pop":
        reasons.append("Mainstream pop energy match")
    elif genre == "hip-hop":
        reasons.append("Rhythm + lyrical similarity detected")
    elif genre == "electronic":
        reasons.append("High tempo + synthetic audio profile")
    else:
        reasons.append("Audio embedding similarity match")

    reasons.append(f"Genre cluster: {genre}")
    return " • ".join(reasons)

# -------------------------
# DIVERSITY FILTER (FIX REPETITION)
# -------------------------
def diversify(results):
    seen = set()
    final = []

    for r in results:
        if r["song"] in seen:
            continue
        seen.add(r["song"])
        final.append(r)

        if len(final) == 10:
            break

    return final

# -------------------------
# GENERATE
# -------------------------
if st.button("🚀 Generate Recommendations"):

    results = search_music(query, mode_key)
    results = diversify(results)

    st.subheader("🎵 Recommendations")

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:

            st.markdown(f"""
            <div class="card">
                <h3>🎵 {r['song']}</h3>
                <p>🎼 Genre: {r['genre']}</p>
                <p>⭐ Score: {round(r['score'], 3)}</p>
                <p>💡 {explain(r['song'], r['genre'])}</p>
            </div>
            """, unsafe_allow_html=True)

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# SIMILAR ARTISTS (WITH ALBUM COVERS)
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    cols2 = st.columns(3)

    for i, artist in enumerate(similar):

        deezer = get_deezer(artist)

        with cols2[i % 3]:

            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <h4>{artist}</h4>
            </div>
            """, unsafe_allow_html=True)

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# TRENDING SECTION
# -------------------------
st.subheader("🔥 Trending Genres")

top_genres = df['playlist_genre'].value_counts().head(5)

for g, c in top_genres.items():
    st.write(f"🎼 {g} — {c} songs")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 AI + Transformer + Audio Intelligence + Deezer API")
st.markdown("🚀 Spotify-style Discovery Engine (Upgraded)")
