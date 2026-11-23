import pandas as pd
from datetime import datetime
import holidays

def extract_date(df: pd.DataFrame) -> pd.DataFrame:

    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df['day_number'] = df['sale_date'].dt.day
    df['day_name'] = df['sale_date'].dt.day_name()
    df['day_of_week'] = df ['sale_date'].dt.dayofweek
    df['week_number'] = df['sale_date'].dt.isocalendar().week
    df['is_weekend'] = df['sale_date'].dt.weekday >= 5
    df['month_number'] = df['sale_date'].dt.month
    df['month_name'] = df['sale_date'].dt.month_name()
    df['year'] = df['sale_date'].dt.year
    NG_holiday =  holidays.country_holidays('NG')
    df['is_holiday'] = df['sale_date'].apply(lambda x: x in NG_holiday)
    df['holiday_name'] = df['sale_date'].apply(lambda x: NG_holiday.get(x))

    return df