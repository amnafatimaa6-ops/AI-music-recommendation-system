import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

# -------------------------
# DATA STATUS
# -------------------------
st.write("📊 Dataset loaded:", len(model.df) if not model.df.empty else 0)

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
# GENERATE BUTTON
# -------------------------
if st.button("Generate 🎧"):

    results = model.search_music(query)

    if not results:
        st.error("⚠️ No results found or model not loaded")

    else:

        # -------------------------
        # 🎵 RECOMMENDATIONS (HORIZONTAL ROW)
        # -------------------------
        st.subheader("🎵 Recommendations")

        cols = st.columns(len(results))

        for i, r in enumerate(results):

            with cols[i]:

                st.markdown(f"**{r['song']}**")
                st.caption(f"{r['genre']} • ⭐ {r['score']}")

                d = model.get_deezer(r["song"])

                if d:

                    if d["image"]:
                        st.image(d["image"], use_container_width=True)

                    if d["preview"]:
                        st.audio(d["preview"])


# -------------------------
# 🎤 SIMILAR ARTISTS (ALBUM COVER ROW)
# -------------------------
if artist:

    st.subheader("🎤 Similar Artists")

    sim = model.get_similar_artists(artist)

    if sim:

        cols = st.columns(len(sim))

        for i, a in enumerate(sim):

            with cols[i]:

                st.markdown(f"**{a['artist']}**")

                if a["image"]:
                    st.image(a["image"], use_container_width=True)

    else:
        st.write("No similar artists found")


# -------------------------
# 🔥 WEEKLY TRENDING (ROW STYLE)
# -------------------------
st.subheader("🔥 Weekly Trending AI Songs")

trend = model.get_weekly_trending()

if trend:

    cols = st.columns(len(trend[:5]))

    for i, t in enumerate(trend[:5]):

        with cols[i]:

            st.markdown(f"**{t['artist']}**")

            if t["image"]:
                st.image(t["image"], use_container_width=True)
