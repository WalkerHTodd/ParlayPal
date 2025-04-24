import pandas as pd
from ridge_qb_model import run_ridge_model
from rf_qb_model import run_rf_model
from xgb_qb_model import run_xgb_meta_model  # Layer 3 added

def main():
    print("=== Running Ridge Regression Model (QB Passing Yards) ===")
    try:
        passing_df = pd.read_csv("../Data/OriginalData/passing.csv")
    except FileNotFoundError:
        print("Error: passing.csv not found. Make sure the file is in the Data/OriginalData folder.")
        return

    ridge_results = run_ridge_model(passing_df)
    print(f"Ridge MSE: {ridge_results['mse']:.2f}")
    print("Top Ridge Feature Coefficients:")
    print(ridge_results['coefficients'])

    print("\n=== Running Random Forest Model (Layer 2 - Team Stats + Share) ===")
    try:
        team_offense = pd.read_csv("../Data/OriginalData/team_offense.csv")
        team_defense = pd.read_csv("../Data/OriginalData/team_defense.csv")
        weather = pd.read_csv("../Data/OriginalData/nfl_2024_weather.csv")
    except FileNotFoundError:
        print("Error: One or more team/weather data files are missing.")
        return

    rf_results = run_rf_model(passing_df, team_offense, team_defense, weather)
    print(f"Random Forest MSE: {rf_results['mse']:.2f}")
    print("Top RF Feature Importances:")
    print(rf_results['feature_importances'].head(10))

    print("\n=== Running XGBoost Meta Model (Layer 3 - Blending Ridge & RF) ===")
    xgb_results = run_xgb_meta_model(passing_df, team_offense, team_defense, weather)
    print(f"XGBoost Meta Model MSE: {xgb_results['mse']:.2f}")

if __name__ == "__main__":
    main()
