
"""
MoodPulse: Large-Scale Music Trend & Mood Analytics
Advanced BDA pipeline using PySpark and Spark MLlib.

Input:
    data/Spotify.csv

Outputs:
    output/processed_tracks/
    output/analytics/
    output/models/
    output/reports/
"""

import json
import time
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import (
    DoubleType, IntegerType, BooleanType
)
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    VectorAssembler, StandardScaler
)
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator


# ============================================================
# 1. CONFIGURATION
# ============================================================

INPUT_PATH = "data/Spotify.csv"
OUTPUT = Path("output")

ANALYTICS_DIR = OUTPUT / "analytics"
REPORTS_DIR = OUTPUT / "reports"
MODELS_DIR = OUTPUT / "models"
PROCESSED_DIR = OUTPUT / "processed_tracks"

for directory in [
    ANALYTICS_DIR, REPORTS_DIR, MODELS_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

START_TIME = time.time()

# Four clusters are an initial experiment, not a proven optimum.
N_CLUSTERS = 4
SEED = 42

NUMERIC_INT = [
    "popularity", "duration_ms", "key",
    "mode", "time_signature"
]

NUMERIC_DOUBLE = [
    "danceability", "energy", "loudness",
    "speechiness", "acousticness",
    "instrumentalness", "liveness",
    "valence", "tempo"
]

AUDIO_FEATURES = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness",
    "liveness", "valence", "loudness", "tempo"
]

BOUNDED_FEATURES = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness",
    "liveness", "valence"
]

REQUIRED_COLUMNS = [
    "track_id", "track_name", "artists",
    "track_genre", "popularity", "duration_ms",
    "energy", "danceability", "valence"
]


# ============================================================
# 2. SPARK SESSION
# ============================================================

spark = (
    SparkSession.builder
    .appName("MoodPulse-Advanced-BDA")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.default.parallelism", "2")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.parquet.compression.codec", "snappy")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


def save_csv(df, filename):
    """Export a small analytical result as a single CSV file."""
    df.toPandas().to_csv(
        str(ANALYTICS_DIR / filename),
        index=False
    )


def write_json(data, filename):
    """Save a machine-readable project report."""
    with open(REPORTS_DIR / filename, "w") as file:
        json.dump(data, file, indent=2, default=str)


