
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------
BASE_DIR = Path.home() / "MoodPulse"
DATA_PATH = BASE_DIR / "data" / "Spotify.csv"
OUTPUT_DIR = BASE_DIR / "output"
ADVANCED_DIR = OUTPUT_DIR / "advanced"
REPORT_DIR = ADVANCED_DIR / "reports"

st.set_page_config(
    page_title="MoodPulse AI Analytics",
    page_icon="🎵",
    layout="wide",
)

# --------------------------------------------------
# PREMIUM MOODPULSE UI THEME
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --mp-bg: #09090F;
    --mp-panel: #151522;
    --mp-border: rgba(167,139,250,0.20);
    --mp-purple: #A78BFA;
    --mp-cyan: #67E8F9;
    --mp-text: #F4F4FA;
    --mp-muted: #A3A3B8;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 5% 0%, rgba(124,58,237,0.16), transparent 35%),
        radial-gradient(ellipse at 95% 10%, rgba(6,182,212,0.09), transparent 32%),
        var(--mp-bg);
    color: var(--mp-text);
}

.block-container {
    max-width: 1500px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -0.04em;
}

h1 {
    font-size: clamp(2.1rem, 4vw, 3.4rem) !important;
    font-weight: 700 !important;
    background: linear-gradient(100deg, #FFFFFF 10%, #C4B5FD 55%, #67E8F9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    padding-bottom: 0.15rem;
}

h2 { font-weight: 600 !important; }
h3 { font-weight: 600 !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12121E, #0C0C14);
    border-right: 1px solid var(--mp-border);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #E9D5FF;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #191929, #11111B);
    border: 1px solid var(--mp-border);
    border-radius: 18px;
    padding: 20px 20px 16px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.18);
    transition: transform 180ms ease, border-color 180ms ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    border-color: rgba(103,232,249,0.5);
}

