import pandas as pd

# Load player data
players_df = pd.read_csv("espn_nhl_players_with_team.csv")

# Load upcoming games
games_df = pd.read_csv("nhl_upcoming_playoff_games.csv")

# Quick check
print(f"✅ Loaded {len(players_df)} players")
print(f"✅ Loaded {len(games_df)} upcoming games")


# Make sure team abbreviations are all uppercase
players_df["team"] = players_df["team"].astype(str).str.upper()
print(f"✅ Found {len(players_df['team'].unique())} unique teams in players data")
print(f"✅ Teams: {players_df['team'].unique()}")
games_df["team1_abbr"] = games_df["team1_abbr"].astype(str).str.upper()
games_df["team2_abbr"] = games_df["team2_abbr"].astype(str).str.upper()


# List of playoff teams
playoff_teams = set(games_df["team1_abbr"]).union(set(games_df["team2_abbr"]))
print(f"✅ Found {len(playoff_teams)} playoff teams")
print(f"✅ Playoff teams: {playoff_teams}")

# Filter players who belong to playoff teams
playoff_players_df = players_df[players_df["team"].isin(playoff_teams)]

print(f"✅ Found {len(playoff_players_df)} players from playoff teams")

# Now, map each player to their game info
rows = []
for idx, player in playoff_players_df.iterrows():
    player_team = player["team"]
    player_id = player["id"]
    player_name = player["fullName"]
    
    # Find all games this player's team is involved in
    team_games = games_df[(games_df["home_team"] == player_team) | (games_df["away_team"] == player_team)]
    
    for _, game in team_games.iterrows():
        opponent = game["away_team"] if game["home_team"] == player_team else game["home_team"]
        rows.append({
            "player_id": player_id,
            "player_name": player_name,
            "team": player_team,
            "opponent": opponent,
            "game_date": game["game_date"],
            "event_id": game["event_id"]
        })

# Save results
if rows:
    matched_df = pd.DataFrame(rows)
    matched_df.to_csv("nhl_playoff_players_ready.csv", index=False)
    print(f"✅ Saved {len(matched_df)} matched players to nhl_playoff_players_ready.csv!")
else:
    print("❌ No matched players found.")
