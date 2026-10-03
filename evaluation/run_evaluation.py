import json
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"
ROOT_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT_DIR / "evaluation" / "questions.json"
RESULTS_FILE = ROOT_DIR / "evaluation" / "sonuclar.json"
REPORT_FILE = ROOT_DIR / "DEGERLENDIRME.md"
SETTINGS_TO_SHOW = ["GENERATION_BACKEND", "GENERATION_MODEL_ID", "EMBEDDING_BACKEND", "EMBEDDING_MODEL_ID", "RAG_MIN_SCORE", "CHAT_HISTORY_LIMIT"]


def ask(question, conversation_id=None):
  body = {"text": question}
  if conversation_id:
    body["conversation_id"] = conversation_id

  request = urllib.request.Request(
    BASE_URL + "/nlp/index/answer",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
  )
  with urllib.request.urlopen(request, timeout=300) as response:
    return json.loads(response.read().decode("utf-8"))


def read_settings():
  settings = {}
  env_file = ROOT_DIR / ".env"

  if not env_file.exists():
    return settings

  for line in env_file.read_text(encoding="utf-8").splitlines():
    key, separator, value = line.partition("=")
    if separator and key.strip() in SETTINGS_TO_SHOW:
      settings[key.strip()] = value.strip().strip('"')

  return settings


def contains(answer, phrase):
  return any(option.casefold() in answer.casefold() for option in phrase.split("|"))


def show(phrase):
  return " veya ".join(f"\"{option}\"" for option in phrase.split("|"))


def describe_source(doc):
  metadata = doc["metadata"]
  section = metadata.get("section") or "-"
  return f"{metadata.get('title')} / {section} / sürüm {metadata.get('version')} (puan {doc['score']:.2f})"


def check(item, response):
  checks = []
  answer = response["answer"]

  checks.append(("Cevaplanabilirlik", response["answerable"] == item["answerable"]))

  for phrase in item.get("must_contain", []):
    checks.append((f"Cevapta {show(phrase)} var", contains(answer, phrase)))

  for phrase in item.get("must_not_contain", []):
    checks.append((f"Cevapta {show(phrase)} yok", not contains(answer, phrase)))

  if item.get("source"):
    found = any(
      doc["metadata"].get("title") == item["source"] and doc["metadata"].get("version") == item["version"]
      for doc in response["sources"]
    )
    checks.append((f"Kaynak: {item['source']}, sürüm {item['version']}", found))

  if item.get("superseded_version"):
    found = any(
      doc["metadata"].get("title") == item["source"] and doc["metadata"].get("version") == item["superseded_version"]
      for doc in response["superseded_sources"]
    )
    checks.append((f"Elenen eski sürüm: {item['superseded_version']}", found))

  if not item["answerable"]:
    checks.append(("Kaynak gösterilmedi", len(response["sources"]) == 0))

  return checks


def expected_text(item):
  if not item["answerable"]:
    return "Cevap verilmemeli (`answerable: false`), kaynak gösterilmemeli."

  parts = ["Cevapta: " + ", ".join(show(phrase) for phrase in item["must_contain"])]

  if item.get("must_not_contain"):
    parts.append("Cevapta olmamalı: " + ", ".join(show(phrase) for phrase in item["must_not_contain"]))

  parts.append(f"Kaynak: {item['source']}, sürüm {item['version']}")

  if item.get("superseded_version"):
    parts.append(f"Elenen eski sürüm: {item['superseded_version']}")

  return ". ".join(parts) + "."


def cell(text):
  return str(text).replace("|", "\\|").replace("\n", " ")


