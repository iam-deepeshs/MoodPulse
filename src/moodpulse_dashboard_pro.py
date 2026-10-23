
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# MOODPULSE STUDIO | Spotify-inspired music analytics
# ============================================================

BASE_DIR = Path.home() / "MoodPulse"
DATA_PATH = BASE_DIR / "data" / "Spotify.csv"
OUTPUT_DIR = BASE_DIR / "output"
ADVANCED_DIR = OUTPUT_DIR / "advanced"
REPORT_DIR = ADVANCED_DIR / "reports"

GREEN = "#1ED760"
GREEN_DARK = "#169C46"
CHARCOAL = "#121212"
PANEL = "#181818"
MUTED = "#B3B3B3"
PALETTE = [
    "#1ED760", "#A7F3D0", "#65D46E",
    "#B7E4C7", "#52B788", "#D9F99D",
]

st.set_page_config(
    page_title="MoodPulse Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- VISUAL DESIGN ---------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --green: #1ED760;
    --bg: #121212;
    --panel: #181818;
    --panel-hover: #242424;
    --muted: #B3B3B3;
    --border: rgba(255,255,255,0.08);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 85% 0%, rgba(30,215,96,0.07), transparent 32%),
        #121212;
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
    color: #FFFFFF;
}

h1 {
    font-size: clamp(2rem, 4vw, 3.25rem) !important;
    font-weight: 700 !important;
}

h2 { font-weight: 600 !important; }
h3 { font-weight: 600 !important; }

[data-testid="stSidebar"] {
    background: #080808;
    border-right: 1px solid rgba(255,255,255,0.07);
}

[data-testid="stSidebar"] h1 {
    font-size: 1.7rem !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
}

.mp-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0 20px;
}

.mp-logo {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: #1ED760;
    color: #06170B;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 23px;
    font-weight: 700;
}

.mp-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
}

.mp-sub {
    color: #1ED760;
    font-size: 10px;
    letter-spacing: 2px;
    font-weight: 700;
}

.mp-eyebrow {
    color: #1ED760;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 0.4rem;
}

.mp-hero {
    padding: 30px;
    border-radius: 22px;
    background: linear-gradient(120deg, #1D4228 0%, #183321 45%, #181818 100%);
    border: 1px solid rgba(30,215,96,0.16);
    margin: 10px 0 24px;
}

.mp-hero h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(1.8rem, 4vw, 3rem);
    line-height: 1.12;
    margin: 0.3rem 0 0.8rem;
}

.mp-hero p {
    color: #D4E8D9;
    max-width: 720px;
    line-height: 1.65;
}

.mp-card {
    background: #181818;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 17px;
    padding: 21px;
    min-height: 120px;
}

.mp-label {
    color: #B3B3B3;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.mp-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    line-height: 1.35;
    font-weight: 700;
    color: #FFFFFF;
}

.mp-note {
    font-size: 0.8rem;
    color: #1ED760;
}

[data-testid="stMetric"] {
    background: #181818;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 18px;
}

[data-testid="stMetricLabel"] {
    color: #B3B3B3 !important;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
}

.stButton > button,
.stDownloadButton > button {
    background: #1ED760;
    color: #07160B;
    border: none;
    border-radius: 30px;
    font-weight: 700;
    padding: 0.55rem 1.15rem;
    transition: all 160ms ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #53F181;
    color: #07160B;
    border: none;
    transform: scale(1.015);
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 10px;
}

[data-testid="stTabs"] [aria-selected="true"] {
    color: #1ED760 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
}

[data-testid="stCaptionContainer"] {
    color: #B3B3B3;
}

hr {
    border-color: rgba(255,255,255,0.10);
}