[data-testid="stMetricLabel"] {
    color: var(--mp-muted) !important;
    font-size: 0.85rem !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif;
    color: #FFFFFF !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(21,21,34,0.8);
    border: 1px solid var(--mp-border);
    padding: 7px;
    border-radius: 15px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 17px;
    font-weight: 600;
    color: var(--mp-muted);
    background: transparent;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(110deg, #7C3AED, #6D28D9) !important;
    color: white !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid rgba(167,139,250,0.35);
    background: linear-gradient(110deg, #7C3AED, #6D28D9);
    color: white;
    font-weight: 600;
    padding: 0.55rem 1rem;
    transition: all 180ms ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #67E8F9;
    box-shadow: 0 0 22px rgba(167,139,250,0.22);
    transform: translateY(-1px);
    color: white;
}

div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid var(--mp-border);
    border-radius: 14px;
    overflow: hidden;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: var(--mp-border);
}

[data-testid="stCaptionContainer"] {
    color: var(--mp-muted);
}

[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stSlider"] label {
    font-weight: 600;
    color: #D8D8E8;
}

footer { visibility: hidden; }

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    [data-testid="stMetric"] {
        padding: 13px;
    }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 2. DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_dataset(path, modified_time):
    df = pd.read_csv(path, low_memory=False)

    # Remove an exported CSV index column if present.
    unwanted = [
        c for c in df.columns
        if c.lower().startswith("unnamed:") or c == "_c0"
    ]
    df = df.drop(columns=unwanted, errors="ignore")

    # Convert numeric columns where available.
    numeric_cols = [
        "popularity", "duration_ms", "danceability",
        "energy", "speechiness", "acousticness",
        "instrumentalness", "liveness", "valence",
        "loudness", "tempo", "mood_score",
        "dance_energy_score", "duration_minutes", "bpm",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


@st.cache_data
def load_report(path, modified_time):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def find_report(filename):
    candidates = [
        REPORT_DIR / filename,
        ADVANCED_DIR / filename,
        OUTPUT_DIR / filename,
    ]

    for path in candidates:
        if path.is_file():
            return path

    return None


def get_report(filename):
    path = find_report(filename)

    if path is None:
        return pd.DataFrame()

    return load_report(str(path), path.stat().st_mtime)


# --------------------------------------------------
# 3. LOAD THE DATASET
# --------------------------------------------------
st.sidebar.title("🎵 MoodPulse")
st.sidebar.caption("Big Data Music Analytics")

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info(
        "Check that your Spotify CSV is saved at "
        "data/Spotify.csv inside the MoodPulse folder."
    )
    st.stop()

df = load_dataset(str(DATA_PATH), DATA_PATH.stat().st_mtime)

# Handle common column naming variations.
genre_col = next(
    (c for c in ["track_genre", "genre", "Genre"] if c in df.columns),
    None,
)
mood_col = next(
    (c for c in ["mood_category", "mood", "Mood"] if c in df.columns),
    None,
)
artist_col = next(
    (c for c in ["artists", "artist", "Artist"] if c in df.columns),
    None,
)
track_col = next(
    (c for c in ["track_name", "track", "Track"] if c in df.columns),
    None,
)

# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.subheader("Filters")

filtered = df.copy()

if genre_col:
    genres = sorted(
        df[genre_col].dropna().astype(str).unique().tolist()
    )
    selected_genres = st.sidebar.multiselect(
        "Music genres",
        genres,
        default=[],
    )
    if selected_genres:
        filtered = filtered[
            filtered[genre_col].astype(str).isin(selected_genres)
        ]

if "popularity" in df.columns:
    popularity_values = df["popularity"].dropna()

    if not popularity_values.empty:
        min_pop = int(popularity_values.min())
        max_pop = int(popularity_values.max())

        if min_pop < max_pop:
            selected_range = st.sidebar.slider(
                "Popularity range",
                min_value=min_pop,
                max_value=max_pop,
                value=(min_pop, max_pop),
            )
            filtered = filtered[
                filtered["popularity"].between(
                    selected_range[0], selected_range[1]
                )
            ]

if "explicit" in df.columns:
    explicit_filter = st.sidebar.selectbox(
        "Explicit content",
        ["All", "Explicit only", "Non-explicit only"],
    )

    if explicit_filter == "Explicit only":
        filtered = filtered[
            filtered["explicit"].astype(str).str.lower().isin(
                ["true", "1", "yes"]
            )
        ]
    elif explicit_filter == "Non-explicit only":
        filtered = filtered[
            filtered["explicit"].astype(str).str.lower().isin(
                ["false", "0", "no"]
            )
        ]

st.sidebar.divider()
st.sidebar.caption(f"Source: {DATA_PATH.name}")
st.sidebar.caption("Analytics powered by PySpark outputs")

# --------------------------------------------------
# 5. HEADER
# --------------------------------------------------
st.title("🎵 MoodPulse AI Analytics Platform")
st.markdown(
    "### Explore music trends, audio characteristics and mood patterns"
)
st.caption(
    "An interactive music analytics dashboard built with Python, "
    "Streamlit, Plotly and Apache Spark."
)

overview_tab, genre_tab, mood_tab, cluster_tab, quality_tab = st.tabs(
    [
        "📊 Overview",
        "🎸 Genre Analytics",
        "😊 Mood Analytics",
        "🧠 Clustering",
        "🛠️ Data Quality",
    ]
)

# --------------------------------------------------
# 6. OVERVIEW
# --------------------------------------------------
with overview_tab:
    st.subheader("Dataset overview")

    total_tracks = len(filtered)
    unique_artists = (
        filtered[artist_col].nunique()
        if artist_col else 0
    )
    unique_genres = (
        filtered[genre_col].nunique()
        if genre_col else 0
    )
    avg_popularity = (
        filtered["popularity"].mean()
        if "popularity" in filtered.columns else None
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tracks", f"{total_tracks:,}")
    c2.metric("Unique artists", f"{unique_artists:,}")
    c3.metric("Genres", f"{unique_genres:,}")
    c4.metric(
        "Average popularity",
        f"{avg_popularity:.1f}" if pd.notna(avg_popularity)
        else "N/A",
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### Track popularity")

        if "popularity" in filtered.columns:
            fig = px.histogram(
                filtered,
                x="popularity",
                nbins=25,
                title="Distribution of track popularity",
                labels={"popularity": "Popularity score"},
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Popularity column is unavailable.")

    with right:
        st.markdown("#### Audio characteristics")

        audio_cols = [
            c for c in [
                "danceability", "energy", "valence",
                "acousticness", "speechiness",
                "instrumentalness",
            ]
            if c in filtered.columns
        ]

        if audio_cols:
            means = (
                filtered[audio_cols]
                .mean()
                .rename_axis("Feature")
                .reset_index(name="Average")
            )

            fig = px.bar(
                means,
                x="Feature",
                y="Average",
                title="Average audio feature values",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Audio feature columns are unavailable.")

    st.markdown("#### Dataset preview")
    st.dataframe(filtered.head(100), use_container_width=True)

    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered tracks",
        data=csv_data,
        file_name="moodpulse_filtered_tracks.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# 7. GENRE ANALYTICS
# --------------------------------------------------
with genre_tab:
    st.subheader("Genre analytics")

    if not genre_col:
        st.warning("No genre column was found in the dataset.")
    else:
        genre_stats = (
            filtered.groupby(genre_col, dropna=True)
            .agg(
                track_count=(genre_col, "size"),
                avg_popularity=("popularity", "mean")
                if "popularity" in filtered.columns
                else (genre_col, "size"),
            )
            .reset_index()
        )

        if "popularity" not in filtered.columns:
            genre_stats = genre_stats.drop(
                columns=["avg_popularity"], errors="ignore"
            )

        genre_stats = genre_stats.sort_values(
            "track_count", ascending=False
        )

        left, right = st.columns(2)

        with left:
            fig = px.bar(
                genre_stats.head(15),
                x="track_count",
                y=genre_col,
                orientation="h",
                title="Top 15 genres by track count",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

        with right:
            if "avg_popularity" in genre_stats.columns:
                popular = genre_stats.sort_values(
                    "avg_popularity", ascending=False
                ).head(15)

                fig = px.bar(
                    popular,
                    x="avg_popularity",
                    y=genre_col,
                    orientation="h",
                    title="Genres by average popularity",
                )
                fig.update_layout(
                    yaxis={"categoryorder": "total ascending"}
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Genre statistics")
        st.dataframe(genre_stats, use_container_width=True)

# --------------------------------------------------
# 8. MOOD ANALYTICS
# --------------------------------------------------
with mood_tab:
    st.subheader("Mood analysis")

    if mood_col:
        mood_stats = (
            filtered[mood_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Mood")
            .reset_index(name="Track count")
        )

        left, right = st.columns(2)

        with left:
            fig = px.pie(
                mood_stats,
                names="Mood",
                values="Track count",
                hole=0.45,
                title="Track distribution by mood",
            )
            st.plotly_chart(fig, use_container_width=True)

        with right:
            fig = px.bar(
                mood_stats,
                x="Mood",
                y="Track count",
                title="Mood category comparison",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Mood categories are rule-based labels from the processing "
            "pipeline; they are not verified human emotion annotations."
        )
    else:
        mood_report = get_report("mood_analytics.csv")

        if mood_report.empty:
            mood_report = get_report("mood_distribution.csv")

        if not mood_report.empty:
            st.dataframe(mood_report, use_container_width=True)
            st.info(
                "Displaying the saved mood report because no mood "
                "column was found in the source CSV."
            )
        else:
            st.info(
                "No mood labels or mood report found. Run the Spark "
                "pipeline to generate mood analytics."
            )

    st.markdown("#### Audio feature relationships")

    scatter_cols = [
        c for c in ["energy", "valence", "danceability", "acousticness"]
        if c in filtered.columns
    ]

    if len(scatter_cols) >= 2:
        x_feature = st.selectbox(
            "X-axis feature",
            scatter_cols,
            index=0,
        )
        y_feature = st.selectbox(
            "Y-axis feature",
            scatter_cols,
            index=1 if len(scatter_cols) > 1 else 0,
        )

        fig = px.scatter(
            filtered.sample(min(len(filtered), 4000), random_state=42),
            x=x_feature,
            y=y_feature,
            color=mood_col if mood_col else None,
            opacity=0.5,
            title=f"{x_feature.title()} vs {y_feature.title()}",
        )
        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# 9. CLUSTERING ANALYTICS
# --------------------------------------------------
with cluster_tab:
    st.subheader("K-Means clustering evaluation")

    evaluation = get_report("clustering_k_evaluation.csv")
    profiles = get_report("existing_k4_cluster_profiles.csv")

    if not evaluation.empty:
        st.markdown("#### Compare K values")

        if {"k", "silhouette_score"}.issubset(evaluation.columns):
            evaluation["k"] = evaluation["k"].astype(str)

            fig = px.bar(
                evaluation.sort_values("k"),
                x="k",
                y="silhouette_score",
                title="Silhouette score by number of clusters",
                labels={
                    "k": "Number of clusters",
                    "silhouette_score": "Silhouette score",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(evaluation, use_container_width=True)
    else:
        st.info(
            "Run src/moodpulse_clustering_eval.py to display the "
            "K-Means comparison."
        )

    if not profiles.empty:
        st.markdown("#### Existing K=4 cluster profiles")

        if "cluster" in profiles.columns:
            profiles["cluster"] = profiles["cluster"].astype(str)

        st.dataframe(profiles, use_container_width=True)

        feature_cols = [
            c for c in profiles.columns
            if c.startswith("avg_")
        ]

        if feature_cols:
            selected_features = st.multiselect(
                "Features to compare",
                feature_cols,
                default=feature_cols[:4],
            )

            if selected_features:
                plot_data = profiles[
                    ["cluster"] + selected_features
                ].melt(
                    id_vars="cluster",
                    var_name="Feature",
                    value_name="Average",
                )

                fig = px.bar(
                    plot_data,
                    x="Feature",
                    y="Average",
                    color="cluster",
                    barmode="group",
                    title="Audio characteristics by cluster",
                )
                st.plotly_chart(fig, use_container_width=True)

        st.download_button(
            "⬇️ Download cluster profiles",
            data=profiles.to_csv(index=False).encode("utf-8"),
            file_name="moodpulse_cluster_profiles.csv",
            mime="text/csv",
        )
    else:
        st.info(
            "Run src/moodpulse_cluster_profiles_v2.py to generate "
            "the cluster profile report."
        )

# --------------------------------------------------
# 10. DATA QUALITY
# --------------------------------------------------
with quality_tab:
    st.subheader("Data quality and processing")

    quality_report = get_report("data_quality.csv")

    q1, q2, q3 = st.columns(3)

    q1.metric("Rows in filtered view", f"{len(filtered):,}")
    q2.metric("Columns", f"{len(filtered.columns):,}")
    q3.metric(
        "Duplicate rows in view",
        f"{int(filtered.duplicated().sum()):,}",
    )

    missing = (
        filtered.isna()
        .sum()
        .rename_axis("Column")
        .reset_index(name="Missing values")
    )
    missing["Missing percentage"] = (
        missing["Missing values"] / max(len(filtered), 1) * 100
    )

    st.markdown("#### Missing values by column")

    missing = missing.sort_values(
        "Missing values", ascending=False
    )

    fig = px.bar(
        missing.head(20),
        x="Missing values",
        y="Column",
        orientation="h",
        title="Columns with the most missing values",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(missing, use_container_width=True)

    if not quality_report.empty:
        st.markdown("#### Spark processing quality report")
        st.dataframe(quality_report, use_container_width=True)
    else:
        st.info(
            "The Spark quality report was not found. The metrics above "
            "are calculated from the currently loaded CSV and filters."
        )

    st.markdown("#### Available analytics reports")

    report_names = [
        "genre_analytics.csv",
        "genre_volume.csv",
        "artist_analytics.csv",
        "mood_analytics.csv",
        "bpm_distribution.csv",
        "explicit_analytics.csv",
        "numeric_summary.csv",
        "correlation_analysis.csv",
        "feature_quantiles.json",
        "clustering_k_evaluation.csv",
        "existing_k4_cluster_profiles.csv",
    ]

    available = []
    for name in report_names:
        path = find_report(name)
        available.append({
            "Report": name,
            "Status": "Available" if path else "Not found",
            "Location": str(path) if path else "-",
        })

    st.dataframe(pd.DataFrame(available), use_container_width=True)

# --------------------------------------------------
# 11. FOOTER
# --------------------------------------------------
st.divider()
st.caption(
    "MoodPulse | Big Data Analytics | PySpark • Streamlit • Plotly"
)
