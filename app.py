import streamlit as st
import requests
from model import search_music, df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

st.markdown("Transformer NLP + Playlist Intelligence + Explainable AI")

# -------------------------
# DEEZER API (ALBUM + PREVIEW)
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
# MODE
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
if st.button("Recommend 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Recommendations")

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:

            st.markdown(f"""
            <div style="
                padding:15px;
                border-radius:15px;
                background:#111;
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
                if deezer["preview"]:
                    st.audio(deezer["preview"])
