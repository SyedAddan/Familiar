import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

_ = load_dotenv(find_dotenv())  # read local .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
OPENAI_API_MODEL = "gpt-3.5-turbo"
TOGETHER_API_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

client = OpenAI(
    api_key=TOGETHER_API_KEY,
    base_url='https://api.together.xyz/v1',
)


def generate_chatbot_response(message, avatarName, avatarRelationship, avatarAdditional, messages):
    if messages == []:
        sys_query = f'''Your Name is {avatarName}, and you have the following relationship with the human being: {avatarRelationship} and the user has provided this additional information about you: {avatarAdditional}.
        If you already know this information then ignore it and just respond to this query of the human: {message} and respond to it while keeping in kind the previous knowledge.
        If you didn't know this information then keep this in mind and hold on to it and respond to this query of the human: {message} and the others to come keeping in mind the context.
        Do not deviate from the context and do not answer questions other than the relevant context or message provided.
        Don't justify your answers.
        Don't give information not mentioned in the CONTEXT INFORMATION.
        You have to maintain a consistent personality and context throughout the conversation.
        You have to maintain a conformting and understanding tone throughout the conversation.'''
        
        messages = [
            {"role": "system", "content": sys_query},
            {"role": "user", "content": message}
        ]
    else:
        messages = messages + [{"role": "user", "content": message}]
        
    
    response = client.chat.completions.create(
        model=TOGETHER_API_MODEL,
        messages=messages
    ).choices[0].message.content
    
    messages = messages + [{"role": "bot", "content": response}]
    
    print(f"Previous History: {messages}")
    print()
    print(f"Response: {response}")
    print()
    
    return response, messages