# -------------------------
# LOAD & MERGE DATASETS (3 FILES)
# -------------------------
def load_data():

    # LOAD EXISTING
    try:
        df1 = pd.read_csv("data/music_df.csv")
    except:
        df1 = pd.DataFrame()

    try:
        df2 = pd.read_csv("data/spotify_songs.csv")
    except:
        df2 = pd.DataFrame()

    # NEW DATASET
    try:
        df3 = pd.read_csv("data/data_by_artist.csv")
    except:
        df3 = pd.DataFrame()

    # -------------------------
    # CLEAN FUNCTION
    # -------------------------
    def clean(df):

        if df.empty:
            return df

        df = df.copy()

        # ARTIST COLUMN FIX
        if "track_artist" not in df.columns:
            if "artist" in df.columns:
                df["track_artist"] = df["artist"]
            elif "artists" in df.columns:
                df["track_artist"] = df["artists"]

        # GENRE FIX
        if "playlist_genre" not in df.columns:
            if "genre" in df.columns:
                df["playlist_genre"] = df["genre"]
            else:
                df["playlist_genre"] = "unknown"

        # MOOD SCORE FIX
        if "mood_score" not in df.columns:
            df["mood_score"] = np.random.rand(len(df))

        return df[["track_artist", "playlist_genre", "mood_score"]]

    df1 = clean(df1)
    df2 = clean(df2)
    df3 = clean(df3)

    # -------------------------
    # MERGE ALL
    # -------------------------
    df = pd.concat([df1, df2, df3], ignore_index=True)

    df.dropna(inplace=True)

    # REMOVE DUPLICATES
    df.drop_duplicates(subset=["track_artist"], inplace=True)

    return df


# FINAL DATAFRAME
df = load_data()
