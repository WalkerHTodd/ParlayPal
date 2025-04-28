# fetch_nhl_recent_playoff_stats.py
import requests
import pandas as pd
import time

# Load the matched playoff players
players_df = pd.read_csv("nhl_playoff_players_ready.csv")

all_stats = []

# For each player, get their last 5 games
for idx, row in players_df.iterrows():
    player_id = row['player_id']
    player_name = row['player_name']
    team = row['team']
    opponent = row['opponent']
    game_date = row['game_date']
    event_id = row['event_id']
    
    url = f"https://sports.core.api.espn.com/v2/sports/hockey/nhl/athletes/{player_id}/stats?lang=en&region=us"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Look for recent games stats if available
            splits = data.get('splits', {}).get('categories', [])
            stat_row = {
                "player_id": player_id,
                "player_name": player_name,
                "team": team,
                "opponent": opponent,
                "game_date": game_date,
                "event_id": event_id
            }
            
            for category in splits:
                for stat in category.get('stats', []):
                    name = stat.get('name')
                    value = stat.get('value')
                    stat_row[name] = value
            
            all_stats.append(stat_row)
        
        else:
            print(f"❌ Failed fetching stats for {player_name} ({player_id}) - Status {response.status_code}")
        
        if idx % 25 == 0:
            print(f"✅ Processed {idx} players...")
        
        time.sleep(0.5)  # Be nice to the server

    except Exception as e:
        print(f"❌ Error fetching stats for {player_name}: {e}")

# Save it
if all_stats:
    stats_df = pd.DataFrame(all_stats)
    stats_df.to_csv("nhl_playoff_players_stats.csv", index=False)
    print("✅ Saved player stats to nhl_playoff_players_stats.csv!")
else:
    print("❌ No player stats found.")