footer { visibility: hidden; }

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .mp-hero { padding: 20px; }
}
</style>
""", unsafe_allow_html=True)


# -------------------- DATA HELPERS ----------------------------

@st.cache_data
def load_dataset(path, modified):
    data = pd.read_csv(path, low_memory=False)
    data.columns = [str(c).strip() for c in data.columns]

    # Remove exported index columns.
    data = data.loc[
        :,
        [
            c for c in data.columns
            if not c.lower().startswith("unnamed:")
            and c != "_c0"
        ],
    ]

    numeric_cols = [
        "popularity", "duration_ms", "danceability", "energy",
        "speechiness", "acousticness", "instrumentalness",
        "liveness", "valence", "loudness", "tempo",
        "mood_score", "dance_energy_score", "duration_minutes",
        "bpm", "key", "mode", "time_signature",
    ]

    for col in numeric_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    return data


@st.cache_data
def load_csv_report(path, modified):
    return pd.read_csv(path, low_memory=False)


@st.cache_data
def load_json_report(path, modified):
    return pd.read_json(path)


def report_path(filename):
    candidates = [
        REPORT_DIR / filename,
        ADVANCED_DIR / filename,
        OUTPUT_DIR / filename,
    ]
    return next((p for p in candidates if p.is_file()), None)


def get_report(filename):
    path = report_path(filename)
    if path is None:
        return pd.DataFrame()

    try:
        return load_csv_report(str(path), path.stat().st_mtime)
    except Exception:
        return pd.DataFrame()


def get_column(data, candidates):
    return next((c for c in candidates if c in data.columns), None)


def safe_mean(data, column):
    if column not in data.columns:
        return None
    result = pd.to_numeric(data[column], errors="coerce").mean()
    return float(result) if pd.notna(result) else None


def fmt_number(value):
    return f"{value:,.0f}" if value is not None and pd.notna(value) else "—"


def fmt_decimal(value, digits=2):
    return f"{value:.{digits}f}" if value is not None and pd.notna(value) else "—"


def apply_chart_theme(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#E8E8E8", size=12),
        title_font=dict(family="Space Grotesk, sans-serif", size=17),
        height=height,
        margin=dict(l=12, r=12, t=55, b=15),
        colorway=PALETTE,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.07)",
            zerolinecolor="rgba(255,255,255,0.12)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.07)",
            zerolinecolor="rgba(255,255,255,0.12)",
        ),
    )
    return fig


def show_download(data, filename, label="Download CSV"):
    st.download_button(
        label,
        data=data.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def section_title(eyebrow, title, description=None):
    st.markdown(f'<div class="mp-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.header(title)
    if description:
        st.caption(description)


# -------------------- LOAD DATA --------------------------------

st.sidebar.markdown("""
<div class="mp-brand">
  <div class="mp-logo">♫</div>
  <div>
    <div class="mp-name">MoodPulse</div>
    <div class="mp-sub">MUSIC INTELLIGENCE</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.caption("YOUR WORKSPACE")

if not DATA_PATH.is_file():
    st.error(f"Dataset not found at `{DATA_PATH}`")
    st.info("Expected location: `MoodPulse/data/Spotify.csv`")
    st.stop()

df = load_dataset(str(DATA_PATH), DATA_PATH.stat().st_mtime)

genre_col = get_column(df, ["track_genre", "genre", "Genre"])
artist_col = get_column(df, ["artists", "artist", "Artist"])
track_col = get_column(df, ["track_name", "track", "Track"])
mood_col = get_column(df, ["mood_category", "mood", "Mood"])

