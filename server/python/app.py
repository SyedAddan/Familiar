from flask import Flask,request,jsonify
import langchain
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
app = Flask(__name__)
llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.0, model=llm_model, openai_api_key="")
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm, 
    memory = memory,
    verbose=True
)
@app.route('/',methods=['POST'])
def hello_world():
    data = request.get_json()
    
    res=conversation.predict(input=data)
    print(res)
    return jsonify({"Response": res}), 200

if __name__ == '__main__':
    app.run(debug=True,port=5000)
