import pandas as pd
from sklearn.linear_model import LinearRegression

def run_meridian_model(df, media_cols, target):
    # Clean and prepare data
    df = df.copy()
    df = df[media_cols + [target]]
    df = df.apply(pd.to_numeric, errors='coerce')  # convert non-numeric to NaN
    df = df.dropna()  # drop rows with NaN

    X = df[media_cols]
    y = df[target]

    # Fit linear regression
    model = LinearRegression()
    model.fit(X, y)

    coefs = model.coef_
    total_contribution = X.mul(coefs).sum().sum()

    results = pd.DataFrame({
        "media_channel": media_cols,
        "coefficient": coefs,
        "estimated_roi": coefs / X.mean(),
        "normalized_contribution": X.mul(coefs).sum() / total_contribution
    }).round(3)

    return results

def recommend_budget_allocation(results, input_value, plan_type):
    results = results.copy()

    if plan_type == "Enter Revenue Target":
        avg_roi = results["estimated_roi"].mean()
        required_spend = input_value / avg_roi
        results["recommended_spend"] = results["estimated_roi"] / results["estimated_roi"].sum() * required_spend
    else:
        results["recommended_spend"] = results["estimated_roi"] / results["estimated_roi"].sum() * input_value

    scenarios = {
        "🟢 Aggressive Plan": results.copy().assign(
            recommended_spend=lambda df: df["estimated_roi"] ** 2 / (df["estimated_roi"] ** 2).sum() * input_value),
        "🟡 Balanced Plan": results.copy(),
        "🔵 Conservative Plan": results[results["estimated_roi"] > results["estimated_roi"].mean()].copy()
    }

    for label, df in scenarios.items():
        df["recommended_spend"] = df["recommended_spend"].round(2)

    results["recommended_spend"] = results["recommended_spend"].round(2)
    return results[["media_channel", "estimated_roi", "recommended_spend"]], scenarios
