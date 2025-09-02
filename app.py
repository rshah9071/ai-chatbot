
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__, template_folder='templates')
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "tinyllama"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is live!"})

@app.route('/chat', methods=['POST'])
def chat():
    app.logger.info("Received request to /chat endpoint")
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_message = data.get('message')
        if not user_message:
            return jsonify({'error': 'No message found'}), 400

        ollama_payload = {
            "model": MODEL_NAME,
            "stream": False,
            "messages": [{"role": "user", "content": user_message}]
        }

        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=120)
        response.raise_for_status()
        
        ollama_response = response.json()
        bot_reply = ollama_response['message']['content']
        return jsonify({'reply': bot_reply})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF
