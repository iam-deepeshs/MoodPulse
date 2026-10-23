
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("MoodPulse-Test")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .getOrCreate()
)

data = [
    ("Happy", 120, 85),
    ("Energetic", 140, 92),
    ("Sad", 75, 30),
    ("Calm", 90, 45),
]

df = spark.createDataFrame(
    data, ["mood", "bpm", "energy"]
)

df.show()
df.groupBy("mood").avg("energy").show()

print("Spark version:", spark.version)
print("MoodPulse Spark test successful!")

spark.stop()

