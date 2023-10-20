from flask import Flask, request, jsonify
import time
from scipy.io import wavfile
from py_handlers.chatbot.chatbot import generate_chatbot_response
from py_handlers.stt.stt import generate_text_from_speech

app = Flask(__name__)


@app.route('/avatarInputs', methods=['POST'])
def avatarInputs():
    try:
        data = request.get_json()
        with open("avatarInputs.txt", "w") as f:
            f.write(data["avatarName"] + "\n")
            f.write(data["avatarContext"])
        return jsonify({"responseText": "Success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong"}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    avatarInputs = {}
    try:
        with open("avatarInputs.txt", "r") as f:
            avatarName = f.readline().strip()
            avatarContext = " ".join(f.readlines()).strip()
            avatarInputs["avatarName"] = avatarName
            avatarInputs["avatarContext"] = avatarContext
        
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong", "responceTime": 0}), 500
    try:
        data = request.get_json()
        start = time.time()
        res = generate_chatbot_response(data["message"], avatarInputs)
        end = time.time()
        responceTime = end - start
        return jsonify({"responseText": res, "responceTime": responceTime}), 200
    except Exception as e:
        print(e)
        return jsonify({"responseText": "Something went wrong", "responceTime": 0}), 500


@app.route('/stt', methods=['POST'])
def stt():
    try:
        audioBlob = request.files['audio']
        text = generate_text_from_speech(audioBlob)
        return jsonify({'text': text}), 200
    except Exception as e:
        print(e)
        return jsonify({'text': 'Something went wrong'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
