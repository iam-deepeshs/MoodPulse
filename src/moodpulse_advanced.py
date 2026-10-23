
"""
MoodPulse Advanced BDA Pipeline
Dataset: data/Spotify.csv

Concepts demonstrated:
- Distributed processing with PySpark
- Robust CSV ingestion and data cleaning
- Data-quality profiling
- Feature engineering
- Genre, artist, and mood analytics
- Approximate quantiles and correlations
- Parquet storage
- Spark MLlib K-Means clustering
- Silhouette evaluation and reporting
"""

from pathlib import Path
from datetime import datetime, timezone
import json
import time

import pandas as pd

from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import IntegerType, DoubleType
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator


# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------

INPUT = "data/Spotify.csv"
OUT = Path("output/advanced")
ANALYTICS = OUT / "analytics"
REPORTS = OUT / "reports"
MODELS = OUT / "models"
PROCESSED = OUT / "processed_tracks"
CLUSTERED = OUT / "clustered_tracks"

for path in [ANALYTICS, REPORTS, MODELS]:
    path.mkdir(parents=True, exist_ok=True)

K = 4
SEED = 42
START = time.time()

INTEGER_COLS = [
    "popularity", "duration_ms", "key",
    "mode", "time_signature"
]

DOUBLE_COLS = [
    "danceability", "energy", "loudness",
    "speechiness", "acousticness", "instrumentalness",
    "liveness", "valence", "tempo"
]

BOUNDED_COLS = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence"
]

FEATURES = [
    "danceability", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness",
    "valence", "loudness", "tempo"
]

REQUIRED = [
    "track_id", "track_name", "artists",
    "track_genre", "popularity", "duration_ms",
    "energy", "danceability", "valence"
]


# ---------------------------------------------------------
# 2. SPARK SESSION
# ---------------------------------------------------------

spark = (
    SparkSession.builder
    .appName("MoodPulse-Advanced")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.default.parallelism", "2")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.sql.parquet.compression.codec", "snappy")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")


def export_csv(dataframe, filename):
    """Export a small aggregated result to CSV."""
    dataframe.toPandas().to_csv(
        str(ANALYTICS / filename), index=False
    )


def export_json(data, filename):
    """Save a JSON report."""
    with open(REPORTS / filename, "w") as file:
        json.dump(data, file, indent=2, default=str)


