import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="MoodPulse Dashboard",
    layout="wide"
)

st.title("🎵 MoodPulse Dashboard")
st.subheader("Big Data Analytics using Apache Spark")

# Load data
df = pd.read_csv("data/spotify.csv")

# Mood logic
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

# Sidebar
st.sidebar.header("Filters")

selected_mood = st.sidebar.multiselect(
    "Select Mood",
    df["mood"].unique(),
    default=df["mood"].unique()
)

filtered_df = df[df["mood"].isin(selected_mood)]

# KPIs
c1, c2, c3 = st.columns(3)

c1.metric("Songs", len(filtered_df))
c2.metric("Artists", filtered_df["artists"].nunique())
c3.metric("Genres", filtered_df["track_genre"].nunique())

# Mood Distribution
st.subheader("Mood Distribution")

mood_counts = (
    filtered_df["mood"]
    .value_counts()
    .reset_index()
)

mood_counts.columns = ["Mood", "Count"]

fig = px.bar(
    mood_counts,
    x="Mood",
    y="Count",
    title="Songs by Mood"
)

st.plotly_chart(fig, use_container_width=True)

# Genre Distribution
st.subheader("Top Genres")

genre_counts = (
    filtered_df["track_genre"]
    .value_counts()
    .head(10)
    .reset_index()
)

genre_counts.columns = ["Genre", "Count"]

fig2 = px.bar(
    genre_counts,
    x="Genre",
    y="Count"
)

st.plotly_chart(fig2, use_container_width=True)

# Popular Artists
st.subheader("Top Artists")

artist_counts = (
    filtered_df["artists"]
    .value_counts()
    .head(10)
    .reset_index()
)

artist_counts.columns = ["Artist", "Count"]

fig3 = px.bar(
    artist_counts,
    x="Artist",
    y="Count"
)

st.plotly_chart(fig3, use_container_width=True)

# Song Browser
st.subheader("Browse Songs")

st.dataframe(
    filtered_df[
        [
            "track_name",
            "artists",
            "track_genre",
            "popularity",
            "mood"
        ]
    ].head(100)
)
