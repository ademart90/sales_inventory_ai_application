from src.schemas.sales_schema import SalesRequest
from src.pipelines.sales_pipeline import sales_ingestion_pipeline
from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Depends
import os

router = APIRouter()
FILE_DIR = "processed"
os.makedirs(FILE_DIR, exist_ok=True)

@router.post('/sales_summary')
async def sales_summary(
    payload: SalesRequest,
    background_tasks: BackgroundTasks
):

    
    file_path = os.path.join(FILE_DIR, os.path.basename(payload.file_name))

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail = f" file not found in folder"
        )
    
    background_tasks.add_task(sales_ingestion_pipeline, file_path)
    
    return {
        'status':'accepted',
        'message': f'Sales summary scheduled for file: {payload.file_name}'

}
