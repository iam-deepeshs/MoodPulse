from pyspark.sql import SparkSession
from pyspark.sql.functions import when
from pyspark.sql.types import *
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
import os

# ==========================================
# CREATE SPARK SESSION
# ==========================================

spark = SparkSession.builder \
    .appName("MoodPulse") \
    .master("local[*]") \
    .getOrCreate()

print("\nMoodPulse Started Successfully!")

# ==========================================
# DEFINE SCHEMA
# ==========================================

schema = StructType([
    StructField("_c0", IntegerType(), True),
    StructField("track_id", StringType(), True),
    StructField("artists", StringType(), True),
    StructField("album_name", StringType(), True),
    StructField("track_name", StringType(), True),
    StructField("popularity", IntegerType(), True),
    StructField("duration_ms", IntegerType(), True),
    StructField("explicit", BooleanType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("energy", DoubleType(), True),
    StructField("key", IntegerType(), True),
    StructField("loudness", DoubleType(), True),
    StructField("mode", IntegerType(), True),
    StructField("speechiness", DoubleType(), True),
    StructField("acousticness", DoubleType(), True),
    StructField("instrumentalness", DoubleType(), True),
    StructField("liveness", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("tempo", DoubleType(), True),
    StructField("time_signature", IntegerType(), True),
    StructField("track_genre", StringType(), True)
])

# ==========================================
# LOAD DATASET
# ==========================================

df = spark.read.csv(
    "data/spotify.csv",
    header=True,
    schema=schema
)

df = df.drop("_c0")

print("\nDataset Loaded Successfully!")
print("Total Songs:", df.count())

# ==========================================
# MOOD CLASSIFICATION
# ==========================================

df = df.withColumn(
    "mood",
    when((df.energy > 0.75) & (df.valence > 0.75), "Party")
    .when(df.valence > 0.70, "Happy")
    .when(df.energy > 0.70, "Energetic")
    .when(df.valence < 0.30, "Sad")
    .otherwise("Neutral")
)

print("\nMood Classification Completed!")

# ==========================================
# MOOD DISTRIBUTION
# ==========================================

print("\n========== MOOD DISTRIBUTION ==========")

mood_dist = (
    df.groupBy("mood")
      .count()
      .orderBy("count", ascending=False)
)

mood_dist.show()

# ==========================================
# TOP GENRES
# ==========================================

print("\n========== TOP GENRES ==========")

top_genres = (
    df.groupBy("track_genre")
      .count()
      .orderBy("count", ascending=False)
)

top_genres.show(15)

# ==========================================
# MOST POPULAR GENRES
# ==========================================

print("\n========== MOST POPULAR GENRES ==========")

genre_popularity = (
    df.groupBy("track_genre")
      .avg("popularity")
      .orderBy("avg(popularity)", ascending=False)
)

genre_popularity.show(15)

# ==========================================
# TOP ARTISTS
# ==========================================

print("\n========== TOP ARTISTS ==========")

top_artists = (
    df.groupBy("artists")
      .avg("popularity")
      .orderBy("avg(popularity)", ascending=False)
)

top_artists.show(10, truncate=False)

# ==========================================
# CORRELATION ANALYSIS
# ==========================================

print("\n========== CORRELATION ANALYSIS ==========")

print(
    "Energy vs Popularity:",
    df.stat.corr("energy", "popularity")
)

print(
    "Danceability vs Popularity:",
    df.stat.corr("danceability", "popularity")
)

print(
    "Valence vs Popularity:",
    df.stat.corr("valence", "popularity")
)

# ==========================================
# K-MEANS CLUSTERING
# ==========================================

print("\n========== K-MEANS CLUSTERING ==========")

# Remove rows having null values
df = df.na.drop(
    subset=[
        "danceability",
        "energy",
        "valence",
        "tempo"
    ]
)

assembler = VectorAssembler(
    inputCols=[
        "danceability",
        "energy",
        "valence",
        "tempo"
    ],
    outputCol="features",
    handleInvalid="skip"
)

dataset = assembler.transform(df)
from pyspark.ml.feature import StandardScaler

scaler = StandardScaler(
    inputCol="features",
    outputCol="scaled_features",
    withMean=True,
    withStd=True
)

scaler_model = scaler.fit(dataset)
dataset = scaler_model.transform(dataset)

kmeans = KMeans(
    k=4,
    seed=1,
    featuresCol="scaled_features"
)

model = kmeans.fit(dataset)

predictions = model.transform(dataset)

print("\nCluster Distribution")

predictions.groupBy("prediction") \
           .count() \
           .show()

# ==========================================
# SAVE RESULTS
# ==========================================

os.makedirs("output", exist_ok=True)

mood_dist.toPandas().to_csv(
    "output/mood_distribution.csv",
    index=False
)

top_genres.toPandas().to_csv(
    "output/top_genres.csv",
    index=False
)

genre_popularity.toPandas().to_csv(
    "output/genre_popularity.csv",
    index=False
)

print("\nResults Saved Successfully!")
print("\nFiles saved inside output/ folder")

spark.stop()

print("\nMoodPulse Completed Successfully!")
