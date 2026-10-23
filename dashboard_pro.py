import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MoodPulse AI",
    page_icon="🎵",
    layout="wide"
)

st.title("🎵 MoodPulse AI Analytics Platform")

df = pd.read_csv("data/spotify.csv")
def classify_mood(row):
    if row["energy"] > 0.75 and row["valence"] > 0.75:
        return "Party"
    elif row["valence"] > 0.7:
        return "Happy"
    elif row["energy"] > 0.7:
        return "Energetic"
    elif row["valence"] < 0.3:
        return "Sad"
    else:
        return "Neutral"

df["mood"] = df.apply(classify_mood, axis=1)

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Mood Analytics",
        "Genre Analytics",
        "Song Explorer"
    ]
)

if page == "Overview":
    st.header("Executive Dashboard")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Songs", len(df))
    c2.metric("Artists", df["artists"].nunique())
    c3.metric("Genres", df["track_genre"].nunique())
    c4.metric("Avg Popularity", round(df["popularity"].mean(), 2))

if page == "Mood Analytics":
    st.header("Mood Analytics")
    mood_counts = (
        df["mood"]
        .value_counts()
        .reset_index()
    )

    mood_counts.columns = ["Mood", "Count"]

    fig = px.pie(
        mood_counts,
        names="Mood",
        values="Count",
        hole=0.55,
        title="Mood Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

if page == "Genre Analytics":
    st.header("Genre Analytics")
    genre_counts = (
        df["track_genre"]
        .value_counts()
        .head(25)
        .reset_index()
    )

    genre_counts.columns = ["Genre", "Count"]

    fig = px.treemap(
        genre_counts,
        path=["Genre"],
        values="Count",
        title="Top Genres"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
    
if page == "Song Explorer":
    st.header("Song Explorer")
    search = st.text_input(
        "Search Song Name"
    )

    if search:

        results = df[
            df["track_name"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

        st.dataframe(
            results.head(50)
        )
