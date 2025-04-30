
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def run_rf_model(passing_df, team_offense_df, team_defense_df, weather_df):
    # Clean and preprocess passing data
    passing_df['date'] = pd.to_datetime(passing_df['date'])
    passing_df['qbr'] = pd.to_numeric(passing_df['qbr'], errors='coerce')
    passing_df['rating'] = pd.to_numeric(passing_df['rating'], errors='coerce')
    passing_df[['completions', 'attempts']] = passing_df['completions/attempts'].str.split('/', expand=True).astype(float)
    passing_df[['sacks_taken', 'sack_yards']] = passing_df['sacks'].str.split('-', expand=True).astype(float)
    passing_df = passing_df.drop(columns=['completions/attempts', 'sacks'])

    # Merge with team offense to calculate share of output
    combined = pd.merge(passing_df, team_offense_df[['game_id', 'team', 'passing_yards']], on=['game_id', 'team'], how='left')
    combined['yard_share'] = combined['yards'] / combined['passing_yards']

    # Add team defense and weather
    combined = pd.merge(combined, team_defense_df.drop(columns=['date', 'opponent'], errors='ignore'), on=['game_id', 'team'], how='left')
    combined = pd.merge(combined, weather_df.drop(columns=['date', 'time_utc', 'location', 'precip_type', 'conditions'], errors='ignore'), on='game_id', how='left')

    # Drop non-numeric and ID columns
    X = combined.drop(columns=['game_id', 'player_id', 'player_name', 'team', 'opponent', 'yards'], errors='ignore')
    X = X.select_dtypes(include='number').fillna(0)
    y = combined['yards']

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)

    importances = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)

    return {
        "model": model,
        "mse": mse,
        "feature_importances": importances
    }
