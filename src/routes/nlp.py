from fastapi import FastAPI , APIRouter, Depends, Request, UploadFile , HTTPException
from fastapi.responses import JSONResponse
import logging
from .schemas.nlp import PushRequest, SearchRequest
from models.ChunkModel import ChunkModel
from models.MessageModel import MessageModel
from models.db_schemes import Message
from models import ResponseStatus
from controller.NLPController import NLPController
import uuid

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter()
nlp_router.prefix = "/api/v1/nlp"
nlp_router.tags = ["nlp"]

@nlp_router.post("/index/push")
async def index_chunks(request:Request, push_request:PushRequest):

  chunk_model = await ChunkModel.create_instance(db_client=request.app.state.db_client)

  nlp_controller = NLPController(vectordb_client=request.app.state.vectordb_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client, template_parser=request.app.state.template_parser)

  has_records = True
  page_no = 1
  inserted_items_count = 0

  idx = 0

  while has_records:
    page_chunks = await chunk_model.get_chunks(page_no=page_no, page_size=push_request.pagesize)
    if len(page_chunks):
      page_no += 1

    if not page_chunks or len(page_chunks) == 0:
      has_records = False
      break

    chunks_ids = list(range(idx, idx + len(page_chunks)))
    idx += len(page_chunks)

    is_inserted = nlp_controller.index_into_vector_db(chunks=page_chunks, do_reset=push_request.do_reset, chunks_ids=chunks_ids)

    if not is_inserted:
      logger.error("Error while indexing")
      return JSONResponse(content={"message": "Error while indexing"}, status_code=400)

    inserted_items_count += len(page_chunks)


  return JSONResponse(content={"message": "Inserted into vector database sucessfully" , "inserted_items_count":inserted_items_count}, status_code=200)

@nlp_router.get("/index/info")
async def get_index_info(request:Request):

  nlp_controller = NLPController(vectordb_client=request.app.state.vectordb_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client, template_parser=request.app.state.template_parser)

  if not nlp_controller.is_index_ready():
    return JSONResponse(content={"message": ResponseStatus.INDEX_NOT_READY.value}, status_code=400)

  collection_info = nlp_controller.get_vector_db_collection_info()

  return JSONResponse(content={"message" : "Success" , "collection_info":collection_info.model_dump()}, status_code=200)

@nlp_router.post("/index/search")
async def search_index(request:Request, search_request:SearchRequest):

  nlp_controller = NLPController(vectordb_client=request.app.state.vectordb_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client, template_parser=request.app.state.template_parser)

  if not nlp_controller.is_index_ready():
    return JSONResponse(content={"message": ResponseStatus.INDEX_NOT_READY.value}, status_code=400)

  results = nlp_controller.search_vector_db_collection(text=search_request.text, limit=search_request.limit)

  return JSONResponse(content={"message" : "Success" , "results": [result.model_dump() for result in results or []]}, status_code=200)

@nlp_router.post("/index/answer")
async def answer_rag(request:Request, search_request:SearchRequest):

  nlp_controller = NLPController(vectordb_client=request.app.state.vectordb_client, generation_client=request.app.state.generation_client, embedding_client=request.app.state.embedding_client, template_parser=request.app.state.template_parser)

  if not nlp_controller.is_index_ready():
    return JSONResponse(content={"message": ResponseStatus.INDEX_NOT_READY.value}, status_code=400)

  message_model = await MessageModel.create_instance(db_client=request.app.state.db_client)

  conversation_id = search_request.conversation_id or uuid.uuid4().hex

  chat_messages = await message_model.get_last_messages(conversation_id=conversation_id, limit=nlp_controller.settings.CHAT_HISTORY_LIMIT)

  answer, answerable, sources, superseded_sources = nlp_controller.answer_rag_question(query=search_request.text, limit=search_request.limit, chat_messages=chat_messages)

  roles = request.app.state.generation_client.enums

  await message_model.create_message(message=Message(message_conversation_id=conversation_id, message_role=roles.USER.value, message_content=search_request.text))
  await message_model.create_message(message=Message(message_conversation_id=conversation_id, message_role=roles.ASSISTANT.value, message_content=answer))

  return JSONResponse(content={"message" : "Success" , "conversation_id": conversation_id, "answerable": answerable, "answer": answer, "sources": [doc.model_dump() for doc in sources], "superseded_sources": [doc.model_dump() for doc in superseded_sources]}, status_code=200)
