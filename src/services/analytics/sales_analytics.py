import pandas as pd



def get_product_info(df: pd.DataFrame) -> dict:
    product_catalog = (
        df[['product_id', 'product_name', 'category', 'unit_cost', 'selling_price']]
        .drop_duplicates(subset=['product_id'])
        .assign(
            unit_cost=lambda x: x['unit_cost'].round(2),
            selling_price=lambda x: x['selling_price'].round(2)
        )
        .set_index('product_name')
    )
    return product_catalog.to_dict(orient='index')

def get_total_revenue(df: pd.DataFrame) -> float:
    return df['total_revenue'].sum() #returns total revenue 

def get_total_units_sold(df: pd.DataFrame) -> int: #total quantity sold overall
    return int(df['quantity'].sum())

def get_average_units_sold(df: pd.DataFrame) -> float:
    return df['quantity'].mean()

def get_total_units_sold_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby('product_name', as_index=False)
        .agg(
            units_sold=('quantity', 'sum')
        )
    ).to_dict()

def get_average_sales_by_product(df:pd.DataFrame) -> pd.DataFrame:
    return(
        df.groupby('product_name', as_index=False)
        .agg(
            units_sold=('quantity', 'mean')
        )
    ).to_dict()

def get_sales_by_product(df: pd.DataFrame) -> pd.DataFrame: #sales by product
    return (
        df.groupby('product_name', as_index=False)
        .agg(
            units_sold=('quantity', 'sum'),
            revenue=('total_revenue', 'sum')
        )    
     ).to_dict()

def get_top_selling_product(df: pd.DataFrame) -> pd.DataFrame:
    top_products = (
        df.groupby('product_name', as_index=False)['quantity']
        .sum()
        .sort_values(by= 'quantity', ascending=False)
        .head(10)
    )
    return top_products.to_dict()

def get_sales_summary(df: pd.DataFrame) -> dict:
    return{
        'total_revenue': get_total_revenue(df),
        'total_units_sold': get_total_units_sold(df),
        'average_units_sold':get_average_units_sold(df)
    }

def _summarize_window(df: pd.DataFrame, days: int) -> dict:
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    end_date = df['sale_date'].max()
    start_date = end_date - pd.Timedelta(days=days - 1)
    
    window_df = df[df['sale_date'] >= start_date].sort_values(['sale_date', 'sale_id'])
    window_df['revenue'] = window_df['quantity'] * window_df['selling_price']
    window_df['profit'] = (window_df['selling_price'] - window_df['unit_cost']) * window_df['quantity']


    products = (
        window_df
        .groupby(['product_name', 'product_id'], as_index=False)
        .agg(
            opening_stock=('opening_stock', 'first'),
            restocked_units=('restocked_units', 'sum'),
            closing_stock=('closing_stock', 'last'),
            quantity_sold=('quantity', 'sum'),
            total_revenue=('revenue', 'sum'),
            profit=('profit', 'sum')
        )
    ).to_dict(orient="records")

    return {
        "period_days": days,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "products": products
    }

def current_sales(df: pd.DataFrame) -> dict:
    return _summarize_window(df, days=1)

def last_7_days(df: pd.DataFrame) -> dict:
    return _summarize_window(df, days=7)

def last_30_days(df: pd.DataFrame) -> dict:
    return _summarize_window(df, days=30)

