# 🎵 MoodPulse AI — Big Data Music Analytics

**Analyze music. Discover moods. Understand trends.**

MoodPulse AI is a Big Data Analytics project that analyzes Spotify track data to uncover music trends, explore audio characteristics, study genre and artist statistics, and visualize inferred mood distributions. It combines **Python, Apache Spark (PySpark), HDFS, Pandas, Plotly, and Streamlit** to demonstrate a data-processing and analytics pipeline with an interactive dashboard.

🔗 **Live Dashboard:** https://moodpulse-bda.streamlit.app/  
💻 **GitHub Repository:** https://github.com/iam-deepeshs/MoodPulse

---

## 📌 Project Overview

Music streaming platforms contain large amounts of information about tracks, artists, genres, popularity, and audio characteristics. Analyzing these data can help reveal patterns in listening preferences and music trends.

MoodPulse processes a Spotify dataset containing approximately **114,000 tracks** and generates analytical summaries that can be explored through an interactive dashboard.

### Objectives

- Analyze music trends across genres and artists.
- Explore audio characteristics such as tempo, energy, and danceability.
- Study the distribution of inferred music moods.
- Apply data cleaning, transformation, aggregation, and clustering techniques.
- Demonstrate the use of PySpark for large-scale data analytics.
- Store analytical data using HDFS.
- Present insights through interactive visualizations.

---

## ✨ Key Features

- **Music Mood Analytics:** Explore the distribution of inferred mood categories, including Happy, Sad, Energetic, Neutral, and Party.
- **Genre Analysis:** Compare track counts, popularity, and genre-level statistics.
- **Artist Analytics:** Examine artist-level summaries and music trends.
- **Audio Feature Analysis:** Explore characteristics such as BPM, energy, danceability, and other available numeric features.
- **Clustering:** Apply a K-Means workflow to investigate groups of tracks with similar feature patterns.
- **Data Quality Reports:** Review dataset quality and processing summaries.
- **Interactive Dashboard:** Explore exported analytical results through charts and visualizations.
- **Big Data Processing:** Use PySpark DataFrame operations and Spark ML functionality for data processing and clustering.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Apache Spark | Data processing and analytics |
| PySpark | Python API for Spark |
| Spark ML | Machine learning and clustering workflow |
| HDFS | Distributed file storage |
| Pandas | CSV loading and data manipulation |
| Plotly | Interactive data visualizations |
| Streamlit | Dashboard and web application |
| Git and GitHub | Version control and source-code hosting |
| Streamlit Community Cloud | Dashboard deployment |

---

## 🏗️ System Architecture

```text
Spotify Dataset (CSV)
        |
        v
Data Loading and Preprocessing
        |
        v
Apache Spark / PySpark
        |
        +--------------------------+
        |                          |
        v                          v
Data Analytics               K-Means Clustering
        |                          |
        +-------------+------------+
                      |
                      v
           Analytics and Reports
             (CSV / JSON)
                      |
          +-----------+-----------+
          |                       |
          v                       v
    HDFS Storage          Local Project Outputs
                                  |
                                  v
                         Streamlit Dashboard
                                  |
                                  v
                       Interactive Visualizations
```

HDFS is used in the local data-storage workflow. The deployed Streamlit dashboard currently reads the dataset and exported analytics from the project repository; a live connection between the cloud dashboard and local HDFS has not been configured.

---

## 📊 Dataset

The project uses a Spotify tracks dataset containing approximately **114,000 records**.

Depending on the available columns, the dataset includes information such as:

- Track and artist information
- Genre
- Popularity
- Danceability
- Energy
- Tempo (BPM)
- Acousticness
- Instrumentalness
- Valence
- Explicit-content indicators

The project analyzes the available fields to generate descriptive statistics, genre and artist summaries, mood distributions, and clustering outputs.

**Note:** Mood categories are analytical classifications inferred from available track features; they should not be interpreted as verified emotional states of listeners.

---

## 🔄 Data Processing Workflow

### 1. Data Ingestion
Load the Spotify CSV dataset into the processing workflow.

### 2. Data Cleaning
Inspect the dataset, handle data-quality issues, and prepare columns for analysis.

### 3. Feature Preparation
Convert applicable numeric columns to appropriate data types and prepare audio features for analysis.

