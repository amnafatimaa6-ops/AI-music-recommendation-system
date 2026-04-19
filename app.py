import streamlit as st
import requests
import model
import json
import datetime

search_music = model.search_music
get_similar_artists = model.get_similar_artists
df = model.df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

# -------------------------
# STYLE
# -------------------------
st.markdown("""
<style>
.main {background-color: #0e1117;}
h1 {color: #1DB954;}
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

# -------------------------
# USER SYSTEM
# -------------------------
USER_DB = "users.json"

def load_users():
    try:
        return json.load(open(USER_DB))
    except:
        return {}

def save_users(data):
    json.dump(data, open(USER_DB, "w"))

users = load_users()

st.sidebar.title("👤 Login")
email = st.sidebar.text_input("Enter Email")

if email:
    if email not in users:
        users[email] = {
            "created_at": str(datetime.datetime.now()),
            "playlists": []
        }
        save_users(users)

    st.session_state["user"] = email
    st.sidebar.success(f"Logged in: {email}")

# -------------------------
# PROFILE PANEL
# -------------------------
if "user" in st.session_state:

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Profile")

    user_data = users.get(st.session_state["user"], {})

    st.sidebar.write("📧", st.session_state["user"])
    st.sidebar.write("📅 Joined:", user_data.get("created_at"))
    st.sidebar.write("🎧 Playlists:", len(user_data.get("playlists", [])))

# -------------------------
# DATA INFO
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Dataset")

st.sidebar.write("Songs:", len(df))
st.sidebar.write("Artists:", df['track_artist'].nunique())
st.sidebar.write("Genres:", df['playlist_genre'].nunique())

# -------------------------
# ACTIVITY LOG
# -------------------------
ACTIVITY_FILE = "activity.json"

def log_activity(email, action):
    try:
        logs = json.load(open(ACTIVITY_FILE))
    except:
        logs = []

    logs.append({
        "user": email,
        "action": action,
        "time": str(datetime.datetime.now())
    })

    json.dump(logs, open(ACTIVITY_FILE, "w"))

# -------------------------
# DEEZER
# -------------------------
def get_deezer(song):
    url = f"https://api.deezer.com/search?q={song}"
    res = requests.get(url).json()

    if "data" not in res or not res["data"]:
        return None

    t = res["data"][0]

    return {
        "image": t["album"]["cover_big"],
        "preview": t["preview"]
    }

# -------------------------
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

artist_list = sorted(df['track_artist'].dropna().unique())
genre_list = sorted(df['playlist_genre'].dropna().unique())

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", artist_list)
    mode_key = "artist"
else:
    query = st.selectbox("Select Genre", genre_list)
    mode_key = "genre"

# -------------------------
# STORE STATE (IMPORTANT FIX)
# -------------------------
if "results" not in st.session_state:
    st.session_state.results = []

# -------------------------
# GENERATE
# -------------------------
if st.button("Generate Playlist 🎧"):

    results = search_music(query, mode_key)
    st.session_state.results = results

    if "user" in st.session_state:
        log_activity(st.session_state["user"], f"Searched {query}")

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

            if deezer:
                st.image(deezer["image"], use_container_width=True)
                st.audio(deezer["preview"])

# -------------------------
# SAVE PLAYLIST (FIXED)
# -------------------------
if st.button("💾 Save Playlist"):

    if "user" not in st.session_state:
        st.warning("Login first")
        st.stop()

    if len(st.session_state.results) == 0:
        st.warning("Generate playlist first")
        st.stop()

    email = st.session_state["user"]

    users[email]["playlists"].append({
        "time": str(datetime.datetime.now()),
        "query": query,
        "mode": mode_key,
        "songs": st.session_state.results
    })

    save_users(users)

    st.success("Playlist saved 🎧")
    st.rerun()

# -------------------------
# SIMILAR ARTISTS
# -------------------------
if mode_key == "artist":

    st.subheader("🎤 Similar Artists")

    similar = get_similar_artists(query)

    cols2 = st.columns(len(similar))

    for i, artist in enumerate(similar):

        deezer = get_deezer(artist)

        with cols2[i]:
            st.markdown(f"<div class='card'>{artist}</div>", unsafe_allow_html=True)

            if deezer:
                st.image(deezer["image"], use_container_width=True)

# -------------------------
# ACTIVITY PANEL
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Activity")

if st.sidebar.button("Show Activity"):
    try:
        logs = json.load(open(ACTIVITY_FILE))
        st.sidebar.write(logs[-10:])
    except:
        st.sidebar.write("No activity")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("🚀 Spotify-style AI Music Engine")
