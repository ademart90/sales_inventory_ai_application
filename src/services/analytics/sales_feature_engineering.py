import pandas as pd

def calculate_financial_metrics(df: pd.DataFrame) -> pd.DataFrame:

    #feature engineering and calculation of financial metrics

    df["total_revenue"] = df["quantity"] * df["selling_price"] 
    df["total_cost"] = df["quantity"] * df["unit_cost"]
    df["profit"] = df["total_revenue"] - df["total_cost"]
    df["profit_margin_%"] = (df["profit"] / df["total_revenue"]) * 100

    return df 



