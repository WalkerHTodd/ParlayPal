import requests
import pandas as pd
import time

# Step 1: Fetch all players basic info
players_url = "https://sports.core.api.espn.com/v3/sports/hockey/nhl/athletes?limit=20000"
response = requests.get(players_url)

if response.status_code != 200:
    raise Exception(f"Failed to fetch players list: {response.status_code}")

players_data = response.json().get("items", [])

player_list = []

# Step 2: Loop through players
for idx, player in enumerate(players_data):
    player_id = player.get("id")
    full_name = player.get("fullName")

    # Skip if no ID
    if not player_id:
        continue

    # Fetch full player info
    detail_url = f"https://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/athletes/{player_id}"
    detail_resp = requests.get(detail_url)

    if detail_resp.status_code != 200:
        print(f"❌ Failed detail fetch for {player_id} ({full_name})")
        continue

    detail_data = detail_resp.json()

    team_abbr = None
    position = None

    # Team Info (better way)
    try:
        if "team" in detail_data:
            team_obj = detail_data["team"]
            if "$ref" in team_obj:
                team_resp = requests.get(team_obj["$ref"])
                if team_resp.status_code == 200:
                    team_data = team_resp.json()
                    team_abbr = team_data.get("abbreviation")
    except Exception as e:
        print(f"⚠️ Error fetching team for {player_id}: {e}")

    # Position Info
    try:
        if "position" in detail_data:
            pos_obj = detail_data["position"]
            if "$ref" in pos_obj:
                pos_resp = requests.get(pos_obj["$ref"])
                if pos_resp.status_code == 200:
                    pos_data = pos_resp.json()
                    position = pos_data.get("abbreviation")
    except Exception as e:
        print(f"⚠️ Error fetching position for {player_id}: {e}")

    player_list.append({
        "id": player_id,
        "fullName": full_name,
        "team": team_abbr,
        "position": position
    })

    if idx % 50 == 0:
        print(f"✅ Processed {idx} players...")

# Step 3: Save to CSV
df = pd.DataFrame(player_list)
df.to_csv("espn_nhl_players_full.csv", index=False)

print("✅ Full ESPN NHL player list saved with team and position!")
