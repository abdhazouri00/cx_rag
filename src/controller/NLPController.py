from .BaseController import BaseController
from models.db_schemes import DataChunk
from typing import List
from stores.llm.LLMEnum import DocumentTypeEnum

class NLPController(BaseController):
  def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
    super().__init__()

    self.vectordb_client = vectordb_client
    self.generation_client = generation_client
    self.embedding_client = embedding_client
    self.template_parser = template_parser
    self.no_answer_marker = "NO_ANSWER"
    self.collection_name = "cx_rag_documents"

  def is_index_ready(self):
    return self.vectordb_client.collection_exist(collection_name=self.collection_name)

  def reset_vectordb_collection(self):
    return self.vectordb_client.delete_collection(collection_name=self.collection_name)

  def get_vector_db_collection_info(self):
    collection_info = self.vectordb_client.get_collection_info(collection_name=self.collection_name)
    return collection_info

  def index_into_vector_db(self, chunks: List[DataChunk], chunks_ids: list[int], do_reset: bool = False):

    #manage items
    texts = [c.chunk_text for c in chunks]
    metadata = [c.chunk_metadata for c in chunks]

    vectors = [ self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value) for text in texts]

    #create collection if not exist
    _ = self.vectordb_client.create_collection(collection_name = self.collection_name, do_reset=do_reset, embedding_size = self.embedding_client.embedding_size)

    #insert into vectordb
    _ = self.vectordb_client.insert_many(collection_name=self.collection_name, texts=texts, vectors=vectors, metadata=metadata, record_ids=chunks_ids)

    return True
  
  def search_vector_db_collection(self, text: str, limit: int = 10):
    vector = self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.QUERY.value)
    return self.vectordb_client.search_by_vector(collection_name=self.collection_name, vector=vector, limit=limit) 
  
  def answer_rag_question(self, query: str, limit: int = 10, chat_messages: list = []):

    previous_questions = [message.message_content for message in chat_messages if message.message_role == self.generation_client.enums.USER.value]

    search_text = query
    if len(previous_questions) > 0:
      search_text = previous_questions[-1] + "\n" + query

    retrieved_docs = self.search_vector_db_collection(text=search_text, limit=limit)

    if not retrieved_docs or len(retrieved_docs) == 0:
      return self.generate_no_answer_response(query=query), False, [], []

    current_docs, superseded_docs = self.select_current_versions(retrieved_docs=retrieved_docs)

    current_docs = [doc for doc in current_docs if doc.score >= self.settings.RAG_MIN_SCORE]
    superseded_docs = [doc for doc in superseded_docs if doc.score >= self.settings.RAG_MIN_SCORE]

    if len(current_docs) == 0:
      return self.generate_no_answer_response(query=query), False, [], []

    system_prompt = self.template_parser.get(group="rag", key="system_prompt", vars={"no_answer_marker": self.no_answer_marker})

    documents_prompts = []

    documents_prompts = [
    self.template_parser.get(
        group="rag",
        key="document_prompt",
        vars={"doc_num": idx + 1, "title": doc.metadata.get("title"), "section": doc.metadata.get("section"), "version": doc.metadata.get("version"), "chunk_text":  self.generation_client.process_text(doc.text)}
    )
    for idx, doc in enumerate(current_docs)
]
    
    footer_prompt = self.template_parser.get(group="rag", key="footer_prompt", vars={"query": query})

    chat_history = [
      self.generation_client.construct_prompt(prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value)
    ]

    for message in chat_messages:
      chat_history.append(self.generation_client.construct_prompt(prompt=message.message_content, role=message.message_role))

    full_prompt = "\n\n".join([*documents_prompts, footer_prompt])

    answer = self.generation_client.generate_text(prompt=full_prompt, chat_history=chat_history)

    if not answer or self.no_answer_marker in answer:
      return self.generate_no_answer_response(query=query), False, [], []

    return answer, True, current_docs, superseded_docs

  def generate_no_answer_response(self, query: str):
    no_answer_prompt = self.template_parser.get(group="rag", key="no_answer_prompt")

    chat_history = [
      self.generation_client.construct_prompt(prompt=no_answer_prompt, role=self.generation_client.enums.SYSTEM.value)
    ]

    answer = self.generation_client.generate_text(prompt=query, chat_history=chat_history)

    if not answer:
      return self.template_parser.get(group="rag", key="no_answer_response")

    return answer

  def select_current_versions(self, retrieved_docs: list):
    latest_versions = {}

    for doc in retrieved_docs:
      title = doc.metadata.get("title")
      version = doc.metadata.get("version", 0)

      if title and version > latest_versions.get(title, 0):
        latest_versions[title] = version

    current_docs = []
    superseded_docs = []

    for doc in retrieved_docs:
      title = doc.metadata.get("title")
      version = doc.metadata.get("version", 0)

      if title and version < latest_versions[title]:
        superseded_docs.append(doc)
      else:
        current_docs.append(doc)

    return current_docs, superseded_docs