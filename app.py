import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

# Dataset info
st.write(f"📊 Total Artists Loaded: {len(model.df)}")

# Search
query = st.text_input("Search artist / song / vibe")

if st.button("Generate 🎧"):

    results = model.search_music(query)

    if not results:
        st.error("No results found")
    else:

        st.subheader("🎵 Recommendations")

        cols = st.columns(3)

        for i, r in enumerate(results):

            with cols[i % 3]:

                st.markdown(f"### 🎵 {r['song']}")
                st.caption(f"{r['genre']} • ⭐ {r['score']}")

                deezer = model.get_deezer(r["song"])

                if deezer:
                    st.image(deezer["image"])

                    if deezer["preview"]:
                        st.audio(deezer["preview"])
                    else:
                        st.warning("No preview available")
