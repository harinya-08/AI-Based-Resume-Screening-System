
import sys, json, PyPDF2, docx, re, os
from transformers import T5ForConditionalGeneration, T5Tokenizer
print("[INFO] Python script started for resume analysis.", file=sys.stderr)

try:
    model = T5ForConditionalGeneration.from_pretrained("./t5_resume_model")
    tokenizer = T5Tokenizer.from_pretrained("./t5_resume_model")
    print("[INFO] T5 model loaded.", file=sys.stderr)
except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    sys.exit(1)
def extract_text(path):
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return ""
    if path.endswith(".pdf"):
        reader = PyPDF2.PdfReader(path)
        return "".join(page.extract_text() or "" for page in reader.pages)
    elif path.endswith(".docx"):
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        print(f"[ERROR] Unsupported file type.", file=sys.stderr)
        return ""
def extract_name(text):
    match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)', text)
    return match.group(1) if match else "Candidate"

def generate_recommendations_t5(text):
    input_text = "generate recommendations: " + text
    inputs = tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    outputs = model.generate(inputs, max_length=128, num_beams=4, early_stopping=True)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    recommendations = [r.strip() for r in decoded.split(".") if r.strip()]
    return recommendations
def compute_score_from_recommendations(recommendations):
    count = len(recommendations)
    score = max(100 - count * 10, 50)
    return score
try:
    file_path = sys.argv[1]
    text = extract_text(file_path)
    if not text:
        raise Exception("No text extracted.")
    name = extract_name(text)
    recommendations = generate_recommendations_t5(text)
    score = compute_score_from_recommendations(recommendations)
    filename_for_frontend = os.path.basename(file_path)
    result = {
        "name": name,
        "score": score,
        "recommendations": recommendations,
        "file": filename_for_frontend
    }
    with open("./public/report.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print(json.dumps(result, ensure_ascii=False))

except Exception as e:
    print(f"[ERROR] {e}", file=sys.stderr)
    sys.exit(1)
