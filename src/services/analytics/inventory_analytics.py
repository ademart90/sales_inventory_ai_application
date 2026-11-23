import pandas as pd
def get_current_inventory(df: pd.DataFrame) -> pd.DataFrame:
    last_sales_day_df  = df[df['sale_date'] == df['sale_date'].max()] #this filters out the last sales date
    return (last_sales_day_df.groupby(['product_name', 'product_id'], as_index=False)
                        .agg(
                                opening_stock =('opening_stock', 'first'), 
                                restocked_units =('restocked_units',  'sum'),
                                closing_stock=('closing_stock', 'last'),
                                quantity_sold=('quantity', 'sum')
                            )

            ).to_dict()

def get_products_with_most_stock(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby('product_name')['closing_stock']
            .last()
            .sort_values(ascending=False)
            .reset_index()
    ).to_dict()

def get_total_inventory_added(df: pd.DataFrame) -> pd.DataFrame:
    return (df.groupby('product_name')['restocked_units']
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        ).to_dict()


def get_sold_inventory(df: pd.DataFrame) -> pd.DataFrame:
    df['inventory_sold'] = df['quantity']*df['unit_cost']
    return (df.groupby('product_name')['inventory_sold']
            .sum()
            .sort_values(ascending=False)
            .reset_index()

    ).to_dict()