st.sidebar.markdown("### Discover")
page = st.sidebar.radio(
    "Navigation",
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

st.sidebar.markdown("---")
st.sidebar.caption("FILTER YOUR DATA")

filtered = df.copy()

if genre_col:
    genres = sorted(df[genre_col].dropna().astype(str).unique())
    selected_genres = st.sidebar.multiselect(
        "Genres",
        options=genres,
        default=[],
    )
    if selected_genres:
        filtered = filtered[
            filtered[genre_col].astype(str).isin(selected_genres)
        ]

if "popularity" in df.columns:
    valid_pop = df["popularity"].dropna()
    if not valid_pop.empty and valid_pop.min() < valid_pop.max():
        min_pop = int(valid_pop.min())
        max_pop = int(valid_pop.max())
        pop_range = st.sidebar.slider(
            "Popularity",
            min_value=min_pop,
            max_value=max_pop,
            value=(min_pop, max_pop),
        )
        filtered = filtered[
            filtered["popularity"].between(pop_range[0], pop_range[1])
        ]

if "explicit" in df.columns:
    explicit_option = st.sidebar.selectbox(
        "Explicit content",
        ["All tracks", "Explicit only", "Non-explicit only"],
    )
    flag = filtered["explicit"].astype(str).str.strip().str.lower()
    if explicit_option == "Explicit only":
        filtered = filtered[flag.isin(["true", "1", "yes"])]
    elif explicit_option == "Non-explicit only":
        filtered = filtered[flag.isin(["false", "0", "no"])]

st.sidebar.markdown("---")
st.sidebar.caption("POWERED BY PYSPARK · STREAMLIT · PLOTLY")
st.sidebar.caption(f"{len(filtered):,} tracks in current view")


# -------------------- HEADER -----------------------------------

st.markdown(
    '<div class="mp-eyebrow">MUSIC DATA INTELLIGENCE · 2026</div>',
    unsafe_allow_html=True,
)

# ============================================================
# PAGE 1: HOME
# ============================================================

if page == "Home":
    st.markdown("""
    <div class="mp-hero">
      <div class="mp-eyebrow">YOUR SOUND, DECODED</div>
      <h2>Understand the music.<br>Discover the patterns.</h2>
      <p>
        MoodPulse transforms music metadata and audio characteristics
        into insights using big-data processing, exploratory analytics
        and unsupervised machine learning.
      </p>
    </div>
    """, unsafe_allow_html=True)

    total_tracks = len(filtered)
    artists = filtered[artist_col].nunique() if artist_col else None
    genres_count = filtered[genre_col].nunique() if genre_col else None
    popularity = safe_mean(filtered, "popularity")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("TRACKS IN VIEW", fmt_number(total_tracks))
    with k2:
        st.metric("UNIQUE ARTISTS", fmt_number(artists))
    with k3:
        st.metric("GENRES", fmt_number(genres_count))
    with k4:
        st.metric("AVG. POPULARITY", fmt_decimal(popularity, 1))

    st.markdown("")
    section_title(
        "THE BIG PICTURE",
        "Your music landscape",
        "Explore popularity, audio characteristics and genre distribution.",
    )

    left, right = st.columns([1.15, 0.85])

    with left:
        if genre_col:
            top_genres = (
                filtered[genre_col]
                .dropna()
                .astype(str)
                .value_counts()
                .head(12)
                .rename_axis("Genre")
                .reset_index(name="Tracks")
                .sort_values("Tracks")
            )
            fig = px.bar(
                top_genres,
                x="Tracks",
                y="Genre",
                orientation="h",
                title="Most represented genres",
                color="Tracks",
                color_continuous_scale=["#155D2D", GREEN],
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                apply_chart_theme(fig, 410),
                use_container_width=True,
            )
        else:
            st.info("Genre column not found.")

    with right:
        if "popularity" in filtered.columns:
            fig = px.histogram(
                filtered.dropna(subset=["popularity"]),
                x="popularity",
                nbins=25,
                title="Popularity distribution",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(
                apply_chart_theme(fig, 410),
                use_container_width=True,
            )
        else:
            st.info("Popularity column not found.")

    feature_cols = [
        c for c in [
            "danceability", "energy", "valence",
            "acousticness", "speechiness", "instrumentalness",
        ]
        if c in filtered.columns
    ]

    if feature_cols:
        st.markdown("#### Audio DNA")
        means = (
            filtered[feature_cols]
            .mean()
            .rename_axis("Feature")
            .reset_index(name="Average")
        )
        means["Feature"] = means["Feature"].str.replace("_", " ").str.title()
        fig = px.bar(
            means,
            x="Feature",
            y="Average",
            color="Average",
            color_continuous_scale=["#174A2A", GREEN],
            title="Average audio feature profile",
        )
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(
            apply_chart_theme(fig, 320),
            use_container_width=True,
        )

    with st.expander("Preview tracks"):
        st.dataframe(filtered.head(100), use_container_width=True)
        show_download(filtered, "moodpulse_filtered_tracks.csv")


# ============================================================
# PAGE 2: GENRE EXPLORER
# ============================================================

elif page == "Genre Explorer":
    section_title(
        "GENRE INTELLIGENCE",
        "Explore the soundscape",
        "Compare genre representation and average popularity.",
    )

    if not genre_col:
        st.warning("No genre column was found in the dataset.")
    else:
        genre_stats = (
            filtered.dropna(subset=[genre_col])
            .groupby(genre_col)
            .size()
            .rename("track_count")
            .reset_index()
        )

        if "popularity" in filtered.columns:
            pop_stats = (
                filtered.groupby(genre_col)["popularity"]
                .mean()
                .rename("avg_popularity")
                .reset_index()
            )
            genre_stats = genre_stats.merge(pop_stats, on=genre_col, how="left")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("GENRES IN VIEW", f"{len(genre_stats):,}")
        with c2:
            st.metric(
                "TRACKS IN VIEW",
                f"{len(filtered):,}",
            )

        left, right = st.columns(2)

        with left:
            top = genre_stats.nlargest(20, "track_count").sort_values("track_count")
            fig = px.bar(
                top,
                x="track_count",
                y=genre_col,
                orientation="h",
                title="Top genres by track count",
                color_discrete_sequence=[GREEN],
            )
            st.plotly_chart(
                apply_chart_theme(fig, 500),
                use_container_width=True,
            )

        with right:
            if "avg_popularity" in genre_stats.columns:
                popular = genre_stats.dropna(
                    subset=["avg_popularity"]
                ).nlargest(20, "avg_popularity").sort_values("avg_popularity")
                fig = px.bar(
                    popular,
                    x="avg_popularity",
                    y=genre_col,
                    orientation="h",
                    title="Highest average popularity",
                    color_discrete_sequence=["#A7F3D0"],
                )
                st.plotly_chart(
                    apply_chart_theme(fig, 500),
                    use_container_width=True,
                )
            else:
                st.info("Popularity data is unavailable.")

        st.subheader("Genre statistics")
        st.dataframe(
            genre_stats.sort_values("track_count", ascending=False),
            use_container_width=True,
        )
        show_download(genre_stats, "moodpulse_genre_analytics.csv")


# ============================================================
# PAGE 3: MOOD LAB
# ============================================================

elif page == "Mood Lab":
    section_title(
        "AUDIO & MOOD",
        "Inside the feeling",
        "Explore mood labels and relationships between audio features.",
    )

    if mood_col:
        mood_stats = (
            filtered[mood_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Mood")
            .reset_index(name="Tracks")
        )

        left, right = st.columns(2)

        with left:
            fig = px.pie(
                mood_stats,
                names="Mood",
                values="Tracks",
                hole=0.62,
                title="Mood distribution",
                color_discrete_sequence=PALETTE,
            )
            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
            )
            st.plotly_chart(
                apply_chart_theme(fig, 390),
                use_container_width=True,
            )

        with right:
            fig = px.bar(
                mood_stats.sort_values("Tracks"),
                x="Tracks",
                y="Mood",
                orientation="h",
                title="Track count by mood",
                color="Tracks",
                color_continuous_scale=["#174A2A", GREEN],
            )
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                apply_chart_theme(fig, 390),
                use_container_width=True,
            )

        st.caption(
            "Mood labels are rule-based categories generated by the "
            "pipeline, not verified human emotion annotations."
        )
    else:
        mood_report = get_report("mood_analytics.csv")
        if mood_report.empty:
            mood_report = get_report("mood_distribution.csv")

        if not mood_report.empty:
            st.info(
                "No mood column was found in the raw CSV. "
                "Showing the saved Spark mood report instead."
            )
            st.dataframe(mood_report, use_container_width=True)
        else:
            st.info(
                "Mood labels and saved mood reports were not found."
            )

    numeric_audio = [
        c for c in [
            "danceability", "energy", "valence", "acousticness",
            "speechiness", "instrumentalness", "liveness",
            "loudness", "tempo",
        ]
        if c in filtered.columns
    ]

    if len(numeric_audio) >= 2:
        st.subheader("Audio feature explorer")
        c1, c2 = st.columns(2)
        with c1:
            x_feature = st.selectbox(
                "Horizontal axis",
                numeric_audio,
                index=0,
            )
        with c2:
            y_feature = st.selectbox(
                "Vertical axis",
                numeric_audio,
                index=min(1, len(numeric_audio) - 1),
            )

        plot_df = filtered.dropna(
            subset=[x_feature, y_feature]
        )
        if len(plot_df) > 4000:
            plot_df = plot_df.sample(4000, random_state=42)

        fig = px.scatter(
            plot_df,
            x=x_feature,
            y=y_feature,
            color=mood_col if mood_col else None,
            opacity=0.65,
            title=f"{x_feature.title()} vs {y_feature.title()}",
            color_discrete_sequence=PALETTE,
            hover_data=[c for c in [track_col, artist_col] if c],
        )
        st.plotly_chart(
            apply_chart_theme(fig, 450),
            use_container_width=True,
        )

        st.subheader("Feature correlation matrix")
        corr = filtered[numeric_audio].corr(numeric_only=True)
        fig = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale=["#163B25", "#1ED760", "#E8F5E9"],
            zmin=-1,
            zmax=1,
            title="Pearson correlation between audio features",
        )
        st.plotly_chart(
            apply_chart_theme(fig, 500),
            use_container_width=True,
        )


