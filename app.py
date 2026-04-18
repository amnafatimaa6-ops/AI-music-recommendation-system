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
# UI STYLE
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
st.markdown("Transformer NLP + Playlist Intelligence + Discovery Engine")

# -------------------------
# USER SYSTEM
# -------------------------
USER_DB = "users.json"

def load_users():
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(data):
    with open(USER_DB, "w") as f:
        json.dump(data, f)

users = load_users()

st.sidebar.title("👤 User Login")
email = st.sidebar.text_input("Enter Email")

if email:
    if email not in users:
        users[email] = {
            "created_at": str(datetime.datetime.now()),
            "playlists": []
        }
        save_users(users)
        st.sidebar.success("New account created 🎉")

    st.session_state["user"] = email
    st.sidebar.success(f"Logged in as {email}")

# -------------------------
# USER PROFILE PANEL
# -------------------------
if "user" in st.session_state:

    st.sidebar.markdown("---")
    st.sidebar.subheader("👤 Profile")

    user_data = users.get(st.session_state["user"], {})

    st.sidebar.write("📧", st.session_state["user"])
    st.sidebar.write("📅 Joined:", user_data.get("created_at", "Unknown"))
    st.sidebar.write("🎧 Saved Playlists:", len(user_data.get("playlists", [])))

# -------------------------
# DATASET INFO PANEL (NEW DATA CONFIRMATION)
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Dataset Info")

st.sidebar.write("Total Songs:", len(df))
st.sidebar.write("Artists:", df['track_artist'].nunique())
st.sidebar.write("Genres:", df['playlist_genre'].nunique())

# -------------------------
# ACTIVITY TRACKING
# -------------------------
ACTIVITY_FILE = "activity_log.json"

def log_activity(email, action):
    try:
        with open(ACTIVITY_FILE, "r") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append({
        "user": email,
        "action": action,
        "time": str(datetime.datetime.now())
    })

    with open(ACTIVITY_FILE, "w") as f:
        json.dump(logs, f)

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
# MODE
# -------------------------
mode = st.radio("Choose Mode", ["🎤 Artist", "🎼 Genre"])

# CLEAN UNIQUE LISTS (FIX NEW DATASET ISSUE)
artist_list = sorted(list(set(df['track_artist'].dropna().astype(str))))
genre_list = sorted(list(set(df['playlist_genre'].dropna().astype(str))))

if mode == "🎤 Artist":
    query = st.selectbox("Select Artist", artist_list)
    mode_key = "artist"

else:
    query = st.selectbox("Select Genre", genre_list)
    mode_key = "genre"

# -------------------------
# GENERATE RECOMMENDATIONS
# -------------------------
if st.button("Generate Playlist 🎧"):

    results = search_music(query, mode_key)

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
    # SAVE PLAYLIST
    # -------------------------
    if st.button("💾 Save Playlist"):

        if "user" in st.session_state:

            users[st.session_state["user"]]["playlists"].append(results)
            save_users(users)

            st.success("Playlist saved 🎧")

        else:
            st.warning("Please login first")

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
                st.markdown(f"<div class='card'><b>{artist}</b></div>", unsafe_allow_html=True)

                if deezer:
                    st.image(deezer["image"], use_container_width=True)

# -------------------------
# ACTIVITY PANEL (ADMIN VIEW)
# -------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Activity Monitor")

if st.sidebar.button("Show Activity"):
    try:
        with open("activity_log.json", "r") as f:
            logs = json.load(f)

        st.sidebar.write(logs[-10:])

    except:
        st.sidebar.write("No activity yet")

# -------------------------
# FOOTER
# -------------------------
st.markdown("---")
st.markdown("💡 Built with Transformer NLP + Audio Intelligence + Deezer API")
st.markdown("🚀 Spotify-style AI Discovery Engine")
