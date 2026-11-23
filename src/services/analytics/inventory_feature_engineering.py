import pandas as pd

def calculate_inventory_metrics(df: pd.DataFrame) -> pd.DataFrame:

#calculation and feature engineering of inventory metrics

    df['sales_volume'] = df['opening_stock'] + df['restocked_units'] - df['closing_stock'] #sales_volume calculation
    df['average_stock'] = (df['opening_stock'] + df['closing_stock'])/2 #average_stock calculation
    df['inventory_turnover_ratio'] = df['sales_volume'] / df['average_stock'] #inventory_turnover_ratio calculation
    df['depletion_rate'] = df['opening_stock'] / df['closing_stock'] #depletion_rate

    return df