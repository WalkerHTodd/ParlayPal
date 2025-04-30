import requests
import pandas as pd
import time

# URL to get all MLB players
players_url = "https://sports.core.api.espn.com/v3/sports/baseball/mlb/athletes?limit=20000"
response = requests.get(players_url)

if response.status_code != 200:
    raise Exception(f"Failed to fetch players: {response.status_code}")

players_data = response.json().get("items", [])

player_list = []

# Loop through ALL players
for idx, player in enumerate(players_data):
    player_id = player.get("id")
    full_name = player.get("fullName")
    position = None
    team_abbr = None
    status = None

    # Fetch detailed info for team, position, and status
    detail_url = f"https://sports.core.api.espn.com/v2/sports/baseball/leagues/mlb/athletes/{player_id}"
    detail_resp = requests.get(detail_url)

    if detail_resp.status_code == 200:
        detail_data = detail_resp.json()

        try:
            if "team" in detail_data and "$ref" in detail_data["team"]:
                team_resp = requests.get(detail_data["team"]["$ref"])
                if team_resp.status_code == 200:
                    team_data = team_resp.json()
                    team_abbr = team_data.get("abbreviation")
        except:
            pass
        
        try:
            if "position" in detail_data and "$ref" in detail_data["position"]:
                pos_resp = requests.get(detail_data["position"]["$ref"])
                if pos_resp.status_code == 200:
                    pos_data = pos_resp.json()
                    position = pos_data.get("abbreviation")
        except:
            pass

        try:
            if "status" in detail_data:
                status = detail_data["status"].get("name")  # Example: "Active", "Inactive", "Free Agent"
        except:
            pass

    player_list.append({
        "id": player_id,
        "fullName": full_name,
        "team": team_abbr,
        "position": position,
        "status": status
    })

    if idx % 50 == 0:
        print(f"✅ Processed {idx} players...")

    # Optional: time.sleep(0.2)  # slow down if you get rate-limited (not strictly needed unless ESPN blocks)

# Save to CSV
df = pd.DataFrame(player_list)
df = df.dropna(subset=["team"])  # Only keep players who have a team
df.to_csv("espn_mlb_players_full.csv", index=False)

print(f"✅ Full player list complete — saved {len(df)} players to espn_mlb_players_full.csv!")
