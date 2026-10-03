from helpers.config import get_settings,Settings
from pathlib import Path
import string
import random

class BaseController:
  def __init__(self):
    self.settings = get_settings()
    self.base_dir = Path(__file__).parent.parent
    self.files_dir = self.base_dir / "assets" / "files"

  def get_files_path(self):
    if not self.files_dir.exists():
      self.files_dir.mkdir(parents=True)
    return self.files_dir

  def generate_random_string(self,length:int = 12):
    return ''.join(random.choices(string.ascii_lowercase +string.digits, k=length))
