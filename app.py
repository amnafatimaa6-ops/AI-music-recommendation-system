import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

st.write(f"📊 Total Artists Loaded: {len(model.df)}")

# -------------------------
# SEARCH BAR (FIXED)
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
# RECOMMENDATIONS
# -------------------------
if st.button("Generate 🎧") and selected:

    results = model.search_music(selected)

    st.subheader("🎵 Recommendations")

    for r in results:

        st.markdown(f"### 🎵 {r['song']}")
        st.caption(f"{r['artist']} • {r['genre']} • ⭐ {r['score']}")

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if selected:

    st.subheader("🎤 Similar Artists")

    artist = selected.split(" - ")[0] if " - " in selected else selected

    sim = model.get_similar_artists(artist)

    for a in sim:
        st.write("🎤", a)

# -------------------------
# TRENDING
# -------------------------
st.subheader("🔥 Weekly Trending Artists")

trend = model.get_weekly_trending()

for t in trend:
    st.write("🎵", t["song"])
