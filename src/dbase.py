import os
import sys
import subprocess
import pandas as pd
from sqlalchemy import text, create_engine, inspect
from db_faker import seed_data

def etl():

    DATABASE_URL = 'sqlite:///./uploaded_files/.test_database.db'
    seed_data()
    engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})

    # Folder to store the exported CSVs
    OUTPUT_DIR = './processed'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Get all table names from the SQLite database
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    tables = {}

    with engine.connect() as conn:
        for table in table_names:
            # Skip SQLite's internal sequence table if present
            if table == 'sqlite_sequence':
                continue

            # Read each table into a DataFrame
            df = pd.read_sql(text(f'SELECT * FROM "{table}"'), conn)

            # 2. Convert and save each individual table to its own CSV first
            individual_csv_path = os.path.join(OUTPUT_DIR, f'{table}.csv')
            df.to_csv(individual_csv_path, index=False)
            print(f'Exported: {individual_csv_path}')

            # Optional: Track which table each row originally came from
            tables[table] = df

            # 2. Merge sales and inventory on ['sale_id', 'product_id']
    if 'sales' in tables and 'inventory' in tables:
        sales_df = tables['sales']
        inventory_df = tables['inventory']

        # Ensure join keys have matching data types before merging
        for col in ['sale_id', 'product_id']:
            sales_df[col] = sales_df[col].astype(str)
            inventory_df[col] = inventory_df[col].astype(str)

        combined_df = pd.merge(
            sales_df,
            inventory_df,
            on=['sale_id', 'product_id'],
            how = 'inner'

        )
    if 'products' in tables:
        product_df = tables['products']
        product_df['product_id'] = product_df['product_id'].astype(str)

        joined_df = pd.merge(
            combined_df,
            product_df,
            on='product_id',
            how='left'
        )


    joined_df.to_csv('./processed/joined_df.csv', index=False)
    print(f'Successfully merged all three tables')

