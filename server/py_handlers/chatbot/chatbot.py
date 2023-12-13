from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())  # read local .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.5, model=llm_model,
                 openai_api_key=OPENAI_API_KEY)
memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)


def generate_chatbot_response(message, avatarName, avatarRelationship, avatarAdditional):
    message = f"Your Name is {avatarName}, and you have the following relationship with the human being: {avatarRelationship} and the user has provided this additional information about you: {avatarAdditional}. If you already know this information then ignore it and just respond to this query of the human: {message} and respond to it while keeping in kind the previous knowledge. If you didn't know this information then keep this in mind and hold on to it and respond to this query of the human: {message} and the others to come keeping in mind the context. Do not deviate from the context and do not answer questions other than the relevant context or message provided. Don't justify your answers. Don't give information not mentioned in the CONTEXT INFORMATION."
    res = conversation.predict(input=message)
    return res
