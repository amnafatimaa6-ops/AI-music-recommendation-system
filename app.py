import streamlit as st
import pandas as pd
import requests
import model

# -------------------------
# MODEL
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
df = model.df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.markdown("""
<style>
.main { background-color: #0e1117; }
h1 { color: #1DB954; }
.card {
    background-color: #181818;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    border: 1px solid #2a2a2a;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Audio Intelligence + Discovery Engine")

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].dropna().unique()))
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].dropna().unique()))
    mode_key = "genre"

# -------------------------
# DEEZER (for songs + artists)
# -------------------------
def get_deezer(query):
    url = f"https://api.deezer.com/search?q={query}"
    res = requests.get(url).json()

    if "data" not in res or len(res["data"]) == 0:
        return None

    t = res["data"][0]

    return {
        "image": t["album"]["cover_big"],
        "preview": t["preview"]
    }

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate Recommendations 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Recommendations")

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:

            st.markdown(f"""
            <div class="card">
                <h4>🎵 {r['song']}</h4>
                <p>🎼 Genre: {r['genre']}</p>
                <p>⭐ Score: {r['score']}</p>
            </div>
            """, unsafe_allow_html=True)

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# SIMILAR ARTISTS + ALBUM COVERS
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

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 Transformer NLP + Deezer API + Audio Intelligence")
st.markdown("🚀 Spotify-style AI Discovery Engine")
