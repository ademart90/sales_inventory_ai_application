import pandas as pd 
import numpy as np
from sklearn.ensemble import IsolationForest

def detect_sales_z_score(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()
    df['rolling_mean'] = df.groupby('product_id')['quantity'].transform(lambda x: x.rolling(30, min_periods=1).mean())
    df['rolling_std'] = df.groupby('product_id')['quantity'].transform(lambda x: x.rolling(30, min_periods=1).std())
    df['z_score'] = (df['quantity'] - df['rolling_mean']) / df['rolling_std']
    sales_anomlies = df[df['z_score'].abs() > 2]

    return sales_anomlies.to_dict()

def detect_isolation_forest(df: pd.DataFrame)-> pd.DataFrame:
    df = df.copy()
    df['scaled_quantity'] = df.groupby('product_id')['quantity'].transform(
       lambda x: (x - x.mean()) / (x.std() if x.std() != 0 else 1) #feature needed for isolation forest
    )
    df['rolling_mean_14d'] = df.groupby('product_id')['quantity'].transform(
        lambda x: x.rolling(window=14, min_periods=1).mean()
    )

    df['sales_velocity_ratio'] = df['quantity'] / (
        df['rolling_mean_14d'] + 1
    )# another feature needed for isolation forest

    #get contamination via iqr
    total_outliers = 0
    grouped = df.groupby('product_id')['quantity']

    for product, group_data in grouped:
        if len(group_data) < 5:
            continue

        q1 = group_data.quantile(0.25)
        q3 = group_data.quantile(0.75)
        iqr = q3 - q1

        #standard outlier boundaries
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3  + (1.5 * iqr)

        product_outlier = group_data[
            (group_data < lower_bound) | (group_data > upper_bound)
        ]

        total_outliers += len(product_outlier)

    total_records = len(df)
    contamination_rate = total_outliers / total_records
    contamination_rate = float(np.clip(contamination_rate, 0.001, 0.05))
    contamination_rate

    feature_columns = ['sales_velocity_ratio', 'scaled_quantity', 'day_of_week', 'month_number']
    X = df[feature_columns]

    #initialising and fitting
    model = IsolationForest(contamination=contamination_rate, random_state=42)
    df['anomaly_label'] = model.fit_predict(X)
    anomalies_isolation  = df[df['anomaly_label'] == -1]

    return anomalies_isolation.to_dict()


        

        