from fastapi import FastAPI, APIRouter, UploadFile, HTTPException, BackgroundTasks, File, Depends
from src.services.upload_services import file_upload
import logging
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()

@router.post('/upload data')
async def save_csv(
    file: UploadFile = File(...),
    
):

    extensions = ('.csv', '.xlsx', '.db', '.xls' )
    if not file.filename.endswith(extensions): 
        logging.warning(f"{file.filename} - unsorported file format")
        raise HTTPException(status_code=400, detail ="upload csv file format")


    file_path = await file_upload(file)

    
    

    return {
        'filename': file.filename,
        'status': 'success'
    }