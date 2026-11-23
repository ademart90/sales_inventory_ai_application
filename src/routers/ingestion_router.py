from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Depends
from src.services.upload_services import file_upload
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.ingestion_schema import IngestionRequest
from src.pipelines.ingestion_pipeline import run_ingestion_pipeline
import os



router = APIRouter()
FILE_DIRS = ["uploaded_files", "processed"]

for directory in FILE_DIRS:
    os.makedirs(directory, exist_ok=True)



@router.get('/files')
async def list_uploaded_files():
    try:

        file_list = []

        for directory in FILE_DIRS:
            if not os.path.exists(directory):
                continue

        

        for item in os.listdir(directory): #iterates through files in the folder
            path = os.path.join(directory, item) #gives the file path

            if os.path.isfile(path):# confirms if this is an available file
                file_list.append({
                    'folder':directory,
                    'file_name':item
                })
        return {'status': 'success',
                'files': file_list
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail = f"unexpected error occurred: {str(e)}"
        )


@router.post('/ingest')
async def ingestion_pipelne(
    payload: IngestionRequest,
    background_tasks: BackgroundTasks
):
    safe_filename = os.path.basename(payload.file_name)
    found_file_path = None

    if payload.folder:
        if payload.folder not in FILE_DIRS:
            raise HTTPException(
                status_code=400,
                detail=f'invalid folder, allowed folders: {FILE_DIRS}'
            )

        candidate_path = os.path.join(payload.folder, safe_filename)
        if os.path.isfile(candidate_path):
          found_file_path = candidate_path

    else:
        for directory in FILE_DIRS:
            candidate_path = os.path.join(directory, safe_filename)
            if os.path.isfile(candidate_path):
                found_file_path = candidate_path
                break

    if not found_file_path:
        raise HTTPException(
            status_code=404,
            detail=f"File '{safe_filename}' not found"
        )
    
    
    background_tasks.add_task(run_ingestion_pipeline, found_file_path)
    
    return {
        'status':'accepted',
        'message': f'ingestion pipeline scheduled for file: {safe_filename}',
        'path': found_file_path
    }