# ============================================================
# PAGE 4: CLUSTER STUDIO
# ============================================================

elif page == "Cluster Studio":
    section_title(
        "UNSUPERVISED LEARNING",
        "Cluster Studio",
        "Compare K-Means configurations and inspect audio-feature profiles.",
    )

    evaluation = get_report("clustering_k_evaluation.csv")
    profiles = get_report("existing_k4_cluster_profiles.csv")

    if not evaluation.empty:
        if {"k", "silhouette_score"}.issubset(evaluation.columns):
            evaluation["k"] = pd.to_numeric(
                evaluation["k"], errors="coerce"
            )
            evaluation["silhouette_score"] = pd.to_numeric(
                evaluation["silhouette_score"], errors="coerce"
            )
            valid_eval = evaluation.dropna(
                subset=["k", "silhouette_score"]
            )

            if not valid_eval.empty:
                best_row = valid_eval.loc[
                    valid_eval["silhouette_score"].idxmax()
                ]

                c1, c2, c3 = st.columns(3)
                c1.metric("K VALUES TESTED", f"{len(valid_eval)}")
                c2.metric("BEST K IN TEST", f"{int(best_row['k'])}")
                c3.metric(
                    "BEST SILHOUETTE",
                    f"{best_row['silhouette_score']:.4f}",
                )

                fig = px.bar(
                    valid_eval.sort_values("k"),
                    x="k",
                    y="silhouette_score",
                    text="silhouette_score",
                    title="Silhouette score by K",
                    color="silhouette_score",
                    color_continuous_scale=["#174A2A", GREEN],
                )
                fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
                fig.update_layout(coloraxis_showscale=False)
                st.plotly_chart(
                    apply_chart_theme(fig, 390),
                    use_container_width=True,
                )

                st.caption(
                    "A higher silhouette score indicates better cluster "
                    "separation under this metric. Interpretability and "
                    "cluster balance also matter."
                )

        st.subheader("Model evaluation table")
        st.dataframe(evaluation, use_container_width=True)
        show_download(evaluation, "moodpulse_kmeans_evaluation.csv")
    else:
        st.warning(
            "Evaluation report not found. Run "
            "src/moodpulse_clustering_eval.py first."
        )

    st.divider()
    st.subheader("Existing K=4 cluster profiles")

    if not profiles.empty:
        if "cluster" in profiles.columns:
            profiles["cluster"] = profiles["cluster"].astype(str)

        st.dataframe(profiles, use_container_width=True)

        feature_cols = [
            c for c in profiles.columns if c.startswith("avg_")
        ]

        if feature_cols:
            selected = st.multiselect(
                "Choose features to compare",
                feature_cols,
                default=feature_cols[:4],
            )

            if selected:
                plot_data = profiles[
                    ["cluster"] + selected
                ].melt(
                    id_vars="cluster",
                    var_name="Audio feature",
                    value_name="Average",
                )
                plot_data["Audio feature"] = (
                    plot_data["Audio feature"]
                    .str.replace("avg_", "", regex=False)
                    .str.replace("_", " ")
                    .str.title()
                )

                fig = px.bar(
                    plot_data,
                    x="Audio feature",
                    y="Average",
                    color="cluster",
                    barmode="group",
                    title="Audio profile by cluster",
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(
                    apply_chart_theme(fig, 420),
                    use_container_width=True,
                )

        show_download(profiles, "moodpulse_k4_cluster_profiles.csv")
    else:
        st.info(
            "Cluster profiles not found. Run "
            "src/moodpulse_cluster_profiles_v2.py first."
        )


# ============================================================
# PAGE 5: DATA QUALITY
# ============================================================

elif page == "Data Quality":
    section_title(
        "DATA GOVERNANCE",
        "Data quality monitor",
        "Inspect missing values, duplicates and available processing reports.",
    )

    missing = filtered.isna().sum().rename("Missing values").reset_index()
    missing.columns = ["Column", "Missing values"]
    missing["Missing %"] = (
        missing["Missing values"] / max(len(filtered), 1) * 100
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ROWS IN VIEW", f"{len(filtered):,}")
    c2.metric("COLUMNS", f"{len(filtered.columns):,}")
    c3.metric("EXACT DUPLICATES IN VIEW", f"{int(filtered.duplicated().sum()):,}")
    c4.metric("CELLS MISSING", f"{int(missing['Missing values'].sum()):,}")

    left, right = st.columns(2)

    with left:
        top_missing = missing.nlargest(20, "Missing values").sort_values(
            "Missing values"
        )
        fig = px.bar(
            top_missing,
            x="Missing values",
            y="Column",
            orientation="h",
            title="Missing values by column",
            color_discrete_sequence=[GREEN],
        )
        st.plotly_chart(
            apply_chart_theme(fig, 460),
            use_container_width=True,
        )

    with right:
        fig = px.histogram(
            missing,
            x="Missing %",
            nbins=20,
            title="Distribution of missing-data percentages",
            color_discrete_sequence=["#A7F3D0"],
        )
        st.plotly_chart(
            apply_chart_theme(fig, 460),
            use_container_width=True,
        )

    st.subheader("Column-level quality report")
    st.dataframe(
        missing.sort_values("Missing values", ascending=False),
        use_container_width=True,
    )
    show_download(missing, "moodpulse_data_quality.csv")

    st.subheader("Available Spark reports")
    report_names = [
        "data_quality.csv",
        "genre_analytics.csv",
        "genre_volume.csv",
        "artist_analytics.csv",
        "mood_analytics.csv",
        "bpm_distribution.csv",
        "explicit_analytics.csv",
        "numeric_summary.csv",
        "correlation_analysis.csv",
        "clustering_k_evaluation.csv",
        "existing_k4_cluster_profiles.csv",
    ]

    report_status = []
    for name in report_names:
        path = report_path(name)
        report_status.append({
            "Report": name,
            "Status": "Available" if path else "Not found",
            "Path": str(path) if path else "—",
        })

    st.dataframe(
        pd.DataFrame(report_status),
        use_container_width=True,
    )

    spark_quality = get_report("data_quality.csv")
    if not spark_quality.empty:
        st.subheader("Spark ETL quality report")
        st.dataframe(spark_quality, use_container_width=True)


# ============================================================
# PAGE 6: PROJECT METHODOLOGY
# ============================================================

elif page == "Project Methodology":
    section_title(
        "BEHIND THE PROJECT",
        "How MoodPulse works",
        "A clear view of the pipeline, analysis and machine-learning workflow.",
    )

    st.markdown("""
    <div class="mp-hero">
      <div class="mp-eyebrow">PROJECT OVERVIEW</div>
      <h2>From raw tracks to music insights.</h2>
      <p>
        MoodPulse uses a Spark-based processing workflow to clean music
        metadata, engineer audio features, analyze trends and investigate
        unsupervised clusters across the Spotify tracks dataset.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Pipeline architecture")

    steps = [
        ("01", "Data ingestion", "Read the Spotify CSV dataset."),
        ("02", "Data cleaning", "Cast types, handle missing values and filter invalid records."),
        ("03", "Feature engineering", "Create derived metrics and rule-based mood categories."),
        ("04", "Distributed analytics", "Aggregate trends by genre, artist, mood and audio features."),
        ("05", "Machine learning", "Evaluate K-Means configurations using a silhouette metric."),
        ("06", "Visualization", "Explore results in the Streamlit dashboard."),
    ]

    for number, title, description in steps:
        st.markdown(
            f"""
            <div class="mp-card" style="margin-bottom:10px; min-height:0;">
              <div style="display:flex; gap:16px; align-items:flex-start;">
                <div style="color:#1ED760;font-size:24px;font-weight:700;
                            font-family:'Space Grotesk',sans-serif;">{number}</div>
                <div>
                  <div style="font-size:17px;font-weight:700;color:#FFFFFF;">
                    {title}
                  </div>
                  <div style="color:#B3B3B3;margin-top:5px;">
                    {description}
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Technology stack")
    tech1, tech2, tech3 = st.columns(3)
    tech1.markdown("**PROCESSING**")
    tech1.write("Apache Spark · PySpark")
    tech2.markdown("**MACHINE LEARNING**")
    tech2.write("Spark MLlib · K-Means")
    tech3.markdown("**PRESENTATION**")
    tech3.write("Streamlit · Plotly · Pandas")

    st.info(
        "The current workflow runs Spark locally and uses saved reports. "
        "HDFS and Hive should only be listed as implemented components if "
        "you separately deploy and test them."
    )

    st.subheader("Current dataset")
    st.write(f"**Source file:** `{DATA_PATH}`")
    st.write(f"**Tracks loaded:** {len(df):,}")
    st.write(f"**Columns:** {len(df.columns):,}")
    st.write(
        "**Distinct genres:** "
        + (
            f"{df[genre_col].nunique():,}"
            if genre_col else "Genre field not found"
        )
    )

    st.subheader("Research and interpretation notes")
    st.markdown("""
    - Silhouette score helps compare cluster separation; it does not
      prove that a cluster represents a particular emotion.
    - Rule-based mood categories are analytical labels, not human
      emotion ground truth.
    - Dataset size and performance claims should be based on measured
      local runs, not assumed large-scale infrastructure.
    """)


# -------------------- FOOTER -----------------------------------

st.divider()
st.markdown(
    """
    <div style="display:flex;justify-content:space-between;gap:12px;
                flex-wrap:wrap;color:#777777;font-size:12px;">
      <span>♫ MOODPULSE STUDIO</span>
      <span>Music data · Machine learning · Analytics</span>
    </div>
    """,
    unsafe_allow_html=True,
)
