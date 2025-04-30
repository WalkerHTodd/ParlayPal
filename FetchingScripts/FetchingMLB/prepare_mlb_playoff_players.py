import pandas as pd

# Load players
players_df = pd.read_csv("../../Data/MLBData/espn_mlb_players_full.csv")
print(f"✅ Loaded {len(players_df)} players.")

# ❗ Only keep players who are Active
players_df = players_df[players_df["status"] == "Active"]

# Load upcoming games
games_df = pd.read_csv("../../Data/MLBData/mlb_upcoming_games.csv")
print(f"✅ Loaded {len(games_df)} upcoming games.")

# Make sure team abbreviations are uppercase and no NaNs
players_df = players_df.dropna(subset=["team"])
players_df["team"] = players_df["team"].astype(str).str.upper()
games_df["home_team"] = games_df["home_team"].astype(str).str.upper()
games_df["away_team"] = games_df["away_team"].astype(str).str.upper()

# Get list of teams playing
teams_playing = set(games_df["home_team"].tolist() + games_df["away_team"].tolist())
print(f"✅ Teams playing: {teams_playing}")

# Filter players who are on teams playing
playoff_players_df = players_df[players_df["team"].isin(teams_playing)]

print(f"✅ Matched {len(playoff_players_df)} active players to upcoming games!")

# Save
if not playoff_players_df.empty:
    playoff_players_df.to_csv("../../Data/MLBData/mlb_playoff_players_ready.csv", index=False)
    print("✅ Saved matched active players to mlb_playoff_players_ready.csv")
else:
    print("❌ No active players matched.")
