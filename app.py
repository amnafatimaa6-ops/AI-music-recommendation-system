import streamlit as st
import model

# -------------------------
# LOAD FUNCTIONS
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
get_deezer = model.get_deezer
get_itunes = model.get_itunes
df = model.df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Deezer + iTunes Stable Engine")

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df["track_artist"].unique()))
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df["playlist_genre"].unique()))
    mode_key = "genre"

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate 🎧"):

    results = search_music(query, mode_key)

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
        # ITUNES (MAIN FIX)
        # -------------------------
        itunes = get_itunes(r["song"], r["song"])

        if itunes:
            st.markdown("### 🎧 Full Track (iTunes)")

            st.image(itunes["image"])

            if itunes["preview"]:
                st.audio(itunes["preview"])

            st.markdown(
                f"[🎵 Open Song]({itunes['url']})",
                unsafe_allow_html=True
            )

        else:
            st.markdown("🎧 No full preview available")

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
st.markdown("💡 Deezer + iTunes Stable AI Music Engine")
