import os
import sys 
import random 
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from faker import Faker
import numpy as np

DATABASE_URL = "sqlite:///uploaded_files/.test_database.db"
engine = create_engine(DATABASE_URL, echo = False)
SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key = True, index=True)
    product_name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, unique=False)
    unit_cost = Column(Float, nullable=False)
    selling_price =Column(Float, nullable=False)
    inventory_history = relationship("Inventory", back_populates="product")



class Suppliers(Base):
    __tablename__ = "suppliers"
    supplier_id = Column(Integer, primary_key = True, index=True)
    supplier_name = Column(String, unique=True, nullable=False)
    lead_time_days = Column(Integer, unique=False, nullable=False)

class Sales(Base):
    __tablename__ = "sales"
    sale_id  =  Column(Integer, primary_key =True, index =True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    sale_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, default = 1)
    inventory_store = relationship("Inventory", back_populates="sale")

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    sale_id = Column(Integer, ForeignKey("sales.sale_id"), nullable=False)
    date = Column(DateTime, nullable=False)
    opening_stock = Column(Integer, default = 0, nullable=False)
    restocked_units = Column(Integer,  default = 0, nullable = False)
    closing_stock= Column(Integer, default = 0, nullable=False)
    product = relationship("Product", back_populates="inventory_history")
    sale = relationship("Sales", back_populates="inventory_store")

def seed_data():
    os.makedirs("uploaded_files", exist_ok=True)  
    print("Initializing databse and tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db=SessionLocal()
    fake = Faker()
    try:
        if db.query(Product).first():
            print("Database alrady contains data. Seeding skipped")
            return
        print("Generating mock products, inventory, suppliers and sales...")

        #create product table
        p_name = ["mouse", "keyboard", "ergonomics chair", "laptops", "fan"]
        categories = {"mouse":"electronics", "keyboard":"electronics", "ergonomics chair":"accessories", "laptops":"electronics", "fan":"electronics"}

        products = []
        for p in p_name:
            unit_cost=round(random.uniform(10, 100), 2)
            markup = random.uniform(0.15, 0.60)
            selling_price = round(unit_cost*(1 + markup), 2)

            product = Product(
                product_name = p,
                category = categories[p],
                unit_cost = unit_cost,
                selling_price = selling_price
            )
            db.add(product)
            products.append(product)

        db.flush()

        #create supplier table
        suppliers = []
        for _ in range(15):
            supplier = Suppliers(
                supplier_name = fake.user_name(),
                lead_time_days = random.randint(1, 11)
            )
            db.add(supplier)
            suppliers.append(supplier)

        db.flush()

        #create sales table
        dates = []
        start_date = datetime(2025, 8, 1).date()
        end_date =  datetime.today().date()
        
        while start_date  <= end_date:
            sales_today = np.random.randint(5, 21)
            dates.extend([start_date] * sales_today)
            start_date += timedelta(days=1)

        sales = []
        for current_date in dates:
            sale = Sales(
                product_id = random.choice(products).product_id,
                sale_date = current_date,
                quantity = random.randint(1, 5)
            )
            db.add(sale)
            sales.append(sale)
        db.flush()
# create inventory table 
        inventory = []
        sales_list = db.query(Sales).all()
    
        inventory_tracker = {sale.product_id: 300 for sale in sales_list}

        for sale in sales_list:
            
            opening_stock = inventory_tracker[sale.product_id]

            inventory_date = sale.sale_date

            restocked =random.choice([10, 20, 30]) if random.random() < 0.2 else 0

            total_available = opening_stock + restocked
            
            sold = sale.quantity


            closing_stock = total_available - sold

            daily_log = Inventory(
                product_id = sale.product_id,
                sale_id = sale.sale_id,
                date = inventory_date,
                opening_stock = opening_stock,
                restocked_units = restocked,
                closing_stock = closing_stock
            )

            inventory_tracker[sale.product_id] = closing_stock
            db.add(daily_log)
            inventory.append(daily_log)
        db.flush()

        db.commit()
        print("Finally!, Database populated and ready.")

    except Exception as e:
        print(f"error during seeding: {e}")
        db.rollback()
    finally:
        db.close()    

if __name__ == "__main__":
    seed_data()







