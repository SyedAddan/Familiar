import os

from dotenv import load_dotenv, find_dotenv

from openai import OpenAI


_ = load_dotenv(find_dotenv())  # read local .env file

GROQ_API_MODEL = os.getenv("GROQ_API_MODEL", "llama-3.3-70b-versatile")

def generate_chatbot_response(message, avatarName, avatarRelationship, avatarAdditional, messages):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    if messages == []:
        sys_query = f'''Your Name is {avatarName}, and you have the following relationship with the human being: {avatarRelationship} and the user has provided this additional information about you: {avatarAdditional}.
        If you already know this information then ignore it and just respond to this query of the human: {message} and respond to it while keeping in kind the previous knowledge.
        If you didn't know this information then keep this in mind and hold on to it and respond to this query of the human: {message} and the others to come keeping in mind the context.
        Do not deviate from the context and do not answer questions other than the relevant context or message provided.
        Don't justify your answers.
        Don't give information not mentioned in the CONTEXT INFORMATION.
        You have to maintain a consistent personality and context throughout the conversation.
        You have to maintain a conformting and understanding tone throughout the conversation.
        Include emojis a lot but only include the faced emojis from this list 😐, 😶, 😏, 🙂, 🙃, 😊, 😇, 😀, 😃, 😄, 😁, 😆, 😝, 😋, 😛, 😝, 😜, 🤪, 😂, 🤣, 😂, 😅, 😉, 😭, 🥺, 😞, 😔, 😳, ☹️, 😚, 😘, 🥰, 😍, 🤩, 😡, 😠, 🤬, 😒, 😱, 😬, 🙄, 🤔, 👀, 😴
        Avoid using the word baby, honey, sweetie and such
        Avoid using ... (elipses)
        Keep your answers short and precise
        '''
        
        messages = [
            {"role": "system", "content": sys_query},
            {"role": "user", "content": message}
        ]
    else:
        messages = messages + [{"role": "user", "content": message}]
        
    response = client.chat.completions.create(
        model=GROQ_API_MODEL,
        messages=messages
    ).choices[0].message.content
    
    messages = messages + [{"role": "assistant", "content": response}]
    
    return response, messages