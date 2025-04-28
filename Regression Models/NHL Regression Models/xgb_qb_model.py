import pandas as pd
import xgboost as xgb
from sklearn.linear_model import RidgeCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def run_xgb_meta_model(passing_df, team_offense_df, team_defense_df, weather_df):
    # Clean + preprocess
    passing_df['date'] = pd.to_datetime(passing_df['date'])
    passing_df['qbr'] = pd.to_numeric(passing_df['qbr'], errors='coerce')
    passing_df['rating'] = pd.to_numeric(passing_df['rating'], errors='coerce')
    passing_df[['completions', 'attempts']] = passing_df['completions/attempts'].str.split('/', expand=True).astype(float)
    passing_df[['sacks_taken', 'sack_yards']] = passing_df['sacks'].str.split('-', expand=True).astype(float)
    passing_df.drop(columns=['completions/attempts', 'sacks'], inplace=True)

    # Rolling averages
    rolling_features = ['completions', 'attempts', 'sacks_taken', 'sack_yards', 'qbr', 'rating']
    for col in rolling_features:
        passing_df[f"{col}_roll3"] = (
            passing_df.groupby("player_name")[col]
            .rolling(window=3, min_periods=1).mean()
            .reset_index(level=0, drop=True)
        )

    # Merge data sources
    combined = pd.merge(passing_df, team_offense_df[["game_id", "team", "passing_yards"]], on=["game_id", "team"], how="left")
    combined["yard_share"] = combined["yards"] / combined["passing_yards"]
    combined = pd.merge(combined, team_defense_df.drop(columns=["date", "opponent"], errors='ignore'), on=["game_id", "team"], how="left")
    combined = pd.merge(combined, weather_df.drop(columns=["date", "time_utc", "location", "precip_type", "conditions"], errors='ignore'), on="game_id", how="left")

    # Prepare model inputs
    ridge_X = combined[[f"{f}_roll3" for f in rolling_features]].fillna(0)
    rf_X = combined.drop(columns=["game_id", "player_id", "player_name", "team", "opponent", "yards"], errors="ignore")
    rf_X = rf_X.select_dtypes(include='number').fillna(0)
    y = combined["yards"]

    # Train/test split
    X_train_ridge, X_test_ridge, X_train_rf, X_test_rf, y_train, y_test = train_test_split(
        ridge_X, rf_X, y, test_size=0.2, random_state=42
    )

    # Train Ridge
    ridge = RidgeCV(alphas=[0.1, 1.0, 10.0])
    ridge.fit(X_train_ridge, y_train)
    ridge_train_preds = ridge.predict(X_train_ridge)
    ridge_test_preds = ridge.predict(X_test_ridge)

    # Train RF
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X_train_rf, y_train)
    rf_train_preds = rf.predict(X_train_rf)
    rf_test_preds = rf.predict(X_test_rf)

    # Blend with XGBoost
    meta_X_train = pd.DataFrame({"ridge": ridge_train_preds, "rf": rf_train_preds})
    meta_X_test = pd.DataFrame({"ridge": ridge_test_preds, "rf": rf_test_preds})
    meta_model = xgb.XGBRegressor(n_estimators=30, random_state=42, verbosity=0)
    meta_model.fit(meta_X_train, y_train)

    # Final output
    final_preds = meta_model.predict(meta_X_test)
    mse = mean_squared_error(y_test, final_preds)

    return {
        "meta_model": meta_model,
        "ridge_model": ridge,
        "rf_model": rf,
        "mse": mse
    }