def main():
  questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
  conversations = {}
  results = []

  for number, item in enumerate(questions, start=1):
    conversation_key = item.get("conversation")
    response = ask(item["question"], conversations.get(conversation_key))

    if conversation_key:
      conversations[conversation_key] = response["conversation_id"]

    checks = check(item, response)
    passed = all(ok for _, ok in checks)
    results.append({"number": number, "item": item, "response": response, "checks": checks, "passed": passed})
    print(f"{number:>2}. {'GEÇTİ' if passed else 'KALDI'}  [{item['type']}] {item['question']}")

  RESULTS_FILE.write_text(
    json.dumps([{"no": r["number"], "question": r["item"]["question"], "expected": r["item"], "actual": r["response"], "passed": r["passed"]} for r in results], ensure_ascii=False, indent=2),
    encoding="utf-8",
  )

  total = len(results)
  passed_total = sum(1 for r in results if r["passed"])
  settings = read_settings()

  lines = []
  lines.append("# Değerlendirme: Beklenen ve Gerçekleşen Sonuçlar")
  lines.append("")
  lines.append(f"Bu rapor `evaluation/run_evaluation.py` betiği tarafından, çalışan API'ye ({BASE_URL}) gerçek istekler gönderilerek üretilmiştir.")
  lines.append("")
  lines.append(f"- **Tarih:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
  lines.append(f"- **Sonuç:** {total} sorudan {passed_total} tanesi beklenen sonucu verdi.")
  for key in SETTINGS_TO_SHOW:
    if key in settings:
      lines.append(f"- **{key}:** `{settings[key]}`")
  lines.append("- **Ham API yanıtları (kanıt):** `evaluation/sonuclar.json`")
  lines.append("")

  lines.append("## Özet")
  lines.append("")
  lines.append("| Soru türü | Soru sayısı | Geçen |")
  lines.append("|---|---|---|")
  for question_type in dict.fromkeys(r["item"]["type"] for r in results):
    group = [r for r in results if r["item"]["type"] == question_type]
    lines.append(f"| {question_type} | {len(group)} | {sum(1 for r in group if r['passed'])} |")
  lines.append("")
  lines.append("Soru türleri: **normal** (belgelerde cevabı olan), **çakışan** (eski ve yeni sürümün farklı söylediği), **sohbet** (aynı konuşmada devam sorusu), **cevaplanamaz** (belgelerde olmayan veya konu dışı).")
  lines.append("")

  lines.append("## Sonuç tablosu")
  lines.append("")
  lines.append("| No | Tür | Soru | Beklenen | Gerçekleşen cevap | Sonuç |")
  lines.append("|---|---|---|---|---|---|")
  for r in results:
    lines.append(f"| {r['number']} | {r['item']['type']} | {cell(r['item']['question'])} | {cell(expected_text(r['item']))} | {cell(r['response']['answer'])} | {'Geçti' if r['passed'] else '**Kaldı**'} |")
  lines.append("")

  lines.append("## Ayrıntılar")
  for r in results:
    item, response = r["item"], r["response"]
    lines.append("")
    lines.append(f"### {r['number']}. {item['question']}")
    lines.append("")
    lines.append(f"- **Tür:** {item['type']}")
    lines.append(f"- **Beklenen:** {expected_text(item)}")
    lines.append(f"- **Gerçekleşen cevap:** {response['answer']}")
    lines.append(f"- **`answerable`:** `{str(response['answerable']).lower()}`")
    if response["sources"]:
      lines.append("- **Kullanılan kaynaklar:**")
      for doc in response["sources"]:
        lines.append(f"  - {describe_source(doc)}")
    else:
      lines.append("- **Kullanılan kaynaklar:** yok")
    if response["superseded_sources"]:
      lines.append("- **Elenen eski sürümler:**")
      for doc in response["superseded_sources"]:
        lines.append(f"  - {describe_source(doc)}")
    lines.append("- **Kontroller:**")
    for name, ok in r["checks"]:
      lines.append(f"  - {'Geçti' if ok else 'Kaldı'}: {name}")
    lines.append(f"- **Sonuç:** {'Geçti' if r['passed'] else 'Kaldı'}")
    if item.get("note"):
      lines.append(f"- **Not:** {item['note']}")

  REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
  print(f"\n{total} sorudan {passed_total} tanesi geçti. Rapor: {REPORT_FILE.name}")


if __name__ == "__main__":
  main()
