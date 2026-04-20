import streamlit as st
import model

search_music = model.search_music
get_similar_artists = model.get_similar_artists
weekly_ai_picks = model.weekly_ai_picks
get_deezer = model.get_deezer
df = model.df

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("AI Discovery Engine • Clean Spotify-style Experience")

# -------------------------
# SEARCH MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre", "🌌 Explore"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df["track_artist"].unique()))

elif mode == "🎼 Genre":
    query = st.selectbox("Select Genre", sorted(df["playlist_genre"].unique()))

else:
    query = st.text_input("Type mood / vibe / anything")

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate 🎧"):

    if query:
        results = search_music(query)

        st.subheader("🎵 Recommendations")

        cols = st.columns(3)

        for i, r in enumerate(results):

            with cols[i % 3]:

                st.markdown(f"### 🎵 {r['song']}")
                st.caption(f"{r['genre']} • ⭐ {r['score']}")

                deezer = get_deezer(r["song"])

                if deezer:
                    st.image(deezer["image"])
                    if deezer["preview"]:
                        st.audio(deezer["preview"])

# -------------------------
# SIMILAR ARTISTS (WITH COVERS)
# -------------------------
if mode == "🎤 Artist" and query:

    st.subheader("🎤 Similar Artists")

    sim = get_similar_artists(query)

    cols = st.columns(len(sim))

    for i, artist in enumerate(sim):

        with cols[i]:
            st.markdown(f"**{artist}**")

            deezer = get_deezer(artist)

            if deezer:
                st.image(deezer["image"])

# -------------------------
# WEEKLY AI PICKS
# -------------------------
st.subheader("🔥 Weekly AI Picks")

weekly = weekly_ai_picks()

cols = st.columns(5)

for i, w in enumerate(weekly):

    with cols[i % 5]:

        st.markdown(f"🎵 {w['song']}")
        deezer = get_deezer(w["song"])

        if deezer:
            st.image(deezer["image"])
            if deezer["preview"]:
                st.audio(deezer["preview"])
