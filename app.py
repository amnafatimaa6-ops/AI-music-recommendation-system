import streamlit as st
import model

st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

# DEBUG INFO
st.write("📊 Dataset loaded:", len(model.df))

mode = st.radio("Choose Mode", ["Artist", "Genre", "Explore"])

query = None

if mode == "Artist":
    if not model.df.empty:
        query = st.selectbox("Artist", model.df["track_artist"].unique())

elif mode == "Genre":
    if not model.df.empty:
        query = st.selectbox("Genre", model.df["playlist_genre"].unique())

else:
    query = st.text_input("Type anything")

if st.button("Generate"):

    results = model.search_music(query)

    if not results:
        st.error("⚠️ Model not loaded or no results")
    else:

        for r in results:

            st.markdown(f"### {r['song']} ({r['genre']})")

            d = model.get_deezer(r["song"])

            if d:
                st.image(d["image"])
                if d["preview"]:
                    st.audio(d["preview"])
