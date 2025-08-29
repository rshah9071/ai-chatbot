from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging
import json

# Set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder='.')  # Points Flask to the current directory for templates
CORS(app)  # Enable CORS for all origins

# Configuration - Local Ollama base URL
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "tinyllama"

@app.route('/', methods=['GET'])
def home():
    """Serve the chatbot homepage."""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "Server is live!"})

@app.route('/chat', methods=['POST'])
def chat():
    """Main endpoint to handle chat messages from the frontend."""
    app.logger.info("Received a request to /chat endpoint")

    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_message = data.get('message')
        app.logger.info(f"User message: {user_message}")

        if not user_message:
            return jsonify({'error': 'No message found in request'}), 400

        # Build payload for /api/generate (works for tinyllama)
        ollama_payload = {
            "model": MODEL_NAME,
            "prompt": user_message
        }

        url = f"{OLLAMA_BASE_URL}/api/generate"
        app.logger.info(f"Sending request to Ollama at {url}")

        response = requests.post(url, json=ollama_payload, stream=True, timeout=120)
        response.raise_for_status()

        # Collect streamed response
        full_text = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    if "response" in data:
                        full_text += data["response"]
                except json.JSONDecodeError:
                    continue

        app.logger.info(f"Successfully received reply from Ollama: {full_text[:50]}...")
        return jsonify({'reply': full_text.strip()})

    except requests.exceptions.ConnectionError:
        error_msg = "Could not connect to the Ollama service. Please ensure it is running on this computer."
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 503
    except requests.exceptions.Timeout:
        error_msg = "The request to the AI model timed out. It might be too busy."
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 504
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error occurred: {str(e)}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0')
