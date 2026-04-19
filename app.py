import streamlit as st
import pandas as pd
import json
import os
import requests
import model

# -------------------------
# MODEL
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
df = model.df

# -------------------------
# FILE
# -------------------------
USER_DB = "users.json"

# -------------------------
# SAFE LOAD USERS
# -------------------------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}

# -------------------------
# SAVE USERS (IMPORTANT FIX)
# -------------------------
def save_users():
    with open(USER_DB, "w") as f:
        json.dump(st.session_state.users, f, indent=4)

# -------------------------
# INIT STATE (CRITICAL)
# -------------------------
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "email" not in st.session_state:
    st.session_state.email = None

if "selected_song" not in st.session_state:
    st.session_state.selected_song = None

# -------------------------
# UI CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.markdown("""
<style>
.main { background-color: #0e1117; }
h1 { color: #1DB954; }
.card {
    background-color: #181818;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    border: 1px solid #2a2a2a;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 AI Music Recommender System")
st.markdown("Transformer NLP + Playlist Intelligence + Discovery Engine")

# -------------------------
# LOGIN
# -------------------------
st.sidebar.header("👤 Login")
email = st.sidebar.text_input("Enter Email")

if email:
    st.session_state.email = email

    if email not in st.session_state.users:
        st.session_state.users[email] = {
            "joined": str(pd.Timestamp.now()),
            "playlists": []
        }
        save_users()

    st.sidebar.success(f"Logged in: {email}")

# -------------------------
# PROFILE SLIDERS
# -------------------------
st.sidebar.subheader("🎛️ Profile Controls")

st.sidebar.slider("Energy Preference", 0.0, 1.0, 0.5)
st.sidebar.slider("Popularity Bias", 0.0, 1.0, 0.5)
st.sidebar.slider("Discovery Mode", 0.0, 1.0, 0.5)

# -------------------------
# PROFILE DISPLAY
# -------------------------
if st.session_state.email:
    user = st.session_state.users[st.session_state.email]

    st.subheader("👤 Profile")
    st.write(f"📧 {st.session_state.email}")
    st.write(f"📅 Joined: {user['joined']}")
    st.write(f"🎧 Playlists: {len(user['playlists'])}")

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].dropna().unique()))
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].dropna().unique()))
    mode_key = "genre"

# -------------------------
# DEEZER
# -------------------------
def get_deezer(song):
    url = f"https://api.deezer.com/search?q={song}"
    res = requests.get(url).json()

    if "data" not in res or len(res["data"]) == 0:
        return None

    t = res["data"][0]

    return {
        "image": t["album"]["cover_big"],
        "preview": t["preview"]
    }

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate Playlist 🎧"):

    results = search_music(query, mode_key)

    st.subheader("🎵 Recommendations")

    cols = st.columns(3)

    for i, r in enumerate(results):

        deezer = get_deezer(r["song"])

        with cols[i % 3]:

            st.markdown(f"""
            <div class="card">
                <h4>🎵 {r['song']}</h4>
                <p>🎼 Genre: {r['genre']}</p>
                <p>⭐ Score: {r['score']}</p>
            </div>
            """, unsafe_allow_html=True)

            # SELECT SONG
            if st.button("🎯 Select", key=f"select_{i}"):
                st.session_state.selected_song = r
                st.rerun()

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# SAVE SONG (FIXED FLOW)
# -------------------------
if st.session_state.email and st.session_state.selected_song:

    st.info(f"Selected: {st.session_state.selected_song['song']}")

    if st.button("➕ Save to Playlist"):

        user = st.session_state.email

        st.session_state.users[user]["playlists"].append(st.session_state.selected_song)

        save_users()

        st.success("Saved successfully 🎧")

        st.session_state.selected_song = None

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    cols2 = st.columns(max(1, len(similar)))

    for i, artist in enumerate(similar):

        with cols2[i % len(cols2)]:
            st.markdown(f"**{artist}**")

# -------------------------
# PLAYLIST
# -------------------------
if st.session_state.email:

    st.subheader("📂 Your Playlist")

    playlist = st.session_state.users[st.session_state.email]["playlists"]

    if not playlist:
        st.info("No songs saved yet.")
    else:
        for song in playlist:
            st.markdown(f"""
            🎵 **{song['song']}**  
            🎼 Genre: {song['genre']}  
            ⭐ Score: {song['score']}  
            ---
            """)

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 Transformer NLP + Deezer API + Audio Intelligence")
st.markdown("🚀 Spotify-style AI Discovery Engine")
