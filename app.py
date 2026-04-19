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
# USER DB
# -------------------------
USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}

    try:
        with open(USER_DB, "r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)

    except json.JSONDecodeError:
        return {}

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

# auto create safe file
if not os.path.exists(USER_DB) or os.stat(USER_DB).st_size == 0:
    with open(USER_DB, "w") as f:
        json.dump({}, f)

users = load_users()

# -------------------------
# SESSION STATE
# -------------------------
if "email" not in st.session_state:
    st.session_state.email = None

if "users" not in st.session_state:
    st.session_state.users = users

if "selected_song" not in st.session_state:
    st.session_state.selected_song = None

# -------------------------
# PAGE
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
        save_users(st.session_state.users)

    st.sidebar.success(f"Logged in: {email}")

# -------------------------
# PROFILE SLIDERS
# -------------------------
st.sidebar.subheader("🎛️ Profile Controls")

energy_pref = st.sidebar.slider("Energy Preference", 0.0, 1.0, 0.5)
popularity_pref = st.sidebar.slider("Popularity Bias", 0.0, 1.0, 0.5)
diversity_pref = st.sidebar.slider("Discovery Mode", 0.0, 1.0, 0.5)

# -------------------------
# PROFILE
# -------------------------
if st.session_state.email:
    st.subheader("👤 Profile")

    user = st.session_state.users[st.session_state.email]

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

            # -------------------------
            # SELECT SONG (FIXED FLOW)
            # -------------------------
            if st.button("🎯 Select", key=f"select_{i}"):
                st.session_state.selected_song = r
                st.success(f"Selected: {r['song']}")

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# SAVE SELECTED SONG (IMPORTANT FIX)
# -------------------------
if st.session_state.email and st.session_state.selected_song:

    st.markdown("### 💾 Save Selected Song")

    st.info(f"🎵 {st.session_state.selected_song['song']}")

    if st.button("➕ Save to Playlist"):

        user = st.session_state.email

        st.session_state.users[user]["playlists"].append(st.session_state.selected_song)
        save_users(st.session_state.users)

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

            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <b>{artist}</b>
            </div>
            """, unsafe_allow_html=True)

# -------------------------
# PLAYLIST
# -------------------------
if st.session_state.email:

    st.subheader("📂 Your Playlist")

    playlist = st.session_state.users[st.session_state.email]["playlists"]

    if len(playlist) == 0:
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
st.markdown("💡 Transformer NLP + Deezer + Audio Intelligence")
st.markdown("🚀 Spotify-style AI Discovery Engine")