try:
    print("\n" + "=" * 60)
    print("MOODPULSE ADVANCED BDA PIPELINE")
    print("=" * 60)

    # -----------------------------------------------------
    # 3. ROBUST DATA INGESTION
    # -----------------------------------------------------

    raw = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .option("mode", "PERMISSIVE")
        .option("multiLine", True)
        .csv(INPUT)
    )

    # Remove the redundant index column.
    if "Unnamed: 0" in raw.columns:
        raw = raw.drop("Unnamed: 0")

    missing_required = set(REQUIRED) - set(raw.columns)
    if missing_required:
        raise ValueError(
            f"Required columns missing: {missing_required}"
        )

    raw_count = raw.count()
    print(f"\nRaw records: {raw_count:,}")
    print(f"Useful input columns: {len(raw.columns)}")

    # -----------------------------------------------------
    # 4. SAFE TYPE CONVERSION
    # -----------------------------------------------------

    df = raw

    for col in INTEGER_COLS:
        df = df.withColumn(
            col, F.expr(f"try_cast(`{col}` AS INT)")
        )

    for col in DOUBLE_COLS:
        df = df.withColumn(
            col, F.expr(f"try_cast(`{col}` AS DOUBLE)")
        )

    df = df.withColumn(
        "explicit",
        F.when(
            F.lower(F.trim(F.col("explicit"))).isin("true", "1"),
            F.lit(True)
        ).when(
            F.lower(F.trim(F.col("explicit"))).isin("false", "0"),
            F.lit(False)
        ).otherwise(F.lit(None).cast("boolean"))
    )

    for col in [
        "track_id", "track_name", "artists",
        "album_name", "track_genre"
    ]:
        df = df.withColumn(
            col,
            F.when(
                F.trim(F.col(col)) == "", None
            ).otherwise(F.trim(F.col(col)))
        )

    # -----------------------------------------------------
    # 5. DATA QUALITY REPORT
    # -----------------------------------------------------

    null_expressions = [
        F.sum(F.when(F.col(c).isNull(), 1).otherwise(0))
        .alias(c)
        for c in df.columns
    ]

    null_values = df.agg(*null_expressions).first().asDict()

    quality_rows = []
    for col in df.columns:
        n = int(null_values.get(col) or 0)
        quality_rows.append({
            "column": col,
            "null_count": n,
            "null_percentage": round(
                n * 100 / max(raw_count, 1), 3
            )
        })

    pd.DataFrame(quality_rows).to_csv(
        REPORTS / "data_quality.csv", index=False
    )

    print("\nMissing values by column:")
    for item in quality_rows:
        if item["null_count"]:
            print(
                f"  {item['column']}: "
                f"{item['null_count']:,}"
            )

    # -----------------------------------------------------
    # 6. DUPLICATE REMOVAL AND VALIDATION
    # -----------------------------------------------------

    before_dedup = df.count()
    df = df.dropDuplicates()
    after_dedup = df.count()

    duplicates_removed = before_dedup - after_dedup

    df = df.dropna(subset=REQUIRED)

    for col in BOUNDED_COLS:
        df = df.withColumn(
            col,
            F.when(
                F.col(col).between(0.0, 1.0),
                F.col(col)
            )
        )

    df = df.filter(
        F.col("popularity").between(0, 100) &
        (F.col("duration_ms") > 0) &
        (F.col("tempo") > 0) &
        F.col("explicit").isNotNull() &
        F.col("key").between(0, 11) &
        F.col("mode").isin(0, 1) &
        F.col("time_signature").between(1, 7)
    )

    for col in BOUNDED_COLS:
        df = df.filter(F.col(col).isNotNull())

    cleaned_count = df.count()

    if cleaned_count == 0:
        raise ValueError("No valid records remain after cleaning.")

    print(f"\nExact duplicates removed: {duplicates_removed:,}")
    print(f"Valid records: {cleaned_count:,}")
    print(
        "Rows removed after deduplication: "
        f"{after_dedup - cleaned_count:,}"
    )

    # -----------------------------------------------------
    # 7. FEATURE ENGINEERING
    # -----------------------------------------------------

    df = (
        df
        .withColumn(
            "duration_minutes",
            F.round(F.col("duration_ms") / 60000.0, 2)
        )
        .withColumn("bpm", F.round("tempo", 1))
        .withColumn(
            "mood_score",
            F.round(
                (F.col("energy") + F.col("valence")) / 2, 3
            )
        )
        .withColumn(
            "dance_energy_score",
            F.round(
                F.col("danceability") * F.col("energy"), 3
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
            .when(F.col("valence") >= 0.60, "Happy")
            .otherwise("Neutral")
        )
    )

    df = df.cache()
    final_count = df.count()

    # -----------------------------------------------------
    # 8. PARQUET STORAGE
    # -----------------------------------------------------

    (
        df.write
        .mode("overwrite")
        .option("compression", "snappy")
        .partitionBy("track_genre")
        .parquet(str(PROCESSED))
    )

    print(f"\nProcessed Parquet saved: {PROCESSED}")

    # -----------------------------------------------------
    # 9. GENRE ANALYTICS
    # -----------------------------------------------------

    genre = df.groupBy("track_genre").agg(
        F.count("*").alias("track_count"),
        F.round(F.avg("popularity"), 2).alias("avg_popularity"),
        F.round(F.avg("energy"), 3).alias("avg_energy"),
        F.round(F.avg("danceability"), 3).alias("avg_danceability"),
        F.round(F.avg("valence"), 3).alias("avg_valence"),
        F.round(F.avg("tempo"), 2).alias("avg_bpm"),
        F.round(F.avg("acousticness"), 3).alias("avg_acousticness")
    )

    export_csv(
        genre.orderBy(F.desc("avg_popularity")),
        "genre_analytics.csv"
    )
    export_csv(
        genre.orderBy(F.desc("track_count")),
        "genre_volume.csv"
    )

    # -----------------------------------------------------
    # 10. ARTIST ANALYTICS
    # -----------------------------------------------------

    artist = (
        df.groupBy("artists")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity"),
            F.round(F.avg("energy"), 3).alias("avg_energy"),
            F.round(F.avg("valence"), 3).alias("avg_valence")
        )
        .filter(F.col("artists").isNotNull())
    )

    export_csv(
        artist.orderBy(
            F.desc("avg_popularity"), F.desc("track_count")
        ).limit(100),
        "artist_analytics.csv"
    )

    # -----------------------------------------------------
    # 11. MOOD ANALYTICS
    # -----------------------------------------------------

    mood = (
        df.groupBy("mood_category")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("energy"), 3).alias("avg_energy"),
            F.round(F.avg("valence"), 3).alias("avg_valence"),
            F.round(F.avg("danceability"), 3)
             .alias("avg_danceability")
        )
        .withColumn(
            "percentage",
            F.round(F.col("track_count") * 100 / final_count, 2)
        )
        .orderBy(F.desc("track_count"))
    )

    export_csv(mood, "mood_analytics.csv")

    # -----------------------------------------------------
    # 12. BPM DISTRIBUTION
    # -----------------------------------------------------

    bpm = (
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
            F.round(F.avg("energy"), 3).alias("avg_energy")
        )
    )

    export_csv(bpm, "bpm_distribution.csv")

    # -----------------------------------------------------
    # 13. EXPLICIT CONTENT ANALYSIS
    # -----------------------------------------------------

    explicit_stats = (
        df.groupBy("explicit")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity"),
            F.round(F.avg("energy"), 3).alias("avg_energy"),
            F.round(F.avg("valence"), 3).alias("avg_valence")
        )
    )

    export_csv(explicit_stats, "explicit_analytics.csv")

    # -----------------------------------------------------
    # 14. STATISTICS AND APPROXIMATE QUANTILES
    # -----------------------------------------------------

    summary = df.select(
        *FEATURES, "popularity", "duration_minutes"
    ).summary(
        "count", "mean", "stddev", "min",
        "25%", "50%", "75%", "max"
    )

    export_csv(summary, "numeric_summary.csv")

    quantile_columns = [
        "energy", "valence", "danceability", "tempo"
    ]

    quantiles = df.approxQuantile(
        quantile_columns,
        [0.25, 0.50, 0.75, 0.95],
        0.01
    )

    export_json({
        col: dict(zip(
            ["p25", "p50", "p75", "p95"], values
        ))
        for col, values in zip(quantile_columns, quantiles)
    }, "feature_quantiles.json")

    # -----------------------------------------------------
    # 15. PEARSON CORRELATION ANALYSIS
    # -----------------------------------------------------

    corr_cols = [
        "popularity", "energy", "danceability",
        "valence", "acousticness", "tempo"
    ]

    correlation_rows = []

    for i, col_a in enumerate(corr_cols):
        for col_b in corr_cols[i + 1:]:
            correlation_rows.append({
                "feature_1": col_a,
                "feature_2": col_b,
                "pearson_correlation": df.stat.corr(col_a, col_b)
            })

    pd.DataFrame(correlation_rows).to_csv(
        ANALYTICS / "correlation_analysis.csv",
        index=False
    )

    # -----------------------------------------------------
    # 16. SPARK MLLIB K-MEANS CLUSTERING
    # -----------------------------------------------------

    print("\nTraining K-Means model...")

    assembler = VectorAssembler(
        inputCols=FEATURES,
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
        k=K,
        seed=SEED,
        featuresCol="features",
        predictionCol="cluster",
        maxIter=30,
        tol=1e-4
    )

    pipeline = Pipeline(stages=[assembler, scaler, kmeans])
    model = pipeline.fit(df)
    predictions = model.transform(df)

    evaluator = ClusteringEvaluator(
        featuresCol="features",
        predictionCol="cluster",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean"
    )

    silhouette = evaluator.evaluate(predictions)

    model.write().overwrite().save(str(MODELS / "kmeans_pipeline"))

    (
        predictions.select(
            "track_id", "track_name", "artists",
            "track_genre", "cluster", "energy",
            "valence", "danceability", "acousticness",
            "tempo", "popularity"
        )
        .write.mode("overwrite")
        .parquet(str(CLUSTERED))
    )

    cluster_profiles = (
        predictions.groupBy("cluster")
        .agg(
            F.count("*").alias("track_count"),
            F.round(F.avg("energy"), 3).alias("avg_energy"),
            F.round(F.avg("valence"), 3).alias("avg_valence"),
            F.round(F.avg("danceability"), 3)
             .alias("avg_danceability"),
            F.round(F.avg("acousticness"), 3)
             .alias("avg_acousticness"),
            F.round(F.avg("tempo"), 2).alias("avg_bpm"),
            F.round(F.avg("popularity"), 2)
             .alias("avg_popularity")
        )
        .orderBy("cluster")
    )

    export_csv(cluster_profiles, "cluster_profiles.csv")

    # -----------------------------------------------------
    # 17. FINAL REPORT
    # -----------------------------------------------------

    elapsed = round(time.time() - START, 2)

    report = {
        "project": "MoodPulse",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "input": INPUT,
        "raw_records": raw_count,
        "exact_duplicates_removed": duplicates_removed,
        "processed_records": final_count,
        "records_removed_after_dedup": after_dedup - final_count,
        "retention_percentage": round(
            final_count * 100 / max(raw_count, 1), 2
        ),
        "cluster_count": K,
        "random_seed": SEED,
        "silhouette_score": silhouette,
        "spark_version": spark.version,
        "processing_seconds": elapsed
    }

    export_json(report, "run_report.json")

    print("\n--- MOOD DISTRIBUTION ---")
    mood.show(truncate=False)

    print("\n--- TOP 10 GENRES BY POPULARITY ---")
    genre.orderBy(F.desc("avg_popularity")).show(10, truncate=False)

    print("\n--- CLUSTER PROFILES ---")
    cluster_profiles.show(truncate=False)

    print("\n--- FINAL REPORT ---")
    print(json.dumps(report, indent=2))

    print("\nAll advanced analytics generated successfully.")

finally:
    spark.stop()

