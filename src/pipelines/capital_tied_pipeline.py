from typing import Literal, Optional
from langchain_core.tools import tool
from ..dbase import engine
from sqlalchemy import text
import json
import duckdb

def calculate_capital_tied_to_inventory():
        conn = duckdb.connect('./uploaded_files/.test_database.db')
        
        query = ('''
            SELECT
                p.product_name,
                p.unit_cost,
                LAST(s.quantity) AS quantity_sold,
                LAST (i.opening_stock) AS opening_stock_quantity,
                LAST(i.restocked_units) AS restocked_unit,
                LAST(i.closing_stock) AS closing_stock_quantity,
                LAST(i.closing_stock) * LAST(p.unit_cost) AS capital_tied

            FROM 
                products p
            LEFT JOIN
                inventory i ON p.product_id = i.product_id

            LEFT JOIN
                sales s ON i.sale_id = s.sale_id

            GROUP BY 
                p.product_name,
                p.unit_cost;
        
    ''')
        df = conn.execute(query).df()
        df.to_csv('capital_tied_to_inventory.csv', index=False)

        filename = f'json_uploads/capital_tied_to_inventory.json'
        
        df.to_json(filename, orient='records', indent=4)
        print(f'file succesfully saved')

if __name__ == '__main__':
        calculate_capital_tied_to_inventory()
             

