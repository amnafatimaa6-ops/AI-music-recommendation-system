import streamlit as st
import requests
from model import search_music, df

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Playlist Intelligence + Production Engine")

# -------------------------
# DEEZER API
# -------------------------
def get_deezer(song):
    url = f"https://api.deezer.com/search?q={song}"
    r = requests.get(url).json()

    if "data" not in r or len(r["data"]) == 0:
        return None

    t = r["data"][0]

    return {
        "image": t["album"]["cover_big"],
        "preview": t["preview"]
    }

# -------------------------
# MODE UI
# -------------------------
mode = st.radio("Choose Mode", ["🎭 Mood", "🎤 Artist", "🎼 Genre"])

if mode == "🎭 Mood":
    query = st.text_input("Enter mood (sad, happy, chill, energetic)")
    mode_key = "mood"

elif mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].unique()))
    mode_key = "artist"

elif mode == "🎼 Genre":
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].unique()))
    mode_key = "genre"

# -------------------------
# RECOMMEND BUTTON
# -------------------------
if st.button("Generate Playlist 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Your AI Playlist")

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:

            st.markdown(f"""
            <div style="
                padding:15px;
                border-radius:15px;
                background:#0f0f0f;
                color:white;
                margin-bottom:15px;
            ">
                <h4>🎵 {r['song']}</h4>
                <p>🎼 Genre: {r['genre']}</p>
                <p>⭐ Score: {r['score']}</p>
            </div>
            """, unsafe_allow_html=True)

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])
