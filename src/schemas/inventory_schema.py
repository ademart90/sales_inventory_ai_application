from datetime import datetime
from pydantic import BaseModel, Field

REQUIRED_COLUMNS = {
    'product_id', 'product_name', 'category',
    'quantity', 'inventory_id', 'sale_id', 'opening_stock',
    'restocked_units', 'closing_stock', 'sale_date', 'selling_price',
    'unit_cost' 
}

class Inventory(BaseModel):
    product_id: str = Field(..., min_lenght=1)
    sale_id: str = Field(..., min_lenght=1)
    inventory_id: str = Field(..., min_lenght=1)
    product_name: str = Field(..., min_lenght=1)
    category: str = Field(default='uncategorized')
    quantity_sold: int = Field(..., ge=0)
    sales_date: datetime

class InventoryRequest(BaseModel):
    file_name: str
