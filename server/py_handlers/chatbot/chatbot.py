from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv()) # read local .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.9, model=llm_model, openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)

def generate_chatbot_response(message):
    res = conversation.predict(input=message)
    return res