import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

# -------------------------
# DATA STATUS
# -------------------------
st.write("📊 Dataset loaded:", 0 if model.df.empty else len(model.df))

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["Artist", "Genre", "Explore"])

query = None
artist = None

# -------------------------
# INPUT HANDLING
# -------------------------
if mode == "Artist":

    if not model.df.empty:
        query = st.selectbox("Artist", model.df["track_artist"].unique())
        artist = query

elif mode == "Genre":

    if not model.df.empty:
        query = st.selectbox("Genre", model.df["playlist_genre"].unique())

else:

    query = st.text_input("Type anything (mood / vibe / artist / genre)")
    artist = query


# -------------------------
# SEARCH / RECOMMENDATIONS
# -------------------------
if st.button("Generate 🎧"):

    results = model.search_music(query)

    if not results:
        st.error("⚠️ No results found or model not loaded")
    else:

        st.subheader("🎵 Recommendations")

        for r in results:

            st.markdown(f"### 🎵 {r['song']}")
            st.caption(f"{r['genre']} • ⭐ {r['score']}")

            deezer = model.get_deezer(r["song"])

            if deezer:

                if deezer["image"]:
                    st.image(deezer["image"], width=200)

                if deezer["preview"]:
                    st.audio(deezer["preview"])


# -------------------------
# 🎤 SIMILAR ARTISTS (WITH COVERS)
# -------------------------
if artist:

    st.subheader("🎤 Similar Artists")

    sim = model.get_similar_artists(artist)

    if sim:

        cols = st.columns(len(sim))

        for i, a in enumerate(sim):

            with cols[i]:

                st.write(a["artist"])

                if a["image"]:
                    st.image(a["image"], width=150)

    else:
        st.write("No similar artists found")


# -------------------------
# 🔥 WEEKLY TRENDING AI SONGS
# -------------------------
st.subheader("🔥 Weekly Trending AI Songs")

trend = model.get_weekly_trending()

if trend:

    cols = st.columns(5)

    for i, t in enumerate(trend):

        with cols[i % 5]:

            st.write(t["artist"])

            if t["image"]:
                st.image(t["image"], width=120)
