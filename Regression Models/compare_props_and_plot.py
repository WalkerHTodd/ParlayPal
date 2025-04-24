import pandas as pd
import requests
import matplotlib.pyplot as plt

API_KEY = "9d4cf8eed78f46d59612481a0eae9da0"
SEASON = "2024REG"

def fetch_player_props(season, week):
    url = f"https://api.sportsdata.io/v3/nfl/odds/json/PlayerPropsByWeek/{season}/{week}"
    headers = {"Ocp-Apim-Subscription-Key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    data = response.json()

    rows = []
    for prop in data:
        rows.append({
            "player": prop.get("Name"),
            "team": prop.get("Team"),
            "vegas_line": prop.get("OverUnder"),
            "sportsbook": prop.get("Sportsbook"),
            "stat_result": prop.get("StatResult"),
            "week": week
        })
    return pd.DataFrame(rows)

def compare_to_model(model_preds_df, season, weeks, actual_df):
    all_weeks_data = []

    for week in weeks:
        props_df = fetch_player_props(season, week)
        props_df = props_df.dropna(subset=["player", "vegas_line"])

        # ✅ Average props per player to eliminate duplicate dots
        avg_props = props_df.groupby(["player", "week"], as_index=False)["vegas_line"].mean()

        # Filter predictions for the same week
        week_model = model_preds_df[model_preds_df["week"] == week].copy()

        # Merge model + averaged props
        merged = pd.merge(week_model, avg_props, on=["player", "week"], how="inner")

        # Merge actuals
        actual_week = actual_df[actual_df["week"] == week].copy()
        actual_week = actual_week.rename(columns={"player_name": "player", "passing_yards": "actual"})
        merged = pd.merge(merged, actual_week[["player", "week", "actual"]], on=["player", "week"], how="left")

        all_weeks_data.append(merged)

    return pd.concat(all_weeks_data, ignore_index=True)

def plot_line_comparison(merged_df):
    weeks = merged_df["week"].unique()
    for week in sorted(weeks):
        df = merged_df[merged_df["week"] == week]
        x = df["player"]

        plt.figure(figsize=(14, 6))
        plt.plot(x, df["model_prediction"], marker='o', label="Model Prediction", color="green")
        plt.plot(x, df["vegas_line"], marker='o', label="Vegas Line", color="blue")
        plt.plot(x, df["actual"], marker='o', label="Actual", color="orange")

        plt.xticks(rotation=45, ha="right")
        plt.ylabel("Passing Yards")
        plt.title(f"Week {week} - Model vs Vegas vs Actual (Passing Yards)")
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    # Example predictions
    model_preds = pd.DataFrame({
        "player": ["Patrick Mahomes", "Josh Allen", "Joe Burrow", "Patrick Mahomes", "Josh Allen"],
        "model_prediction": [305.5, 278.0, 260.0, 295.0, 265.0],
        "week": [1, 1, 1, 2, 2]
    })

    # Example actual stats
    actual_passing = pd.DataFrame({
        "player_name": ["Patrick Mahomes", "Josh Allen", "Joe Burrow", "Patrick Mahomes", "Josh Allen"],
        "passing_yards": [320, 265, 270, 310, 270],
        "week": [1, 1, 1, 2, 2]
    })

    merged = compare_to_model(model_preds, SEASON, weeks=[1, 2], actual_df=actual_passing)
    print(merged[["player", "week", "model_prediction", "vegas_line", "actual"]])
    plot_line_comparison(merged)
