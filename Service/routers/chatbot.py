from fastapi import APIRouter
from Service.common.http.chatbot_request import ChatbotRequest
from Service.common.http.chatbot_response import ChatbotResponse
from Service.common.http.llm_ask_request import LLMAskRequest
from Service.services.chatbot_service import chatbot_service_logic
from Service.services.llm_ask_service import llm_ask

router = APIRouter()

@router.post("/chatbot", response_model=ChatbotResponse)
async def chat_model(request: ChatbotRequest):
    try:

        print("chatbot service was called!")
        answer = await chatbot_service_logic(request)
        return ChatbotResponse(response=answer)
    except:
        return ChatbotResponse(response="Error in chatbot api")

# 和大语言模型聊天, 需要传入用户(老师)的id和学校
@router.post("/llmAsk", response_model=ChatbotResponse)
async def llm_ask_model(request: LLMAskRequest) -> ChatbotResponse:
    try:
        answer = await llm_ask(request)
        return ChatbotResponse(response=answer)
    except:
        return ChatbotResponse(response="Error in llm ask api.")
    