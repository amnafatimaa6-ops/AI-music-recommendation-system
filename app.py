import streamlit as st
import model

# -------------------------
# LOAD FUNCTIONS
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
get_deezer = model.get_deezer
get_itunes = model.get_itunes
get_youtube = model.get_youtube_fallback
df = model.df

# -------------------------
# UI
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Deezer + iTunes + YouTube Search Engine")

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
        # ITUNES
        # -------------------------
        itunes = get_itunes(r["song"], r["song"])

        if itunes:
            st.markdown("### 🎧 Full Track (iTunes)")
            st.image(itunes["image"])

            if itunes["preview"]:
                st.audio(itunes["preview"])

            st.markdown(f"[🎵 Open Song]({itunes['url']})")

        # -------------------------
        # YOUTUBE (FIXED LINK - ALWAYS WORKS)
        # -------------------------
        yt = get_youtube(r["song"], r["song"])

        if yt:
            st.markdown("### ▶️ YouTube (Search)")
            st.markdown(f"🔎 `{yt['query']}`")
            st.markdown(f"[▶ Open on YouTube]({yt['url']})")

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
st.markdown("💡 Stable AI Music Engine vFinal (Deezer + iTunes + YouTube Search)")
