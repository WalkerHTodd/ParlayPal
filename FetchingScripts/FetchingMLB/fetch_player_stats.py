import pandas as pd
import requests
import time

# Load matched players
matched_players_df = pd.read_csv("mlb_playoff_players_ready.csv")

recent_stats = []

def fetch_recent_games(player_id):
    url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}/statistics?season=2024&seasontype=2"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        splits = data.get("splits", {}).get("categories", [])
        return splits
    else:
        print(f"❌ Failed to fetch stats for player {player_id}")
        return []

for idx, row in matched_players_df.iterrows():
    player_id = row["id"]
    player_name = row["fullName"]
    team = row["team"]
    position = row["position"]

    stats = fetch_recent_games(player_id)
    if stats:
        for stat_block in stats:
            stat_name = stat_block.get("name")
            for stat in stat_block.get("stats", []):
                recent_stats.append({
                    "player_id": player_id,
                    "player_name": player_name,
                    "team": team,
                    "position": position,
                    "category": stat_name,
                    "stat_name": stat.get("name"),
                    "stat_value": stat.get("value")
                })

    if idx % 20 == 0:
        print(f"✅ Processed {idx} players...")
    # time.sleep(0.5)  # be kind to server

# Save all recent stats
if recent_stats:
    stats_df = pd.DataFrame(recent_stats)
    stats_df.to_csv("mlb_recent_player_stats.csv", index=False)
    print("✅ Saved recent player stats to mlb_recent_player_stats.csv")
else:
    print("❌ No stats found.")
