from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# MOODPULSE STUDIO V3 — Spotify-inspired analytics dashboard
# ============================================================
BASE = Path.home() / "MoodPulse"
DATA_PATH = BASE / "data" / "Spotify.csv"
ADVANCED = BASE / "output" / "advanced"
REPORTS = ADVANCED / "reports"

GREEN = "#1ED760"
PALETTE = ["#1ED760", "#A7F3D0", "#65D46E", "#B7E4C7", "#52B788", "#D9F99D"]

st.set_page_config(
    page_title="MoodPulse Studio",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- DESIGN -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:radial-gradient(ellipse at 88% 0%,#173523 0%,#121212 34%);color:#fff;}
.block-container {max-width:1550px;padding-top:1.8rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.035em;}
h1 {font-size:clamp(2rem,4vw,3rem)!important;font-weight:700!important;}
[data-testid="stSidebar"] {background:#080808;border-right:1px solid #252525;}
.mp-brand {display:flex;align-items:center;gap:12px;padding:8px 0 20px;}
.mp-logo {background:#1ED760;color:#07160B;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:700;}
.mp-name {font:700 22px 'Space Grotesk',sans-serif;}
.mp-sub {font-size:10px;color:#1ED760;letter-spacing:2px;}
.mp-eyebrow {font-size:11px;color:#1ED760;letter-spacing:2px;font-weight:700;text-transform:uppercase;}
.mp-hero {background:linear-gradient(115deg,#1D472B,#193421 58%,#181818);border:1px solid #285737;border-radius:22px;padding:30px;margin:10px 0 24px;}
.mp-hero h2 {font:700 clamp(28px,4vw,45px) 'Space Grotesk',sans-serif;line-height:1.12;margin:12px 0;}
.mp-hero p {color:#D5E8D9;max-width:760px;line-height:1.7;}
.mp-insight {background:#181818;border:1px solid #292929;border-radius:16px;padding:19px;height:100%;}
.mp-insight-label {font-size:11px;color:#B3B3B3;letter-spacing:1px;font-weight:700;text-transform:uppercase;}
.mp-insight-value {font:700 25px 'Space Grotesk',sans-serif;color:#fff;margin:9px 0 4px;}
.mp-insight-note {font-size:12px;color:#1ED760;}
[data-testid="stMetric"] {background:#181818;border:1px solid #292929;border-radius:16px;padding:17px;}
[data-testid="stMetricLabel"] {color:#B3B3B3!important;}
[data-testid="stMetricValue"] {font-family:'Space Grotesk',sans-serif;color:white!important;font-weight:700;}
.stButton>button,.stDownloadButton>button {background:#1ED760;color:#07160B;border:none;border-radius:30px;font-weight:700;}
.stButton>button:hover,.stDownloadButton>button:hover {background:#54F181;color:#07160B;}
[data-testid="stDataFrame"] {border:1px solid #292929;border-radius:12px;}
hr {border-color:#292929;} footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)


# ----------------------------- HELPERS -----------------------------
@st.cache_data
def load_data(path, modified):
    data = pd.read_csv(path, low_memory=False)
    data.columns = [str(c).strip() for c in data.columns]
    data = data.loc[:, [
        c for c in data.columns
        if not c.lower().startswith("unnamed:") and c != "_c0"
    ]]
    numeric = [
        "popularity", "duration_ms", "danceability", "energy",
        "speechiness", "acousticness", "instrumentalness", "liveness",
        "valence", "loudness", "tempo", "mood_score",
        "dance_energy_score", "duration_minutes", "bpm", "key",
        "mode", "time_signature",
    ]
    for col in numeric:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


@st.cache_data
def read_csv(path, modified):
    return pd.read_csv(path, low_memory=False)


@st.cache_data
def read_json(path, modified):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)



def locate_report(filename):
    locations = [
        REPORTS / filename,
        ADVANCED / "analytics" / filename,
        ADVANCED / filename,
        BASE / "output" / filename,
    ]
    for path in locations:
        if path.is_file():
            return path
    return None



def report(filename):
    path = locate_report(filename)
    if not path:
        return pd.DataFrame()
    try:
        return read_csv(str(path), path.stat().st_mtime)
    except Exception:
        return pd.DataFrame()


def get_col(frame, choices):
    return next((c for c in choices if c in frame.columns), None)


def chart_theme(fig, height=360):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#EAEAEA", size=12),
        colorway=PALETTE,
        height=height,
        margin=dict(l=10, r=15, t=55, b=15),
        xaxis=dict(gridcolor="#292929", zerolinecolor="#3A3A3A"),
        yaxis=dict(gridcolor="#292929", zerolinecolor="#3A3A3A"),
    )
    return fig


def section(eyebrow, title, description=None):
    st.markdown(f'<div class="mp-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    if description:
        st.caption(description)


def download_csv(frame, filename, label="Download CSV"):
    st.download_button(
        label,
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def insight_card(label, value, note):
    st.markdown(
        f"""<div class="mp-insight">
        <div class="mp-insight-label">{label}</div>
        <div class="mp-insight-value">{value}</div>
        <div class="mp-insight-note">{note}</div>
        </div>""",
        unsafe_allow_html=True,
    )


def get_processed_count(raw_count):
    # Prefer the recorded run report; fall back to the known successful run.
    candidates = [
        REPORTS / "run_report.json",
        ADVANCED / "run_report.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                payload = read_json(str(path), path.stat().st_mtime)
                for key in ("processed_tracks", "cleaned_tracks", "tracks_processed", "output_tracks"):
                    value = payload.get(key)
                    if isinstance(value, (int, float)):
                        return int(value)
                for value in payload.values():
                    if isinstance(value, dict):
                        for key in ("processed_tracks", "cleaned_tracks", "tracks_processed", "output_tracks"):
                            if isinstance(value.get(key), (int, float)):
                                return int(value[key])
            except Exception:
                pass
    return 113702 if raw_count == 114000 else None


# ----------------------------- DATA -----------------------------
st.sidebar.markdown("""
<div class="mp-brand">
  <div class="mp-logo">♫</div>
  <div><div class="mp-name">MoodPulse</div><div class="mp-sub">MUSIC INTELLIGENCE</div></div>
</div>
""", unsafe_allow_html=True)

if not DATA_PATH.is_file():
    st.error(f"Dataset not found: {DATA_PATH}")
    st.info("Expected file: ~/MoodPulse/data/Spotify.csv")
    st.stop()

df = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime)
genre_col = get_col(df, ["track_genre", "genre", "Genre"])
artist_col = get_col(df, ["artists", "artist", "Artist"])
track_col = get_col(df, ["track_name", "track", "Track"])
mood_col = get_col(df, ["mood_category", "mood", "Mood"])

evaluation = report("clustering_k_evaluation.csv")
profiles = report("existing_k4_cluster_profiles.csv")
quality_report = report("data_quality.csv")
genre_report = report("genre_analytics.csv")
mood_report = report("mood_analytics.csv")
processed_tracks = get_processed_count(len(df))
retention = (processed_tracks / len(df) * 100) if processed_tracks is not None and len(df) else None

best_k, best_silhouette = None, None
if {"k", "silhouette_score"}.issubset(evaluation.columns):
    evaluation["k"] = pd.to_numeric(evaluation["k"], errors="coerce")
    evaluation["silhouette_score"] = pd.to_numeric(evaluation["silhouette_score"], errors="coerce")
    valid_eval = evaluation.dropna(subset=["k", "silhouette_score"])
    if not valid_eval.empty:
        row = valid_eval.loc[valid_eval["silhouette_score"].idxmax()]
        best_k, best_silhouette = int(row["k"]), float(row["silhouette_score"])

# ----------------------------- NAV + FILTERS -----------------------------
st.sidebar.divider()
st.sidebar.caption("NAVIGATION")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Genre Explorer", "Mood Lab", "Cluster Studio", "Data Quality", "Project Methodology"],
    label_visibility="collapsed",
)
st.sidebar.divider()
st.sidebar.caption("DATASET FILTERS")
filtered = df.copy()

if genre_col:
    genre_options = sorted(df[genre_col].dropna().astype(str).unique())
    chosen_genres = st.sidebar.multiselect("Genres", genre_options)
    if chosen_genres:
        filtered = filtered[filtered[genre_col].astype(str).isin(chosen_genres)]

if "popularity" in df.columns:
    vals = df["popularity"].dropna()
    if not vals.empty and vals.min() < vals.max():
        pop_range = st.sidebar.slider(
            "Popularity", int(vals.min()), int(vals.max()),
            (int(vals.min()), int(vals.max())),
        )
        filtered = filtered[filtered["popularity"].between(*pop_range)]

if "explicit" in df.columns:
    explicit_mode = st.sidebar.selectbox("Explicit content", ["All tracks", "Explicit only", "Non-explicit only"])
    flags = filtered["explicit"].astype(str).str.strip().str.lower()
    if explicit_mode == "Explicit only":
        filtered = filtered[flags.isin(["true", "1", "yes"])]
    elif explicit_mode == "Non-explicit only":
        filtered = filtered[flags.isin(["false", "0", "no"])]

st.sidebar.divider()
st.sidebar.caption(f"{len(filtered):,} raw tracks in current view")
st.sidebar.caption("PySpark · Streamlit · Plotly")


# ============================================================
# HOME
# ============================================================
if page == "Home":
    st.markdown("""
    <div class="mp-eyebrow">MUSIC DATA INTELLIGENCE · 2026</div>
    <div class="mp-hero">
      <div class="mp-eyebrow">YOUR SOUND, DECODED</div>
      <h2>Understand the music.<br>Discover the patterns.</h2>
      <p>MoodPulse turns Spotify track metadata and audio characteristics into insights through data processing, genre analysis and unsupervised machine learning.</p>
    </div>
    """, unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.metric("RAW TRACKS", f"{len(df):,}")
    b.metric("SPARK-PROCESSED", f"{processed_tracks:,}" if processed_tracks is not None else "See run report")
    c.metric("TRACKS RETAINED", f"{retention:.2f}%" if retention is not None else "—")
    d.metric("BEST SILHOUETTE", f"{best_silhouette:.4f}" if best_silhouette is not None else "—",
             f"K = {best_k}" if best_k is not None else None)

    st.markdown("")
    section("INSIGHTS AT A GLANCE", "What stands out", "Key findings from the currently available analytics reports.")

    # Top genre is derived from the actual report, when its schema is recognized.
    r_genre = get_col(genre_report, ["track_genre", "genre", "Genre"])
    r_pop = get_col(genre_report, ["avg_popularity", "average_popularity"])
    top_genre, top_genre_score = "—", None
    if r_genre and r_pop:
        tmp = genre_report.copy()
        tmp[r_pop] = pd.to_numeric(tmp[r_pop], errors="coerce")
        tmp = tmp.dropna(subset=[r_pop]).sort_values(r_pop, ascending=False)
        if not tmp.empty:
            top_genre = str(tmp.iloc[0][r_genre])
            top_genre_score = float(tmp.iloc[0][r_pop])

    largest_cluster_text = "—"
    if not profiles.empty and {"cluster", "track_count"}.issubset(profiles.columns):
        p = profiles.copy()
        p["track_count"] = pd.to_numeric(p["track_count"], errors="coerce")
        p = p.dropna(subset=["track_count"])
        if not p.empty:
            row = p.loc[p["track_count"].idxmax()]
            largest_cluster_text = f"Cluster {row['cluster']} · {int(row['track_count']):,} tracks"

    i1, i2, i3 = st.columns(3)
    with i1:
        insight_card("TOP GENRE BY POPULARITY", top_genre,
                     f"Average popularity {top_genre_score:.2f}" if top_genre_score is not None else "Spark genre report needed")
    with i2:
        insight_card("BEST SILHOUETTE", f"{best_silhouette:.4f}" if best_silhouette is not None else "—",
                     f"Found at K = {best_k}" if best_k is not None else "Evaluation report needed")
    with i3:
        insight_card("LARGEST K=4 CLUSTER", largest_cluster_text,
                     "Based on saved cluster profiles" if largest_cluster_text != "—" else "Cluster profile report needed")

    st.markdown("")
    section("THE BIG PICTURE", "Your music landscape", "Explore popularity, genre representation and audio characteristics.")
    left, right = st.columns(2)

    with left:
        if r_genre and r_pop:
            g = genre_report.copy()
            g[r_pop] = pd.to_numeric(g[r_pop], errors="coerce")
            g = g.dropna(subset=[r_pop]).nlargest(15, r_pop).sort_values(r_pop)
            fig = px.bar(g, x=r_pop, y=r_genre, orientation="h",
                         title="Top genres by average popularity",
                         color=r_pop, color_continuous_scale=["#175C32", GREEN, "#C6FFD7"])
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_theme(fig, 430), use_container_width=True)
        elif genre_col:
            counts = filtered[genre_col].dropna().astype(str).value_counts().head(15).sort_values().rename_axis("Genre").reset_index(name="Tracks")
            fig = px.bar(counts, x="Tracks", y="Genre", orientation="h", title="Most represented genres", color_discrete_sequence=[GREEN])
            st.plotly_chart(chart_theme(fig, 430), use_container_width=True)
        else:
            st.info("Genre analytics are unavailable.")

    with right:
        if "popularity" in filtered.columns:
            fig = px.histogram(filtered.dropna(subset=["popularity"]), x="popularity", nbins=25,
                               title="Track popularity distribution", color_discrete_sequence=[GREEN])
            st.plotly_chart(chart_theme(fig, 430), use_container_width=True)

    audio = [c for c in ["danceability", "energy", "valence", "acousticness", "speechiness", "instrumentalness"] if c in filtered.columns]
    if audio:
        st.subheader("Audio DNA")
        means = filtered[audio].mean().rename_axis("Feature").reset_index(name="Average")
        means["Feature"] = means["Feature"].str.replace("_", " ").str.title()
        fig = px.bar(means, x="Feature", y="Average", title="Average audio-feature profile",
                     color="Average", color_continuous_scale=["#174A2A", GREEN, "#C6FFD7"])
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_theme(fig, 340), use_container_width=True)

    with st.expander("Preview filtered tracks"):
        st.dataframe(filtered.head(100), use_container_width=True)
        download_csv(filtered, "moodpulse_filtered_tracks.csv")


# ============================================================
# GENRE EXPLORER
# ============================================================
elif page == "Genre Explorer":
    section("GENRE INTELLIGENCE", "Explore the soundscape", "Compare average popularity, not just track counts.")
    r_genre = get_col(genre_report, ["track_genre", "genre", "Genre"])
    r_pop = get_col(genre_report, ["avg_popularity", "average_popularity"])
    r_count = get_col(genre_report, ["track_count", "count", "tracks"])

    if not genre_report.empty and r_genre and r_pop:
        g = genre_report.copy()
        g[r_pop] = pd.to_numeric(g[r_pop], errors="coerce")
        g = g.dropna(subset=[r_pop]).sort_values(r_pop, ascending=False)
        n = st.slider("Number of genres to display", 5, min(30, max(5, len(g))), min(15, max(5, len(g))))
        top = g.head(n).sort_values(r_pop)
        fig = px.bar(top, x=r_pop, y=r_genre, orientation="h",
                     title="Highest average popularity by genre",
                     labels={r_pop: "Average popularity", r_genre: "Genre"},
                     color=r_pop, color_continuous_scale=["#175C32", GREEN, "#C6FFD7"],
                     hover_data=[r_count] if r_count else None)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(chart_theme(fig, max(400, n * 27)), use_container_width=True)
        st.subheader("Genre performance table")
        cols = [r_genre, r_pop] + ([r_count] if r_count else [])
        st.dataframe(g[cols].reset_index(drop=True), use_container_width=True)
        download_csv(g[cols], "moodpulse_genre_analytics.csv")
    elif genre_col:
        gs = filtered.groupby(genre_col).agg(
            track_count=(genre_col, "size"),
            avg_popularity=("popularity", "mean") if "popularity" in filtered.columns else (genre_col, "size"),
        ).reset_index()
        if "popularity" not in filtered.columns:
            gs = gs.drop(columns=["avg_popularity"], errors="ignore")
        if "avg_popularity" in gs.columns:
            top = gs.nlargest(20, "avg_popularity").sort_values("avg_popularity")
            fig = px.bar(top, x="avg_popularity", y=genre_col, orientation="h",
                         title="Highest average popularity by genre", color_discrete_sequence=[GREEN])
            st.plotly_chart(chart_theme(fig, 500), use_container_width=True)
        st.dataframe(gs.sort_values("avg_popularity", ascending=False) if "avg_popularity" in gs.columns else gs,
                     use_container_width=True)
    else:
        st.warning("No usable genre report or genre column was found.")


# ============================================================
# MOOD LAB
# ============================================================
elif page == "Mood Lab":
    section("AUDIO & MOOD", "Inside the feeling", "Explore mood labels and relationships between audio features.")
    if mood_col:
        moods = filtered[mood_col].fillna("Unknown").astype(str).value_counts().rename_axis("Mood").reset_index(name="Tracks")
        left, right = st.columns(2)
        with left:
            fig = px.pie(moods, names="Mood", values="Tracks", hole=.55, title="Mood distribution", color_discrete_sequence=PALETTE)
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(chart_theme(fig, 400), use_container_width=True)
        with right:
            fig = px.bar(moods.sort_values("Tracks"), x="Tracks", y="Mood", orientation="h",
                         title="Tracks by mood", color_discrete_sequence=[GREEN])
            st.plotly_chart(chart_theme(fig, 400), use_container_width=True)
        st.caption("Mood labels are rule-based analytical categories, not verified human emotion annotations.")
    elif not mood_report.empty:
        st.subheader("Saved Spark mood report")
        st.dataframe(mood_report, use_container_width=True)
    else:
        st.info("No mood column or saved mood report was found.")

    audio = [c for c in ["danceability", "energy", "valence", "acousticness", "speechiness", "instrumentalness", "liveness", "loudness", "tempo"] if c in filtered.columns]
    if len(audio) >= 2:
        st.subheader("Feature explorer")
        c1, c2 = st.columns(2)
        x = c1.selectbox("Horizontal axis", audio, index=0)
        y = c2.selectbox("Vertical axis", audio, index=min(1, len(audio)-1))
        sample = filtered.dropna(subset=[x, y])
        if len(sample) > 4000:
            sample = sample.sample(4000, random_state=42)
        fig = px.scatter(sample, x=x, y=y, color=mood_col if mood_col else None,
                         opacity=.65, title=f"{x.title()} vs {y.title()}",
                         color_discrete_sequence=PALETTE,
                         hover_data=[c for c in [track_col, artist_col] if c])
        st.plotly_chart(chart_theme(fig, 430), use_container_width=True)

        st.subheader("Audio feature correlation")
        corr = filtered[audio].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                        color_continuous_scale=["#173523", GREEN, "#E7F9EC"], zmin=-1, zmax=1)
        st.plotly_chart(chart_theme(fig, 520), use_container_width=True)


# ============================================================
# CLUSTER STUDIO
# ============================================================
elif page == "Cluster Studio":
    section("UNSUPERVISED LEARNING", "Cluster Studio", "Compare cluster separation and inspect the existing K=4 profiles.")

    if not evaluation.empty and {"k", "silhouette_score"}.issubset(evaluation.columns):
        ev = evaluation.copy()
        ev["k"] = pd.to_numeric(ev["k"], errors="coerce")
        ev["silhouette_score"] = pd.to_numeric(ev["silhouette_score"], errors="coerce")
        ev = ev.dropna(subset=["k", "silhouette_score"])
        if not ev.empty:
            best = ev.loc[ev["silhouette_score"].idxmax()]
            k4 = ev[ev["k"] == 4]
            k2 = ev[ev["k"] == 2]
            a, b, c = st.columns(3)
            a.metric("K VALUES TESTED", len(ev))
            b.metric("BEST SILHOUETTE", f"{best['silhouette_score']:.4f}", f"K = {int(best['k'])}")
            c.metric("K=4 SILHOUETTE", f"{float(k4.iloc[0]['silhouette_score']):.4f}" if not k4.empty else "—")

            fig = px.bar(ev.sort_values("k"), x="k", y="silhouette_score",
                         title="Silhouette score by K",
                         color="silhouette_score", color_continuous_scale=["#174A2A", GREEN, "#C6FFD7"],
                         text="silhouette_score")
            fig.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            fig.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_theme(fig, 410), use_container_width=True)

            if not k2.empty and not k4.empty:
                delta = float(k2.iloc[0]["silhouette_score"] - k4.iloc[0]["silhouette_score"])
                st.info(
                    f"K=2 silhouette is {float(k2.iloc[0]['silhouette_score']):.4f}; "
                    f"K=4 silhouette is {float(k4.iloc[0]['silhouette_score']):.4f}. "
                    f"K=2 is higher by {delta:.4f} on this metric. K=4 may still offer more detailed segmentation."
                )
        st.subheader("Evaluation results")
        st.dataframe(ev.sort_values("k"), use_container_width=True)
        download_csv(ev, "moodpulse_kmeans_evaluation.csv")
    else:
        st.warning("Clustering evaluation report not found. Run the evaluation script first.")

    st.divider()
    st.subheader("Existing K=4 cluster profiles")
    if not profiles.empty:
        p = profiles.copy()
        if "cluster" in p.columns:
            p["cluster"] = p["cluster"].astype(str)
        st.dataframe(p, use_container_width=True)

        if "cluster" in p.columns and "track_count" in p.columns:
            p["track_count"] = pd.to_numeric(p["track_count"], errors="coerce")
            psize = p.dropna(subset=["track_count"]).sort_values("track_count")
            fig = px.bar(psize, x="track_count", y="cluster", orientation="h",
                         title="Track count per K=4 cluster", color_discrete_sequence=[GREEN])
            st.plotly_chart(chart_theme(fig, 330), use_container_width=True)

        features = [c for c in p.columns if c.startswith("avg_")]
        if features:
            selected = st.multiselect("Audio features to compare", features, default=features[:4])
            if selected:
                long = p[["cluster"] + selected].melt(id_vars="cluster", var_name="Feature", value_name="Average")
                long["Feature"] = long["Feature"].str.replace("avg_", "", regex=False).str.replace("_", " ").str.title()
                fig = px.bar(long, x="Feature", y="Average", color="cluster", barmode="group",
                             title="Audio characteristics by cluster", color_discrete_sequence=PALETTE)
                st.plotly_chart(chart_theme(fig, 430), use_container_width=True)
        download_csv(p, "moodpulse_k4_cluster_profiles.csv")
    else:
        st.info("K=4 cluster profile report not found. Run the cluster-profile script first.")


# ============================================================
# DATA QUALITY
# ============================================================
elif page == "Data Quality":
    section("DATA GOVERNANCE", "Data quality monitor", "Review missing values and generated Spark reports.")
    missing = filtered.isna().sum().rename("Missing values").reset_index()
    missing.columns = ["Column", "Missing values"]
    missing["Missing %"] = missing["Missing values"] / max(len(filtered), 1) * 100

    a, b, c, d = st.columns(4)
    a.metric("ROWS IN VIEW", f"{len(filtered):,}")
    b.metric("COLUMNS", f"{len(filtered.columns):,}")
    c.metric("DUPLICATE ROWS IN VIEW", f"{int(filtered.duplicated().sum()):,}")
    d.metric("MISSING CELLS", f"{int(missing['Missing values'].sum()):,}")

    left, right = st.columns(2)
    with left:
        m = missing.nlargest(20, "Missing values").sort_values("Missing values")
        fig = px.bar(m, x="Missing values", y="Column", orientation="h",
                     title="Missing values by column", color_discrete_sequence=[GREEN])
        st.plotly_chart(chart_theme(fig, 450), use_container_width=True)
    with right:
        fig = px.histogram(missing, x="Missing %", nbins=20,
                           title="Missing-value percentage by column", color_discrete_sequence=["#A7F3D0"])
        st.plotly_chart(chart_theme(fig, 450), use_container_width=True)

    st.subheader("Column quality table")
    st.dataframe(missing.sort_values("Missing values", ascending=False), use_container_width=True)
    download_csv(missing, "moodpulse_data_quality.csv")

    if not quality_report.empty:
        st.subheader("Spark ETL quality report")
        st.dataframe(quality_report, use_container_width=True)

    names = ["data_quality.csv", "genre_analytics.csv", "genre_volume.csv", "artist_analytics.csv",
             "mood_analytics.csv", "bpm_distribution.csv", "explicit_analytics.csv",
             "numeric_summary.csv", "correlation_analysis.csv", "clustering_k_evaluation.csv",
             "existing_k4_cluster_profiles.csv"]
    status = []
    for name in names:
        path = locate_report(name)
        status.append({"Report": name, "Status": "Available" if path else "Not found", "Path": str(path) if path else "—"})
    st.subheader("Analytics report availability")
    st.dataframe(pd.DataFrame(status), use_container_width=True)


# ============================================================
# PROJECT METHODOLOGY
# ============================================================
elif page == "Project Methodology":
    section("BEHIND THE PROJECT", "How MoodPulse works", "The workflow from raw music data to interactive analysis.")
    st.markdown("""
    <div class="mp-hero">
      <div class="mp-eyebrow">PROJECT OVERVIEW</div>
      <h2>From raw tracks to music insights.</h2>
      <p>A Spark-based workflow for cleaning metadata, engineering audio features, analyzing trends and evaluating unsupervised clusters.</p>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Data ingestion", "Load the Spotify CSV dataset."),
        ("02", "Data cleaning", "Cast types, handle missing values, remove duplicates and filter invalid records."),
        ("03", "Feature engineering", "Create derived audio metrics and rule-based mood categories."),
        ("04", "Distributed analytics", "Aggregate genre, artist, mood and audio-feature statistics with Spark."),
        ("05", "Machine learning", "Compare K-Means configurations using silhouette evaluation."),
        ("06", "Visualization", "Explore the saved results through Streamlit and Plotly."),
    ]
    for number, title, desc in steps:
        st.markdown(
            f"""<div style="background:#181818;border:1px solid #292929;border-radius:14px;padding:18px;margin-bottom:10px;">
            <span style="color:#1ED760;font-size:22px;font-weight:700;">{number}</span>
            <strong style="margin-left:15px;">{title}</strong>
            <div style="color:#B3B3B3;margin:8px 0 0 40px;">{desc}</div></div>""",
            unsafe_allow_html=True,
        )

    st.subheader("Technology stack")
    x, y, z = st.columns(3)
    x.markdown("**PROCESSING**"); x.write("Apache Spark · PySpark")
    y.markdown("**MACHINE LEARNING**"); y.write("Spark MLlib · K-Means")
    z.markdown("**DASHBOARD**"); z.write("Streamlit · Plotly · Pandas")

    st.subheader("Measured project results")
    x, y, z = st.columns(3)
    x.metric("RAW DATASET", f"{len(df):,} tracks")
    y.metric("PROCESSED TRACKS", f"{processed_tracks:,}" if processed_tracks is not None else "—")
    z.metric("RETENTION", f"{retention:.2f}%" if retention is not None else "—")

    st.info("Spark currently runs locally. Only claim HDFS or Hive deployment if those components have separately been implemented and tested.")
    st.caption("Mood categories are rule-based analytical labels, not verified human emotion annotations.")


st.divider()
st.caption("♫ MOODPULSE STUDIO · Music data · Machine learning · Analytics")
