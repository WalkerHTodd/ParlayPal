import requests
import pandas as pd
from datetime import datetime

# Fetch TODAY'S games
today = datetime.now().strftime("%Y%m%d")  # ⚡ ESPN expects YYYYMMDD (no hyphens)

url = f"https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard?dates={today}"
response = requests.get(url)

games = []

if response.status_code == 200:
    data = response.json()
    events = data.get("events", [])

    for event in events:
        competitions = event.get("competitions", [])
        if competitions:
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            if len(competitors) == 2:
                home_team = competitors[0]["team"]["abbreviation"]
                away_team = competitors[1]["team"]["abbreviation"]
                games.append({
                    "date": today,
                    "home_team": home_team,
                    "away_team": away_team
                })
else:
    print(f"❌ Failed to fetch games (status {response.status_code})")

# Save games
if games:
    games_df = pd.DataFrame(games)
    games_df.to_csv("../../Data/MLBData/mlb_upcoming_games.csv", index=False)
    print(f"✅ Saved {len(games)} upcoming MLB games to mlb_upcoming_games.csv")
else:
    print("❌ No games found today.")
