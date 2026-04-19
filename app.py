import streamlit as st
import model
from youtubesearchpython import VideosSearch

# -------------------------
# LOAD MODEL FUNCTIONS
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
get_deezer = model.get_deezer
df = model.df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Deezer + YouTube Hybrid Engine")

# -------------------------
# CLEAN YOUTUBE QUERY
# -------------------------
def build_youtube_query(song, artist):
    song = str(song).split(",")[0]
    artist = str(artist).split(",")[0]
    return f"{artist} {song} official audio"

# -------------------------
# YOUTUBE ENGINE (ROBUST)
# -------------------------
def get_youtube_video(song, artist):
    try:
        query = build_youtube_query(song, artist)

        search = VideosSearch(query, limit=10)
        results = search.result().get("result", [])

        for v in results:
            link = v.get("link", "")

            if link:
                return {
                    "title": v.get("title", "Unknown"),
                    "url": link,
                    "thumbnail": v["thumbnails"][0]["url"]
                }

        # fallback search
        fallback = VideosSearch(song + " audio", limit=5)
        results2 = fallback.result().get("result", [])

        for v in results2:
            link = v.get("link", "")
            if link:
                return {
                    "title": v.get("title", "Unknown"),
                    "url": link,
                    "thumbnail": v["thumbnails"][0]["url"]
                }

        return None

    except:
        return None

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

        st.markdown("---")

        st.markdown(f"""
        ## 🎵 {r['song']}
        🎼 Genre: {r['genre']}  
        ⭐ Score: {r['score']}
        """)

        # -------------------------
        # DEEZER
        # -------------------------
        deezer = get_deezer(r["song"])

        if deezer:
            st.image(deezer["image"], width=300)
            st.audio(deezer["preview"])

        # -------------------------
        # YOUTUBE (FIXED)
        # -------------------------
        yt = get_youtube_video(r["song"], r["song"])

        if yt:
            st.markdown("### ▶️ Full Song (YouTube)")
            st.image(yt["thumbnail"])

            st.markdown(
                f"[▶ Watch on YouTube]({yt['url']})",
                unsafe_allow_html=True
            )

        else:
            st.markdown("🎧 YouTube not found — Deezer preview only")

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    for a in similar:
        st.write("🎤", a)

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 Deezer + YouTube Hybrid AI Music Engine")
