from pyspark.sql import SparkSession
from pyspark.sql.functions import when
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans

# Create Spark Session
spark = SparkSession.builder \
    .appName("MoodPulse") \
    .master("local[*]") \
    .getOrCreate()

# Load Dataset
df = spark.read.csv(
    "data/spotify.csv",
    header=True,
    inferSchema=True
)

df = df.drop("_c0")

print("Checking for bad rows...")

df.select(
    "popularity",
    "energy",
    "danceability",
    "valence",
    "explicit"
).show(20, truncate=False)

print("\nSchema:")
df.printSchema()

print("\nDataset Loaded Successfully")
print("Total Songs:", df.count())

# DEBUG
print("\nSchema before mood classification:")
df.printSchema()

# Explicitly cast important columns
from pyspark.sql.functions import col

df = df.withColumn("energy", col("energy").cast("double"))
df = df.withColumn("valence", col("valence").cast("double"))
df = df.withColumn("danceability", col("danceability").cast("double"))
df = df.withColumn("popularity", col("popularity").cast("int"))

# Mood Classification
df = df.withColumn(
    "mood",
    when((df.energy > 0.75) & (df.valence > 0.75), "Party")
    .when(df.valence > 0.7, "Happy")
    .when(df.energy > 0.7, "Energetic")
    .when(df.valence < 0.3, "Sad")
    .otherwise("Neutral")
)

# Mood Distribution
print("\nMood Distribution")
mood_dist = df.groupBy("mood").count().orderBy("count", ascending=False)
mood_dist.show()

# Top Genres
print("\nTop Genres")
top_genres = df.groupBy("track_genre") \
               .count() \
               .orderBy("count", ascending=False)

top_genres.show(15)

# Genre Popularity
print("\nMost Popular Genres")
genre_popularity = df.groupBy("track_genre") \
                     .avg("popularity") \
                     .orderBy("avg(popularity)", ascending=False)

genre_popularity.show(15)

# Correlation Analysis
print("\nCorrelation Analysis")

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

# K-Means Clustering
print("\nRunning K-Means Clustering")

assembler = VectorAssembler(
    inputCols=[
        "danceability",
        "energy",
        "valence",
        "tempo"
    ],
    outputCol="features"
)

dataset = assembler.transform(df)

kmeans = KMeans(
    k=4,
    seed=1,
    featuresCol="features"
)

model = kmeans.fit(dataset)

predictions = model.transform(dataset)

print("\nCluster Distribution")

predictions.groupBy("prediction") \
           .count() \
           .show()

# Save Results
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

spark.stop()
