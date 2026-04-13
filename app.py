import streamlit as st
import requests
from model import search_by_mood, df

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender (Transformer + Deezer)")

# -------------------------
# DEEZER API
# -------------------------
def get_deezer(query):
    url = f"https://api.deezer.com/search?q={query}"
    res = requests.get(url).json()

    if "data" not in res or len(res["data"]) == 0:
        return None

    track = res["data"][0]

    return {
        "title": track["title"],
        "artist": track["artist"]["name"],
        "image": track["album"]["cover_big"],
        "preview": track["preview"]
    }

# -------------------------
# UI MODE SELECTION
# -------------------------
mode = st.radio("Choose Mode", ["🎭 Mood Search", "🎤 Artist Search", "🎼 Genre Search"])

query = ""

if mode == "🎭 Mood Search":
    query = st.text_input("Describe mood (sad, happy, chill, energetic)")

elif mode == "🎤 Artist Search":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].unique()))

elif mode == "🎼 Genre Search":
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].unique()))

# -------------------------
# RECOMMEND BUTTON
# -------------------------
if st.button("Recommend 🎧"):

    results = search_by_mood(query)

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:
            st.markdown("### 🎵 " + r["song"])
            st.write("🎼 Genre:", r["genre"])
            st.write("⭐ Score:", r["score"])

            if deezer:
                st.image(deezer["image"])

                if deezer["preview"]:
                    st.audio(deezer["preview"])
