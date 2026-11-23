from pathlib import Path
from datetime import datetime
from src.services.analytics.sales_analytics import get_average_sales_by_product, get_average_units_sold, get_sales_by_product, get_sales_summary, get_top_selling_product, get_total_revenue, get_total_units_sold, get_total_units_sold_by_product, current_sales, last_30_days, last_7_days, get_product_info
import json
import logging
from src.services.ingestion.readers import read_file
from src.services.ml.anomaly import detect_isolation_forest, detect_sales_z_score
from src.services.analytics.sales_feature_engineering import calculate_financial_metrics
from src.services.analytics.date_extraction import extract_date
def sales_ingestion_pipeline(file_path: str) -> dict:

    path = Path(file_path)

    df = read_file(file_path)
    df = calculate_financial_metrics(df)
    df = extract_date(df=df)
    df["sale_date"] = df["sale_date"].astype(str)


    summary = {
        'products_information': get_product_info(df),
        'total_overall_revenue' :float(df['total_revenue'].sum()),
        'total_quantity_sold': get_total_units_sold(df),
        'sales_by_product': get_sales_by_product(df),
        'top_selling_product': get_top_selling_product(df),
        'average_quantity_sold': get_average_units_sold(df),
        'total_qauntity_by_product': get_total_units_sold_by_product(df),
        'average_sales_by_product': get_average_sales_by_product(df),
        'sales_anomaly_detected_by_z_score': detect_sales_z_score(df),
        'sales_anomaly_detected_by_isolation forest': detect_isolation_forest(df),
        'last_recorded_sales':current_sales(df),
        'last_7_days':last_7_days(df),
        'last_30_days':last_30_days(df)
    }

    

    logging.info(f"successfully processed {path.name}. Revenue: {summary['total_overall_revenue']:.2f}")

    result =  {
          'file_name': path.name,
          'status':'success',
          'summary': summary
    }

    try: 
    
        
        filename = f'json_uploads/sales_summary.json'
    
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
    
            print(f'sales_summary for {path.name} finished and data saved to {filename}')
    
    except Exception as e:
        print(f'sales summary successful, json saving failed: {e}')

    df = df.to_csv(f'processed/sales_{path.name}')

def load_clean_sales(file_path: str) -> str:
    with open(file_path, 'r') as file:
        raw_text = file.read().replace(': NaN', ':null')
        data = json.loads(raw_text)

    summary = data.get('summary', {})

    # Remove duplicate section to save tokens
    summary.pop("total_qauntity_by_product", None)

    # Keep only essential columns from anomalies
    anomalies = summary.get("sales_anomaly_detected_by_z_score", {})
    keep_cols = ["sale_id", "product_id", "sale_date", "quantity", "closing_stock", "rolling_mean"]
    if anomalies:
        summary["sales_anomaly_detected_by_z_score"] = {
            k: v for k, v in anomalies.items() if k in keep_cols
        }

    # Compact JSON without whitespace
    return json.dumps(summary, separators=(',', ':'))






