
import pandas as pd
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def prepare_data(passing_df):
    # Clean and preprocess the passing data
    passing_df['date'] = pd.to_datetime(passing_df['date'])
    passing_df[['completions', 'attempts']] = passing_df['completions/attempts'].str.split('/', expand=True).astype(float)
    passing_df[['sacks_taken', 'sack_yards']] = passing_df['sacks'].str.split('-', expand=True).astype(float)
    passing_df['qbr'] = pd.to_numeric(passing_df['qbr'], errors='coerce')
    passing_df['rating'] = pd.to_numeric(passing_df['rating'], errors='coerce')
    passing_df = passing_df.drop(columns=['completions/attempts', 'sacks'])

    # Sort for rolling calculations
    passing_df = passing_df.sort_values(by=['player_name', 'date'])

    # Compute rolling averages
    rolling_features = ['completions', 'attempts', 'sacks_taken', 'sack_yards', 'qbr', 'rating']
    for feature in rolling_features:
        passing_df[f"{feature}_roll3"] = (
            passing_df.groupby("player_name")[feature]
            .rolling(window=3, min_periods=1).mean()
            .reset_index(level=0, drop=True)
        )
    
    passing_df = passing_df.dropna(subset=['yards'])
    return passing_df, [f"{f}_roll3" for f in rolling_features]

def run_ridge_model(passing_df):
    passing_df, features = prepare_data(passing_df)

    X = passing_df[features].fillna(0)
    y = passing_df["yards"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    ridge = RidgeCV(alphas=[0.1, 1.0, 10.0])
    ridge.fit(X_train, y_train)

    y_pred = ridge.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    coefficients = pd.Series(ridge.coef_, index=features).sort_values(ascending=False)

    return {
        "model": ridge,
        "mse": mse,
        "coefficients": coefficients
    }
