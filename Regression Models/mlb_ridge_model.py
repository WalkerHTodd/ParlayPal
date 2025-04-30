import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

# Load player stats
pivot_df = pd.read_csv("../Data/MLBData/mlb_recent_player_stats.csv")
print("✅ Loaded player stats:", pivot_df.shape)

# Pivot the data to get stats as columns
pivot_df = pivot_df.pivot_table(
    index=["player_id", "player_name", "team", "position"], 
    columns="stat_name", 
    values="stat_value", 
    aggfunc="first"
).fillna(0).reset_index()

# Only keep hitters (not pitchers)
pivot_df = pivot_df[pivot_df["position"].isin(["C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"])]

# Drop players with no at-bats
pivot_df = pivot_df[pivot_df.get("atBats", 0) > 0]

# (1) Normalize stats per game
pivot_df["hits_per_game"] = pivot_df.get("hits", 0) / 5
pivot_df["atBats_per_game"] = pivot_df.get("atBats", 0) / 5
pivot_df["strikeouts_per_game"] = pivot_df.get("strikeOuts", 0) / 5
pivot_df["walks_per_game"] = pivot_df.get("baseOnBalls", 0) / 5

# (2) Set features and target
X = pivot_df[["atBats_per_game"]]  # Feature
y = pivot_df["hits_per_game"]      # Target

# (3) Train Ridge Regression
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = Ridge(alpha=1.0)
model.fit(X_train, y_train)

# (4) Predict
pivot_df["predicted_hits_per_game"] = model.predict(X)

# (5) Clean up output
output_df = pivot_df[["player_name", "team", "position", "predicted_hits_per_game"]]
output_df = output_df.sort_values(by="predicted_hits_per_game", ascending=False)

# Save
output_df.to_csv("mlb_predicted_hits_per_game.csv", index=False)

print("✅ New predictions saved to mlb_predicted_hits_per_game.csv!")
print(output_df.head(20))
