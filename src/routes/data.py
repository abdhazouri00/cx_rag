from fastapi import FastAPI , APIRouter, Depends, Request, UploadFile , HTTPException
from fastapi.responses import JSONResponse
from helpers.config import get_settings,Settings
from controller import DataController, ProcessController
import aiofiles
import logging
from .schemas.data import ProcessRequest
from models.db_schemes import DataChunk
from models.AssetModel import AssetModel
from models.ChunkModel import ChunkModel
from models.AssetModel import Asset
from models.enums.AssetTypeEnum import AssetTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter()
data_router.prefix = "/api/v1/data"
data_router.tags = ["data"]
data_controller = DataController()

@data_router.post('/upload')
async def upload_file(request:Request, file:UploadFile, app_settings:Settings = Depends(get_settings)):

  is_valid = data_controller.validate_file(file)
  if not is_valid:
    return is_valid

  file_path , file_id = data_controller.generate_unique_path(file.filename)

  try:
    async with aiofiles.open(file_path, 'wb') as f:
      while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
        await f.write(chunk)
  except Exception as e:
    logger.error(f"Error while upload file : {e}")
    return JSONResponse(
      status_code=400,
      content={"message": "file upload failed"}
    )

  asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)
  asset_resource = Asset(asset_type = AssetTypeEnum.FILE.value, asset_name = file_id , asset_size=file_path.stat().st_size)

  asset_record = await asset_model.create_asset(asset=asset_resource)

  return JSONResponse(content={"message": "File uploaded successfully" , "file_id" : asset_record.asset_name}, status_code=200)

@data_router.post('/process')
async def process_file(request:Request, processRequest:ProcessRequest):

  do_reset = processRequest.do_reset

  process_controller = ProcessController()

  asset_model = await AssetModel.create_instance(db_client=request.app.state.db_client)

  all_files = await asset_model.get_all_assets(asset_type=AssetTypeEnum.FILE.value)

  documents_metadata = process_controller.get_documents_metadata(assets=all_files)

  files_ids = {}
  if processRequest.file_id:

    asset_record = await asset_model.get_asset_records(asset_name=processRequest.file_id)

    if asset_record is None:
      return JSONResponse(content={"message": "File not found"}, status_code=400)

    files_ids = {asset_record.asset_id:asset_record.asset_name}

  else:
    files_ids = {
      record.asset_id : record.asset_name
      for record in all_files
    }

  if len(files_ids) == 0:
    return JSONResponse(content={"message": "No files to process"}, status_code=400)

  chunk_model = await ChunkModel.create_instance(db_client = request.app.state.db_client)

  if do_reset == 1:
        await chunk_model.delete_all_chunks()

  no_records = 0
  no_files = 0

  for asset_id ,file_id in files_ids.items():
    file_content = process_controller.get_file_content(file_id=file_id)

    if file_content is None:
      logger.error(f"File {file_id} is empty")
      continue

    chunks = process_controller.process_file_content(content=file_content, document_metadata=documents_metadata[asset_id], chunk_size=processRequest.chunk_size, overlap_size=processRequest.overlap_size)

    if chunks is None or len(chunks) == 0:
      return JSONResponse(content={"message": "File processing failed"}, status_code=400)

    file_chunks_records = [DataChunk(chunk_text=chunk.page_content,chunk_metadata=chunk.metadata,
                                    chunk_order=i+1, chunk_asset_id=asset_id) for i,chunk in enumerate(chunks)]

    no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
    no_files += 1

  return JSONResponse(content={"message": "File processed successfully" , "file_id" : file_id , "inserted_records" : no_records , "processed_files": no_files}, status_code=200)