try:
    print("\n" + "=" * 65)
    print("MOODPULSE | ADVANCED BIG DATA ANALYTICS")
    print("=" * 65)

    # ========================================================
    # 3. DATA INGESTION
    # ========================================================

    raw = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .option("mode", "PERMISSIVE")
        .csv(INPUT_PATH)
    )

    # The CSV contains a redundant exported index.
    if "Unnamed: 0" in raw.columns:
        raw = raw.drop("Unnamed: 0")

    missing_columns = set(REQUIRED_COLUMNS) - set(raw.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    raw_count = raw.count()

    print(f"\nRaw records: {raw_count:,}")
    print(f"Input columns: {len(raw.columns)}")

    # ========================================================
    # 4. EXPLICIT DATA-TYPE CONVERSION
    # ========================================================

    df = raw

    for col in NUMERIC_INT:
        df = df.withColumn(
            col, F.col(col).cast(IntegerType())
        )

    for col in NUMERIC_DOUBLE:
        df = df.withColumn(
            col, F.col(col).cast(DoubleType())
        )

    df = df.withColumn(
        "explicit",
        F.when(
            F.lower(F.trim(F.col("explicit"))).isin(
                "true", "1"
            ), F.lit(True)
        ).when(
            F.lower(F.trim(F.col("explicit"))).isin(
                "false", "0"
            ), F.lit(False)
        ).otherwise(F.lit(None).cast(BooleanType()))
    )

    # Normalize blank strings and whitespace.
    for col in ["track_id", "track_name", "artists",
                "album_name", "track_genre"]:
        df = df.withColumn(
            col,
            F.when(
                F.trim(F.col(col)) == "",
                None
            ).otherwise(F.trim(F.col(col)))
        )

    # ========================================================
    # 5. DATA-QUALITY PROFILING
    # ========================================================

    print("\n--- DATA QUALITY PROFILE ---")

    quality_exprs = []

    for col in df.columns:
        quality_exprs.append(
            F.sum(
                F.when(
                    F.col(col).isNull(), 1
                ).otherwise(0)
            ).alias(col)
        )

    null_counts = df.agg(*quality_exprs).first().asDict()

    quality_report = []

    for col in df.columns:
        nulls = int(null_counts.get(col) or 0)

        quality_report.append({
            "column": col,
            "null_count": nulls,
            "null_percentage": round(
                100 * nulls / max(raw_count, 1), 3
            )
        })

    pd.DataFrame(quality_report).to_csv(
        REPORTS_DIR / "data_quality.csv",
        index=False
    )

    # Identify rows containing invalid numeric conversions.
    numeric_cols = NUMERIC_INT + NUMERIC_DOUBLE

    invalid_numeric_condition = None

    for col in numeric_cols:
        condition = (
            F.col(col).isNull() &
            F.col(col).isNotNull()
        )

        # Null values are measured separately. A conversion failure
        # is best detected against the original string column.
        original = raw.select(col).withColumnRenamed(
            col, f"original_{col}"
        )

    # ========================================================
    # 6. DEDUPLICATION AND VALIDATION
    # ========================================================

    before_dedup = df.count()
    df = df.dropDuplicates()
    after_dedup = df.count()

    exact_duplicates_removed = before_dedup - after_dedup

    # Track IDs may repeat in some datasets. We only remove
    # exact duplicates here; distinct versions are not assumed
    # to be the same track.

    df = df.dropna(subset=REQUIRED_COLUMNS)

    # Validate bounded audio features.
    for col in BOUNDED_FEATURES:
        df = df.withColumn(
            col,
            F.when(
                F.col(col).between(0.0, 1.0),
                F.col(col)
            )
        )

    # Remove physically or analytically invalid values.
    df = df.filter(
        F.col("popularity").between(0, 100) &
        (F.col("duration_ms") > 0) &
        (F.col("tempo") > 0) &
        F.col("explicit").isNotNull()
    )

    for col in BOUNDED_FEATURES:
        df = df.filter(F.col(col).isNotNull())

    # Restrict music-theory categorical fields to expected ranges.
    df = df.filter(
        F.col("key").between(0, 11) &
        F.col("mode").isin(0, 1) &
        F.col("time_signature").between(1, 7)
    )

    cleaned_count = df.count()

    if cleaned_count == 0:
        raise ValueError(
            "No valid records remain after cleaning."
        )

    print(f"Exact duplicates removed: "
          f"{exact_duplicates_removed:,}")
    print(f"Cleaned records: {cleaned_count:,}")
    print(f"Rows removed during validation: "
          f"{after_dedup - cleaned_count:,}")

    # ========================================================
    # 7. FEATURE ENGINEERING
    # ========================================================

    df = (
        df
        .withColumn(
            "duration_minutes",
            F.round(F.col("duration_ms") / 60000.0, 2)
        )
        .withColumn(
            "bpm",
            F.round(F.col("tempo"), 1)
        )
        .withColumn(
            "mood_score",
            F.round(
                (F.col("energy") + F.col("valence")) / 2,
                3
            )
        )
        .withColumn(
            "dance_energy_score",
            F.round(
                F.col("danceability") * F.col("energy"),
                3
            )
        )
        .withColumn(
            "mood_category",
            F.when(
                (F.col("energy") >= 0.65) &
                (F.col("valence") >= 0.60),
                "Energetic"
            )
            .when(
                (F.col("energy") < 0.40) &
                (F.col("valence") < 0.40),
                "Sad"
            )
            .when(
                (F.col("danceability") >= 0.70) &
                (F.col("energy") >= 0.60),
                "Party"
            )
            .when(
                F.col("valence") >= 0.60,
                "Happy"
            )
            .otherwise("Neutral")
        )
    )

    # Persist the reused DataFrame in memory for local Spark jobs.
    df = df.cache()
    final_count = df.count()

    # ========================================================
    # 8. DISTRIBUTED STORAGE: PARQUET
    # ========================================================

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .partitionBy("track_genre")
        .parquet(str(PROCESSED_DIR))
    )

    print(f"\nParquet dataset written: {PROCESSED_DIR}")

    # ========================================================
    # 9. GENRE ANALYTICS
    # ========================================================

    genre_stats = (
        df.groupBy("track_genre")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy"),
            F.round(F.avg("danceability"), 3)
             .alias("avg_danceability"),
            F.round(F.avg("valence"), 3)
             .alias("avg_valence"),
            F.round(F.avg("tempo"), 2)
             .alias("avg_bpm"),
            F.round(F.avg("acousticness"), 3)
             .alias("avg_acousticness")
        )
    )

    save_csv(
        genre_stats.orderBy(F.desc("avg_popularity")),
        "genre_analytics.csv"
    )

    save_csv(
        genre_stats.orderBy(F.desc("track_count")),
        "genre_volume.csv"
    )

    # ========================================================
    # 10. ARTIST ANALYTICS
    # ========================================================

    artist_stats = (
        df.groupBy("artists")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy"),
            F.round(F.avg("valence"), 3)
             .alias("avg_valence")
        )
        .filter(F.col("artists").isNotNull())
    )

    save_csv(
        artist_stats.orderBy(
            F.desc("avg_popularity"),
            F.desc("track_count")
        ).limit(100),
        "artist_analytics.csv"
    )

    # ========================================================
    # 11. MOOD DISTRIBUTION
    # ========================================================

    mood_stats = (
        df.groupBy("mood_category")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy"),
            F.round(F.avg("valence"), 3)
             .alias("avg_valence"),
            F.round(F.avg("danceability"), 3)
             .alias("avg_danceability")
        )
        .withColumn(
            "percentage",
            F.round(
                100 * F.col("track_count") / final_count,
                2
            )
        )
        .orderBy(F.desc("track_count"))
    )

    save_csv(mood_stats, "mood_analytics.csv")

    # ========================================================
    # 12. BPM DISTRIBUTION
    # ========================================================

    bpm_stats = (
        df.withColumn(
            "bpm_band",
            F.when(F.col("tempo") < 60, "Below 60")
             .when(F.col("tempo") < 90, "60-89")
             .when(F.col("tempo") < 120, "90-119")
             .when(F.col("tempo") < 150, "120-149")
             .otherwise("150+")
        )
        .groupBy("bpm_band")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy")
        )
    )

    save_csv(bpm_stats, "bpm_distribution.csv")

    # ========================================================
    # 13. EXPLICIT VS NON-EXPLICIT
    # ========================================================

    explicit_stats = (
        df.groupBy("explicit")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy"),
            F.round(F.avg("valence"), 3)
             .alias("avg_valence")
        )
    )

    save_csv(explicit_stats, "explicit_analytics.csv")

    # ========================================================
    # 14. DISTRIBUTED STATISTICAL ANALYSIS
    # ========================================================

    numeric_summary = df.select(
        *AUDIO_FEATURES,
        "popularity",
        "duration_minutes"
    ).summary(
        "count", "mean", "stddev", "min", "25%", "50%",
        "75%", "max"
    )

    save_csv(numeric_summary, "numeric_summary.csv")

    # Approximate quantiles reduce the cost of exact quantile work.
    quantiles = df.approxQuantile(
        ["energy", "valence", "danceability", "tempo"],
        [0.25, 0.50, 0.75, 0.95],
        0.01
    )

    quantile_report = {
        col: {
            "p25": values[0],
            "p50": values[1],
            "p75": values[2],
            "p95": values[3]
        }
        for col, values in zip(
            ["energy", "valence", "danceability", "tempo"],
            quantiles
        )
    }

    write_json(quantile_report, "feature_quantiles.json")

    # Correlation matrix for selected numeric features.
    correlations = []

    corr_features = [
        "popularity", "energy", "danceability",
        "valence", "acousticness", "tempo"
    ]

    for i, col_a in enumerate(corr_features):
        for col_b in corr_features[i + 1:]:
            value = df.stat.corr(col_a, col_b)

            correlations.append({
                "feature_1": col_a,
                "feature_2": col_b,
                "pearson_correlation": value
            })

    pd.DataFrame(correlations).to_csv(
        ANALYTICS_DIR / "correlation_analysis.csv",
        index=False
    )

    # ========================================================
    # 15. K-MEANS CLUSTERING USING SPARK MLLIB
    # ========================================================

    print("\n--- K-MEANS CLUSTERING ---")

    # Assemble features and standardize them so loudness/tempo
    # do not dominate features with smaller numeric scales.
    assembler = VectorAssembler(
        inputCols=AUDIO_FEATURES,
        outputCol="raw_features",
        handleInvalid="skip"
    )

    scaler = StandardScaler(
        inputCol="raw_features",
        outputCol="features",
        withMean=True,
        withStd=True
    )

    kmeans = KMeans(
        k=N_CLUSTERS,
        seed=SEED,
        featuresCol="features",
        predictionCol="cluster",
        maxIter=30,
        tol=1e-4
    )

    ml_pipeline = Pipeline(
        stages=[assembler, scaler, kmeans]
    )

    model = ml_pipeline.fit(df)

    predictions = model.transform(df)

    evaluator = ClusteringEvaluator(
        featuresCol="features",
        predictionCol="cluster",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean"
    )

    silhouette = evaluator.evaluate(predictions)

    model.write().overwrite().save(
        str(MODELS_DIR / "kmeans_pipeline")
    )

    # Save the cluster ID for each track.
    cluster_tracks = predictions.select(
        "track_id", "track_name", "artists",
        "track_genre", "cluster",
        "energy", "valence", "danceability",
        "acousticness", "tempo", "popularity"
    )

    (
        cluster_tracks.write
        .mode("overwrite")
        .parquet(str(OUTPUT / "clustered_tracks"))
    )

    cluster_profiles = (
        predictions.groupBy("cluster")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("energy"), 3)
             .alias("avg_energy"),
            F.round(F.avg("valence"), 3)
             .alias("avg_valence"),
            F.round(F.avg("danceability"), 3)
             .alias("avg_danceability"),
            F.round(F.avg("acousticness"), 3)
             .alias("avg_acousticness"),
            F.round(F.avg("tempo"), 2)
             .alias("avg_bpm"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity")
        )
        .orderBy("cluster")
    )

    save_csv(cluster_profiles, "cluster_profiles.csv")

    print(f"Silhouette score: {silhouette:.4f}")
    print("Interpretation: higher is generally better, but")
    print("compare multiple k values before selecting a model.")

    # ========================================================
    # 16. RUN METRICS AND FINAL REPORT
    # ========================================================

    elapsed_seconds = round(time.time() - START_TIME, 2)

    report = {
        "project": "MoodPulse",
        "run_timestamp_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "input_file": INPUT_PATH,
        "raw_records": raw_count,
        "exact_duplicates_removed": exact_duplicates_removed,
        "processed_records": final_count,
        "records_removed_after_dedup": (
            after_dedup - final_count
        ),
        "retention_percentage": round(
            100 * final_count / max(raw_count, 1), 2
        ),
        "features_used_for_clustering": AUDIO_FEATURES,
        "kmeans_clusters": N_CLUSTERS,
        "kmeans_seed": SEED,
        "silhouette_score": silhouette,
        "processing_seconds": elapsed_seconds,
        "spark_version": spark.version
    }

    write_json(report, "run_report.json")

    print("\n--- MOOD DISTRIBUTION ---")
    mood_stats.show(truncate=False)

    print("\n--- TOP GENRES BY POPULARITY ---")
    genre_stats.orderBy(
        F.desc("avg_popularity")
    ).show(10, truncate=False)

    print("\n--- CLUSTER PROFILES ---")
    cluster_profiles.show(truncate=False)

    print("\n--- FINAL METRICS ---")
    print(json.dumps(report, indent=2))

    print("\nMoodPulse BDA pipeline completed successfully.")

finally:
    spark.stop()

