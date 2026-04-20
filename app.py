import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

st.write(f"📊 Total Artists Loaded: {len(model.df)}")

# -------------------------
# SEARCH
# -------------------------
query = st.text_input("Search artist / song / vibe")

selected = query

if query:
    suggestions = model.df[
        model.df["track_artist"].str.contains(query, case=False, na=False) |
        model.df["track_name"].str.contains(query, case=False, na=False)
    ][["track_artist", "track_name"]].head(10)

    if not suggestions.empty:
        options = (suggestions["track_artist"] + " - " + suggestions["track_name"]).tolist()
        selected = st.selectbox("Suggestions", options)

# -------------------------
# RECOMMENDATIONS (WITH AUDIO + COVER)
# -------------------------
if st.button("Generate 🎧") and selected:

    results = model.search_music(selected)

    st.subheader("🎵 Recommendations")

    for r in results:

        st.markdown(f"### 🎵 {r['song']}")
        st.caption(f"{r['artist']} • {r['genre']}")

        data = model.get_deezer(r["song"])

        if data:
            st.image(data["image"])
            st.audio(data["preview"])

# -------------------------
# SIMILAR ARTISTS (WITH COVERS)
# -------------------------
if selected:

    st.subheader("🎤 Similar Artists")

    artist = selected.split(" - ")[0] if " - " in selected else selected

    sim = model.get_similar_artists(artist)

    cols = st.columns(len(sim)) if sim else []

    for i, a in enumerate(sim):

        with cols[i]:

            st.write("🎤", a)

            data = model.get_deezer(a)

            if data:
                st.image(data["image"])

# -------------------------
# TRENDING
# -------------------------
st.subheader("🔥 Weekly Trending Artists")

trend = model.get_weekly_trending()

for t in trend:
    st.write("🎵", t["song"])
