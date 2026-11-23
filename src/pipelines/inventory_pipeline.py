import pandas as pd 
import logging
from pathlib import Path
from src.services.analytics.inventory_analytics import get_current_inventory, get_products_with_most_stock, get_sold_inventory, get_total_inventory_added
from src.services.ingestion.readers import read_file
from src.services.analytics.inventory_feature_engineering import calculate_inventory_metrics
import json
from datetime import datetime

def inventory_ingestion_pipeline(file_path: str) -> dict:

    path = Path(file_path)

    df = read_file(file_path)
    df = calculate_inventory_metrics(df)

    summary =  {
        'current_inventory': get_current_inventory(df),
        'product_by_stock':get_products_with_most_stock(df),
        'total_restocked_units_by_product': get_total_inventory_added(df),
        'inventory_sold_by_product': get_sold_inventory(df)
    }
        

    logging.info(f"successfully processed {path.name}.")

    result =  {
          'file_name': path.name,
          'status':'success',
          'summary': summary
    }

    try: 
    
        
        filename = f'json_uploads/inventory_summary.json'
    
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)
    
            print(f'inventory_summary for {path.name} finished and data saved to {filename}')
    
    except Exception as e:
        print(f'inventory summary successful, json saving failed: {e}')

    df = df.to_csv(f'processed/inventory_{path.name}')

def load_clean_inventory(file_path: str) -> str:
    with open(file_path, 'r') as file:
            raw_text = file.read().replace(': NaN', ':null')
            data = json.loads(raw_text)

    summary = data.get('summary', {})

    
    return json.dumps(summary, separators=(',', ':'))


