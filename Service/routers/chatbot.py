from fastapi import APIRouter
from Service.common.http.chatbot_request import ChatbotRequest
from Service.common.http.chatbot_response import ChatbotResponse
from Service.common.http.llm_chat_request import LLMChatRequest
from Service.services.chatbot_service import chatbot_service_logic
from Service.services.llm_chat_service import llm_chat

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
@router.post("/llm-chat", response_model=ChatbotResponse)
async def llm_ask_model(request: LLMChatRequest) -> ChatbotResponse:
    try:
        answer = await llm_chat(request)
        return ChatbotResponse(response=answer)
    except:
        return ChatbotResponse(response="Error in llm ask api.")
    