import pandas as pd

def missing_and_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    
    df = df.drop_duplicates()

    df = df.dropna(subset=['product_id', 'product_name'])

    return df





