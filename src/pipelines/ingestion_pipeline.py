import logging
from pathlib import Path
import pandas as pd
from src.services.ingestion.readers import read_file
from src.services.ingestion.validators import validate_columns
from src.services.ingestion.cleaners import missing_and_duplicates
from src.services.analytics.sales_feature_engineering import calculate_financial_metrics
import json
from datetime import datetime


def run_ingestion_pipeline(file_path: str) -> dict:
    path = Path(file_path)

    df = read_file(file_path)
    df= validate_columns(df)
    df = missing_and_duplicates(df)
    df = calculate_financial_metrics(df)
   

    summary = {
        'total_records': len(df),
        'total_overall_revenue':float(df['total_revenue'].sum())

    } 
    logging.info(f"successfully processed {path.name}. Revenue: {summary['total_overall_revenue']:.2f}")

    result =  {
      'file_name': path.name,
      'status':'success',
      'summary': summary,
      'data': df.to_dict(orient='records')

   }

    try: 

       timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
       filename = f'json_uploads/processed_{path.name}_{timestamp}.json'

       with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4)

        print(f'pipeline for {path.name} finished and data saved to {filename}')

    except Exception as e:
       print(f'pipeline successful, json saving failed: {e}')


    
   
