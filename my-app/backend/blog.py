import os
import json
import requests
from flask import Flask, Blueprint, request, jsonify

# Create a Flask Blueprint for blog-related routes
blog_bp = Blueprint('blog', __name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json"
}

@blog_bp.route("/api/generate_blogs", methods=["POST"])
def generate_blogs():
    data = request.get_json(force=True)
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    api_payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": ("""
                            You are an AI assistant that generates amazing blog articles on any topic. Please follow these instructions:

Generate a good, detailed, and sizable article for each topic provided.

Return the output as a JSON list.

The JSON should have objects with the keys "title" (for the article title) and "content" (for the article body).

Make sure the output strictly follows this JSON format.


[
  {
    "title": "Your Article Title",
    "content": "The full content of the article..."
  },
  ...
]
                            
                            
                            """)
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        api_response = requests.post(PERPLEXITY_URL, headers=HEADERS, json=api_payload, timeout=30)
        api_response.raise_for_status()
        result = api_response.json()
        content = result['choices'][0]['message']['content']

        # The response content should be parsed as JSON list string
        blogs = json.loads(content)

        # blogs expected format: [{"title": "...", "body": "..."}, {...}]
        return jsonify({"blogs": blogs})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
