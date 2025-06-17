from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) 

GEMINI_API_KEY = 'AIzaSyB8y5bwT0iMS7LvZaGcBessIM5ycOrkQg4'
GEMINI_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

@app.route('/generate-mcq', methods=['POST'])
def generate_mcq():
    import re, json
    data = request.json
    subject = data.get("subject")
    chapter = data.get("chapter")
    count = data.get("count", 10)

    prompt = f"""
Generate exactly {count} HARD-LEVEL, CONCEPT-BASED MCQs for CBSE Class 10.
Subject: {subject}, Chapter: "{chapter}"

Rules:
- Only include questions from NCERT syllabus.
- Return only the JSON array with this format:
[
  {{
    "question": "What is ...?",
    "options": ["A", "B", "C", "D"],
    "correct": 0
  }}
]
- No explanation or markdown, only JSON array.
"""

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # Gemini API request
    response = requests.post(
        f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}",
        headers=headers,
        json=body
    )

    result = response.json()
    print("🔍 FULL GEMINI RESPONSE:", json.dumps(result, indent=2))

    # Extract content safely
    try:
        content = result['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        return jsonify({"error": "No valid content returned from Gemini."})

    content = content.strip()
    content = re.sub(r'```(?:json)?', '', content)

    # Extract JSON array
    match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
    if not match:
        return jsonify({"error": "Gemini output did not contain a valid JSON array."})

    json_block = match.group()

    try:
        questions = json.loads(json_block)
        return jsonify({"questions": questions})
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse Gemini response."})



if __name__ == '__main__':
   import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
