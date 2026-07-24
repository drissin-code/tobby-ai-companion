"""
server.py — Local API bridge between Tobby's Python brain and
the Electron HUD (tobby_ui.html).

The HUD sends typed messages here via HTTP, this calls the same
LangGraph brain used by main.py, and sends the reply back as JSON.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from graph_brain import get_tobby_response_full

app = Flask(__name__)
CORS(app)  # allows the Electron HTML page to call this server


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input.strip():
        return jsonify({"reply": "Sir, I didn't catch that.", "action": None})

    result = get_tobby_response_full(user_input)
    return jsonify(result)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Tobby backend is online"})


if __name__ == "__main__":
    print("Starting Tobby backend server on http://localhost:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False)