### 4. Exploratory Analytics
Calculate summaries for genres, artists, mood categories, audio features, popularity, and other available attributes.

### 5. Clustering
Use a K-Means pipeline to investigate groupings among tracks based on selected features.

### 6. Output Generation
Export analytical results and reports as CSV and JSON files.

### 7. Visualization
Use Streamlit, Pandas, and Plotly to display the analytical results through an interactive dashboard.

---

## 📁 Project Structure

```text
MoodPulse/
├── data/
│   └── Spotify.csv
├── output/
│   ├── advanced/
│   │   ├── analytics/
│   │   │   ├── artist_analytics.csv
│   │   │   ├── bpm_distribution.csv
│   │   │   ├── cluster_profiles.csv
│   │   │   ├── correlation_analysis.csv
│   │   │   ├── explicit_analytics.csv
│   │   │   ├── genre_analytics.csv
│   │   │   ├── genre_volume.csv
│   │   │   ├── mood_analytics.csv
│   │   │   └── numeric_summary.csv
│   │   └── reports/
│   │       ├── clustering_k_evaluation.csv
│   │       ├── data_quality.csv
│   │       ├── feature_quantiles.json
│   │       └── run_report.json
│   ├── genre_popularity.csv
│   ├── mood_distribution.csv
│   └── top_genres.csv
├── src/
│   ├── moodpulse_advanced.py
│   ├── moodpulse_analysis.py
│   ├── moodpulse_dashboard.py
│   ├── moodpulse_dashboard_pro.py
│   ├── moodpulse_dashboard_pro_v2.py
│   ├── moodpulse_dashboard_pro_v3.py
│   ├── moodpulse_dashboard_pro_v4.py
│   ├── moodpulse_etl.py
│   └── moodpulse_final.py
├── dashboard.py
├── dashboard_pro.py
├── requirements.txt
├── .gitignore
└── README.md
```

*The tree highlights the main project files and selected outputs. Additional scripts and generated artifacts may be present in the repository.*

---

## 🚀 Run the Dashboard Locally

### Prerequisites

- Python 3.10 or a compatible version supported by your dependencies
- Git
- A terminal

### 1. Clone the repository

```bash
git clone https://github.com/iam-deepeshs/MoodPulse.git
cd MoodPulse
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it using:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run src/moodpulse_dashboard_pro_v4.py
```

Streamlit will display a local URL, typically `http://localhost:8501`.

---

## ⚙️ Running the PySpark Pipeline

The advanced processing script is:

```text
src/moodpulse_advanced.py
```

Activate an environment with compatible Java, Python, and PySpark installations before running it.

For example:

```bash
python src/moodpulse_advanced.py
```

Check the script's configuration and input/output paths before running it. The processing pipeline may require additional dependencies and Spark/Hadoop configuration beyond the dashboard's `requirements.txt`.

**Important:** `requirements.txt` currently contains the dashboard's primary dependencies. It is not a complete environment specification for reproducing the entire Spark/HDFS workflow.

---

## ☁️ Deployment

The Streamlit dashboard is deployed using Streamlit Community Cloud.

**Live application:** https://moodpulse-bda.streamlit.app/

The hosted application uses the GitHub repository as its source. The PySpark processing environment and HDFS storage remain separate local components; the complete processing pipeline has not been deployed as a cloud service.

---

## 🔮 Future Enhancements

- Integrate the dashboard with cloud-hosted analytics storage.
- Automate dataset ingestion and Spark processing.
- Schedule regular data-processing jobs.
- Add more advanced clustering evaluation and model comparisons.
- Improve filtering, search, and drill-down functionality.
- Add automated data-quality checks and testing.
- Implement a reproducible deployment workflow for the complete pipeline.

---

## 🎯 Expected Outcomes

MoodPulse demonstrates how music datasets can be processed and explored through a combination of big-data processing, descriptive analytics, clustering, and interactive visualization.

The project provides a foundation for exploring relationships among music genres, track popularity, audio characteristics, and inferred moods.

---

## 👨‍💻 Author

**Deepesh Srivastava**  
B.Tech — Artificial Intelligence and Machine Learning

GitHub: https://github.com/iam-deepeshs

---

## 📄 License

No license has been specified for this repository yet. Add an appropriate license if you intend to permit others to reuse, modify, or distribute the project.
