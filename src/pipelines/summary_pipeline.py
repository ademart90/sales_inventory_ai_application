from langchain_core.tools import tool
from ..dbase import engine
import json
import duckdb

def sales_summary():
    conn = duckdb.connect('./uploaded_files/.test_database.db')
    query = ('''
            SELECT
                p.product_name,
                p.selling_price,
                SUM(s.quantity) AS total_quantity_sold,
                SUM(s.quantity * p.selling_price) AS total_revenue
            FROM 
                products p
            LEFT JOIN
                sales s ON p.product_id = s.product_id
            GROUP BY
                p.product_name,
                p.selling_price;
                        
                    
    ''')

    df = conn.execute(query).df()
    df.to_csv('summary.csv', index=False)
    
    filename = f'json_uploads/summary.json'
            
    df.to_json(filename, orient='records', indent=4)
    print(f' {filename} file succesfully saved')



if __name__ == '__main__':
        sales_summary()

    