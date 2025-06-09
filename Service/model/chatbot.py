from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatZhipuAI

from Service.config import chatbot_model, chatbot_temperature
from Service.api_key import *

# Initialize the ChatZhipuAI model
chat_model = ChatZhipuAI(
    model=chatbot_model,
    temperature=chatbot_temperature
    )

def chatbot(query: str, context: str, prompt: str) -> str:
    global chatbot_model
    
    # chat_model = ChatZhipuAI(
    #     model=chatbot_model,
    #     temperature=chatbot_temperature
    #     )
    
    prompt = ChatPromptTemplate.from_template(template=prompt)
    formatted_prompt = prompt.format(context=context, input=query)

    # print("formatted_prompt: ", formatted_prompt)
    
    # Get the response from the chatbot
    response = chat_model.invoke(formatted_prompt)
    # print("response: ", response)
    return response.content