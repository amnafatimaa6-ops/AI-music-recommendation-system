import streamlit as st
import model

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
st.markdown("Transformer NLP + Deezer Engine (Stable Version)")

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df["track_artist"].unique()) if not df.empty else [])
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df["playlist_genre"].unique()) if not df.empty else [])
    mode_key = "genre"

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate 🎧"):

    results = search_music(query, mode_key)

    if not results:
        st.warning("No data available or model not loaded properly.")
    else:

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
                st.image(deezer["image"], width=250)
                st.audio(deezer["preview"])

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
st.markdown("💡 Stable AI Music Engine (Crash-Proof Version)")
