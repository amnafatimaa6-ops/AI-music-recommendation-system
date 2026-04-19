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
# YOUTUBE FUNCTION (FIXED)
# -------------------------
def get_youtube_video(song, artist):
    try:
        query = f"{song} {artist} official audio"
        search = VideosSearch(query, limit=1)
        result = search.result()

        if result and result["result"]:
            v = result["result"][0]

            return {
                "title": v["title"],
                "url": v["link"],
                "thumbnail": v["thumbnails"][0]["url"]
            }

        return None

    except:
        return None

# -------------------------
# MODE SELECTION
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df["track_artist"].unique()))
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df["playlist_genre"].unique()))
    mode_key = "genre"

# -------------------------
# GENERATE BUTTON
# -------------------------
if st.button("Generate 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Recommendations")

    # -------------------------
    # SONG LOOP
    # -------------------------
    for r in results:

        st.markdown("---")

        st.markdown(f"""
        ## 🎵 {r['song']}
        🎼 Genre: {r['genre']}  
        ⭐ Score: {r['score']}
        """)

        # -------------------------
        # DEEZER (COVER + PREVIEW)
        # -------------------------
        deezer = get_deezer(r["song"])

        if deezer:
            st.image(deezer["image"], width=300)
            st.audio(deezer["preview"])

        # -------------------------
        # YOUTUBE (FULL SONG FIXED)
        # -------------------------
        yt = get_youtube_video(r["song"], r["song"])

        if yt:
            st.markdown("### ▶️ Full Song (YouTube)")
            st.image(yt["thumbnail"])
            st.video(yt["url"])

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    for artist in similar:
        st.write("🎤", artist)

    st.subheader("🎶 Artist Full Songs (YouTube)")

    for artist in similar:

        yt = get_youtube_video(artist, artist)

        if yt:
            st.markdown(f"**{yt['title']}**")
            st.video(yt["url"])

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 Deezer + YouTube Hybrid AI Music Engine")
