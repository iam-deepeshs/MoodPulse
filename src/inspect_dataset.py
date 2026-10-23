
import pandas as pd

path = "data/Spotify.csv"

df = pd.read_csv(path, nrows=5)

print("\n--- COLUMN NAMES ---")
print(df.columns.tolist())

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- SAMPLE RECORDS ---")
print(df.head().to_string())

print("\n--- FILE INFORMATION ---")
print("Columns:", len(df.columns))
print("Sample rows inspected:", len(df))

