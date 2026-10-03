from .BaseController import BaseController
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from models import ProcessingEnum
from fastapi import HTTPException

class ProcessController(BaseController):
  def __init__(self):
    super().__init__()

    self.files_path = self.get_files_path()

  def get_file_extension(self,file_name:str):
    return Path(file_name).suffix.lower()

  def get_file_loader(self, file_id:str):
    file_extension = self.get_file_extension(file_name=file_id)
    file_path = self.files_path / file_id

    if not file_path.exists():
      return None

    if file_extension == ProcessingEnum.TXT.value:
      return TextLoader(str(file_path),encoding="utf-8")

    if file_extension == ProcessingEnum.PDF.value:
      return PyMuPDFLoader(str(file_path))
    
    return None
  
  def get_file_content(self , file_id : str):
    loader = self.get_file_loader(file_id)
    if loader is None:
        file_ext = self.get_file_extension(file_id)
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type: {file_ext}. Only PDF and TXT are allowed."
        )
    return loader.load()
  
  def get_document_name(self, file_id:str):
    return Path(file_id).stem.split("_", 1)[-1].replace("_", " ")

  def get_documents_metadata(self, assets:list):
    uploads_count = {}
    documents_metadata = {}

    for asset in assets:
      document_name = self.get_document_name(file_id=asset.asset_name)
      uploads_count[document_name] = uploads_count.get(document_name, 0) + 1

      documents_metadata[asset.asset_id] = {
        "title": document_name,
        "version": uploads_count[document_name],
        "effective_date": asset.created_at.date().isoformat(),
      }

    return documents_metadata

  def split_by_sections(self, file_text:str, document_metadata:dict):
    sections = ("\n" + file_text).split("\n## ")[1:]

    chunks = []

    for section in sections:
      section_title = section.splitlines()[0].strip()
      chunks.append(Document(page_content=section.strip(), metadata={**document_metadata, "section": section_title}))

    return chunks

  def process_file_content(self,content:list, document_metadata:dict, chunk_size:int = 500 , overlap_size:int = 100):
    file_text = "\n".join([record.page_content for record in content]).lstrip("\ufeff")

    section_chunks = self.split_by_sections(file_text=file_text, document_metadata=document_metadata)

    if len(section_chunks) > 0:
      return section_chunks

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap_size, length_function=len)

    chunks = text_splitter.create_documents([file_text], metadatas = [document_metadata])

    return chunks
