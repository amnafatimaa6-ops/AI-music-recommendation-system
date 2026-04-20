
# AI Music Recommender System 🎧✨

Transformer NLP + Audio Intelligence + Hybrid Discovery Engine

🌟 Overview

This project is an AI-powered music recommendation system that simulates a mini Spotify-like discovery engine built from scratch.
----------------------------------------------------------------------------------------------------------------------------------

It combines:

🧠 Transformer-based NLP (Sentence-BERT) for semantic understanding

🎼 Spotify audio feature engineering for music intelligence

⚖️ Hybrid recommendation scoring (text + audio fusion)

🎤 Artist & genre-based discovery system

🎧 Deezer API integration for album covers + 30s previews

🌐 Streamlit web app deployment

--------------------------------------------------------------------------------------------------------------

🚀 Live Demo


👉 https://ai-music-recommendation-system-lpfrsdplgtwhr5yb3ns4mx.streamlit.app/


### 📸 App Demo 1
![Demo 1](demo1.gif)



### 📸 App Demo 2
![Demo 2](demo2.gif)



### 📸 App Demo 3
![Demo 3](demo3.gif)

--------------------------------------------------------------------------------------------------------------
🧠 Tech Stack

Python 🐍

Streamlit 🎈

Sentence Transformers (SBERT) 🤖

Scikit-learn 📊

Pandas / NumPy 📁

Deezer API 🎧

-----------------------------------------------------------------------------------------------------------

📊 Dataset

Spotify Audio Features Dataset including:

energy
danceability
valence
tempo
loudness
speechiness
acousticness
instrumentalness
genre
artist

----------------------------------------------------------------------------------------------------------

🧠 Model Architecture
1. Text Understanding (Transformer NLP)
Combines track_artist + genre + metadata
Encodes using Sentence-BERT embeddings

3. Audio Intelligence Layer

Engineered features include:

mood_score

intensity score

danceability index

genre signals

3. Hybrid Scoring System
final_score = 0.6 × text_similarity + 0.4 × audio_similarity

🎧 Key Features
🎤 Artist Mode

Select an artist
Get similar artists
Get recommended tracks

🎼 Genre Mode
Explore songs by genre clusters
Discover related artists

🌌 Explore Mode
Type any mood / vibe / keyword
AI interprets intent semantically

▶️ Music Preview System

🎨 Album covers (Deezer API)

🎧 30-second audio previews

🎵 Real-time song playback

🧠 Key Innovations

This is NOT a basic ML project.

It includes:

Transformer-based semantic understanding
Hybrid recommendation scoring system
Diversity-aware ranking engine
Cold-start fallback system
Real-time music preview integration
Dataset fusion across multiple sources

---------------------------------------------------------------------------------------

📁 Project Structure

AI-Music-Recommender/

│── app.py                  # Streamlit frontend  
│── model.py                # AI recommendation engine  
│── music_df.csv            # Spotify dataset  
│── spotify_songs.csv       # Additional dataset  
│── text_embeddings.pkl     # Precomputed SBERT embeddings  
│── audio_matrix.npy        # Feature matrix  
│── requirements.txt        # Dependencies  
│
│── .streamlit/
│     └── config.toml       
⚙️ How It Works

---------------------------------------------------------------------------------------------------

Step 1: User Input

User selects or types:

Artist

Genre

Mood / vibe

Step 2: AI Processing

Sentence-BERT encodes query
Cosine similarity computed
Audio features fused with semantic score

Step 3: Ranking Engine
Removes duplicates
Applies genre weighting
Adds exploration factor

Step 4: Output Layer
Ranked songs
Similar artists
Album covers
Audio previews

Step 5: Fallback System

Ensures:

No empty results
Always returns recommendations
Handles cold-start queries
🧪 Example Output

Input: Taylor Swift

Output:

🎵 Taylor Swift — pop — 0.75

🎵 Tate McRae — pop — 0.54

🎵 Eminem, Rihanna — blues — 0.70

🎵 Madonna — pop — 0.56


------------------------------------------------------------------------------------------

⚠️ Smart Fallback System

🧠 Problem

Real users often search:

Rare artists 🎤
Small genres 🎼
Out-of-dataset queries ❌

🛠 Solution

System automatically:

Falls back to closest semantic matches
Uses genre clustering
Ensures results are always returned

---------------------------------------------------------------------------------------------

🌐 Deployment
Streamlit Cloud deployment
GitHub-integrated CI workflow
Real-time API calls to Deezer

---------------------------------------------------------------------------------------------

💡 Future Improvements
Spotify OAuth integration
Personalized user taste profiles
Playlist generation engine
Reinforcement learning ranking system
“For You” AI feed

-------------------------------------------------------------------------------------------

🏁 Summary

This project demonstrates:

🎯 A full-stack AI recommendation system combining NLP, audio intelligence, and real-time music APIs.

It bridges:

Machine Learning 🤖

NLP 🧠

Recommender Systems 🎧

Web Deployment 🌐
