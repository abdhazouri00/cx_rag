from .BaseController import BaseController
from fastapi import HTTPException, UploadFile
from models import ResponseStatus
import re

class DataController(BaseController):
  def __init__(self):
    super().__init__()
    self.size_scale = 1024 * 1024 # converts mb to bytes

  def validate_file(self,file:UploadFile):
    if file.content_type not in self.settings.FILE_ALLOWED_TYPES:
      raise HTTPException(status_code=400,detail=ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value)
    
    if file.size  > self.settings.FILE_MAX_SIZE * self.size_scale:
      raise HTTPException(status_code=400,detail=ResponseStatus.FILE_SIZE_EXCEEDS_LIMIT.value)
    
    return True
  
  def generate_unique_path(self,orig_file_name:str):

    random_key = self.generate_random_string()
    files_path = self.get_files_path()
    cleaned_file_name = self.get_clean_file_name(orig_file_name)
    new_file_path = files_path / f"{random_key}_{cleaned_file_name}"

    while new_file_path.exists():
      random_key = self.generate_random_string()
      new_file_path = files_path / f"{random_key}_{cleaned_file_name}"
    
    return new_file_path , random_key + "_" + cleaned_file_name

  def get_clean_file_name(self,orig_file_name:str):
    cleaned_file_name = orig_file_name.strip().replace(' ','_')
    cleaned_file_name = re.sub(r'[^\w.]','', cleaned_file_name)
    return cleaned_file_name