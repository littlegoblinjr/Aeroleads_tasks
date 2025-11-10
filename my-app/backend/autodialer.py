import os
import json
import requests
import ast
import time
import pandas as pd
from flask import Flask, request, Response, send_file
from flask_cors import CORS
from twilio.rest import Client
from datetime import datetime

from blog import blog_bp

app = Flask(__name__)
app.register_blueprint(blog_bp)
CORS(app)

# --- Configuration ---

PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

OUT_DIR = "out"
CSV_PATH = os.path.join(OUT_DIR, "call_logs.csv")
os.makedirs(OUT_DIR, exist_ok=True)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def ndjson_line(obj):
    return json.dumps(obj, default=str) + "\n"

def call_perplexity_and_get_numbers(prompt):
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant that extracts all phone numbers from any given text or query. Always return the phone numbers only as a Python list of strings, e.g.: [\"+18001234567\", \"9876543210\"]. If there are no phone numbers in the text, return an empty list ([]). Do not include any explanation, text, or formatting other than the Python list.",
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 500,
    }
    resp = requests.post(PERPLEXITY_URL, headers=headers, json=data, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    content = j['choices'][0]['message']['content']
    numbers = ast.literal_eval(content)
    return numbers

@app.route("/api/process_prompt", methods=["POST"])
def process_prompt_stream():
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "")
    results = []

    def generator():
        yield ndjson_line({"type": "status", "message": "received_prompt", "prompt": prompt})
        try:
            yield ndjson_line({"type": "status", "message": "calling_perplexity"})
            numbers = call_perplexity_and_get_numbers(prompt)
            yield ndjson_line({"type": "status", "message": "perplexity_done", "numbers_found": numbers})
        except Exception as e:
            yield ndjson_line({"type": "error", "message": "perplexity_failed", "detail": str(e)})
            return

        if not numbers:
            yield ndjson_line({"type": "done", "message": "no_numbers"})
            return

        for idx, to in enumerate(numbers, start=1):
            yield ndjson_line({"type": "calling", "number": to, "index": idx, "total": len(numbers)})
            try:
                
                
                call = client.calls.create(
                    to=to,
                    from_=TWILIO_FROM_NUMBER,
                    twiml='<Response><Say>This is a test</Say></Response>'
                )
                sid = getattr(call, "sid", "")
                status = getattr(call, "status", None)
                results.append({"to": to, "sid": sid, "status": status})
                yield ndjson_line({"type": "result", "to": to, "sid": sid, "status": status})
            except Exception as e:
                results.append({"to": to, "sid": "", "status": "error", "error": str(e)})
                yield ndjson_line({"type": "result", "to": to, "sid": "", "status": "error", "error": str(e)})
            time.sleep(0.2)

        # Save CSV (append or create)
        df = pd.DataFrame(results)
        df["timestamp"] = datetime.now().isoformat()
        if os.path.exists(CSV_PATH):
            try:
                existing = pd.read_csv(CSV_PATH)
                out_df = pd.concat([existing, df], ignore_index=True)
            except Exception:
                out_df = df
        else:
            out_df = df
        out_df.to_csv(CSV_PATH, index=False)
        try:
            preview = out_df.tail(20).to_dict(orient="records")
        except Exception:
            preview = []
        yield ndjson_line({"type": "done", "message": "finished", "results": results, "csv_preview": preview, "csv_path": CSV_PATH})

    return Response(generator(), mimetype="application/x-ndjson")

@app.route("/download_csv")
def download_csv():
    if not os.path.exists(CSV_PATH):
        return {"error": "CSV not found"}, 404
    return send_file(CSV_PATH, as_attachment=True, download_name="call_logs.csv")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
