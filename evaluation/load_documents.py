import json
import sys
import urllib.request
import uuid
from pathlib import Path

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"
DOCUMENTS_DIR = Path(__file__).resolve().parent.parent / "documents"


def post_json(path, body):
  request = urllib.request.Request(
    BASE_URL + path,
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
  )
  with urllib.request.urlopen(request, timeout=600) as response:
    return json.loads(response.read().decode("utf-8"))


def upload(file_path):
  boundary = uuid.uuid4().hex
  head = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'
    "Content-Type: text/plain\r\n\r\n"
  ).encode("utf-8")
  tail = f"\r\n--{boundary}--\r\n".encode("utf-8")

  request = urllib.request.Request(
    BASE_URL + "/data/upload",
    data=head + file_path.read_bytes() + tail,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
  )
  with urllib.request.urlopen(request, timeout=120) as response:
    return json.loads(response.read().decode("utf-8"))


def main():
  old_versions = sorted((DOCUMENTS_DIR / "eski_surum").glob("*.txt"))
  current_versions = sorted(DOCUMENTS_DIR.glob("*.txt"))

  for file_path in old_versions + current_versions:
    result = upload(file_path)
    print("uploaded:", file_path.relative_to(DOCUMENTS_DIR).as_posix(), "->", result["file_id"])

  print("process:", post_json("/data/process", {"do_reset": 1}))
  print("push:", post_json("/nlp/index/push", {"do_reset": 1}))


if __name__ == "__main__":
  main()
