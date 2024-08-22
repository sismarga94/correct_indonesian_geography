import io
from http.client import HTTPException

import pandas as pd
from fastapi import APIRouter, Depends

from fastapi import UploadFile, File
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.models.location import CheckGeographicResponse, CheckGeographicRequest
from app.repositories.api_repository import ApiRepository
from app.services.api_service import ApiService
from app.utils.database import get_db
from app.utils.normal_text_filter import NormalFiltering
from app.utils.text_distance_filter import TextDistanceFiltering
import openpyxl

api_router = APIRouter()


def get_db_session():
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


def get_service(db: Session = Depends(get_db_session)):
    repository = ApiRepository(db)
    normal_filter = NormalFiltering()
    td_filter = TextDistanceFiltering()
    return ApiService(repository, normal_filter, td_filter)


@api_router.post("/api/check", response_model=CheckGeographicResponse, tags=["Check Geographic"])
async def check_geographic(request: CheckGeographicRequest, service: ApiService = Depends(get_service)):
    return service.check_geographic(request)


@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...), service: ApiService = Depends(get_service)):
    if not file.filename.endswith(('.csv', '.xls', '.xlsx', '.xml', '.json')):
        raise HTTPException(status_code=400, detail="Invalid file format. Only XML, CSV, JSON, and Excel files are allowed.")

    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(contents))
    elif file.filename.endswith('.xml'):
        df = pd.read_xml(io.BytesIO(contents))
    elif file.filename.endswith('.json'):
        df = pd.read_json(io.BytesIO(contents))
    else:
        df = pd.read_excel(io.BytesIO(contents), engine='openpyxl')

    processed_data = service.process_file(df)

    output = io.BytesIO()
    if file.filename.endswith('.csv'):
        processed_data.to_csv(output, index=False, sep="|")
    elif file.filename.endswith('.xml'):
        processed_data.to_xml(output, index=False)
    elif file.filename.endswith('.json'):
        processed_data.to_json(output, index=False)
    else:
        processed_data.to_excel(output, index=False)
    output.seek(0)

    return StreamingResponse(
        output,
        media_type='application/octet-stream',
        headers={"Content-Disposition": f"attachment;filename={file.filename}"}
    )
