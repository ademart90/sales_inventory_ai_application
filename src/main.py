from fastapi import FastAPI
from src.routers import upload_router, ingestion_router, sales_router, inventory_router, report_router
from src.utils.logger import logger_setup 
from contextlib import asynccontextmanager
from src.pipelines.sales_pipeline import sales_ingestion_pipeline
from src.pipelines.inventory_pipeline import inventory_ingestion_pipeline
import os
from src.dbase import etl

etl()

app = FastAPI(docs_url='/docs')

FILE_DIR ='processed'

@asynccontextmanager
async def lifespan(app: FastAPI):
    file_path = os.path.join(FILE_DIR, 'joined_df.csv')
    sales_ingestion_pipeline(file_path=file_path)
    inventory_ingestion_pipeline(file_path=file_path)
    print('sales and inventory jsons up to date')
    yield

app= FastAPI(lifespan=lifespan)


logger_setup()


app.include_router(upload_router.router, tags=['Upload File'])
app.include_router(ingestion_router.router, tags=['Check & Ingest Data Folder'])
app.include_router(sales_router.router, tags=['Sales Summary'])
app.include_router(inventory_router.router, tags=['Inventory Summary'])
app.include_router(report_router.router, tags=['Generate Report with AI'])