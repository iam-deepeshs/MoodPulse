import os
import json
import time

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------
BASE_DIR = os.path.expanduser("~/MoodPulse")
DATA_PATH = os.path.join(BASE_DIR, "output/advanced/processed_tracks")
OUTPUT_DIR = os.path.join(BASE_DIR, "output/advanced/reports")

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

K_VALUES = [2, 3, 4, 5, 6]


# --------------------------------------------------
# 2. START SPARK
# --------------------------------------------------
spark = (
    SparkSession.builder
    .appName("MoodPulse-Clustering-Evaluation")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .config("spark.sql.shuffle.partitions", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

start_time = time.time()

try:
    print("\n" + "=" * 60)
    print("       MOODPULSE: K-MEANS MODEL EVALUATION")
    print("=" * 60)

    # --------------------------------------------------
    # 3. LOAD PROCESSED DATA
    # --------------------------------------------------
    df = spark.read.parquet(DATA_PATH)

    missing_features = [c for c in FEATURES if c not in df.columns]

    if missing_features:
        raise ValueError(
            f"Missing feature columns: {missing_features}"
        )

    # Keep only rows with complete feature values.
    for feature in FEATURES:
        df = df.filter(df[feature].isNotNull())

    # Use the same feature engineering approach for every K.
    assembler = VectorAssembler(
        inputCols=FEATURES,
        outputCol="raw_features",
        handleInvalid="skip",
    )

    scaler = StandardScaler(
        inputCol="raw_features",
        outputCol="features",
        withMean=True,
        withStd=True,
    )

    prepared = Pipeline(
        stages=[assembler, scaler]
    ).fit(df).transform(df).select("features").cache()

    total_rows = prepared.count()

    print(f"\nTracks evaluated: {total_rows:,}")
    print(f"K values tested: {K_VALUES}")
    print("\nTraining and evaluating models...\n")

    # --------------------------------------------------
    # 4. EVALUATE DIFFERENT K VALUES
    # --------------------------------------------------
    evaluator = ClusteringEvaluator(
        featuresCol="features",
        predictionCol="prediction",
        metricName="silhouette",
        distanceMeasure="squaredEuclidean",
    )

    results = []

    for k in K_VALUES:
        model_start = time.time()

        kmeans = KMeans(
            k=k,
            seed=42,
            featuresCol="features",
            predictionCol="prediction",
            maxIter=30,
            tol=0.0001,
        )

        model = kmeans.fit(prepared)
        predictions = model.transform(prepared).cache()

        silhouette = evaluator.evaluate(predictions)

        cluster_sizes = {
            int(row["prediction"]): int(row["count"])
            for row in predictions.groupBy("prediction")
            .count()
            .collect()
        }

        sizes = list(cluster_sizes.values())

        result = {
            "k": k,
            "silhouette_score": float(silhouette),
            "training_cost": float(model.summary.trainingCost),
            "iterations": int(model.summary.numIter),
            "smallest_cluster": min(sizes),
            "largest_cluster": max(sizes),
            "cluster_sizes": json.dumps(cluster_sizes),
            "runtime_seconds": round(
                time.time() - model_start, 2
            ),
        }

        results.append(result)

        print(
            f"K={k} | "
            f"Silhouette={silhouette:.4f} | "
            f"Iterations={result['iterations']} | "
            f"Runtime={result['runtime_seconds']} sec"
        )

        predictions.unpersist()

    prepared.unpersist()

    # --------------------------------------------------
    # 5. SAVE RESULTS
    # --------------------------------------------------
    results.sort(
        key=lambda x: x["silhouette_score"],
        reverse=True,
    )

    output_csv = os.path.join(
        OUTPUT_DIR, "clustering_k_evaluation.csv"
    )

    result_df = spark.createDataFrame(results)
    result_df.coalesce(1).write.mode("overwrite").option(
        "header", True
    ).csv(output_csv + "_spark")

    # Also save a convenient single CSV file using Python's
    # standard library, without converting all tracks to Pandas.
    import csv

    with open(output_csv, "w", newline="") as file:
        writer = csv.DictWriter(
            file, fieldnames=list(results[0].keys())
        )
        writer.writeheader()
        writer.writerows(results)

    # --------------------------------------------------
    # 6. DISPLAY RANKING
    # --------------------------------------------------
    print("\n" + "=" * 60)
    print("             MODEL COMPARISON")
    print("=" * 60)

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. K={result['k']} | "
            f"Silhouette={result['silhouette_score']:.4f} | "
            f"Cluster sizes={result['cluster_sizes']}"
        )

    best = results[0]

    print("\n" + "-" * 60)
    print(f"Best silhouette score: {best['silhouette_score']:.4f}")
    print(f"Best K by silhouette: {best['k']}")
    print(f"Results saved to: {output_csv}")
    print(
        f"Total runtime: {time.time() - start_time:.2f} seconds"
    )
    print("-" * 60)

finally:
    spark.stop()
