
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import PipelineModel

BASE_DIR = os.path.expanduser("~/MoodPulse")
DATA_PATH = os.path.join(
    BASE_DIR, "output/advanced/processed_tracks"
)
MODEL_PATH = os.path.join(
    BASE_DIR, "output/advanced/models/kmeans_pipeline"
)
OUTPUT_DIR = os.path.join(
    BASE_DIR, "output/advanced/reports"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

FEATURES = [
    "danceability",
    "energy",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "loudness",
    "tempo",
]

spark = (
    SparkSession.builder
    .appName("MoodPulse-Cluster-Profiles-v2")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

try:
    print("\nLoading processed tracks...")
    df = spark.read.parquet(DATA_PATH)

    print("Loading saved K-Means pipeline...")
    model = PipelineModel.load(MODEL_PATH)

    print("Generating cluster assignments...")
    predictions = model.transform(df)

    # The saved pipeline's cluster output column is "cluster".
    cluster_col = (
        "cluster"
        if "cluster" in predictions.columns
        else "prediction"
    )

    if cluster_col not in predictions.columns:
        raise ValueError(
            f"No cluster column found. Available columns: "
            f"{predictions.columns}"
        )

    print(f"Using cluster column: {cluster_col}")

    # Calculate the average audio features for each cluster.
    profile = predictions.groupBy(cluster_col).agg(
        F.count("*").alias("track_count"),
        *[
            F.avg(feature).alias(f"avg_{feature}")
            for feature in FEATURES
        ],
    )

    profile = (
        profile
        .withColumnRenamed(cluster_col, "cluster")
        .orderBy("cluster")
    )

    print("\n" + "=" * 65)
    print("       MOODPULSE: EXISTING K=4 CLUSTER PROFILES")
    print("=" * 65)

    profile.show(truncate=False)

    # Save the small aggregated result as a CSV file.
    output_path = os.path.join(
        OUTPUT_DIR,
        "existing_k4_cluster_profiles.csv",
    )

    profile.toPandas().to_csv(output_path, index=False)

    print("\nCluster profiles saved successfully!")
    print(output_path)

finally:
    spark.stop()
