from flask import Flask, request, jsonify
from transformers import T5ForConditionalGeneration, T5Tokenizer, BertTokenizer, BertForSequenceClassification
import torch, re

app = Flask(__name__)
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
bert_model = BertForSequenceClassification.from_pretrained("bert-base-uncased")
t5_tokenizer = T5Tokenizer.from_pretrained("./t5_resume_model")
t5_model = T5ForConditionalGeneration.from_pretrained("./t5_resume_model")
@app.route("/api/score", methods=["POST"])
def score_resume():
    data = request.json
    text = data["resume_text"]
    match = re.search(r'([A-Z][a-z]+(?: [A-Z][a-z]+)*)', text)
    name = match.group(1) if match else "Candidate"
    inputs = bert_tokenizer.encode_plus(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        output = bert_model(**inputs)
        logit = output.logits[0][1]
        score = int(torch.sigmoid(logit).item() * 100)
    input_text = "generate recommendations: " + text

    inputs = t5_tokenizer.encode(input_text, return_tensors="pt", truncation=True)
    outputs = t5_model.generate(inputs, max_length=128, num_beams=4)
    recommendation = t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return jsonify({
        "candidate_name": name,
        "score": score,
        "pdf_url": "",  
        "recommendations": [recommendation]
    })
if __name__ == "__main__":
    app.run(debug=True)
