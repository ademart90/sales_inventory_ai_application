import io
import pandas as pd
import logging
from pathlib import Path

def read_file(file_path: str):
    path = Path(file_path)
    

    if path.suffix.lower() == '.csv':
        logging.info(f'{path} uploaded')
        return pd.read_csv(path)

    elif path.suffix.lower() in ['.xls', '.xlsx']:
        logging.info(f'{path} uploaded')
        return pd.read_excel(path)

    else: 
        raise ValueError('UPLOAD CSV OR EXCEL FILE')