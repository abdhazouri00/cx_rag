from enum import Enum

class ResponseStatus(Enum):
  FILE_TYPE_NOT_SUPPORTED = "File type not supported"
  FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds the maximum limit"
  FILE_UPLOAD_SUCCESS = "File uploaded successfully"
  FILE_UPLOAD_FAILED = "File upload failed"
  FILE_VALIDATION_SUCCESS = "File validation successful"
  INDEX_NOT_READY = "Nothing is indexed yet. Upload, process and push documents first."