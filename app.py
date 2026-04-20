import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

st.write(f"📊 Total Artists Loaded: {len(model.df)}")

# -------------------------
# SEARCH + SUGGESTIONS
# -------------------------
query = st.text_input("Search artist / song / vibe")

selected = query

if query:
    suggestions = model.df[
        model.df["track_artist"].str.contains(query, case=False, na=False)
    ]["track_artist"].unique()[:10]

    if len(suggestions) > 0:
        selected = st.selectbox("Suggestions", suggestions)

# -------------------------
# GENERATE RESULTS
# -------------------------
if st.button("Generate 🎧") and selected:

    results = model.search_music(selected)

    st.subheader("🎵 Recommendations")

    cols = st.columns(3)

    for i, r in enumerate(results):

        with cols[i % 3]:

            st.markdown(f"### 🎵 {r['song']}")
            st.caption(f"{r['genre']} • ⭐ {r['score']}")

            d = model.get_deezer(r["song"])

            if d:
                st.image(d["image"])
                if d["preview"]:
                    st.audio(d["preview"])

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if selected:

    st.subheader("🎤 Similar Artists")

    sim = model.get_similar_artists(selected)

    cols = st.columns(len(sim)) if sim else []

    for i, artist in enumerate(sim):

        with cols[i]:

            st.markdown(f"**{artist}**")

            d = model.get_deezer(artist)

            if d:
                st.image(d["image"])

# -------------------------
# WEEKLY TRENDING
# -------------------------
st.subheader("🔥 Weekly AI Trending")

weekly = model.get_weekly_trending()

cols = st.columns(5)

for i, w in enumerate(weekly):

    with cols[i % 5]:

        st.markdown(f"🎵 {w['song']}")

        d = model.get_deezer(w["song"])

        if d:
            st.image(d["image"])
            if d["preview"]:
                st.audio(d["preview"])
