
from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# MOODPULSE STUDIO V2
# =========================================================

BASE = Path.home() / "MoodPulse"
DATA = BASE / "data" / "Spotify.csv"
REPORTS = BASE / "output" / "advanced" / "reports"

GREEN = "#1ED760"
PALETTE = ["#1ED760", "#A7F3D0", "#65D46E", "#B7E4C7", "#52B788"]

st.set_page_config(
    page_title="MoodPulse Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------- DESIGN -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: radial-gradient(ellipse at 90% 0%, #173523 0%, #121212 34%);
    color: #FFFFFF;
}
.block-container {
    max-width: 1550px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.035em;
}
h1 {
    font-size: clamp(2rem, 4vw, 3rem) !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] {
    background: #080808;
    border-right: 1px solid #252525;
}
.mp-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 20px;
}
.mp-logo {
    background: #1ED760;
    color: #07160B;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    font-weight: 700;
}
.mp-name {
    font: 700 22px 'Space Grotesk', sans-serif;
}
.mp-sub {
    font-size: 10px;
    color: #1ED760;
    letter-spacing: 2px;
}
.mp-hero {
    background: linear-gradient(115deg, #1D472B, #193421 58%, #181818);
    border: 1px solid #285737;
    border-radius: 22px;
    padding: 30px;
    margin: 10px 0 24px;
}
.mp-eyebrow {
    font-size: 11px;
    color: #1ED760;
    letter-spacing: 2px;
    font-weight: 700;
}
.mp-hero h2 {
    font: 700 clamp(28px, 4vw, 45px) 'Space Grotesk', sans-serif;
    line-height: 1.12;
    margin: 12px 0;
}
.mp-hero p {
    color: #D5E8D9;
    max-width: 760px;
    line-height: 1.7;
}
[data-testid="stMetric"] {
    background: #181818;
    border: 1px solid #292929;
    border-radius: 16px;
    padding: 18px;
}
[data-testid="stMetricLabel"] {
    color: #B3B3B3 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif;
    color: white !important;
    font-weight: 700;
}
.stButton > button, .stDownloadButton > button {
    background: #1ED760;
    color: #07160B;
    border: none;
    border-radius: 30px;
    font-weight: 700;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #54F181;
    color: #07160B;
}
[data-testid="stDataFrame"] {
    border: 1px solid #292929;
    border-radius: 12px;
}
hr { border-color: #292929; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# --------------------- DATA HELPERS -----------------------

@st.cache_data
def load_data(path, modified):
    df = pd.read_csv(path, low_memory=False)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, [
        c for c in df.columns
        if not c.lower().startswith("unnamed:") and c != "_c0"
    ]]
    for col in [
        "popularity", "duration_ms", "danceability", "energy",
        "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "loudness", "tempo",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_report(name):
    path = REPORTS / name
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def chart_theme(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#EAEAEA"),
        colorway=PALETTE,
        height=height,
        margin=dict(l=10, r=10, t=55, b=15),
        xaxis=dict(gridcolor="#292929"),
        yaxis=dict(gridcolor="#292929"),
    )
    return fig


# --------------------- LOAD DATA --------------------------

st.sidebar.markdown("""
<div class="mp-brand">
  <div class="mp-logo">♫</div>
  <div>
    <div class="mp-name">MoodPulse</div>
    <div class="mp-sub">MUSIC INTELLIGENCE</div>
  </div>
</div>
""", unsafe_allow_html=True)

if not DATA.exists():
    st.error(f"Dataset not found: {DATA}")
    st.stop()

df = load_data(str(DATA), DATA.stat().st_mtime)

genre_col = next(
    (c for c in ["track_genre", "genre", "Genre"] if c in df.columns),
    None,
)
artist_col = next(
    (c for c in ["artists", "artist", "Artist"] if c in df.columns),
    None,
)
mood_col = next(
    (c for c in ["mood_category", "mood", "Mood"] if c in df.columns),
    None,
)

# Saved reports from Spark
evaluation = get_report("clustering_k_evaluation.csv")
profiles = get_report("existing_k4_cluster_profiles.csv")
quality_report = get_report("data_quality.csv")
genre_report = get_report("genre_analytics.csv")
mood_report = get_report("mood_analytics.csv")

raw_tracks = len(df)
processed_tracks = 113702  # From the successful Spark run
retention = processed_tracks / raw_tracks * 100 if raw_tracks else 0

best_k = None
best_silhouette = None

if not evaluation.empty and {
    "k", "silhouette_score"
}.issubset(evaluation.columns):
    evaluation["k"] = pd.to_numeric(evaluation["k"], errors="coerce")
    evaluation["silhouette_score"] = pd.to_numeric(
        evaluation["silhouette_score"], errors="coerce"
    )
    valid = evaluation.dropna(subset=["k", "silhouette_score"])
    if not valid.empty:
        best = valid.loc[valid["silhouette_score"].idxmax()]
        best_k = int(best["k"])
        best_silhouette = float(best["silhouette_score"])

st.sidebar.divider()
st.sidebar.caption("NAVIGATION")

page = st.sidebar.radio(
    "Go to",
    [
        "Home",
        "Genre Explorer",
        "Mood Lab",
        "Cluster Studio",
        "Data Quality",
        "Project Methodology",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("DATASET FILTERS")

filtered = df.copy()

if genre_col:
    options = sorted(df[genre_col].dropna().astype(str).unique())
    chosen = st.sidebar.multiselect("Genres", options)
    if chosen:
        filtered = filtered[filtered[genre_col].astype(str).isin(chosen)]

if "popularity" in df.columns:
    valid_pop = df["popularity"].dropna()
    if not valid_pop.empty and valid_pop.min() < valid_pop.max():
        pop_range = st.sidebar.slider(
            "Popularity",
            int(valid_pop.min()),
            int(valid_pop.max()),
            (int(valid_pop.min()), int(valid_pop.max())),
        )
        filtered = filtered[
            filtered["popularity"].between(*pop_range)
        ]

st.sidebar.caption(f"{len(filtered):,} raw tracks in current view")
st.sidebar.caption("PySpark · Streamlit · Plotly")


# =========================================================
# HOME
# =========================================================

if page == "Home":
    st.markdown("""
    <div class="mp-eyebrow">MUSIC DATA INTELLIGENCE · 2026</div>
    <div class="mp-hero">
      <div class="mp-eyebrow">YOUR SOUND, DECODED</div>
      <h2>Understand the music.<br>Discover the patterns.</h2>
      <p>
        Explore 114,000 Spotify tracks through big-data processing,
        genre analysis, audio-feature relationships and unsupervised
        machine learning.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RAW TRACKS", f"{raw_tracks:,}")
    c2.metric("SPARK-PROCESSED", f"{processed_tracks:,}")
    c3.metric("TRACKS RETAINED", f"{retention:.2f}%")
    c4.metric(
        "BEST SILHOUETTE",
        f"{best_silhouette:.4f}" if best_silhouette is not None else "—",
        f"K = {best_k}" if best_k is not None else None,
    )

    st.markdown("")
    st.markdown('<div class="mp-eyebrow">THE BIG PICTURE</div>',
                unsafe_allow_html=True)
    st.header("Your music landscape")

    left, right = st.columns(2)

    with left:
        if not genre_report.empty:
            st.subheader("Genre analytics · Spark")
            st.dataframe(genre_report.head(12), use_container_width=True)
        elif genre_col:
            counts = (
                filtered[genre_col].dropna().astype(str)
                .value_counts().head(15).sort_values()
                .rename_axis("Genre").reset_index(name="Tracks")
            )
            fig = px.bar(
                counts, x="Tracks", y="Genre",
                orientation="h", title="Tracks per genre",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(chart_theme(fig, 410), use_container_width=True)

    with right:
        if "popularity" in filtered.columns:
            fig = px.histogram(
                filtered.dropna(subset=["popularity"]),
                x="popularity", nbins=25,
                title="Track popularity distribution",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(chart_theme(fig, 410), use_container_width=True)

    audio = [
        c for c in [
            "danceability", "energy", "valence",
            "acousticness", "speechiness", "instrumentalness",
        ] if c in filtered.columns
    ]
    if audio:
        st.subheader("Audio DNA")
        means = filtered[audio].mean().rename_axis("Feature").reset_index(name="Average")
        means["Feature"] = means["Feature"].str.replace("_", " ").str.title()
        fig = px.bar(
            means, x="Feature", y="Average",
            title="Average audio-feature profile",
            color="Average",
            color_continuous_scale=["#174A2A", GREEN],
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_theme(fig, 340), use_container_width=True)


# =========================================================
# GENRE EXPLORER
# =========================================================


elif page == "Genre Explorer":
    st.markdown(
        '<div class="mp-eyebrow">GENRE INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )
    st.title("Explore the soundscape")

    if not genre_report.empty:
        st.subheader("Genre performance · Spark analytics")

        genre_name = next(
            (c for c in ["track_genre", "genre", "Genre"]
             if c in genre_report.columns),
            None,
        )
        popularity_name = next(
            (c for c in ["avg_popularity", "average_popularity"]
             if c in genre_report.columns),
            None,
        )
        count_name = next(
            (c for c in ["track_count", "count", "tracks"]
             if c in genre_report.columns),
            None,
        )

        if genre_name and popularity_name:
            chart_df = genre_report.copy()
            chart_df[popularity_name] = pd.to_numeric(
                chart_df[popularity_name], errors="coerce"
            )
            chart_df = chart_df.dropna(subset=[popularity_name])
            chart_df = chart_df.sort_values(
                popularity_name, ascending=False
            )

            top_n = st.slider(
                "Number of genres",
                min_value=5,
                max_value=min(30, len(chart_df)),
                value=min(15, len(chart_df)),
            )

            top = chart_df.head(top_n).sort_values(popularity_name)

            fig = px.bar(
                top,
                x=popularity_name,
                y=genre_name,
                orientation="h",
                title="Highest average popularity by genre",
                labels={
                    popularity_name: "Average popularity",
                    genre_name: "Genre",
                },
                color=popularity_name,
                color_continuous_scale=["#175C32", "#1ED760", "#C6FFD7"],
                hover_data=[count_name] if count_name else None,
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                chart_theme(fig, max(400, top_n * 27)),
                use_container_width=True,
            )

            st.subheader("Genre performance table")
            columns = [genre_name, popularity_name]
            if count_name:
                columns.append(count_name)

            st.dataframe(
                chart_df[columns].reset_index(drop=True),
                use_container_width=True,
            )

            st.download_button(
                "Download genre analytics",
                data=chart_df.to_csv(index=False).encode("utf-8"),
                file_name="moodpulse_genre_analytics.csv",
                mime="text/csv",
            )
        else:
            st.warning(
                "Expected genre or popularity columns were not found. "
                "Available columns: " + ", ".join(genre_report.columns)
            )
            st.dataframe(genre_report, use_container_width=True)

    elif genre_col:
        genre_stats = filtered.groupby(genre_col).agg(
            track_count=(genre_col, "size"),
            avg_popularity=("popularity", "mean")
            if "popularity" in filtered.columns
            else (genre_col, "size"),
        ).reset_index()

        if "popularity" not in filtered.columns:
            genre_stats = genre_stats.drop(
                columns=["avg_popularity"], errors="ignore"
            )

        if "avg_popularity" in genre_stats.columns:
            top = genre_stats.nlargest(
                20, "avg_popularity"
            ).sort_values("avg_popularity")

            fig = px.bar(
                top,
                x="avg_popularity",
                y=genre_col,
                orientation="h",
                title="Highest average popularity by genre",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(
                chart_theme(fig, 500),
                use_container_width=True,
            )

        st.dataframe(genre_stats, use_container_width=True)
    else:
        st.warning("No genre column was found in the dataset.")

# =========================================================
# MOOD LAB
# =========================================================

elif page == "Mood Lab":
    st.markdown('<div class="mp-eyebrow">AUDIO & MOOD</div>',
                unsafe_allow_html=True)
    st.title("Inside the feeling")

    if mood_col:
        moods = (
            filtered[mood_col].fillna("Unknown").astype(str)
            .value_counts().rename_axis("Mood")
            .reset_index(name="Tracks")
        )
        left, right = st.columns(2)
        with left:
            fig = px.pie(
                moods, names="Mood", values="Tracks", hole=0.55,
                title="Mood distribution", color_discrete_sequence=PALETTE,
            )
            st.plotly_chart(chart_theme(fig, 400), use_container_width=True)
        with right:
            fig = px.bar(
                moods.sort_values("Tracks"), x="Tracks", y="Mood",
                orientation="h", title="Tracks by mood",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(chart_theme(fig, 400), use_container_width=True)
    elif not mood_report.empty:
        st.dataframe(mood_report, use_container_width=True)
    else:
        st.info("Mood labels are not available in the raw CSV or saved report.")

    audio = [
        c for c in [
            "danceability", "energy", "valence", "acousticness",
            "speechiness", "instrumentalness", "liveness", "loudness", "tempo",
        ] if c in filtered.columns
    ]

    if len(audio) >= 2:
        st.subheader("Feature correlation matrix")
        corr = filtered[audio].corr(numeric_only=True)
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=["#173523", GREEN, "#E7F9EC"],
            zmin=-1, zmax=1,
        )
        st.plotly_chart(chart_theme(fig, 540), use_container_width=True)


# =========================================================
# CLUSTER STUDIO
# =========================================================

elif page == "Cluster Studio":
    st.markdown('<div class="mp-eyebrow">UNSUPERVISED LEARNING</div>',
                unsafe_allow_html=True)
    st.title("Cluster Studio")

    if not evaluation.empty:
        if {"k", "silhouette_score"}.issubset(evaluation.columns):
            valid = evaluation.dropna(subset=["k", "silhouette_score"])
            if not valid.empty:
                best = valid.loc[valid["silhouette_score"].idxmax()]
                a, b, c = st.columns(3)
                a.metric("K VALUES TESTED", len(valid))
                b.metric("BEST K", int(best["k"]))
                c.metric("BEST SILHOUETTE", f"{best['silhouette_score']:.4f}")

                fig = px.bar(
                    valid.sort_values("k"),
                    x="k", y="silhouette_score",
                    title="Silhouette score by K",
                    color="silhouette_score",
                    color_continuous_scale=["#174A2A", GREEN],
                )
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(chart_theme(fig, 400), use_container_width=True)

        st.dataframe(evaluation, use_container_width=True)
    else:
        st.warning("Run the clustering evaluation script to create the report.")

    st.divider()
    st.subheader("Existing K=4 cluster profiles")
    if not profiles.empty:
        st.dataframe(profiles, use_container_width=True)
        features = [c for c in profiles.columns if c.startswith("avg_")]
        if "cluster" in profiles.columns and features:
            selected = st.multiselect(
                "Audio features",
                features,
                default=features[:4],
            )
            if selected:
                chart_data = profiles[["cluster"] + selected].melt(
                    id_vars="cluster",
                    var_name="Feature",
                    value_name="Average",
                )
                fig = px.bar(
                    chart_data, x="Feature", y="Average",
                    color="cluster", barmode="group",
                    title="Audio profile by cluster",
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(chart_theme(fig, 430), use_container_width=True)
    else:
        st.info("Run the cluster-profile script to create this report.")


# =========================================================
# DATA QUALITY
# =========================================================

elif page == "Data Quality":
    st.markdown('<div class="mp-eyebrow">DATA GOVERNANCE</div>',
                unsafe_allow_html=True)
    st.title("Data quality monitor")

    missing = filtered.isna().sum().rename("Missing").reset_index()
    missing.columns = ["Column", "Missing values"]
    missing["Missing %"] = (
        missing["Missing values"] / max(len(filtered), 1) * 100
    )

    a, b, c = st.columns(3)
    a.metric("ROWS IN VIEW", f"{len(filtered):,}")
    b.metric("COLUMNS", f"{len(filtered.columns):,}")
    c.metric("DUPLICATE ROWS IN VIEW", f"{int(filtered.duplicated().sum()):,}")

    fig = px.bar(
        missing.nlargest(20, "Missing values").sort_values("Missing values"),
        x="Missing values", y="Column", orientation="h",
        title="Missing values by column",
        color_discrete_sequence=[GREEN],
    )
    st.plotly_chart(chart_theme(fig, 460), use_container_width=True)
    st.dataframe(missing, use_container_width=True)

    if not quality_report.empty:
        st.subheader("Spark ETL quality report")
        st.dataframe(quality_report, use_container_width=True)


# =========================================================
# PROJECT METHODOLOGY
# =========================================================

elif page == "Project Methodology":
    st.markdown('<div class="mp-eyebrow">BEHIND THE PROJECT</div>',
                unsafe_allow_html=True)
    st.title("How MoodPulse works")

    st.markdown("""
    <div class="mp-hero">
      <div class="mp-eyebrow">PROJECT OVERVIEW</div>
      <h2>From raw tracks to music insights.</h2>
      <p>
        A Spark-based analytics workflow for cleaning music metadata,
        engineering audio features, discovering trends and evaluating
        unsupervised clusters.
      </p>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Data ingestion", "Read the Spotify CSV dataset."),
        ("02", "Data cleaning", "Cast types, handle missing values and filter invalid records."),
        ("03", "Feature engineering", "Create derived metrics and rule-based mood categories."),
        ("04", "Distributed analytics", "Aggregate trends by genre, artist, mood and audio features."),
        ("05", "Machine learning", "Compare K-Means configurations with silhouette evaluation."),
        ("06", "Visualization", "Explore the output through Streamlit and Plotly."),
    ]

    for number, title, description in steps:
        st.markdown(f"""
        <div style="background:#181818;border:1px solid #292929;
                    border-radius:14px;padding:18px;margin-bottom:10px;">
          <span style="color:#1ED760;font-size:22px;font-weight:700;">
            {number}
          </span>
          <strong style="margin-left:15px;">{title}</strong>
          <div style="color:#B3B3B3;margin:8px 0 0 40px;">
            {description}
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("Technology stack")
    x, y, z = st.columns(3)
    x.markdown("**PROCESSING**")
    x.write("Apache Spark · PySpark")
    y.markdown("**MACHINE LEARNING**")
    y.write("Spark MLlib · K-Means")
    z.markdown("**DASHBOARD**")
    z.write("Streamlit · Plotly · Pandas")

    st.info(
        "Spark currently runs locally. Only claim HDFS or Hive deployment "
        "if those components have been separately implemented and tested."
    )


# --------------------- FOOTER ------------------------------

st.divider()
st.caption("♫ MOODPULSE STUDIO · Music data, machine learning and analytics")
