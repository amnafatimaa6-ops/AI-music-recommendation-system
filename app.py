import streamlit as st
import model
from youtubesearchpython import VideosSearch

search_music = model.search_music
get_similar_artists = model.get_similar_artists
get_deezer = model.get_deezer
df = model.df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Deezer + YouTube Music Engine")

# -------------------------
# YOUTUBE ENGINE
# -------------------------
def get_youtube_song(query):
    try:
        search = VideosSearch(query + " official audio", limit=1)
        r = search.result()["result"][0]

        return {
            "title": r["title"],
            "url": r["link"],
            "thumb": r["thumbnails"][0]["url"]
        }
    except:
        return None

def get_artist_songs(artist):
    try:
        search = VideosSearch(artist + " top songs", limit=5)
        return search.result()["result"]
    except:
        return []

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df["track_artist"].unique()))
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df["playlist_genre"].unique()))
    mode_key = "genre"

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Recommendations")

    for r in results:

        st.markdown(f"""
        ### 🎵 {r['song']}
        🎼 {r['genre']}  
        ⭐ {r['score']}
        """)

        # Deezer preview
        deezer = get_deezer(r["song"])
        if deezer:
            st.image(deezer["image"])
            st.audio(deezer["preview"])

        # YouTube full song
        yt = get_youtube_song(r["song"])
        if yt:
            st.video(yt["url"])

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    for a in similar:
        st.write("🎤", a)

    st.subheader("🎶 Artist Full Songs (YouTube)")

    songs = get_artist_songs(query)

    for s in songs:
        st.markdown(f"**{s['title']}**")
        st.video(s["link"])

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 AI + Deezer + YouTube Hybrid Music Engine")
