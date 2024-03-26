import warnings
warnings.filterwarnings("ignore")
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_together import Together
import os
def together_Ai(model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
                temperature=0.0, tokens=192):
    """
    Create and initialize a Together AI language model.

    Parameters:
    - model_name (str, optional): The name of the Together AI language model.
    - temperature (float, optional): The parameter for randomness in text generation.
    - tokens (int, optional): The maximum number of tokens to generate.

    Returns:
    - llm (Together): The initialized Together AI language model.
    """

    api_key = "519b88e82f4652cef4b0fa8b249529369081160a1da9bf5cef63e0c0c996329a"

    model_name = "togethercomputer/llama-2-7b-chat"

    llm = Together(
        model=model_name,
        temperature=temperature,
        max_tokens=tokens,
        together_api_key=api_key
    )

    return llm
llm=together_Ai()
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