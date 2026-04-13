import streamlit as st
import requests
from model import search_by_mood, df

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="AI Music Recommender", layout="wide")

st.title("🎧 AI Music Recommender System")

st.markdown("Built with Transformer NLP + Hybrid Recommendation Engine")

# -------------------------
# MODE SELECTION
# -------------------------
mode = st.radio("Choose Mode", ["🎭 Mood Search", "🎤 Artist Search", "🎼 Genre Search"])

query = ""

if mode == "🎭 Mood Search":
    query = st.text_input("Describe mood (sad, happy, chill, energetic)")

elif mode == "🎤 Artist Search":
    query = st.selectbox("Select Artist", sorted(df['track_artist'].unique()))

elif mode == "🎼 Genre Search":
    query = st.selectbox("Select Genre", sorted(df['playlist_genre'].unique()))

# -------------------------
# RECOMMEND BUTTON
# -------------------------
if st.button("Recommend 🎧"):

    results = search_by_mood(query)

    st.subheader("🎵 Recommended Songs")

    cols = st.columns(3)

    for i, r in enumerate(results):

        with cols[i % 3]:

            st.markdown(f"""
            <div style="
                padding:15px;
                border-radius:15px;
                background:#111;
                color:white;
                margin-bottom:15px;
                box-shadow:0px 0px 12px rgba(255,255,255,0.1);
            ">
                <h4>🎵 {r['song']}</h4>
                <p><b>Genre:</b> {r['genre']}</p>
                <p><b>Score:</b> {r['score']}</p>
                <p style="color:lightgray;">💡 {r['why']}</p>
            </div>
            """, unsafe_allow_html=True)
