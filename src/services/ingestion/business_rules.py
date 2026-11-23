import pandas as pd
def business_rules_validation(df: pd.DataFrame) -> dict:
    sales_dates = pd.to_datetime(df['sale_date'], errors ='coerce')
    current_time = pd.Timestamp.now()

    #1. can quantity be negative?
    df['quantity'] = pd.to_numeric(df["quantity"], errors='coerce')
    negative_quantity_count = int((df['quantity'] < 0).sum())
    has_negative_quantity = negative_quantity_count > 0

    #2. can sale date  be in the future?
    future_date_count = int((sales_dates > current_time).sum())
    has_future_date = future_date_count > 0 

    business_rules_results = {
        "can quantity be negative?": {
            "answer": "yes" if has_negative_quantity else "no",
            "flagged_row_count": negative_quantity_count,
            "percentage":f"{(negative_quantity_count/len(df)) * 100:.2f}%"
        },

        "can sale date be in the future?": {
            "answer": "yes" if has_future_date else "no",
            "flagged_row_count": future_date_count,
            "percentage":f"{(future_date_count/len(df)) * 100:.2f}%"
        }
    }

    return business_rules_results