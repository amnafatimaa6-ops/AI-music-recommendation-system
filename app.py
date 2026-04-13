import streamlit as st
import requests
from model import search_by_mood

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
# UI
# -------------------------
query = st.text_input("💭 Describe mood or artist")

if st.button("Recommend"):
    results = search_by_mood(query)

    for r in results:
        st.subheader(r["song"])
        st.write(r["genre"])
        st.write(f"Score: {r['score']}")

        deezer = get_deezer(r["song"])

        if deezer:
            st.image(deezer["image"])

            if deezer["preview"]:
                st.audio(deezer["preview"])
