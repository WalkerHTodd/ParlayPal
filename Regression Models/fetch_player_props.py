import requests
import pandas as pd

API_KEY = "9d4cf8eed78f46d59612481a0eae9da0"
SEASON = "2024REG"
WEEK = 1

def fetch_player_props(season, week):
    url = f"https://api.sportsdata.io/v3/nfl/odds/json/PlayerPropsByWeek/{season}/{week}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    data = response.json()
    print(f"Fetched {len(data)} props")
    if len(data) == 0:
        print("⚠️ Warning: No props returned by the API.")
        rows = []
    for prop in data:
        rows.append({
            "player": prop["PlayerName"],
            "team": prop["Team"],
            "position": prop["Position"],
            "stat_type": prop["StatType"],
            "line": prop["Value"],
            "over_odds": prop["OverOdds"],
            "under_odds": prop["UnderOdds"],
            "sportsbook": prop["Sportsbook"],
            "game": f"{prop['AwayTeam']} @ {prop['HomeTeam']}"
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = fetch_player_props(SEASON, WEEK)
    print(df[df["stat_type"].str.contains("Passing Yards", case=False)].head())
