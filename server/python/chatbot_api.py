from flask import Flask, request, jsonify
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv, find_dotenv
import os
import time

_ = load_dotenv(find_dotenv()) # read local .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.9, model=llm_model, openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)


@app.route('/chatbot', methods=['POST'])
def hello_world():
    try:
        data = request.get_json()
        start = time.time()
        res = conversation.predict(input=data["message"])
        end = time.time()
        responceTime = end - start
        return jsonify({"responseText": res, "responceTime": responceTime}), 200
    except:
        return jsonify({"responseText": "Something went wrong", "responceTime": 0}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
