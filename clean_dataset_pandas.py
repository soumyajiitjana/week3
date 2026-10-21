import pandas as pd
import numpy as np

df = pd.read_csv("data(2).csv")

# 1. Normalize dates (remove quote marks and handle YYYYMMDD)
df["Date"] = df["Date"].astype("string").str.strip().str.strip("'\"")
df["Date"] = df["Date"].replace({"20201226": "2020/12/26", "": pd.NA})
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
# Dataset appears to be daily; the missing date falls between Dec 21 and Dec 23.
df.loc[df["Date"].isna(), "Date"] = pd.Timestamp("2020-12-22")

# 2. Convert numeric fields
for col in ["Duration", "Pulse", "Maxpulse", "Calories"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 3. Remove exact duplicate rows
df = df.drop_duplicates()

# 4. Correct an obvious typo: 450 minutes -> 45 minutes
df.loc[df["Duration"] == 450, "Duration"] = 45

# 5. Impute missing calories using the median
df["Calories"] = df["Calories"].fillna(df["Calories"].median())

# 6. Filter invalid rows
df = df[df["Duration"].between(1, 180)]
df = df[df["Maxpulse"] >= df["Pulse"]].copy()

# 7. Create new columns
df["Duration_hours"] = (df["Duration"] / 60).round(2)
df["Calories_per_minute"] = (df["Calories"] / df["Duration"]).round(2)
df["Heart_Rate_Gap"] = df["Maxpulse"] - df["Pulse"]
df["Workout_Intensity"] = np.select(
    [df["Pulse"] < 100, df["Pulse"].between(100, 110), df["Pulse"] > 110],
    ["Low", "Moderate", "High"],
    default="Moderate"
)

df = df.sort_values("Date").reset_index(drop=True)
df.to_csv("cleaned_workout_data.csv", index=False)
print(df.head())
print("Final rows:", len(df))
