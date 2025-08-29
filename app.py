# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, template_folder='.') # Points Flask to the current directory for templates
# Enable CORS for all origins. For a production app, you'd restrict this.
CORS(app)

# Configuration - Connect to your LOCAL Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2"

# This is the new homepage route that serves index.html
@app.route('/', methods=['GET'])
def home():
    """Returns the homepage of the chatbot app."""
    # This will now serve the index.html file
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to check if the server is running."""
    return jsonify({"status": "OK", "message": "Server is live!"})

@app.route('/chat', methods=['POST'])
def chat():
    """The main endpoint to handle chat messages from the website."""
    app.logger.info("Received a request to /chat endpoint")
    
    try:
        data = request.get_json()
        if not data:
            app.logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
        
        user_message = data.get('message')
        app.logger.info(f"User message: {user_message}")
        
        if not user_message:
            return jsonify({'error': 'No message found in request'}), 400

        ollama_payload = {
            "model": llama3.2,
            "stream": False,
            "messages": [{"role": "user", "content": user_message}]
        }
        app.logger.info(f"Sending request to Ollama at {OLLAMA_URL}")
        
        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=120)
        response.raise_for_status()
        
        ollama_response = response.json()
        bot_reply = ollama_response['message']['content']
        
        app.logger.info(f"Successfully received reply from Ollama: {bot_reply[:50]}...")

        return jsonify({'reply': bot_reply})

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
    except KeyError:
        error_msg = "Received an unexpected response format from the AI model."
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        app.logger.error(error_msg)
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    app.logger.info("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0')
