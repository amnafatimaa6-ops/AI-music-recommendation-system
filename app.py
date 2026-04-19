import streamlit as st
import pandas as pd
import json
import os
import requests
import model

# -------------------------
# MODEL IMPORTS
# -------------------------
search_music = model.search_music
get_similar_artists = model.get_similar_artists
df = model.df

# -------------------------
# USER DB FILE
# -------------------------
USER_DB = "users.json"

# -------------------------
# SAFE LOAD USERS (FIXED JSON ERROR)
# -------------------------
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

# -------------------------
# SAVE USERS
# -------------------------
def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)

# AUTO REPAIR EMPTY FILE
if not os.path.exists(USER_DB) or os.stat(USER_DB).st_size == 0:
    with open(USER_DB, "w") as f:
        json.dump({}, f)

users = load_users()

# -------------------------
# PAGE CONFIG
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
# LOGIN SYSTEM
# -------------------------
st.sidebar.header("👤 Login")
email = st.sidebar.text_input("Enter Email")

if email:
    if email not in users:
        users[email] = {
            "joined": str(pd.Timestamp.now()),
            "playlists": []
        }
        save_users(users)

    st.sidebar.success(f"Logged in: {email}")

# -------------------------
# USER PROFILE
# -------------------------
if email:
    st.subheader("👤 Profile")
    st.write(f"📧 {email}")
    st.write(f"📅 Joined: {users[email]['joined']}")
    st.write(f"🎧 Playlists: {len(users[email]['playlists'])}")

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].dropna().unique()))
    mode_key = "artist"

elif mode == "🎼 Genre":
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].dropna().unique()))
    mode_key = "genre"

# -------------------------
# DEEZER API
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
            # SAVE PLAYLIST (FIXED)
            # -------------------------
            if email:
                if st.button(f"➕ Save {i}"):
                    users[email]["playlists"].append(r)
                    save_users(users)
                    st.success("Saved to playlist!")

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

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
# PLAYLIST VIEW
# -------------------------
if email:
    st.subheader("📂 Your Playlist")

    if len(users[email]["playlists"]) == 0:
        st.info("No songs saved yet.")
    else:
        for song in users[email]["playlists"]:
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
st.markdown("💡 Built with Transformer NLP + Audio Intelligence + Deezer API")
st.markdown("🚀 Spotify-style AI Discovery Engine")
