from src.schemas.inventory_schema import InventoryRequest
from src.pipelines.inventory_pipeline import inventory_ingestion_pipeline
from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Depends
import os

router = APIRouter()
FILE_DIR = "processed"
os.makedirs(FILE_DIR, exist_ok=True)

@router.post('/inventory_summary')
async def inventory_summary(
    payload: InventoryRequest,
    background_tasks: BackgroundTasks
):

    
    file_path = os.path.join(FILE_DIR, os.path.basename(payload.file_name))

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=404,
            detail = f" file not found in folder"
        )
    
    background_tasks.add_task(inventory_ingestion_pipeline, file_path)
    
    return {
        'status':'accepted',
        'message': f'Inventory summary scheduled for file: {payload.file_name}'

}
