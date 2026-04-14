# 🎧✨ AI MUSIC RECOMMENDER SYSTEM  
Transformer NLP + Playlist Intelligence + Discovery Engine 🚀
🌟 Overview

This project is an AI-powered music recommendation system that combines:

🧠 Transformer-based NLP (Sentence-BERT)
🎼 Audio feature engineering (Spotify dataset)
⚖️ Hybrid scoring (text + audio similarity)
🎤 Artist & genre-based discovery system
🎧 Deezer API for real song previews
🌐 Streamlit web app deployment

It behaves like a mini Spotify recommendation engine, but built from scratch.

🚀 Live Demo

👉 (Add your Streamlit Cloud link here)
Example:

https://ai-music-recommendation-system-lpfrsdplgtwhr5yb3ns4mx.streamlit.app/

🧠 Tech Stack
Python 🐍
Streamlit 🎈
Sentence Transformers 🤖
Scikit-learn 📊
Pandas / NumPy 📁
Deezer API 🎧

📊 Dataset

Spotify Audio Features Dataset:

Includes:

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


🧠 Model Architecture
1. Text Understanding (Transformer NLP)
track_artist + genre + subgenre → Sentence-BERT embeddings
2. Audio Intelligence

Engineered features:

mood_score
intensity
dance_index
rap_score
3. Hybrid Scoring System
final_score =
    0.6 × text_similarity +
    0.4 × audio_similarity


🎧 Features
🎤 Artist Mode
Select an artist
Get similar artists
Get top recommended tracks

▶️ Music Preview
Album cover images
30-sec audio preview (Deezer API)


🧠 Key Innovation

This is NOT a basic ML project.

It includes:

Transformer-based semantic understanding
Audio feature fusion
Hybrid recommendation scoring
Diversity-aware ranking system
Real-time music preview integration


AI-Music-Recommender/

│
├── app.py              # Streamlit frontend

├── model.py            # AI recommendation engine

├── music_df.csv        # Spotify dataset

├── text_embeddings.pkl # Precomputed embeddings

├── audio_matrix.npy    # Feature matrix

├── requirements.txt    # Dependencies


⚙️ How It Works

Step 1: User Input

Artist OR Genre selection

Step 2: AI Processing

Transformer encodes query

Cosine similarity computation

Audio feature blending

Step 3: Ranking Engine

Removes duplicates

Applies genre penalty

Adds exploration factor

Step 4: Output Layer

Ranked songs

Similar artists

Album covers + previews

Step 5: Fallback Layer (if needed)

Ensures minimum results always shown

├── .streamlit/config.toml  # UI config

🧪 Example Output
Input: Taylor Swift

Output:
🎵 Taylor Swift — pop — 0.75  
🎵 Tate McRae — pop — 0.54  
🎵 Eminem, Rihanna — blues — 0.70  
🎵 Madonna — pop — 0.56  

🌐 Deployment
Streamlit 
GitHub integration


⚠️ Smart Fallback System (Cold Start Handling)
🧠 Problem

In real-world usage, users may search for:

Rare artists 🎤
Low-representation genres 🎼
Out-of-dataset queries ❌

This can lead to:

Empty recommendations
Poor quality matches
Reduced user experience















