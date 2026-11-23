import pandas as pd
from src.schemas.inventory_schema import REQUIRED_COLUMNS, Inventory
from typing import List
from pydantic import ValidationError


def validate_columns(df: pd.DataFrame) -> pd.DataFrame:

    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_') #e.g product name becomes product_name

    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if  any(missing_cols):
        raise ValueError(f'missing required columns: {missing_cols}')

    return df

def convert_types(df: pd.DataFrame) -> List[Inventory]:
    prepared_records = []
    raw_records = df.to_dict(orient='records')

    for index, record in enumerate(raw_records):
        try:
            validated_columns = Inventory(**record)
            prepared_records.append(validated_columns)
        except ValidationError as e:
            print(f'row {index} skipped. conversion...')



